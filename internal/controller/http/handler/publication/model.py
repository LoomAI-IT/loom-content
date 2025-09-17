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
class GeneratePublicationBody(BaseModel):
    organization_id: int
    category_id: int
    creator_id: int
    need_images: bool
    text_reference: str
    time_for_publication: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": 1,
                "category_id": 1,
                "creator_id": 1,
                "need_images": True,
                "text_reference": "Новая статья о технологиях искусственного интеллекта",
                "time_for_publication": "2024-12-31T10:00:00Z"
            }
        }


class RegeneratePublicationImageBody(BaseModel):
    prompt: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Сделай изображение более ярким и добавь больше синих оттенков"
            }
        }


class RegeneratePublicationTextBody(BaseModel):
    prompt: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Сделай текст более дружелюбным и добавь призыв к действию"
            }
        }


class ChangePublicationBody(BaseModel):
    name: Optional[str] = None
    text: Optional[str] = None
    tags: Optional[List[str]] = None
    time_for_publication: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Обновленное название публикации",
                "text": "Обновленный текст публикации",
                "tags": ["#технологии", "#AI", "#инновации"],
                "time_for_publication": "2024-12-31T10:00:00Z"
            }
        }


class ModeratePublicationBody(BaseModel):
    moderator_id: int
    moderation_status: ModerationStatusEnum
    moderation_comment: Optional[str] = ""

    class Config:
        json_schema_extra = {
            "example": {
                "moderator_id": 1,
                "moderation_status": "approved",
                "moderation_comment": "Публикация одобрена"
            }
        }


# РУБРИКИ
class CreateCategoryBody(BaseModel):
    organization_id: int
    prompt_for_image_style: str
    prompt_for_text_style: str

    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": 1,
                "prompt_for_image_style": "Минималистичный стиль с корпоративными цветами",
                "prompt_for_text_style": "Профессиональный тон, дружелюбный подход"
            }
        }


class UpdateCategoryBody(BaseModel):
    prompt_for_image_style: Optional[str] = None
    prompt_for_text_style: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "prompt_for_image_style": "Обновленный стиль изображений",
                "prompt_for_text_style": "Обновленный стиль текста"
            }
        }


# АВТОПОСТИНГ
class CreateAutopostingBody(BaseModel):
    organization_id: int
    filter_prompt: str
    rewrite_prompt: str
    tg_channels: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": 1,
                "filter_prompt": "Фильтровать контент по технологической тематике",
                "rewrite_prompt": "Переписать в стиле компании",
                "tg_channels": ["@channel1", "@channel2"]
            }
        }


class UpdateAutopostingBody(BaseModel):
    filter_prompt: Optional[str] = None
    rewrite_prompt: Optional[str] = None
    enabled: Optional[bool] = None
    tg_channels: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "filter_prompt": "Обновленный фильтр",
                "rewrite_prompt": "Обновленный промпт переписывания",
                "enabled": True,
                "tg_channels": ["@channel1", "@channel2", "@channel3"]
            }
        }


# НАРЕЗКА ВИДЕО
class GenerateVideoCutBody(BaseModel):
    organization_id: int
    creator_id: int
    youtube_video_reference: str
    time_for_publication: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": 1,
                "creator_id": 1,
                "youtube_video_reference": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "time_for_publication": "2024-12-31T10:00:00Z"
            }
        }


class ChangeVideoCutBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    time_for_publication: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Обновленное название видео",
                "description": "Обновленное описание видео",
                "tags": ["#видео", "#контент", "#маркетинг"],
                "time_for_publication": "2024-12-31T10:00:00Z"
            }
        }


class ModerateVideoCutBody(BaseModel):
    moderator_id: int
    moderation_status: ModerationStatusEnum
    moderation_comment: Optional[str] = ""

    class Config:
        json_schema_extra = {
            "example": {
                "moderator_id": 1,
                "moderation_status": "approved",
                "moderation_comment": "Видеонарезка одобрена"
            }
        }


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