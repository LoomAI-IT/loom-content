from internal import interface, model
from internal.migration.base import Migration, MigrationInfo


class UpdateCategoriesTableMigration(Migration):

    def get_info(self) -> MigrationInfo:
        return MigrationInfo(
            version="v0_0_4",
            name="update_categories_table",
            depends_on="v0_0_1"
        )

    async def up(self, db: interface.IDB):
        await db.multi_query([
            delete_old_column,
            update_categories_table_up
        ])

    async def down(self, db: interface.IDB):
        await db.multi_query(
            [
                update_categories_table_down,
                return_old_column,
            ]
        )

delete_old_column = """
ALTER TABLE categories DROP COLUMN IF EXISTS prompt_for_text_style;
"""

update_categories_table_up = """
-- Добавляем новые колонки
ALTER TABLE categories 
    ADD COLUMN IF NOT EXISTS goal TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS structure_skeleton TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS structure_flex_level_min INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS structure_flex_level_max INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS structure_flex_level_comment TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS must_have TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS must_avoid TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS social_networks_rules TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS len_min INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS len_max INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS n_hashtags_min INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS n_hashtags_max INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS cta_type TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS tone_of_voice TEXT[] DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS brand_rules TEXT[] DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS good_samples JSONB[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS additional_info TEXT[] NOT NULL DEFAULT '{}';
"""

update_categories_table_down = """
-- Удаляем новые колонки
ALTER TABLE categories 
    DROP COLUMN IF EXISTS goal,
    DROP COLUMN IF EXISTS structure_skeleton,
    DROP COLUMN IF EXISTS structure_flex_level_min,
    DROP COLUMN IF EXISTS structure_flex_level_max,
    DROP COLUMN IF EXISTS structure_flex_level_comment,
    DROP COLUMN IF EXISTS must_have,
    DROP COLUMN IF EXISTS must_avoid,
    DROP COLUMN IF EXISTS social_networks_rules,
    DROP COLUMN IF EXISTS len_min,
    DROP COLUMN IF EXISTS len_max,
    DROP COLUMN IF EXISTS n_hashtags_min,
    DROP COLUMN IF EXISTS n_hashtags_max,
    DROP COLUMN IF EXISTS cta_type,
    DROP COLUMN IF EXISTS tone_of_voice,
    DROP COLUMN IF EXISTS brand_rules,
    DROP COLUMN IF EXISTS good_samples,
    DROP COLUMN IF EXISTS additional_info;

"""

return_old_column = """
ALTER TABLE categories 
    ADD COLUMN IF NOT EXISTS prompt_for_text_style TEXT NOT NULL DEFAULT '';
"""