from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class ModerationStatus(Enum):
    DRAFT = "draft"
    MODERATION = "moderation"
    REJECTED = "rejected"
    APPROVED = "approved"
    PUBLISHED = "published"


@dataclass
class Category:
    id: int
    organization_id: int

    name: str
    prompt_for_image_style: str
    prompt_for_text_style: str

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['Category']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
                name=row.name,
                prompt_for_image_style=row.prompt_for_image_style,
                prompt_for_text_style=row.prompt_for_text_style,
                created_at=row.created_at
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "name": self.name,
            "prompt_for_image_style": self.prompt_for_image_style,
            "prompt_for_text_style": self.prompt_for_text_style,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Publication:
    id: int
    organization_id: int
    category_id: int
    creator_id: int
    moderator_id: int

    vk_source: bool
    tg_source: bool

    text_reference: str
    text: str
    image_fid: str
    image_name: str

    openai_rub_cost: int

    moderation_status: ModerationStatus
    moderation_comment: str

    publication_at: datetime
    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['Publication']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
                category_id=row.category_id,
                creator_id=row.creator_id,
                moderator_id=row.moderator_id,
                vk_source=row.vk_source,
                tg_source=row.tg_source,
                text_reference=row.text_reference,
                text=row.text,
                image_fid=row.image_fid,
                image_name=row.image_name,
                openai_rub_cost=row.openai_rub_cost,
                moderation_status=ModerationStatus(row.moderation_status),
                moderation_comment=row.moderation_comment,
                publication_at=row.publication_at,
                created_at=row.created_at
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "category_id": self.category_id,
            "creator_id": self.creator_id,
            "moderator_id": self.moderator_id,
            "vk_source": self.vk_source,
            "tg_source": self.tg_source,
            "text_reference": self.text_reference,
            "text": self.text,
            "image_fid": self.image_fid,
            "image_name": self.image_name,
            "openai_rub_cost": self.openai_rub_cost,
            "moderation_status": self.moderation_status.value,
            "moderation_comment": self.moderation_comment,
            "publication_at": self.publication_at.isoformat() if self.publication_at else None,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Autoposting:
    id: int
    organization_id: int

    enabled: bool
    filter_prompt: str
    rewrite_prompt: str
    tg_channels: list[str]

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['Autoposting']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
                enabled=row.enabled,
                filter_prompt=row.filter_prompt,
                rewrite_prompt=row.rewrite_prompt,
                tg_channels=row.tg_channels,
                created_at=row.created_at
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "enabled": self.enabled,
            "filter_prompt": self.filter_prompt,
            "rewrite_prompt": self.rewrite_prompt,
            "tg_channels": self.tg_channels,
            "created_at": self.created_at.isoformat()
        }
