from internal import interface, model
from internal.migration.base import Migration, MigrationInfo


class UpdateCategorySchema(Migration):

    def get_info(self) -> MigrationInfo:
        return MigrationInfo(
            version="v0_0_22",
            name="update_category_schema",
            depends_on="v0_0_15"
        )

    async def up(self, db: interface.IDB):
        queries = [
            add_new_category_fields,
            convert_additional_info_to_jsonb,
            drop_old_category_fields
        ]

        await db.multi_query(queries)

    async def down(self, db: interface.IDB):
        queries = [
            restore_old_category_fields,
            convert_additional_info_to_text_array,
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
    ADD COLUMN IF NOT EXISTS bad_samples JSONB[] DEFAULT '{}';
"""

convert_additional_info_to_jsonb = """
-- Create temporary column
ALTER TABLE categories ADD COLUMN IF NOT EXISTS additional_info_new JSONB[] DEFAULT '{}';

-- Convert TEXT[] to JSONB[] by wrapping each string in a JSON object
UPDATE categories
SET additional_info_new = ARRAY(
    SELECT jsonb_build_object('text', elem)
    FROM unnest(additional_info) AS elem
)
WHERE additional_info IS NOT NULL AND array_length(additional_info, 1) > 0;

-- Drop old column and rename new one
ALTER TABLE categories DROP COLUMN IF EXISTS additional_info;
ALTER TABLE categories RENAME COLUMN additional_info_new TO additional_info;
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

convert_additional_info_to_text_array = """
-- Create temporary column
ALTER TABLE categories ADD COLUMN IF NOT EXISTS additional_info_old TEXT[] DEFAULT '{}';

-- Convert JSONB[] to TEXT[] by extracting 'text' field or converting to string
UPDATE categories
SET additional_info_old = ARRAY(
    SELECT COALESCE(elem->>'text', elem::text)
    FROM unnest(additional_info) AS elem
)
WHERE additional_info IS NOT NULL AND array_length(additional_info, 1) > 0;

-- Drop new column and rename old one
ALTER TABLE categories DROP COLUMN IF EXISTS additional_info;
ALTER TABLE categories RENAME COLUMN additional_info_old TO additional_info;
"""

drop_new_category_fields = """
ALTER TABLE categories
    DROP COLUMN IF EXISTS hint,
    DROP COLUMN IF EXISTS creativity_level,
    DROP COLUMN IF EXISTS audience_segment,
    DROP COLUMN IF EXISTS cta_strategy,
    DROP COLUMN IF EXISTS bad_samples;
"""
