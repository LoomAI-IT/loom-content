from pydantic import BaseModel


# ПУБЛИКАЦИИ
class GeneratePublicationTextBody(BaseModel):
    category_id: int
    text_reference: str


class TestGeneratePublicationTextBody(BaseModel):
    text_reference: str
    organization_id: int
    name: str
    hint: str

    goal: str
    tone_of_voice: list[str]
    brand_rules: list[str]

    creativity_level: int
    audience_segments: str

    len_min: int
    len_max: int

    n_hashtags_min: int
    n_hashtags_max: int

    cta_type: str
    cta_strategy: dict

    good_samples: list[dict]
    bad_samples: list[dict]
    additional_info: list[dict]

    prompt_for_image_style: str


class RegeneratePublicationTextBody(BaseModel):
    category_id: int
    publication_text: str
    prompt: str | None = None


class GeneratePublicationImageBody(BaseModel):
    category_id: int
    publication_text: str
    text_reference: str
    prompt: str | None = None


class ModeratePublicationBody(BaseModel):
    publication_id: int
    moderator_id: int
    moderation_status: str
    moderation_comment: str = ""


# РУБРИКИ
class CreateCategoryBody(BaseModel):
    organization_id: int
    name: str
    hint: str

    goal: str
    tone_of_voice: list[str]
    brand_rules: list[str]

    creativity_level: int
    audience_segments: str

    len_min: int
    len_max: int

    n_hashtags_min: int
    n_hashtags_max: int

    cta_type: str
    cta_strategy: dict

    good_samples: list[dict]
    bad_samples: list[dict]
    additional_info: list[dict]

    prompt_for_image_style: str


class UpdateCategoryBody(BaseModel):
    name: str = None
    hint: str = None
    goal: str = None
    tone_of_voice: list[str] = None
    brand_rules: list[str] = None

    creativity_level: int = None
    audience_segments: str = None

    len_min: int = None
    len_max: int = None

    n_hashtags_min: int = None
    n_hashtags_max: int = None

    cta_type: str = None
    cta_strategy: dict = None

    good_samples: list[dict] = None
    bad_samples: list[dict] = None
    additional_info: list[dict] = None

    prompt_for_image_style: str = None


# РУБРИКИ ДЛЯ АВТОПОСТИНГА
class CreateAutopostingCategoryBody(BaseModel):
    organization_id: int
    name: str
    prompt_for_image_style: str

    goal: str

    structure_skeleton: list[str]
    structure_flex_level_min: int
    structure_flex_level_max: int
    structure_flex_level_comment: str

    must_have: list[str]
    must_avoid: list[str]

    social_networks_rules: str

    len_min: int
    len_max: int

    n_hashtags_min: int
    n_hashtags_max: int

    cta_type: str
    tone_of_voice: list[str]

    brand_rules: list[str]
    good_samples: list[dict]

    additional_info: list[str]


class UpdateAutopostingCategoryBody(BaseModel):
    name: str = None
    prompt_for_image_style: str = None

    goal: str = None

    structure_skeleton: list[str] = None
    structure_flex_level_min: int = None
    structure_flex_level_max: int = None
    structure_flex_level_comment: str = None

    must_have: list[str] = None
    must_avoid: list[str] = None

    social_networks_rules: str = None

    len_min: int = None
    len_max: int = None

    n_hashtags_min: int = None
    n_hashtags_max: int = None

    cta_type: str = None
    tone_of_voice: list[str] = None

    brand_rules: list[str] = None
    good_samples: list[dict] = None

    additional_info: list[str] = None


# АВТОПОСТИНГ
class CreateAutopostingBody(BaseModel):
    organization_id: int
    autoposting_category_id: int
    period_in_hours: int
    filter_prompt: str
    tg_channels: list[str] = None
    required_moderation: bool = False
    need_image: bool


class UpdateAutopostingBody(BaseModel):
    autoposting_category_id: int = None
    period_in_hours: int = None
    filter_prompt: str = None
    enabled: bool = None
    tg_channels: list[str] = None
    required_moderation: bool = None
    need_image: bool = None
