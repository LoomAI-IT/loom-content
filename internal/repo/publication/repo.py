import json
from datetime import datetime

from pkg.trace_wrapper import traced_method
from .sql_query import *
from internal import interface, model


class PublicationRepo(interface.IPublicationRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB,
    ):
        self.tracer = tel.tracer()
        self.db = db

    # ПУБЛИКАЦИИ
    @traced_method()
    async def create_publication(
            self,
            organization_id: int,
            category_id: int,
            creator_id: int,
            text_reference: str,
            text: str,
            moderation_status: str,
    ) -> int:
        args = {
            'organization_id': organization_id,
            'category_id': category_id,
            'creator_id': creator_id,
            'text_reference': text_reference,
            'text': text,
            'moderation_status': moderation_status,
        }

        publication_id = await self.db.insert(create_publication, args)
        return publication_id

    @traced_method()
    async def change_publication(
            self,
            publication_id: int,
            moderator_id: int = None,
            vk_source: bool = None,
            tg_source: bool = None,
            text: str = None,
            moderation_status: str = None,
            moderation_comment: str = None,
            publication_at: datetime = None,
            image_fid: str = None,
            image_name: str = None,
    ) -> None:
        args = {
            'publication_id': publication_id,
            'moderator_id': moderator_id,
            'vk_source': vk_source,
            'tg_source': tg_source,
            'text': text,
            'moderation_status': moderation_status if moderation_status else None,
            'moderation_comment': moderation_comment,
            'publication_at': publication_at,
            'image_fid': image_fid,
            'image_name': image_name,
        }

        await self.db.update(change_publication, args)

    @traced_method()
    async def delete_publication(self, publication_id: int) -> None:
        args = {'publication_id': publication_id}
        await self.db.delete(delete_publication, args)

    @traced_method()
    async def delete_publication_by_category_id(self, category_id: int) -> None:
        args = {'category_id': category_id}
        await self.db.delete(delete_publication_by_category_id, args)

    @traced_method()
    async def get_publication_by_id(self, publication_id: int) -> list[model.Publication]:
        args = {'publication_id': publication_id}
        rows = await self.db.select(get_publication_by_id, args)
        publications = model.Publication.serialize(rows) if rows else []

        return publications

    @traced_method()
    async def get_publications_by_organization(self, organization_id: int) -> list[model.Publication]:
        args = {'organization_id': organization_id}
        rows = await self.db.select(get_publications_by_organization, args)
        publications = model.Publication.serialize(rows) if rows else []

        return publications

    # РУБРИКИ

    @traced_method()
    async def create_category(
            self,
            organization_id: int,
            name: str,
            prompt_for_image_style: str,
            goal: str,
            structure_skeleton: list[str],
            structure_flex_level_min: int,
            structure_flex_level_max: int,
            structure_flex_level_comment: str,
            must_have: list[str],
            must_avoid: list[str],
            social_networks_rules: str,
            len_min: int,
            len_max: int,
            n_hashtags_min: int,
            n_hashtags_max: int,
            cta_type: str,
            tone_of_voice: list[str],
            brand_rules: list[str],
            good_samples: list[dict],
            additional_info: list[str]
    ) -> int:
        args = {
            'organization_id': organization_id,
            'name': name,
            'prompt_for_image_style': prompt_for_image_style,
            'goal': goal,
            'structure_skeleton': structure_skeleton,
            'structure_flex_level_min': structure_flex_level_min,
            'structure_flex_level_max': structure_flex_level_max,
            'structure_flex_level_comment': structure_flex_level_comment,
            'must_have': must_have,
            'must_avoid': must_avoid,
            'social_networks_rules': social_networks_rules,
            'len_min': len_min,
            'len_max': len_max,
            'n_hashtags_min': n_hashtags_min,
            'n_hashtags_max': n_hashtags_max,
            'cta_type': cta_type,
            'tone_of_voice': tone_of_voice,
            'brand_rules': brand_rules,
            'good_samples': [json.dumps(good_sample) for good_sample in good_samples],
            'additional_info': additional_info,
        }

        category_id = await self.db.insert(create_category, args)
        return category_id

    @traced_method()
    async def update_category(
            self,
            category_id: int,
            name: str = None,
            prompt_for_image_style: str = None,
            goal: str = None,
            structure_skeleton: list[str] = None,
            structure_flex_level_min: int = None,
            structure_flex_level_max: int = None,
            structure_flex_level_comment: str = None,
            must_have: list[str] = None,
            must_avoid: list[str] = None,
            social_networks_rules: str = None,
            len_min: int = None,
            len_max: int = None,
            n_hashtags_min: int = None,
            n_hashtags_max: int = None,
            cta_type: str = None,
            tone_of_voice: list[str] = None,
            brand_rules: list[str] = None,
            good_samples: list[dict] = None,
            additional_info: list[str] = None
    ) -> None:
        args = {
            'category_id': category_id,
            'name': name,
            'prompt_for_image_style': prompt_for_image_style,
            'goal': goal,
            'structure_skeleton': structure_skeleton,
            'structure_flex_level_min': structure_flex_level_min,
            'structure_flex_level_max': structure_flex_level_max,
            'structure_flex_level_comment': structure_flex_level_comment,
            'must_have': must_have,
            'must_avoid': must_avoid,
            'social_networks_rules': social_networks_rules,
            'len_min': len_min,
            'len_max': len_max,
            'n_hashtags_min': n_hashtags_min,
            'n_hashtags_max': n_hashtags_max,
            'cta_type': cta_type,
            'tone_of_voice': tone_of_voice,
            'brand_rules': brand_rules,
            'good_samples': [json.dumps(good_sample) for good_sample in good_samples] if good_samples else None,
            'additional_info': additional_info,
        }

        await self.db.update(update_category, args)

    @traced_method()
    async def get_category_by_id(self, category_id: int) -> list[model.Category]:
        args = {'category_id': category_id}
        rows = await self.db.select(get_category_by_id, args)
        categories = model.Category.serialize(rows) if rows else []

        return categories

    @traced_method()
    async def get_categories_by_organization(self, organization_id: int) -> list[model.Category]:
        args = {'organization_id': organization_id}
        rows = await self.db.select(get_categories_by_organization, args)
        categories = model.Category.serialize(rows) if rows else []

        return categories

    @traced_method()
    async def delete_category(self, category_id: int) -> None:
        args = {'category_id': category_id}
        await self.db.delete(delete_category, args)

    # РУБРИКИ ДЛЯ АВТОПОСТИНГА

    @traced_method()
    async def create_autoposting_category(
            self,
            organization_id: int,
            name: str,
            prompt_for_image_style: str,
            goal: str,
            structure_skeleton: list[str],
            structure_flex_level_min: int,
            structure_flex_level_max: int,
            structure_flex_level_comment: str,
            must_have: list[str],
            must_avoid: list[str],
            social_networks_rules: str,
            len_min: int,
            len_max: int,
            n_hashtags_min: int,
            n_hashtags_max: int,
            cta_type: str,
            tone_of_voice: list[str],
            brand_rules: list[str],
            good_samples: list[dict],
            additional_info: list[str]
    ) -> int:
        args = {
            'organization_id': organization_id,
            'name': name,
            'prompt_for_image_style': prompt_for_image_style,
            'goal': goal,
            'structure_skeleton': structure_skeleton,
            'structure_flex_level_min': structure_flex_level_min,
            'structure_flex_level_max': structure_flex_level_max,
            'structure_flex_level_comment': structure_flex_level_comment,
            'must_have': must_have,
            'must_avoid': must_avoid,
            'social_networks_rules': social_networks_rules,
            'len_min': len_min,
            'len_max': len_max,
            'n_hashtags_min': n_hashtags_min,
            'n_hashtags_max': n_hashtags_max,
            'cta_type': cta_type,
            'tone_of_voice': tone_of_voice,
            'brand_rules': brand_rules,
            'good_samples': [json.dumps(good_sample) for good_sample in good_samples] if good_samples else None,
            'additional_info': additional_info
        }

        autoposting_category_id = await self.db.insert(create_autoposting_category, args)
        return autoposting_category_id

    @traced_method()
    async def update_autoposting_category(
            self,
            autoposting_category_id: int,
            name: str = None,
            prompt_for_image_style: str = None,
            goal: str = None,
            structure_skeleton: list[str] = None,
            structure_flex_level_min: int = None,
            structure_flex_level_max: int = None,
            structure_flex_level_comment: str = None,
            must_have: list[str] = None,
            must_avoid: list[str] = None,
            social_networks_rules: str = None,
            len_min: int = None,
            len_max: int = None,
            n_hashtags_min: int = None,
            n_hashtags_max: int = None,
            cta_type: str = None,
            tone_of_voice: list[str] = None,
            brand_rules: list[str] = None,
            good_samples: list[dict] = None,
            additional_info: list[str] = None
    ) -> None:
        args = {
            'autoposting_category_id': autoposting_category_id,
            'name': name,
            'prompt_for_image_style': prompt_for_image_style,
            'goal': goal,
            'structure_skeleton': structure_skeleton,
            'structure_flex_level_min': structure_flex_level_min,
            'structure_flex_level_max': structure_flex_level_max,
            'structure_flex_level_comment': structure_flex_level_comment,
            'must_have': must_have,
            'must_avoid': must_avoid,
            'social_networks_rules': social_networks_rules,
            'len_min': len_min,
            'len_max': len_max,
            'n_hashtags_min': n_hashtags_min,
            'n_hashtags_max': n_hashtags_max,
            'cta_type': cta_type,
            'tone_of_voice': tone_of_voice,
            'brand_rules': brand_rules,
            'good_samples': [json.dumps(good_sample) for good_sample in good_samples] if good_samples else None,
            'additional_info': additional_info
        }

        await self.db.update(update_autoposting_category, args)

    @traced_method()
    async def delete_autoposting_category(self, autoposting_category_id: int) -> None:
        args = {'autoposting_category_id': autoposting_category_id}
        await self.db.delete(delete_autoposting_category, args)

    @traced_method()
    async def get_autoposting_category_by_id(self, autoposting_category_id: int) -> list[model.AutopostingCategory]:
        args = {'autoposting_category_id': autoposting_category_id}
        rows = await self.db.select(get_autoposting_category_by_id, args)

        return model.AutopostingCategory.serialize(rows)

    # АВТОПОСТИНГ

    @traced_method()
    async def create_autoposting(
            self,
            organization_id: int,
            autoposting_category_id: int,
            period_in_hours: int,
            filter_prompt: str,
            tg_channels: list[str],
            required_moderation: bool,
            need_image: bool
    ) -> int:
        args = {
            'organization_id': organization_id,
            'autoposting_category_id': autoposting_category_id,
            'period_in_hours': period_in_hours,
            'filter_prompt': filter_prompt,
            'tg_channels': tg_channels,
            'required_moderation': required_moderation,
            'need_image': need_image,
        }

        autoposting_id = await self.db.insert(create_autoposting, args)

        return autoposting_id

    @traced_method()
    async def update_autoposting(
            self,
            autoposting_id: int,
            autoposting_category_id: int = None,
            period_in_hours: int = None,
            filter_prompt: str = None,
            enabled: bool = None,
            tg_channels: list[str] = None,
            required_moderation: bool = None,
            need_image: bool = None,
            last_active: datetime = None
    ) -> None:
        args = {
            'autoposting_id': autoposting_id,
            'autoposting_category_id': autoposting_category_id,
            'period_in_hours': period_in_hours,
            'filter_prompt': filter_prompt,
            'enabled': enabled,
            'tg_channels': tg_channels,
            'required_moderation': required_moderation,
            'need_image': need_image,
            'last_active': last_active,
        }

        await self.db.update(update_autoposting, args)

    @traced_method()
    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        args = {'organization_id': organization_id}
        rows = await self.db.select(get_autoposting_by_organization, args)
        autopostings = model.Autoposting.serialize(rows) if rows else []

        return autopostings

    @traced_method()
    async def get_autoposting_by_id(self, autoposting_id: int) -> list[model.Autoposting]:
        args = {'autoposting_id': autoposting_id}
        rows = await self.db.select(get_autoposting_by_id, args)
        autopostings = model.Autoposting.serialize(rows) if rows else []

        return autopostings

    @traced_method()
    async def get_all_autopostings(self) -> list[model.Autoposting]:
        rows = await self.db.select(get_all_autopostings, {})
        autopostings = model.Autoposting.serialize(rows) if rows else []

        return autopostings

    @traced_method()
    async def delete_autoposting(self, autoposting_id: int) -> None:
        args = {'autoposting_id': autoposting_id}
        await self.db.delete(delete_autoposting, args)

    # ПРОСМОТРЕННЫЕ TELEGRAM ПОСТЫ

    @traced_method()
    async def create_viewed_telegram_post(
            self,
            autoposting_id: int,
            tg_channel_username: str,
            link: str
    ) -> int:
        args = {
            'autoposting_id': autoposting_id,
            'tg_channel_username': tg_channel_username,
            'link': link
        }

        viewed_post_id = await self.db.insert(create_viewed_telegram_post, args)
        return viewed_post_id

    @traced_method()
    async def get_viewed_telegram_post(
            self,
            autoposting_id: int,
            tg_channel_username: str
    ) -> list[model.ViewedTelegramPost]:
        args = {
            'autoposting_id': autoposting_id,
            'tg_channel_username': tg_channel_username
        }
        rows = await self.db.select(get_viewed_telegram_post, args)
        viewed_posts = model.ViewedTelegramPost.serialize(rows) if rows else []

        return viewed_posts
