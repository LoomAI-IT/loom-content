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
    hint,
    goal,
    tone_of_voice,
    brand_rules,
    creativity_level,
    audience_segment,
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
    :hint,
    :goal,
    :tone_of_voice,
    :brand_rules,
    :creativity_level,
    :audience_segment,
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
    hint = COALESCE(:hint, hint),
    goal = COALESCE(:goal, goal),
    tone_of_voice = COALESCE(:tone_of_voice, tone_of_voice),
    brand_rules = COALESCE(:brand_rules, brand_rules),
    creativity_level = COALESCE(:creativity_level, creativity_level),
    audience_segment = COALESCE(:audience_segment, audience_segment),
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
