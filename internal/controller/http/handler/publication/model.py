from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ModerationStatusEnum(str, Enum):
    DRAFT = "draft"
    MODERATION = "moderation"
    REJECTED = "rejected"
    APPROVED = "approved"
    PUBLISHED = "published"


# ПУБЛИКАЦИИ
class GeneratePublicationTextBody(BaseModel):
    category_id: int
    text_reference: str


class RegeneratePublicationTextBody(BaseModel):
    category_id: int
    publication_text: str
    prompt: str = None


class GeneratePublicationImageBody(BaseModel):
    category_id: int
    publication_text: str
    text_reference: str
    prompt: str = None

class CreatePublicationBody(BaseModel):
    organization_id: int
    category_id: int
    creator_id: int
    text_reference: str
    name: str
    text: str
    tags: list[str]
    moderation_status: str
    image_url: str = None


class ChangePublicationBody(BaseModel):
    name: str = None
    text: str = None
    tags: list[str] = None
    time_for_publication: datetime = None


class ModeratePublicationBody(BaseModel):
    publication_id: int
    moderator_id: int
    moderation_status: ModerationStatusEnum
    moderation_comment: Optional[str] = ""


# РУБРИКИ
class CreateCategoryBody(BaseModel):
    organization_id: int
    name: str
    prompt_for_image_style: str
    prompt_for_text_style: str


class UpdateCategoryBody(BaseModel):
    name: Optional[str] = None
    prompt_for_image_style: Optional[str] = None
    prompt_for_text_style: Optional[str] = None


# АВТОПОСТИНГ
class CreateAutopostingBody(BaseModel):
    organization_id: int
    filter_prompt: str
    rewrite_prompt: str
    tg_channels: Optional[List[str]] = None


class UpdateAutopostingBody(BaseModel):
    filter_prompt: Optional[str] = None
    rewrite_prompt: Optional[str] = None
    enabled: Optional[bool] = None
    tg_channels: Optional[List[str]] = None


# НАРЕЗКА ВИДЕО
class GenerateVideoCutBody(BaseModel):
    organization_id: int
    creator_id: int
    youtube_video_reference: str
    time_for_publication: Optional[datetime] = None


class ChangeVideoCutBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    time_for_publication: Optional[datetime] = None


class ModerateVideoCutBody(BaseModel):
    moderator_id: int
    moderation_status: ModerationStatusEnum
    moderation_comment: Optional[str] = ""


# RESPONSE MODELS
class PublicationResponse(BaseModel):
    message: str
    publication_id: int


class CategoryResponse(BaseModel):
    message: str
    category_id: int


class AutopostingResponse(BaseModel):
    message: str
    autoposting_id: int


class VideoCutResponse(BaseModel):
    message: str
    video_cut_id: int


class DataResponse(BaseModel):
    message: str
    data: dict


class ListDataResponse(BaseModel):
    message: str
    data: List[dict]


class SuccessResponse(BaseModel):
    message: str
