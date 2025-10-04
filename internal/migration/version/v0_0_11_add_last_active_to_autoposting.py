from internal import interface
from internal.migration.base import Migration, MigrationInfo


class AddLastActiveToAutopostingMigration(Migration):

    def get_info(self) -> MigrationInfo:
        return MigrationInfo(
            version="v0_0_11",
            name="add_last_active_to_autoposting",
            depends_on="v0_0_8"
        )

    async def up(self, db: interface.IDB):
        await db.multi_query([
            add_last_active_column,
            add_link_column
        ])

    async def down(self, db: interface.IDB):
        await db.multi_query([
            drop_last_active_column,
            drop_link_column
        ])


add_last_active_column = """
ALTER TABLE autopostings
    ADD COLUMN IF NOT EXISTS last_active TIMESTAMP,
"""

add_link_column = """
ALTER TABLE viewed_telegram_posts
    ADD COLUMN IF NOT EXISTS link TEXT NOT NULL DEFAULT '';
"""

drop_last_active_column = """
ALTER TABLE autopostings
    DROP COLUMN IF EXISTS last_active,
"""

drop_link_column = """
ALTER TABLE viewed_telegram_posts
    DROP COLUMN IF EXISTS link;
"""
