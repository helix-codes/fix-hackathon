import "dotenv/config";

import { deriveObjectId } from "../utils/derive-object-id";
import {
    GAME_CHARACTER_ID,
    STORAGE_A_ITEM_ID,
} from "../utils/constants";
import {
    getEnvConfig,
    handleError,
    hydrateWorldConfig,
    initializeContext,
} from "../utils/helper";
import { getCharacterOwnerCap } from "../character/helper";
import { getOwnerCap as getStorageOwnerCap } from "../storage-unit/helper";

async function main() {
    try {
        const env = getEnvConfig();
        const ctx = initializeContext(env.network, env.adminExportedKey);
        await hydrateWorldConfig(ctx);

        const { client, config, address } = ctx;
        const characterId = deriveObjectId(config.objectRegistry, GAME_CHARACTER_ID, config.packageId);
        const storageUnitId = deriveObjectId(
            config.objectRegistry,
            STORAGE_A_ITEM_ID,
            config.packageId
        );

        const storageOwnerCapId = await getStorageOwnerCap(storageUnitId, client, config, address);
        const characterOwnerCapId = await getCharacterOwnerCap(characterId, client, config, address);

        const storageUnit = await client.getObject({
            id: storageUnitId,
            options: { showContent: true, showType: true },
        });
        const dynamicFields = await client.getDynamicFields({
            parentId: storageUnitId,
        });

        const dynamicObjects = [];
        for (const field of dynamicFields.data) {
            const object = await client.getDynamicFieldObject({
                parentId: storageUnitId,
                name: field.name,
            });
            dynamicObjects.push({
                field,
                object,
            });
        }

        console.log(
            JSON.stringify(
                {
                    storage_unit_id: storageUnitId,
                    character_id: characterId,
                    storage_owner_cap_id: storageOwnerCapId,
                    character_owner_cap_id: characterOwnerCapId,
                    storage_unit: storageUnit,
                    dynamic_fields: dynamicFields,
                    dynamic_objects: dynamicObjects,
                },
                null,
                2
            )
        );
    } catch (error) {
        handleError(error);
    }
}

main();
