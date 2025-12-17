from abc import abstractmethod
from datetime import datetime
from typing import Protocol

from fastapi.responses import JSONResponse

from internal import model
from internal.controller.http.handler.autoposting.model import *


class IAutopostingController(Protocol):
    @abstractmethod
    async def create_autoposting(
            self,
            body: CreateAutopostingBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def create_autoposting_category(
            self,
            body: CreateAutopostingCategoryBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def update_autoposting(
            self,
            autoposting_id: int,
            body: UpdateAutopostingBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def update_autoposting_category(
            self,
            autoposting_category_id: int,
            body: UpdateAutopostingCategoryBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def get_autoposting_category_by_id(self, autoposting_category_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def get_autoposting_by_organization(self, organization_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def delete_autoposting(self, autoposting_id: int) -> JSONResponse:
        pass


class IAutopostingService(Protocol):

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def create_publication_from_random_suitable_post(
            self,
            autoposting: model.Autoposting,
            suitable_posts: list[dict]
    ): pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def get_autoposting_category_by_id(self, autoposting_category_id: int) -> model.AutopostingCategory:
        pass

    @abstractmethod
    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        pass

    @abstractmethod
    async def get_active_autopostings(self) -> list[model.Autoposting]:
        pass

    @abstractmethod
    async def get_suitable_posts(self, autoposting: model.Autoposting, channel_username: str) -> list[dict]: pass

    @abstractmethod
    async def delete_autoposting(self, autoposting_id: int) -> None:
        pass


class IAutopostingRepo(Protocol):
    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def create_viewed_telegram_post(
            self,
            autoposting_id: int,
            tg_channel_username: str,
            link: str
    ) -> int:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def get_autoposting_category_by_id(self, autoposting_category_id: int) -> list[model.AutopostingCategory]:
        pass

    @abstractmethod
    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        pass

    @abstractmethod
    async def get_all_autopostings(self) -> list[model.Autoposting]:
        pass

    @abstractmethod
    async def get_autoposting_by_id(self, autoposting_id: int) -> list[model.Autoposting]: pass

    @abstractmethod
    async def get_viewed_telegram_post(
            self,
            autoposting_id: int,
            tg_channel_username: str
    ) -> list[model.ViewedTelegramPost]:
        pass

    @abstractmethod
    async def delete_autoposting(self, autoposting_id: int) -> None:
        pass

    @abstractmethod
    async def delete_autoposting_category(self, autoposting_category_id: int) -> None: pass


class IAutopostingPromptGenerator(Protocol):
    @abstractmethod
    async def get_filter_post_system_prompt(
            self,
            filter_prompt: str,
            post_text: str
    ) -> str: pass

    @abstractmethod
    async def get_generate_autoposting_text_system_prompt(
            self,
            autoposting_category: model.AutopostingCategory,
            organization: model.Organization,
            source_post_text: str,
            web_search_result: str
    ) -> str:
        pass

    @abstractmethod
    async def get_generate_autoposting_image_system_prompt(
            self,
            prompt_for_image_style: str,
            publication_text: str
    ) -> str:
        pass
