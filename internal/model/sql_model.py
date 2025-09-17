create_categories_table = """
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    
    name TEXT NOT NULL,
    prompt_for_image_style TEXT NOT NULL,
    prompt_for_text_style TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_video_cuts_table = """
CREATE TABLE IF NOT EXISTS video_cuts (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    organization_id INTEGER NOT NULL,
    
    creator_id INTEGER NOT NULL,
    moderator_id INTEGER DEFAULT NULL,
    inst_source_id INTEGER,
    youtube_source_id INTEGER,
    
    youtube_video_reference TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    video_fid TEXT DEFAULT '',
    video_name TEXT DEFAULT '',
    
    vizard_rub_cost INTEGER DEFAULT 0,
    moderation_status TEXT DEFAULT 'на модерации',
    moderation_comment TEXT DEFAULT '',
    
    time_for_publication TIMESTAMP,
    publication_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_publications_table = """
CREATE TABLE IF NOT EXISTS publications (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    
    creator_id INTEGER NOT NULL,
    moderator_id INTEGER DEFAULT NULL,
    vk_source_id INTEGER,
    tg_source_id INTEGER,
    
    text_reference TEXT NOT NULL,
    name TEXT NOT NULL,
    text TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    image_fid TEXT,
    image_name TEXT,
    
    openai_rub_cost INTEGER DEFAULT 0,
    
    moderation_status TEXT DEFAULT 'на модерации',
    moderation_comment TEXT DEFAULT '',
    
    time_for_publication TIMESTAMP,
    publication_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_autopostings_table = """
CREATE TABLE IF NOT EXISTS autopostings (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    
    enabled bool DEFAULT FALSE,
    filter_prompt TEXT NOT NULL,
    rewrite_prompt TEXT NOT NULL,
    tg_channels TEXT[] DEFAULT '{}',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

drop_categories_table = """
DROP TABLE IF EXISTS categories CASCADE;
"""

drop_video_cuts_table = """
DROP TABLE IF EXISTS video_cuts CASCADE;
"""

drop_publications_table = """
DROP TABLE IF EXISTS publications CASCADE;
"""

drop_autopostings_table = """
DROP TABLE IF EXISTS autopostings CASCADE;
"""

create_organization_tables_queries = [
    create_categories_table,
    create_video_cuts_table,
    create_publications_table,
    create_autopostings_table,
]

drop_organization_tables_queries = [
    drop_autopostings_table,
    drop_publications_table,
    drop_video_cuts_table,
    drop_categories_table,
]