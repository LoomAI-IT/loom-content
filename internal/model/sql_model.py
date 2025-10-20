create_categories_table = """
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,

    name TEXT NOT NULL,
    hint TEXT NOT NULL,

    goal TEXT NOT NULL,
    tone_of_voice TEXT[] DEFAULT '{}',
    brand_rules TEXT[] DEFAULT '{}',

    creativity_level INTEGER DEFAULT 5,
    audience_segment TEXT NOT NULL,

    len_min INTEGER NOT NULL,
    len_max INTEGER NOT NULL,

    n_hashtags_min INTEGER NOT NULL,
    n_hashtags_max INTEGER NOT NULL,

    cta_type TEXT NOT NULL,
    cta_strategy JSONB DEFAULT '{}',

    good_samples JSONB[] DEFAULT '{}',
    bad_samples JSONB[] DEFAULT '{}',
    additional_info JSONB[] DEFAULT '{}',

    prompt_for_image_style TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_video_cuts_table = """
CREATE TABLE IF NOT EXISTS video_cuts (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    organization_id INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    moderator_id INTEGER DEFAULT 0,
    
    inst_source BOOLEAN DEFAULT FALSE,
    youtube_source BOOLEAN DEFAULT FALSE,
    
    youtube_video_reference TEXT NOT NULL,
    name TEXT DEFAULT '',
    description TEXT DEFAULT '',
    transcript TEXT DEFAULT '',
    tags TEXT[] DEFAULT '{}',
    video_fid TEXT DEFAULT '',
    video_name TEXT DEFAULT '',
    original_url TEXT DEFAULT '',
    
    vizard_rub_cost INTEGER DEFAULT 0,
    moderation_status TEXT DEFAULT '',
    moderation_comment TEXT DEFAULT '',
    
    publication_at TIMESTAMP DEFAULT NULL,
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
    vk_source BOOLEAN DEFAULT FALSE,
    tg_source BOOLEAN DEFAULT FALSE,
    vk_link TEXT DEFAULT '',
    tg_link TEXT DEFAULT '',
    
    text_reference TEXT NOT NULL,
    text TEXT NOT NULL,
    image_fid TEXT,
    image_name TEXT,
    
    openai_rub_cost INTEGER DEFAULT 0,
    
    moderation_status TEXT DEFAULT '',
    moderation_comment TEXT DEFAULT '',
    
    publication_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_autopostings_table = """
CREATE TABLE IF NOT EXISTS autopostings (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    autoposting_category_id INTEGER NOT NULL,

    period_in_hours INTEGER NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    filter_prompt TEXT NOT NULL,
    tg_channels TEXT[] DEFAULT '{}',
    required_moderation BOOLEAN DEFAULT FALSE,
    need_image BOOLEAN DEFAULT FALSE,

    last_active TIMESTAMP DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_viewed_telegram_posts_table = """
CREATE TABLE IF NOT EXISTS viewed_telegram_posts (
    id SERIAL PRIMARY KEY,
    autoposting_id INTEGER NOT NULL,
    
    tg_channel_username TEXT NOT NULL,
    link TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_autoposting_categories_table = """
CREATE TABLE IF NOT EXISTS autoposting_categories (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    
    name TEXT NOT NULL,
    prompt_for_image_style TEXT NOT NULL,

    goal TEXT NOT NULL,
    
    structure_skeleton TEXT[] NOT NULL,
    structure_flex_level_min INTEGER NOT NULL,
    structure_flex_level_max INTEGER NOT NULL,
    structure_flex_level_comment TEXT NOT NULL,
    
    must_have TEXT[] NOT NULL,
    must_avoid TEXT[] NOT NULL,
    
    social_networks_rules TEXT NOT NULL,
    
    len_min INTEGER NOT NULL,
    len_max INTEGER NOT NULL,
    
    n_hashtags_min INTEGER NOT NULL,
    n_hashtags_max INTEGER NOT NULL,
    
    cta_type TEXT NOT NULL,
    tone_of_voice TEXT[] DEFAULT '{}',
    
    brand_rules TEXT[] DEFAULT '{}',
    good_samples JSONB[] NOT NULL,
    
    additional_info TEXT[] NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_youtubes_table = """
CREATE TABLE IF NOT EXISTS youtubes (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    autoselect BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_instagrams_table = """
CREATE TABLE IF NOT EXISTS instagrams (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    autoselect BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_telegrams_table = """
CREATE TABLE IF NOT EXISTS telegrams (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    autoselect BOOLEAN DEFAULT TRUE,
    tg_channel_username TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_vkontakte_table = """
CREATE TABLE IF NOT EXISTS vkontakte (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    autoselect BOOLEAN DEFAULT TRUE,

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

drop_youtubes_table = """
DROP TABLE IF EXISTS youtubes CASCADE;
"""

drop_instagrams_table = """
DROP TABLE IF EXISTS instagrams CASCADE;
"""

drop_telegrams_table = """
DROP TABLE IF EXISTS telegrams CASCADE;
"""

drop_vkontakte_table = """
DROP TABLE IF EXISTS vkontakte CASCADE;
"""

drop_viewed_telegram_posts_table = """
DROP TABLE IF EXISTS viewed_telegram_posts CASCADE;
"""

drop_autoposting_categories_table = """
DROP TABLE IF EXISTS autoposting_categories CASCADE;
"""

create_organization_tables_queries = [
    create_categories_table,
    create_video_cuts_table,
    create_publications_table,
    create_autopostings_table,
    create_youtubes_table,
    create_instagrams_table,
    create_telegrams_table,
    create_vkontakte_table,
    create_viewed_telegram_posts_table,
    create_autoposting_categories_table
]

drop_queries = [
    drop_autopostings_table,
    drop_publications_table,
    drop_video_cuts_table,
    drop_categories_table,
    drop_youtubes_table,
    drop_instagrams_table,
    drop_telegrams_table,
    drop_vkontakte_table,
    drop_viewed_telegram_posts_table,
    drop_autoposting_categories_table
]