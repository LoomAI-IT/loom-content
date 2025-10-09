from internal import interface, model
from internal.migration.base import Migration, MigrationInfo


class AddLinkToPublication(Migration):

    def get_info(self) -> MigrationInfo:
        return MigrationInfo(
            version="v0_0_15",
            name="add_link_to_publication",
            depends_on="v0_0_1"
        )

    async def up(self, db: interface.IDB):
        queries = [
            alter_publication_add_fields
        ]

        await db.multi_query(queries)

    async def down(self, db: interface.IDB):
        queries = [
            alter_publication_drop_new_fields
        ]

        await db.multi_query(queries)

alter_publication_add_fields = """
ALTER TABLE publications
    ADD COLUMN IF NOT EXISTS vk_link TEXT DEFAULT '',
    ADD COLUMN IF NOT EXISTS tg_link TEXT DEFAULT '';
"""

alter_publication_drop_new_fields = """
ALTER TABLE publications
    DROP COLUMN IF EXISTS vk_link,
    DROP COLUMN IF EXISTS tg_link;
"""
