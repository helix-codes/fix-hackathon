import "dotenv/config";

import { deriveObjectId } from "../utils/derive-object-id";
import {
    GAME_CHARACTER_ID,
    GATE_ITEM_ID_1,
    GATE_ITEM_ID_2,
    NWN_ITEM_ID,
    PLANNER_RESOURCES,
    STORAGE_A_ITEM_ID,
} from "../utils/constants";
import { getEnvConfig, handleError, hydrateWorldConfig, initializeContext } from "../utils/helper";
import { getCharacterOwnerCap } from "../character/helper";
import {
    getAssemblyTypes,
    getConnectedAssemblies,
    getFuelQuantity,
    isNetworkNodeOnline,
} from "../network-node/helper";
import { getOwnerCap as getStorageOwnerCap } from "../storage-unit/helper";

type InventoryKind = "storage_owner" | "character_owned" | "open_storage" | "unknown";

type InventoryEntrySummary = {
    inventory_key: string;
    inventory_kind: InventoryKind;
    type_id: string;
    item_id: string;
    quantity: number;
    volume: string;
    tenant: string;
};

type LocalnetSnapshot = {
    tenant: string;
    world_package_id: string;
    object_registry_id: string;
    character_id: string;
    expected_structure_ids: {
        network_node: string;
        storage_unit: string;
        gate_one: string;
        gate_two: string;
    };
    storage_owner_cap_id: string | null;
    character_owner_cap_id: string | null;
    network_node: {
        object_id: string;
        fuel_quantity: number | null;
        is_online: boolean;
    };
    connected_structures: Array<{ object_id: string; kind: string }>;
    planner_resource_catalog: Array<{
        label: string;
        type_id: string;
        item_id: string;
        quantity: number;
        inventory: string;
        approximate_richness: string;
        freshness_hours: number;
        exact_coordinates: string;
        full_scan_payload: string;
        recommended_route: string;
        price_units: number;
    }>;
    storage_inventory_entries: InventoryEntrySummary[];
};

async function main() {
    try {
        const snapshot = await buildLocalnetSnapshot();
        console.log(JSON.stringify(snapshot, null, 2));
    } catch (error) {
        handleError(error);
    }
}

async function buildLocalnetSnapshot(): Promise<LocalnetSnapshot> {
    const env = getEnvConfig();
    const ctx = initializeContext(env.network, env.adminExportedKey);
    await hydrateWorldConfig(ctx);

    const { client, config, address } = ctx;
    const characterId = deriveObjectId(config.objectRegistry, GAME_CHARACTER_ID, config.packageId);
    const networkNodeId = deriveObjectId(config.objectRegistry, NWN_ITEM_ID, config.packageId);
    const storageUnitId = deriveObjectId(config.objectRegistry, STORAGE_A_ITEM_ID, config.packageId);
    const gateOneId = deriveObjectId(config.objectRegistry, GATE_ITEM_ID_1, config.packageId);
    const gateTwoId = deriveObjectId(config.objectRegistry, GATE_ITEM_ID_2, config.packageId);
    const storageOwnerCapId = await getStorageOwnerCap(storageUnitId, client, config, address);
    const characterOwnerCapId = await getCharacterOwnerCap(characterId, client, config, address);

    await assertWorldPackageReachable(client, config.packageId);

    const connectedAssemblies =
        (await getConnectedAssemblies(networkNodeId, client, config, address)) || [];
    const assemblyTypes = await getAssemblyTypes(connectedAssemblies, client);
    const fuelQuantity = await getFuelQuantity(networkNodeId, client, config, address);
    const networkNodeOnline = await isNetworkNodeOnline(networkNodeId, client, config, address);
    const inventoryEntries = await loadStorageInventoryEntries(
        storageUnitId,
        client,
        storageOwnerCapId,
        characterOwnerCapId
    );

    return {
        tenant: env.tenant,
        world_package_id: config.packageId,
        object_registry_id: config.objectRegistry,
        character_id: characterId,
        expected_structure_ids: {
            network_node: networkNodeId,
            storage_unit: storageUnitId,
            gate_one: gateOneId,
            gate_two: gateTwoId,
        },
        storage_owner_cap_id: storageOwnerCapId,
        character_owner_cap_id: characterOwnerCapId,
        network_node: {
            object_id: networkNodeId,
            fuel_quantity: fuelQuantity === null ? null : Number(fuelQuantity),
            is_online: networkNodeOnline,
        },
        connected_structures: assemblyTypes.map((entry) => ({
            object_id: entry.id,
            kind: entry.kind,
        })),
        planner_resource_catalog: PLANNER_RESOURCES.map((resource) => ({
            label: resource.label,
            type_id: resource.typeId.toString(),
            item_id: resource.itemId.toString(),
            quantity: resource.quantity,
            inventory: resource.inventory,
            approximate_richness: resource.approximateRichness,
            freshness_hours: resource.freshnessHours,
            exact_coordinates: resource.exactCoordinates,
            full_scan_payload: resource.fullScanPayload,
            recommended_route: resource.recommendedRoute,
            price_units: resource.priceUnits,
        })),
        storage_inventory_entries: inventoryEntries,
    };
}

async function assertWorldPackageReachable(
    client: ReturnType<typeof initializeContext>["client"],
    packageId: string
): Promise<void> {
    const worldPackage = await client.getObject({
        id: packageId,
        options: { showType: true },
    });
    if (!worldPackage.data) {
        throw new Error(`World package ${packageId} is not reachable on localnet.`);
    }
}

async function loadStorageInventoryEntries(
    storageUnitId: string,
    client: ReturnType<typeof initializeContext>["client"],
    storageOwnerCapId: string | null,
    characterOwnerCapId: string | null
): Promise<InventoryEntrySummary[]> {
    const storageInventories = await client.getDynamicFields({
        parentId: storageUnitId,
    });
    const inventoryEntries: InventoryEntrySummary[] = [];
    for (const field of storageInventories.data) {
        const fieldObject = await client.getDynamicFieldObject({
            parentId: storageUnitId,
            name: field.name,
        });
        const contents =
            fieldObject.data?.content?.dataType === "moveObject"
                ? ((fieldObject.data.content.fields as any)?.value?.fields?.items?.fields?.contents ??
                  [])
                : [];
        for (const entry of contents) {
            const value = entry?.fields?.value?.fields;
            if (!value) {
                continue;
            }
            inventoryEntries.push({
                inventory_key: String(field.name.value),
                inventory_kind: classifyInventoryKey(
                    String(field.name.value),
                    storageOwnerCapId,
                    characterOwnerCapId
                ),
                type_id: String(value.type_id),
                item_id: String(value.item_id),
                quantity: Number(value.quantity),
                volume: String(value.volume),
                tenant: String(value.tenant),
            });
        }
    }
    return inventoryEntries;
}

function classifyInventoryKey(
    inventoryKey: string,
    storageOwnerCapId: string | null,
    characterOwnerCapId: string | null
): InventoryEntrySummary["inventory_kind"] {
    if (storageOwnerCapId && inventoryKey === storageOwnerCapId) {
        return "storage_owner";
    }
    if (characterOwnerCapId && inventoryKey === characterOwnerCapId) {
        return "character_owned";
    }
    return "open_storage";
}

main();
