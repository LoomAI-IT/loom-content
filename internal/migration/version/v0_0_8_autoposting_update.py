from internal import interface
from internal.migration.base import Migration, MigrationInfo


class AutopostingUpdateMigration(Migration):

    def get_info(self) -> MigrationInfo:
        return MigrationInfo(
            version="v0_0_8",
            name="autoposting_update",
            depends_on="v0_0_4"
        )

    async def up(self, db: interface.IDB):
        await db.multi_query([
            create_autoposting_categories_table,
            drop_old_autoposting_columns,
            add_new_autoposting_columns,
            create_viewed_telegram_posts_table
        ])

    async def down(self, db: interface.IDB):
        await db.multi_query([
            drop_viewed_telegram_posts_table,
            drop_new_autoposting_columns,
            restore_old_autoposting_columns,
            drop_autoposting_categories_table
        ])


create_autoposting_categories_table = """
CREATE TABLE IF NOT EXISTS autoposting_categories (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,

    name TEXT NOT NULL,
    prompt_for_image_style TEXT NOT NULL,

    goal TEXT NOT NULL,

    -- Структура контента
    structure_skeleton TEXT[] NOT NULL,
    structure_flex_level_min INTEGER NOT NULL,
    structure_flex_level_max INTEGER NOT NULL,
    structure_flex_level_comment TEXT NOT NULL,

    -- Требования к контенту
    must_have TEXT[] NOT NULL,
    must_avoid TEXT[] NOT NULL,

    -- Правила для соцсетей
    social_networks_rules TEXT NOT NULL,

    -- Ограничения по длине
    len_min INTEGER NOT NULL,
    len_max INTEGER NOT NULL,

    -- Ограничения по хештегам
    n_hashtags_min INTEGER NOT NULL,
    n_hashtags_max INTEGER NOT NULL,

    -- Стиль и тон
    cta_type TEXT NOT NULL,
    tone_of_voice TEXT[] DEFAULT '{}',

    -- Бренд и примеры
    brand_rules TEXT[] DEFAULT '{}',
    good_samples JSONB[] NOT NULL,

    -- Дополнительная информация
    additional_info TEXT[] NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

drop_old_autoposting_columns = """
ALTER TABLE autopostings
    DROP COLUMN IF EXISTS rewrite_prompt;
"""

add_new_autoposting_columns = """
ALTER TABLE autopostings
    ADD COLUMN IF NOT EXISTS autoposting_categories_id INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS period_in_hours INTEGER NOT NULL DEFAULT 0;
"""

create_viewed_telegram_posts_table = """
CREATE TABLE IF NOT EXISTS viewed_telegram_posts (
    id SERIAL PRIMARY KEY,
    autoposting_id INTEGER NOT NULL,

    tg_channel_username TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

drop_viewed_telegram_posts_table = """
DROP TABLE IF EXISTS viewed_telegram_posts;
"""

drop_new_autoposting_columns = """
ALTER TABLE autopostings
    DROP COLUMN IF EXISTS autoposting_categories_id,
    DROP COLUMN IF EXISTS period_in_hours;
"""

restore_old_autoposting_columns = """
ALTER TABLE autopostings
    ADD COLUMN IF NOT EXISTS rewrite_prompt TEXT NOT NULL DEFAULT '';
"""

drop_autoposting_categories_table = """
DROP TABLE IF EXISTS autoposting_categories;
"""
