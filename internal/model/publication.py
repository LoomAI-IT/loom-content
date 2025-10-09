from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ModerationStatus(Enum):
    DRAFT = "draft"
    MODERATION = "moderation"
    REJECTED = "rejected"
    APPROVED = "approved"


@dataclass
class Category:
    id: int
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

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list['Category']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
                name=row.name,
                prompt_for_image_style=row.prompt_for_image_style,
                goal=row.goal,
                structure_skeleton=row.structure_skeleton,
                structure_flex_level_min=row.structure_flex_level_min,
                structure_flex_level_max=row.structure_flex_level_max,
                structure_flex_level_comment=row.structure_flex_level_comment,
                must_have=row.must_have,
                must_avoid=row.must_avoid,
                social_networks_rules=row.social_networks_rules,
                len_min=row.len_min,
                len_max=row.len_max,
                n_hashtags_min=row.n_hashtags_min,
                n_hashtags_max=row.n_hashtags_max,
                cta_type=row.cta_type,
                tone_of_voice=row.tone_of_voice,
                brand_rules=row.brand_rules,
                good_samples=row.good_samples,
                additional_info=row.additional_info,
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
            "goal": self.goal,
            "structure_skeleton": self.structure_skeleton,
            "structure_flex_level_min": self.structure_flex_level_min,
            "structure_flex_level_max": self.structure_flex_level_max,
            "structure_flex_level_comment": self.structure_flex_level_comment,
            "must_have": self.must_have,
            "must_avoid": self.must_avoid,
            "social_networks_rules": self.social_networks_rules,
            "len_min": self.len_min,
            "len_max": self.len_max,
            "n_hashtags_min": self.n_hashtags_min,
            "n_hashtags_max": self.n_hashtags_max,
            "cta_type": self.cta_type,
            "tone_of_voice": self.tone_of_voice,
            "brand_rules": self.brand_rules,
            "good_samples": self.good_samples,
            "additional_info": self.additional_info,
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

    vk_link: str
    tg_link: str

    text_reference: str
    text: str
    image_fid: str
    image_name: str

    openai_rub_cost: int # TODO нигде не используется, невозможно посчитать

    moderation_status: ModerationStatus
    moderation_comment: str

    publication_at: datetime
    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list['Publication']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
                category_id=row.category_id,
                creator_id=row.creator_id,
                moderator_id=row.moderator_id,
                vk_source=row.vk_source,
                tg_source=row.tg_source,
                vk_link=row.vk_link,
                tg_link=row.tg_link,
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
            "vk_link": self.vk_link,
            "tg_link": self.tg_link,
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
class AutopostingCategory:
    id: int
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

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list['AutopostingCategory']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
                name=row.name,
                prompt_for_image_style=row.prompt_for_image_style,
                goal=row.goal,
                structure_skeleton=row.structure_skeleton,
                structure_flex_level_min=row.structure_flex_level_min,
                structure_flex_level_max=row.structure_flex_level_max,
                structure_flex_level_comment=row.structure_flex_level_comment,
                must_have=row.must_have,
                must_avoid=row.must_avoid,
                social_networks_rules=row.social_networks_rules,
                len_min=row.len_min,
                len_max=row.len_max,
                n_hashtags_min=row.n_hashtags_min,
                n_hashtags_max=row.n_hashtags_max,
                cta_type=row.cta_type,
                tone_of_voice=row.tone_of_voice,
                brand_rules=row.brand_rules,
                good_samples=row.good_samples,
                additional_info=row.additional_info,
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
            "goal": self.goal,
            "structure_skeleton": self.structure_skeleton,
            "structure_flex_level_min": self.structure_flex_level_min,
            "structure_flex_level_max": self.structure_flex_level_max,
            "structure_flex_level_comment": self.structure_flex_level_comment,
            "must_have": self.must_have,
            "must_avoid": self.must_avoid,
            "social_networks_rules": self.social_networks_rules,
            "len_min": self.len_min,
            "len_max": self.len_max,
            "n_hashtags_min": self.n_hashtags_min,
            "n_hashtags_max": self.n_hashtags_max,
            "cta_type": self.cta_type,
            "tone_of_voice": self.tone_of_voice,
            "brand_rules": self.brand_rules,
            "good_samples": self.good_samples,
            "additional_info": self.additional_info,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Autoposting:
    id: int
    organization_id: int
    autoposting_category_id: int

    period_in_hours: int
    enabled: bool
    filter_prompt: str
    tg_channels: list[str]
    required_moderation: bool
    need_image: bool

    last_active: datetime
    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list['Autoposting']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
                autoposting_category_id=row.autoposting_category_id,
                period_in_hours=row.period_in_hours,
                enabled=row.enabled,
                filter_prompt=row.filter_prompt,
                tg_channels=row.tg_channels,
                required_moderation=row.required_moderation,
                need_image=row.need_image,
                last_active=row.last_active,
                created_at=row.created_at
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "autoposting_category_id": self.autoposting_category_id,
            "period_in_hours": self.period_in_hours,
            "enabled": self.enabled,
            "filter_prompt": self.filter_prompt,
            "tg_channels": self.tg_channels,
            "required_moderation": self.required_moderation,
            "need_image": self.need_image,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ViewedTelegramPost:
    id: int
    autoposting_id: int

    tg_channel_username: str
    link: str

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list['ViewedTelegramPost']:
        return [
            cls(
                id=row.id,
                autoposting_id=row.autoposting_id,
                tg_channel_username=row.tg_channel_username,
                link=row.link,
                created_at=row.created_at
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "autoposting_id": self.autoposting_id,
            "tg_channel_username": self.tg_channel_username,
            "link": self.link,
            "created_at": self.created_at.isoformat()
        }
