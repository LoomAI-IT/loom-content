from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class ModerationStatus(Enum):
    PENDING = "на модерации"
    REJECTED = "отклонен"
    APPROVED = "принят"


@dataclass
class Category:
    id: int
    organization_id: int

    prompt_for_image_style: str
    prompt_for_text_style: str

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['Category']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
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
            "prompt_for_image_style": self.prompt_for_image_style,
            "prompt_for_text_style": self.prompt_for_text_style,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class VideoCut:
    id: int
    project_id: int
    organization_id: int
    creator_id: int
    moderator_id: int

    inst_source_id: int
    youtube_source_id: int

    youtube_video_reference: str
    name: str
    description: str
    tags: list[str]
    video_fid: str
    video_name: str

    vizard_id: int
    moderation_status: ModerationStatus
    moderation_comment: str

    time_for_publication: datetime
    publication_at: datetime
    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['VideoCut']:
        return [
            cls(
                id=row.id,
                project_id=row.project_id,
                organization_id=row.organization_id,
                creator_id=row.creator_id,
                moderator_id=row.moderator_id,
                inst_source_id=row.inst_source_id,
                youtube_source_id=row.youtube_source_id,
                youtube_video_reference=row.youtube_video_reference,
                name=row.name,
                description=row.description,
                tags=row.tags,
                video_fid=row.video_fid,
                video_name=row.video_name,
                vizard_id=row.vizard_id,
                moderation_status=ModerationStatus(row.moderation_status),
                moderation_comment=row.moderation_comment,
                time_for_publication=row.time_for_publication,
                publication_at=row.publication_at,
                created_at=row.created_at
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "organization_id": self.organization_id,
            "creator_id": self.creator_id,
            "moderator_id": self.moderator_id,
            "inst_source_id": self.inst_source_id,
            "youtube_source_id": self.youtube_source_id,
            "youtube_video_reference": self.youtube_video_reference,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "video_fid": self.video_fid,
            "video_name": self.video_name,
            "vizard_id": self.vizard_id,
            "moderation_status": self.moderation_status.value,
            "moderation_comment": self.moderation_comment,
            "time_for_publication": self.time_for_publication.isoformat() if self.time_for_publication else None,
            "publication_at": self.publication_at.isoformat() if self.publication_at else None,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Publication:
    id: int
    organization_id: int
    category_id: int
    creator_id: int
    moderator_id: int

    vk_source_id: int
    tg_source_id: int

    text_reference: str
    name: str
    text: str
    image_fid: str
    image_name: str

    moderation_status: ModerationStatus
    moderation_comment: str

    time_for_publication: datetime
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
                vk_source_id=row.vk_source_id,
                tg_source_id=row.tg_source_id,
                text_reference=row.text_reference,
                name=row.name,
                text=row.text,
                image_fid=row.image_fid,
                image_name=row.image_name,
                moderation_status=ModerationStatus(row.moderation_status),
                moderation_comment=row.moderation_comment,
                time_for_publication=row.time_for_publication,
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
            "vk_source_id": self.vk_source_id,
            "tg_source_id": self.tg_source_id,
            "text_reference": self.text_reference,
            "name": self.name,
            "text": self.text,
            "image_fid": self.image_fid,
            "image_name": self.image_name,
            "moderation_status": self.moderation_status.value,
            "moderation_comment": self.moderation_comment,
            "time_for_publication": self.time_for_publication.isoformat() if self.time_for_publication else None,
            "publication_at": self.publication_at.isoformat() if self.publication_at else None,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Autoposting:
    id: int
    organization_id: int

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
            "filter_prompt": self.filter_prompt,
            "rewrite_prompt": self.rewrite_prompt,
            "tg_channels": self.tg_channels,
            "created_at": self.created_at.isoformat()
        }
