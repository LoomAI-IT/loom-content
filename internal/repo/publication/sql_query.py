# ПУБЛИКАЦИИ
create_publication = """
INSERT INTO publications (
    organization_id,
    category_id,
    creator_id,
    text_reference,
    text,
    moderation_status
)
VALUES (
    :organization_id,
    :category_id,
    :creator_id,
    :text_reference,
    :text,
    :moderation_status
)
RETURNING id;
"""

change_publication = """
UPDATE publications
SET 
    moderator_id = COALESCE(:moderator_id, moderator_id),
    vk_source = COALESCE(:vk_source, vk_source),
    tg_source = COALESCE(:tg_source, tg_source),
    text = COALESCE(:text, text),
    moderation_status = COALESCE(:moderation_status, moderation_status),
    moderation_comment = COALESCE(:moderation_comment, moderation_comment),
    publication_at = COALESCE(:publication_at, publication_at),
    image_fid = COALESCE(:image_fid, image_fid),
    image_name = COALESCE(:image_name, image_name)
WHERE id = :publication_id;
"""

delete_publication = """
DELETE FROM publications
WHERE id = :publication_id;
"""

add_openai_rub_cost_to_publication = """
UPDATE publications
SET openai_rub_cost = openai_rub_cost + :amount_rub
WHERE id = :publication_id;
"""

get_publication_by_id = """
SELECT * FROM publications
WHERE id = :publication_id;
"""

get_publications_by_organization = """
SELECT * FROM publications
WHERE organization_id = :organization_id
ORDER BY created_at DESC;
"""

# РУБРИКИ
create_category = """
INSERT INTO categories (
    organization_id,
    name,
    prompt_for_image_style,
    goal,
    structure_skeleton,
    structure_flex_level_min,
    structure_flex_level_max,
    structure_flex_level_comment,
    must_have,
    must_avoid,
    social_networks_rules,
    len_min,
    len_max,
    n_hashtags_min,
    n_hashtags_max,
    cta_type,
    tone_of_voice,
    brand_rules,
    good_samples,
    additional_info
)
VALUES (
    :organization_id,
    :name,
    :prompt_for_image_style,
    :goal,
    :structure_skeleton,
    :structure_flex_level_min,
    :structure_flex_level_max,
    :structure_flex_level_comment,
    :must_have,
    :must_avoid,
    :social_networks_rules,
    :len_min,
    :len_max,
    :n_hashtags_min,
    :n_hashtags_max,
    :cta_type,
    :tone_of_voice,
    :brand_rules,
    :good_samples,
    :additional_info
)
RETURNING id;
"""

update_category = """
UPDATE categories
SET
    name = COALESCE(:name, name),
    prompt_for_image_style = COALESCE(:prompt_for_image_style, prompt_for_image_style),
    goal = COALESCE(:goal, goal),
    structure_skeleton = COALESCE(:structure_skeleton, structure_skeleton),
    structure_flex_level_min = COALESCE(:structure_flex_level_min, structure_flex_level_min),
    structure_flex_level_max = COALESCE(:structure_flex_level_max, structure_flex_level_max),
    structure_flex_level_comment = COALESCE(:structure_flex_level_comment, structure_flex_level_comment),
    must_have = COALESCE(:must_have, must_have),
    must_avoid = COALESCE(:must_avoid, must_avoid),
    social_networks_rules = COALESCE(:social_networks_rules, social_networks_rules),
    len_min = COALESCE(:len_min, len_min),
    len_max = COALESCE(:len_max, len_max),
    n_hashtags_min = COALESCE(:n_hashtags_min, n_hashtags_min),
    n_hashtags_max = COALESCE(:n_hashtags_max, n_hashtags_max),
    cta_type = COALESCE(:cta_type, cta_type),
    tone_of_voice = COALESCE(:tone_of_voice, tone_of_voice),
    brand_rules = COALESCE(:brand_rules, brand_rules),
    good_samples = COALESCE(:good_samples, good_samples),
    additional_info = COALESCE(:additional_info, additional_info)
WHERE id = :category_id;
"""

get_category_by_id = """
SELECT * FROM categories
WHERE id = :category_id;
"""

get_categories_by_organization = """
SELECT * FROM categories
WHERE organization_id = :organization_id
ORDER BY created_at DESC;
"""

delete_category = """
DELETE FROM categories
WHERE id = :category_id;
"""

# АВТОПОСТИНГ
create_autoposting = """
INSERT INTO autopostings (
    organization_id,
    filter_prompt,
    rewrite_prompt,
    tg_channels,
    enabled
)
VALUES (
    :organization_id,
    :filter_prompt,
    :rewrite_prompt,
    :tg_channels,
    FALSE
)
RETURNING id;
"""

update_autoposting = """
UPDATE autopostings
SET 
    filter_prompt = COALESCE(:filter_prompt, filter_prompt),
    rewrite_prompt = COALESCE(:rewrite_prompt, rewrite_prompt),
    enabled = COALESCE(:enabled, enabled),
    tg_channels = COALESCE(:tg_channels, tg_channels)
WHERE id = :autoposting_id;
"""

get_autoposting_by_organization = """
SELECT * FROM autopostings
WHERE organization_id = :organization_id
ORDER BY created_at DESC;
"""

delete_autoposting = """
DELETE FROM autopostings
WHERE id = :autoposting_id;
"""