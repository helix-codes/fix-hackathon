import "dotenv/config";

import { Transaction } from "@mysten/sui/transactions";
import { SuiJsonRpcClient } from "@mysten/sui/jsonRpc";
import { Ed25519Keypair } from "@mysten/sui/keypairs/ed25519";
import { getConfig, MODULES } from "../utils/config";
import { deriveObjectId } from "../utils/derive-object-id";
import {
    GAME_CHARACTER_B_ID,
    GAME_CHARACTER_ID,
    PLANNER_RESOURCES,
    STORAGE_A_ITEM_ID,
    type PlannerResourceSeed,
} from "../utils/constants";
import {
    getEnvConfig,
    handleError,
    hydrateWorldConfig,
    initializeContext,
    requireEnv,
    shareHydratedConfig,
} from "../utils/helper";
import { executeSponsoredTransaction } from "../utils/transaction";
import { getCharacterOwnerCap } from "../character/helper";
import { getOwnerCap as getStorageOwnerCap } from "./helper";

const DELAY_MS = 1500;


async function mintPlannerResource(
    storageUnit: string,
    characterId: string,
    ownerCapId: string,
    playerAddress: string,
    resource: PlannerResourceSeed,
    adminAddress: string,
    client: SuiJsonRpcClient,
    playerKeypair: Ed25519Keypair,
    adminKeypair: Ed25519Keypair,
    config: ReturnType<typeof getConfig>,
    ownerCapType: string
) {
    const tx = new Transaction();
    tx.setSender(playerAddress);
    tx.setGasOwner(adminAddress);

    const [ownerCap, receipt] = tx.moveCall({
        target: `${config.packageId}::${MODULES.CHARACTER}::borrow_owner_cap`,
        typeArguments: [ownerCapType],
        arguments: [tx.object(characterId), tx.object(ownerCapId)],
    });

    tx.moveCall({
        target: `${config.packageId}::${MODULES.STORAGE_UNIT}::game_item_to_chain_inventory`,
        typeArguments: [ownerCapType],
        arguments: [
            tx.object(storageUnit),
            tx.object(config.adminAcl),
            tx.object(characterId),
            ownerCap,
            tx.pure.u64(resource.itemId),
            tx.pure.u64(resource.typeId),
            tx.pure.u64(resource.volume),
            tx.pure.u32(resource.quantity),
        ],
    });

    tx.moveCall({
        target: `${config.packageId}::${MODULES.CHARACTER}::return_owner_cap`,
        typeArguments: [ownerCapType],
        arguments: [tx.object(characterId), ownerCap, receipt],
    });

    const result = await executeSponsoredTransaction(
        tx,
        client,
        playerKeypair,
        adminKeypair,
        playerAddress,
        adminAddress,
        { showEvents: true }
    );

    console.log(
        `Seeded planner resource ${resource.label} (${resource.typeId.toString()}) x${resource.quantity}`
    );
    console.log("Transaction digest:", result.digest);
}


async function main() {
    try {
        const env = getEnvConfig();
        const adminCtx = initializeContext(env.network, env.adminExportedKey);
        await hydrateWorldConfig(adminCtx);
        const playerAKey = requireEnv("PLAYER_A_PRIVATE_KEY");
        const playerACtx = initializeContext(env.network, playerAKey);
        shareHydratedConfig(adminCtx, playerACtx);
        const playerBKey = requireEnv("PLAYER_B_PRIVATE_KEY");
        const playerBCtx = initializeContext(env.network, playerBKey);
        shareHydratedConfig(adminCtx, playerBCtx);

        const { client, keypair: adminKeypair, config } = adminCtx;
        const adminAddress = adminKeypair.getPublicKey().toSuiAddress();
        const storageUnit = deriveObjectId(
            config.objectRegistry,
            STORAGE_A_ITEM_ID,
            config.packageId
        );
        const storageOwnerCapId = await getStorageOwnerCap(
            storageUnit,
            client,
            config,
            playerACtx.address
        );
        if (!storageOwnerCapId) {
            throw new Error(`OwnerCap not found for ${storageUnit}`);
        }

        const characterAId = deriveObjectId(
            config.objectRegistry,
            GAME_CHARACTER_ID,
            config.packageId
        );
        const characterBId = deriveObjectId(
            config.objectRegistry,
            GAME_CHARACTER_B_ID,
            config.packageId
        );
        const characterBOwnerCapId = await getCharacterOwnerCap(
            characterBId,
            client,
            config,
            playerBCtx.address
        );
        const existingTypeIds = await getExistingStorageTypeIds(storageUnit, client);

        for (const resource of PLANNER_RESOURCES) {
            if (existingTypeIds.has(resource.typeId.toString())) {
                console.log(
                    `Planner resource ${resource.label} (${resource.typeId.toString()}) already present, skipping`
                );
                continue;
            }

            if (resource.inventory === "character_owned") {
                if (!characterBOwnerCapId) {
                    throw new Error(`Character owner cap not found for ${characterBId}`);
                }
                await mintPlannerResource(
                    storageUnit,
                    characterBId,
                    characterBOwnerCapId,
                    playerBCtx.address,
                    resource,
                    adminAddress,
                    client,
                    playerBCtx.keypair,
                    adminKeypair,
                    config,
                    `${config.packageId}::${MODULES.CHARACTER}::Character`
                );
                await delay(DELAY_MS);
                continue;
            }

            await mintPlannerResource(
                storageUnit,
                characterAId,
                storageOwnerCapId,
                playerACtx.address,
                resource,
                adminAddress,
                client,
                playerACtx.keypair,
                adminKeypair,
                config,
                `${config.packageId}::${MODULES.STORAGE_UNIT}::StorageUnit`
            );
            await delay(DELAY_MS);
        }
    } catch (error) {
        handleError(error);
    }
}

async function getExistingStorageTypeIds(
    storageUnitId: string,
    client: SuiJsonRpcClient
): Promise<Set<string>> {
    const dynamicFields = await client.getDynamicFields({
        parentId: storageUnitId,
    });
    const typeIds = new Set<string>();
    for (const field of dynamicFields.data) {
        const object = await client.getDynamicFieldObject({
            parentId: storageUnitId,
            name: field.name,
        });
        const contents =
            object.data?.content?.dataType === "moveObject"
                ? ((object.data.content.fields as any)?.value?.fields?.items?.fields?.contents ?? [])
                : [];
        for (const entry of contents) {
            const typeId = entry?.fields?.value?.fields?.type_id;
            if (typeId !== undefined && typeId !== null) {
                typeIds.add(String(typeId));
            }
        }
    }
    return typeIds;
}

function delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

main();
