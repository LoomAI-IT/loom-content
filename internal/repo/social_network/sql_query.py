# СОЗДАНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
create_youtube = """
INSERT INTO youtubes (
    organization_id
)
VALUES (
    :organization_id
)
RETURNING id;
"""

create_instagram = """
INSERT INTO instagrams (
    organization_id
)
VALUES (
    :organization_id
)
RETURNING id;
"""

create_telegram = """
INSERT INTO telegrams (
    organization_id,
    tg_channel_username
)
VALUES (
    :organization_id,
    :tg_channel_username
)
RETURNING id;
"""

update_telegram = """
UPDATE telegrams
SET 
    tg_channel_username = COALESCE(:tg_channel_username, tg_channel_username),
    autoselect = COALESCE(:autoselect, autoselect)
WHERE organization_id = :organization_id;
"""

delete_telegram = """
DELETE FROM telegrams
WHERE organization_id = :organization_id;
"""

create_vkontakte = """
INSERT INTO vkontakte (
    organization_id
)
VALUES (
    :organization_id
)
RETURNING id;
"""

# ПОЛУЧЕНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
get_youtubes_by_organization = """
SELECT * FROM youtubes
WHERE organization_id = :organization_id
ORDER BY created_at DESC;
"""

get_instagrams_by_organization = """
SELECT * FROM instagrams
WHERE organization_id = :organization_id
ORDER BY created_at DESC;
"""

get_telegrams_by_organization = """
SELECT * FROM telegrams
WHERE organization_id = :organization_id
ORDER BY created_at DESC;
"""

get_vkontakte_by_organization = """
SELECT * FROM vkontakte
WHERE organization_id = :organization_id
ORDER BY created_at DESC;
"""