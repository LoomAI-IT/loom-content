
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
    tags,
    video_name,
    video_fid
)
VALUES (
    :project_id,
    :organization_id,
    :creator_id,
    :youtube_video_reference,
    :name,
    :description,
    :tags,
    :video_name,
    :video_fid
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