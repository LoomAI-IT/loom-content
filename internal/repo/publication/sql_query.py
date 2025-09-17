# ПУБЛИКАЦИИ
create_publication = """
INSERT INTO publications (
    organization_id,
    category_id,
    creator_id,
    text_reference,
    name,
    text,
    tags,
    moderation_status
)
VALUES (
    :organization_id,
    :category_id,
    :creator_id,
    :text_reference,
    :name,
    :text,
    :tags,
    :moderation_status
)
RETURNING id;
"""

change_publication = """
UPDATE publications
SET 
    moderator_id = COALESCE(:moderator_id, moderator_id),
    name = COALESCE(:name, name),
    text = COALESCE(:text, text),
    tags = COALESCE(:tags, tags),
    moderation_status = COALESCE(:moderation_status, moderation_status),
    moderation_comment = COALESCE(:moderation_comment, moderation_comment),
    time_for_publication = COALESCE(:time_for_publication, time_for_publication),
    publication_at = COALESCE(:publication_at, publication_at),
    image_fid = COALESCE(:image_fid, image_fid),
    image_name = COALESCE(:image_name, image_name)
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
    prompt_for_text_style
)
VALUES (
    :organization_id,
    :name,
    :prompt_for_image_style,
    :prompt_for_text_style
)
RETURNING id;
"""

update_category = """
UPDATE categories
SET 
    name = COALESCE(:name, name),
    prompt_for_image_style = COALESCE(:prompt_for_image_style, prompt_for_image_style),
    prompt_for_text_style = COALESCE(:prompt_for_text_style, prompt_for_text_style)
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

# НАРЕЗКА
create_video_cut = """
INSERT INTO video_cuts (
    project_id,
    organization_id,
    creator_id,
    youtube_video_reference,
    name,
    description,
    tags,
    time_for_publication,
    moderation_status
)
VALUES (
    :project_id,
    :organization_id,
    :creator_id,
    :youtube_video_reference,
    :name,
    :description,
    :tags,
    :time_for_publication,
    'draft'
)
RETURNING id;
"""

change_video_cut = """
UPDATE video_cuts
SET 
    moderator_id = COALESCE(:moderator_id, moderator_id),
    inst_source_id = COALESCE(:inst_source_id, inst_source_id),
    youtube_source_id = COALESCE(:youtube_source_id, youtube_source_id),
    name = COALESCE(:name, name),
    description = COALESCE(:description, description),
    tags = COALESCE(:tags, tags),
    moderation_status = COALESCE(:moderation_status, moderation_status),
    moderation_comment = COALESCE(:moderation_comment, moderation_comment),
    time_for_publication = COALESCE(:time_for_publication, time_for_publication)
WHERE id = :video_cut_id;
"""

add_vizard_rub_cost_to_video_cut = """
UPDATE video_cuts
SET vizard_rub_cost = vizard_rub_cost + :amount_rub
WHERE id = :video_cut_id;
"""

get_video_cut_by_id = """
SELECT * FROM video_cuts
WHERE id = :video_cut_id;
"""

get_video_cuts_by_organization = """
SELECT * FROM video_cuts
WHERE organization_id = :organization_id
ORDER BY created_at DESC;
"""