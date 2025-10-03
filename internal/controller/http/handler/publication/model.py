from pydantic import BaseModel
from typing import Optional, List


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
    moderation_comment: Optional[str] = ""


# РУБРИКИ
class CreateCategoryBody(BaseModel):
    organization_id: int
    name: str
    prompt_for_image_style: str

    goal: str

    # Структура контента
    structure_skeleton: List[str]
    structure_flex_level_min: int
    structure_flex_level_max: int
    structure_flex_level_comment: str

    # Требования к контенту
    must_have: List[str]
    must_avoid: List[str]

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
    tone_of_voice: List[str] = []

    # Бренд и примеры
    brand_rules: List[str] = []
    good_samples: List[dict] = []

    # Дополнительная информация
    additional_info: List[str] = []


class UpdateCategoryBody(BaseModel):
    name: Optional[str] = None
    prompt_for_image_style: Optional[str] = None

    goal: Optional[str] = None

    # Структура контента
    structure_skeleton: Optional[List[str]] = None
    structure_flex_level_min: Optional[int] = None
    structure_flex_level_max: Optional[int] = None
    structure_flex_level_comment: Optional[str] = None

    # Требования к контенту
    must_have: Optional[List[str]] = None
    must_avoid: Optional[List[str]] = None

    # Правила для соцсетей
    social_networks_rules: Optional[str] = None

    # Ограничения по длине
    len_min: Optional[int] = None
    len_max: Optional[int] = None

    # Ограничения по хештегам
    n_hashtags_min: Optional[int] = None
    n_hashtags_max: Optional[int] = None

    # Стиль и тон
    cta_type: Optional[str] = None
    tone_of_voice: Optional[List[str]] = None

    # Бренд и примеры
    brand_rules: Optional[List[str]] = None
    good_samples: Optional[List[dict]] = None

    # Дополнительная информация
    additional_info: Optional[List[str]] = None


# АВТОПОСТИНГ
class CreateAutopostingBody(BaseModel):
    organization_id: int
    filter_prompt: str
    rewrite_prompt: str
    tg_channels: Optional[List[str]] | None = None


class UpdateAutopostingBody(BaseModel):
    filter_prompt: Optional[str] | None = None
    rewrite_prompt: Optional[str] | None = None
    enabled: Optional[bool] | None = None
    tg_channels: Optional[List[str]] | None = None
