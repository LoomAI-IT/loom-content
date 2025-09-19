
# НАРЕЗКА
create_vizard_project = """
INSERT INTO video_cuts (
    project_id,
    organization_id,
    creator_id,
    youtube_video_reference
)
VALUES (
    :project_id,
    :organization_id,
    :creator_id,
    :youtube_video_reference
)
RETURNING id;
"""

create_vizard_video_cut = """
INSERT INTO video_cuts (
    project_id,
    organization_id,
    creator_id,
    youtube_video_reference,
    name,
    description,
    transcript,
    tags,
    video_name,
    video_fid,
    original_url,
    vizard_rub_cost,
    moderation_status
)
VALUES (
    :project_id,
    :organization_id,
    :creator_id,
    :youtube_video_reference,
    :name,
    :description,
    :transcript,
    :tags,
    :video_name,
    :video_fid,
    :original_url,
    :vizard_rub_cost,
    'draft'
)
RETURNING id;
"""

change_video_cut = """
UPDATE video_cuts
SET 
    moderator_id = COALESCE(:moderator_id, moderator_id),
    inst_source = COALESCE(:inst_source, inst_source),
    youtube_source = COALESCE(:youtube_source, youtube_source),
    name = COALESCE(:name, name),
    description = COALESCE(:description, description),
    tags = COALESCE(:tags, tags),
    moderation_status = COALESCE(:moderation_status, moderation_status),
    moderation_comment = COALESCE(:moderation_comment, moderation_comment)
WHERE id = :video_cut_id;
"""

delete_video_cut = """
DELETE FROM video_cuts
WHERE id = :video_cut_id;
"""

get_video_cut_by_id = """
SELECT * FROM video_cuts
WHERE id = :video_cut_id;
"""

get_video_cuts_by_project_id = """
SELECT * FROM video_cuts
WHERE project_id = :project_id
ORDER BY created_at DESC;
"""

get_video_cuts_by_organization = """
SELECT * FROM video_cuts
WHERE organization_id = :organization_id
ORDER BY created_at DESC;
"""