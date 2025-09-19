from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


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
    prompt_for_text_style: str


class UpdateCategoryBody(BaseModel):
    name: Optional[str] | None = None
    prompt_for_image_style: Optional[str] | None = None
    prompt_for_text_style: Optional[str] | None = None


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
