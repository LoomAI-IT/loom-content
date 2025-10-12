import io
from abc import abstractmethod
from datetime import datetime
from typing import Protocol

from fastapi import UploadFile, Form, File
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse

from internal import model

from internal.controller.http.handler.publication.model import *


class IPublicationController(Protocol):
    # Публикация
    @abstractmethod
    async def generate_publication_text(
            self,
            body: GeneratePublicationTextBody,
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def regenerate_publication_text(
            self,
            body: RegeneratePublicationTextBody,
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def generate_publication_image(
            self,
            category_id: int = Form(...),
            publication_text: str = Form(...),
            text_reference: str = Form(...),
            prompt: str | None = Form(None),
            image_file: UploadFile = File(None),
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def create_publication(
            self,
            organization_id: int = Form(...),
            category_id: int = Form(...),
            creator_id: int = Form(...),
            text_reference: str = Form(...),
            text: str = Form(...),
            moderation_status: str = Form(...),
            image_url: str = Form(None),
            image_file: UploadFile = File(None),
    ) -> JSONResponse: pass

    @abstractmethod
    async def change_publication(
            self,
            publication_id: int,
            vk_source: bool = Form(None),
            tg_source: bool = Form(None),
            text: str = Form(None),
            image_url: str = Form(None),
            image_file: UploadFile = File(None),
    ) -> JSONResponse: pass

    @abstractmethod
    async def delete_publication(
            self,
            publication_id: int,
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def delete_publication_image(
            self,
            publication_id: int,
    ): pass

    @abstractmethod
    async def send_publication_to_moderation(
            self,
            publication_id: int,
    ): pass

    @abstractmethod
    async def moderate_publication(
            self,
            body: ModeratePublicationBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def get_publication_by_id(self, publication_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def get_publications_by_organization(self, organization_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def download_publication_image(
            self,
            publication_id: int
    ) -> StreamingResponse:
        pass

    @abstractmethod
    async def download_other_image(
            self,
            image_fid: str,
            image_name: str
    ) -> StreamingResponse: pass

    # РУБРИКИ
    @abstractmethod
    async def create_category(
            self,
            body: CreateCategoryBody,
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def get_category_by_id(self, category_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def get_categories_by_organization(self, organization_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def update_category(
            self,
            category_id: int,
            body: UpdateCategoryBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def delete_category(self, category_id: int) -> JSONResponse:
        pass

    # РУБРИКИ ДЛЯ АВТОПОСТИНГА
    @abstractmethod
    async def create_autoposting_category(
            self,
            body: CreateAutopostingCategoryBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def get_autoposting_category_by_id(self, autoposting_category_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def update_autoposting_category(
            self,
            autoposting_category_id: int,
            body: UpdateAutopostingCategoryBody
    ) -> JSONResponse:
        pass

    # АВТОПОСТИНГ
    @abstractmethod
    async def create_autoposting(
            self,
            body: CreateAutopostingBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def get_autoposting_by_organization(self, organization_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def update_autoposting(
            self,
            autoposting_id: int,
            body: UpdateAutopostingBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def delete_autoposting(self, autoposting_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def transcribe_audio(
            self,
            organization_id: int = Form(...),
            audio_file: UploadFile = File(...),
    ) -> JSONResponse:
        pass


class IPublicationService(Protocol):
    # Публикация
    @abstractmethod
    async def generate_publication_text(
            self,
            category_id: int,
            text_reference: str
    ) -> dict: pass

    @abstractmethod
    async def regenerate_publication_text(
            self,
            category_id: int,
            publication_text: str,
            prompt: str = None
    ) -> dict: pass

    @abstractmethod
    async def generate_publication_image(
            self,
            category_id: int,
            publication_text: str,
            text_reference: str,
            prompt: str = None,
            image_file: UploadFile = None
    ) -> list[str]: pass

    @abstractmethod
    async def create_publication(
            self,
            organization_id: int,
            category_id: int,
            creator_id: int,
            text_reference: str,
            text: str,
            moderation_status: str,
            image_url: str = None,
            image_file: UploadFile = None,
    ) -> int: pass

    @abstractmethod
    async def change_publication(
            self,
            publication_id: int,
            vk_source: bool = None,
            tg_source: bool = None,
            vk_link: str = None,
            tg_link: str = None,
            text: str = None,
            image_url: str = None,
            image_file: UploadFile = None,
    ) -> None: pass

    @abstractmethod
    async def delete_publication(
            self,
            publication_id: int,
    ) -> None:
        pass

    @abstractmethod
    async def delete_publication_image(
            self,
            publication_id: int,
    ) -> None: pass

    @abstractmethod
    async def send_publication_to_moderation(
            self,
            publication_id: int,
    ) -> None: pass

    @abstractmethod
    async def moderate_publication(
            self,
            publication_id: int,
            moderator_id: int,
            moderation_status: str,
            moderation_comment: str = ""
    ) -> dict:
        pass

    @abstractmethod
    async def get_publication_by_id(self, publication_id: int) -> model.Publication:
        pass

    @abstractmethod
    async def get_publications_by_organization(self, organization_id: int) -> list[model.Publication]:
        pass

    @abstractmethod
    async def download_publication_image(
            self,
            publication_id: int
    ) -> tuple[io.BytesIO, str]:
        pass

    @abstractmethod
    async def download_other_image(
            self,
            image_fid: str,
            image_name: str
    ) -> tuple[io.BytesIO, str]: pass

    # РУБРИКИ
    @abstractmethod
    async def create_category(
            self,
            organization_id: int,
            name: str,
            goal: str,
            tone_of_voice: list[str],
            brand_rules: list[str],
            brand_vocabulary: list[dict],
            tone_variations: list[dict],
            structure_variations: list[dict],
            creativity_level: int,
            experimentation_zones: list[str],
            surprise_factors: list[dict],
            humor_policy: dict,
            audience_segments: list[dict],
            emotional_palette: list[dict],
            platform_specific_rules: dict,
            must_have: list[dict],
            must_avoid: list[dict],
            len_min: int,
            len_max: int,
            n_hashtags_min: int,
            n_hashtags_max: int,
            cta_type: str,
            cta_strategy: dict,
            good_samples: list[dict],
            bad_samples: list[dict],
            additional_info: list[dict],
            prompt_for_image_style: str
    ) -> int:
        pass

    @abstractmethod
    async def get_category_by_id(self, category_id: int) -> model.Category:
        pass

    @abstractmethod
    async def get_categories_by_organization(self, organization_id: int) -> list[model.Category]:
        pass

    @abstractmethod
    async def update_category(
            self,
            category_id: int,
            name: str = None,
            goal: str = None,
            tone_of_voice: list[str] = None,
            brand_rules: list[str] = None,
            brand_vocabulary: list[dict] = None,
            tone_variations: list[dict] = None,
            structure_variations: list[dict] = None,
            creativity_level: int = None,
            experimentation_zones: list[str] = None,
            surprise_factors: list[dict] = None,
            humor_policy: dict = None,
            audience_segments: list[dict] = None,
            emotional_palette: list[dict] = None,
            platform_specific_rules: dict = None,
            must_have: list[dict] = None,
            must_avoid: list[dict] = None,
            len_min: int = None,
            len_max: int = None,
            n_hashtags_min: int = None,
            n_hashtags_max: int = None,
            cta_type: str = None,
            cta_strategy: dict = None,
            good_samples: list[dict] = None,
            bad_samples: list[dict] = None,
            additional_info: list[dict] = None,
            prompt_for_image_style: str = None
    ) -> None:
        pass

    @abstractmethod
    async def delete_category(self, category_id: int) -> None:
        pass

    # РУБРИКИ ДЛЯ АВТОПОСТИНГА
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
    async def get_autoposting_category_by_id(self, autoposting_category_id: int) -> model.AutopostingCategory:
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

    # АВТОПОСТИНГ
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
    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        pass

    @abstractmethod
    async def get_all_autopostings(self) -> list[model.Autoposting]:
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
    async def delete_autoposting(self, autoposting_id: int) -> None:
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
    async def get_viewed_telegram_post(
            self,
            autoposting_id: int,
            tg_channel_username: str
    ) -> list[model.ViewedTelegramPost]:
        pass

    @abstractmethod
    async def transcribe_audio(
            self,
            audio_file: UploadFile,
            organization_id: int,
    ) -> str:
        pass

    @abstractmethod
    async def generate_autoposting_publication_text(
            self,
            autoposting_category_id: int,
            source_post_text: str
    ) -> dict:
        pass

    @abstractmethod
    async def generate_autoposting_publication_image(
            self,
            autoposting_category_id: int,
            publication_text: str
    ) -> list[str]:
        pass


class IPublicationRepo(Protocol):
    @abstractmethod
    async def create_publication(
            self,
            organization_id: int,
            category_id: int,
            creator_id: int,
            text_reference: str,
            text: str,
            moderation_status: str,
    ) -> int:
        pass

    @abstractmethod
    async def change_publication(
            self,
            publication_id: int,
            moderator_id: int = None,
            vk_source: bool = None,
            tg_source: bool = None,
            vk_link: str = None,
            tg_link: str = None,
            text: str = None,
            moderation_status: str = None,
            moderation_comment: str = None,
            publication_at: datetime = None,
            image_fid: str = None,
            image_name: str = None,
    ) -> None: pass

    @abstractmethod
    async def delete_publication(self, publication_id: int) -> None: pass

    @abstractmethod
    async def delete_publication_by_category_id(self, category_id: int) -> None: pass

    @abstractmethod
    async def get_publication_by_id(self, publication_id: int) -> list[model.Publication]:
        pass

    @abstractmethod
    async def get_publications_by_organization(self, organization_id: int) -> list[model.Publication]:
        pass

    # РУБРИКИ
    @abstractmethod
    async def create_category(
            self,
            organization_id: int,
            name: str,
            goal: str,
            tone_of_voice: list[str],
            brand_rules: list[str],
            brand_vocabulary: list[dict],
            tone_variations: list[dict],
            structure_variations: list[dict],
            creativity_level: int,
            experimentation_zones: list[str],
            surprise_factors: list[dict],
            humor_policy: dict,
            audience_segments: list[dict],
            emotional_palette: list[dict],
            platform_specific_rules: dict,
            must_have: list[dict],
            must_avoid: list[dict],
            len_min: int,
            len_max: int,
            n_hashtags_min: int,
            n_hashtags_max: int,
            cta_type: str,
            cta_strategy: dict,
            good_samples: list[dict],
            bad_samples: list[dict],
            additional_info: list[dict],
            prompt_for_image_style: str
    ) -> int:
        pass

    @abstractmethod
    async def update_category(
            self,
            category_id: int,
            name: str = None,
            goal: str = None,
            tone_of_voice: list[str] = None,
            brand_rules: list[str] = None,
            brand_vocabulary: list[dict] = None,
            tone_variations: list[dict] = None,
            structure_variations: list[dict] = None,
            creativity_level: int = None,
            experimentation_zones: list[str] = None,
            surprise_factors: list[dict] = None,
            humor_policy: dict = None,
            audience_segments: list[dict] = None,
            emotional_palette: list[dict] = None,
            platform_specific_rules: dict = None,
            must_have: list[dict] = None,
            must_avoid: list[dict] = None,
            len_min: int = None,
            len_max: int = None,
            n_hashtags_min: int = None,
            n_hashtags_max: int = None,
            cta_type: str = None,
            cta_strategy: dict = None,
            good_samples: list[dict] = None,
            bad_samples: list[dict] = None,
            additional_info: list[dict] = None,
            prompt_for_image_style: str = None
    ) -> None:
        pass

    @abstractmethod
    async def get_category_by_id(self, category_id: int) -> list[model.Category]:
        pass

    @abstractmethod
    async def get_categories_by_organization(self, organization_id: int) -> list[model.Category]:
        pass

    @abstractmethod
    async def delete_category(self, category_id: int) -> None:
        pass

    # РУБРИКИ ДЛЯ АВТОПОСТИНГА
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
    async def delete_autoposting_category(self, autoposting_category_id: int) -> None: pass

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
    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        pass

    @abstractmethod
    async def get_all_autopostings(self) -> list[model.Autoposting]:
        pass

    @abstractmethod
    async def get_autoposting_by_id(self, autoposting_id: int) -> list[model.Autoposting]: pass

    @abstractmethod
    async def delete_autoposting(self, autoposting_id: int) -> None:
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
    async def get_viewed_telegram_post(
            self,
            autoposting_id: int,
            tg_channel_username: str
    ) -> list[model.ViewedTelegramPost]:
        pass


class IPublicationPromptGenerator(Protocol):
    @abstractmethod
    async def get_generate_publication_text_system_prompt(
            self,
            category: model.Category,
            organization: model.Organization,
    ) -> str:
        pass

    @abstractmethod
    async def get_generate_publication_text_system_prompt_INoT(
            self,
            user_text_reference: str,
            category: model.Category,
            organization: model.Organization,
    ) -> str:
        pass

    @abstractmethod
    async def get_regenerate_publication_text_system_prompt(
            self,
            category: model.Category,
            organization: model.Organization,
            publication_text: str,
    ) -> str:
        pass

    @abstractmethod
    async def get_generate_publication_image_system_prompt(
            self,
            prompt_for_image_style: str,
            publication_text: str
    ) -> str:
        pass

    @abstractmethod
    async def get_regenerate_publication_image_system_prompt(
            self,
            prompt_for_image_style: str,
            publication_text: str,
            changes: str
    ) -> str:
        pass

    @abstractmethod
    async def get_filter_post_system_prompt(
            self,
            filter_prompt: str,
            post_text: str
    ) -> str:
        pass

    @abstractmethod
    async def get_generate_autoposting_text_system_prompt(
            self,
            autoposting_category: model.AutopostingCategory,
            organization: model.Organization,
            source_post_text: str
    ) -> str:
        pass

    @abstractmethod
    async def get_generate_autoposting_image_system_prompt(
            self,
            prompt_for_image_style: str,
            publication_text: str
    ) -> str:
        pass
