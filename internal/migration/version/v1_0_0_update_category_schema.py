from internal import interface
from internal.migration.base import Migration, MigrationInfo


class UpdateCategorySchema(Migration):

    def get_info(self) -> MigrationInfo:
        return MigrationInfo(
            version="v1_0_0",
            name="update_category_schema",
            depends_on="v0_0_15"
        )

    async def up(self, db: interface.IDB):
        queries = [
            add_new_category_fields,
            drop_additional_info_up,
            create_additional_info_up,
            drop_old_category_fields
        ]

        await db.multi_query(queries)

    async def down(self, db: interface.IDB):
        queries = [
            restore_old_category_fields,
            drop_additional_info_down,
            create_additional_info_down,
            drop_new_category_fields
        ]

        await db.multi_query(queries)

# UP migration queries

add_new_category_fields = """
ALTER TABLE categories
    ADD COLUMN IF NOT EXISTS hint TEXT DEFAULT '',
    ADD COLUMN IF NOT EXISTS creativity_level INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS audience_segment TEXT DEFAULT '',
    ADD COLUMN IF NOT EXISTS cta_strategy JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS bad_samples JSONB[] DEFAULT'{}';
"""

drop_additional_info_up = """
ALTER TABLE categories DROP COLUMN IF EXISTS additional_info;
"""

create_additional_info_up = """
ALTER TABLE categories ADD COLUMN additional_info JSONB[] DEFAULT '{}';
"""

drop_old_category_fields = """
ALTER TABLE categories
    DROP COLUMN IF EXISTS structure_skeleton,
    DROP COLUMN IF EXISTS structure_flex_level_min,
    DROP COLUMN IF EXISTS structure_flex_level_max,
    DROP COLUMN IF EXISTS structure_flex_level_comment,
    DROP COLUMN IF EXISTS must_have,
    DROP COLUMN IF EXISTS must_avoid,
    DROP COLUMN IF EXISTS social_networks_rules;
"""

# DOWN migration queries

restore_old_category_fields = """
ALTER TABLE categories
    ADD COLUMN IF NOT EXISTS structure_skeleton TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS structure_flex_level_min INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS structure_flex_level_max INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS structure_flex_level_comment TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS must_have TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS must_avoid TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS social_networks_rules TEXT NOT NULL DEFAULT '';
"""

drop_additional_info_down = """
ALTER TABLE categories DROP COLUMN IF EXISTS additional_info;
"""

create_additional_info_down = """
ALTER TABLE categories ADD COLUMN additional_info TEXT[] DEFAULT '{}';
"""

drop_new_category_fields = """
ALTER TABLE categories
    DROP COLUMN IF EXISTS hint,
    DROP COLUMN IF EXISTS creativity_level,
    DROP COLUMN IF EXISTS audience_segment,
    DROP COLUMN IF EXISTS cta_strategy,
    DROP COLUMN IF EXISTS bad_samples;
"""
