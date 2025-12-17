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
    audience_segment: str

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
    audience_segment: str

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
    audience_segment: str = None

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


class GenerateCategoriesBody(BaseModel):
    organization_id: int