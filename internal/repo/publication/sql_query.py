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
    vk_link = COALESCE(:vk_link, vk_link),
    tg_link = COALESCE(:tg_link, tg_link),
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

delete_publication_by_category_id = """
DELETE FROM publications
WHERE category_id = :category_id;
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
    goal,
    tone_of_voice,
    brand_rules,
    brand_vocabulary,
    tone_variations,
    structure_variations,
    creativity_level,
    experimentation_zones,
    surprise_factors,
    humor_policy,
    audience_segments,
    emotional_palette,
    platform_specific_rules,
    must_have,
    must_avoid,
    len_min,
    len_max,
    n_hashtags_min,
    n_hashtags_max,
    cta_type,
    cta_strategy,
    good_samples,
    bad_samples,
    additional_info,
    prompt_for_image_style
)
VALUES (
    :organization_id,
    :name,
    :goal,
    :tone_of_voice,
    :brand_rules,
    :brand_vocabulary,
    :tone_variations,
    :structure_variations,
    :creativity_level,
    :experimentation_zones,
    :surprise_factors,
    :humor_policy,
    :audience_segments,
    :emotional_palette,
    :platform_specific_rules,
    :must_have,
    :must_avoid,
    :len_min,
    :len_max,
    :n_hashtags_min,
    :n_hashtags_max,
    :cta_type,
    :cta_strategy,
    :good_samples,
    :bad_samples,
    :additional_info,
    :prompt_for_image_style
)
RETURNING id;
"""

update_category = """
UPDATE categories
SET
    name = COALESCE(:name, name),
    goal = COALESCE(:goal, goal),
    tone_of_voice = COALESCE(:tone_of_voice, tone_of_voice),
    brand_rules = COALESCE(:brand_rules, brand_rules),
    brand_vocabulary = COALESCE(:brand_vocabulary, brand_vocabulary),
    tone_variations = COALESCE(:tone_variations, tone_variations),
    structure_variations = COALESCE(:structure_variations, structure_variations),
    creativity_level = COALESCE(:creativity_level, creativity_level),
    experimentation_zones = COALESCE(:experimentation_zones, experimentation_zones),
    surprise_factors = COALESCE(:surprise_factors, surprise_factors),
    humor_policy = COALESCE(:humor_policy, humor_policy),
    audience_segments = COALESCE(:audience_segments, audience_segments),
    emotional_palette = COALESCE(:emotional_palette, emotional_palette),
    platform_specific_rules = COALESCE(:platform_specific_rules, platform_specific_rules),
    must_have = COALESCE(:must_have, must_have),
    must_avoid = COALESCE(:must_avoid, must_avoid),
    len_min = COALESCE(:len_min, len_min),
    len_max = COALESCE(:len_max, len_max),
    n_hashtags_min = COALESCE(:n_hashtags_min, n_hashtags_min),
    n_hashtags_max = COALESCE(:n_hashtags_max, n_hashtags_max),
    cta_type = COALESCE(:cta_type, cta_type),
    cta_strategy = COALESCE(:cta_strategy, cta_strategy),
    good_samples = COALESCE(:good_samples, good_samples),
    bad_samples = COALESCE(:bad_samples, bad_samples),
    additional_info = COALESCE(:additional_info, additional_info),
    prompt_for_image_style = COALESCE(:prompt_for_image_style, prompt_for_image_style)
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

# РУБРИКИ ДЛЯ АВТОПОСТИНГА
create_autoposting_category = """
INSERT INTO autoposting_categories (
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

update_autoposting_category = """
UPDATE autoposting_categories
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
WHERE id = :autoposting_category_id;
"""

delete_autoposting_category = """
DELETE FROM autoposting_categories
WHERE id = :autoposting_category_id;
"""

get_autoposting_category_by_id = """
SELECT * FROM autoposting_categories
WHERE id = :autoposting_category_id;
"""

# АВТОПОСТИНГ
create_autoposting = """
INSERT INTO autopostings (
    organization_id,
    autoposting_category_id,
    period_in_hours,
    filter_prompt,
    tg_channels,
    enabled,
    required_moderation,
    need_image
)
VALUES (
    :organization_id,
    :autoposting_category_id,
    :period_in_hours,
    :filter_prompt,
    :tg_channels,
    FALSE,
    :required_moderation,
    :need_image
)
RETURNING id;
"""

update_autoposting = """
UPDATE autopostings
SET
    autoposting_category_id = COALESCE(:autoposting_category_id, autoposting_category_id),
    period_in_hours = COALESCE(:period_in_hours, period_in_hours),
    filter_prompt = COALESCE(:filter_prompt, filter_prompt),
    enabled = COALESCE(:enabled, enabled),
    tg_channels = COALESCE(:tg_channels, tg_channels),
    required_moderation = COALESCE(:required_moderation, required_moderation),
    need_image = COALESCE(:need_image, need_image),
    last_active = COALESCE(:last_active, last_active)
WHERE id = :autoposting_id;
"""

get_autoposting_by_organization = """
SELECT * FROM autopostings
WHERE organization_id = :organization_id
ORDER BY created_at DESC;
"""

get_autoposting_by_id = """
SELECT * FROM autopostings
WHERE id = :autoposting_id
ORDER BY created_at DESC;
"""

get_all_autopostings = """
SELECT * FROM autopostings
ORDER BY created_at DESC;
"""

delete_autoposting = """
DELETE FROM autopostings
WHERE id = :autoposting_id;
"""

# ПРОСМОТРЕННЫЕ TELEGRAM ПОСТЫ
create_viewed_telegram_post = """
INSERT INTO viewed_telegram_posts (
    autoposting_id,
    tg_channel_username,
    link
)
VALUES (
    :autoposting_id,
    :tg_channel_username,
    :link
)
RETURNING id;
"""

get_viewed_telegram_post = """
SELECT * FROM viewed_telegram_posts
WHERE autoposting_id = :autoposting_id
  AND tg_channel_username = :tg_channel_username;
"""