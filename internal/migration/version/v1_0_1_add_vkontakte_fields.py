from internal import interface
from internal.migration.base import Migration, MigrationInfo


class AddVkontakteFields(Migration):

    def get_info(self) -> MigrationInfo:
        return MigrationInfo(
            version="v1_0_1",
            name="add_vkontakte_fields",
            depends_on="v1_0_0"
        )

    async def up(self, db: interface.IDB):
        queries = [
            add_vkontakte_fields
        ]

        await db.multi_query(queries)

    async def down(self, db: interface.IDB):
        queries = [
            drop_vkontakte_fields
        ]

        await db.multi_query(queries)

# UP migration queries

add_vkontakte_fields = """
ALTER TABLE vkontakte
    ADD COLUMN IF NOT EXISTS access_token TEXT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS refresh_token TEXT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS device_id TEXT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS user_id INTEGER DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS vk_group_id INTEGER DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS vk_group_name TEXT DEFAULT NULL;
"""

# DOWN migration queries

drop_vkontakte_fields = """
ALTER TABLE vkontakte
    DROP COLUMN IF EXISTS access_token,
    DROP COLUMN IF EXISTS refresh_token,
    DROP COLUMN IF EXISTS device_id,
    DROP COLUMN IF EXISTS user_id,
    DROP COLUMN IF EXISTS vk_group_id,
    DROP COLUMN IF EXISTS vk_group_name;
"""
