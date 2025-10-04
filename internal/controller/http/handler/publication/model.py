from pydantic import BaseModel


# ПУБЛИКАЦИИ
class GeneratePublicationTextBody(BaseModel):
    category_id: int
    text_reference: str


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
    prompt_for_image_style: str

    goal: str

    # Структура контента
    structure_skeleton: list[str]
    structure_flex_level_min: int
    structure_flex_level_max: int
    structure_flex_level_comment: str

    # Требования к контенту
    must_have: list[str]
    must_avoid: list[str]

    # Правила для соцсетей
    social_networks_rules: str

    # Ограничения по длине
    len_min: int
    len_max: int

    # Ограничения по хештегам
    n_hashtags_min: int
    n_hashtags_max: int

    # Стиль и тон
    cta_type: str
    tone_of_voice: list[str] = []

    # Бренд и примеры
    brand_rules: list[str] = []
    good_samples: list[dict] = []

    # Дополнительная информация
    additional_info: list[str] = []


class UpdateCategoryBody(BaseModel):
    name: str = None
    prompt_for_image_style: str = None

    goal: str = None

    # Структура контента
    structure_skeleton: list[str] = None
    structure_flex_level_min: int = None
    structure_flex_level_max: int = None
    structure_flex_level_comment: str = None

    # Требования к контенту
    must_have: list[str] = None
    must_avoid: list[str] = None

    # Правила для соцсетей
    social_networks_rules: str = None

    # Ограничения по длине
    len_min: int = None
    len_max: int = None

    # Ограничения по хештегам
    n_hashtags_min: int = None
    n_hashtags_max: int = None

    # Стиль и тон
    cta_type: str = None
    tone_of_voice: list[str] = None

    # Бренд и примеры
    brand_rules: list[str] = None
    good_samples: list[dict] = None

    # Дополнительная информация
    additional_info: list[str] = None


# РУБРИКИ ДЛЯ АВТОПОСТИНГА
class CreateAutopostingCategoryBody(BaseModel):
    organization_id: int
    name: str
    prompt_for_image_style: str

    goal: str

    # Структура контента
    structure_skeleton: list[str]
    structure_flex_level_min: int
    structure_flex_level_max: int
    structure_flex_level_comment: str

    # Требования к контенту
    must_have: list[str]
    must_avoid: list[str]

    # Правила для соцсетей
    social_networks_rules: str

    # Ограничения по длине
    len_min: int
    len_max: int

    # Ограничения по хештегам
    n_hashtags_min: int
    n_hashtags_max: int

    # Стиль и тон
    cta_type: str
    tone_of_voice: list[str]

    # Бренд и примеры
    brand_rules: list[str]
    good_samples: list[dict]

    # Дополнительная информация
    additional_info: list[str]


class UpdateAutopostingCategoryBody(BaseModel):
    name: str = None
    prompt_for_image_style: str = None

    goal: str = None

    # Структура контента
    structure_skeleton: list[str] = None
    structure_flex_level_min: int = None
    structure_flex_level_max: int = None
    structure_flex_level_comment: str = None

    # Требования к контенту
    must_have: list[str] = None
    must_avoid: list[str] = None

    # Правила для соцсетей
    social_networks_rules: str = None

    # Ограничения по длине
    len_min: int = None
    len_max: int = None

    # Ограничения по хештегам
    n_hashtags_min: int = None
    n_hashtags_max: int = None

    # Стиль и тон
    cta_type: str = None
    tone_of_voice: list[str] = None

    # Бренд и примеры
    brand_rules: list[str] = None
    good_samples: list[dict] = None

    # Дополнительная информация
    additional_info: list[str] = None


# АВТОПОСТИНГ
class CreateAutopostingBody(BaseModel):
    organization_id: int
    autoposting_category_id: int
    period_in_hours: int
    filter_prompt: str
    tg_channels: list[str]= None
    required_moderation: bool = False


class UpdateAutopostingBody(BaseModel):
    autoposting_category_id: int = None
    period_in_hours: int = None
    filter_prompt: str = None
    enabled: bool = None
    tg_channels: list[str] = None
    required_moderation: bool = None
