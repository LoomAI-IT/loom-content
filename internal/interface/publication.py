import io
from abc import abstractmethod
from typing import Protocol
from datetime import datetime

from fastapi import UploadFile
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse

from internal import model

from internal.controller.http.handler.publication.model import *


class IPublicationController(Protocol):
    # Публикация
    @abstractmethod
    async def generate_publication(
            self,
            body: GeneratePublicationBody,
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def regenerate_publication_image(
            self,
            body: RegeneratePublicationImageBody,
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def regenerate_publication_text(
            self,
            body: RegeneratePublicationTextBody,
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def change_publication(
            self,
            body: ChangePublicationBody,
    ) -> JSONResponse: pass

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
            body: UpdateCategoryBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def delete_category(self, category_id: int) -> JSONResponse:
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
            body: UpdateAutopostingBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def delete_autoposting(self, autoposting_id: int) -> JSONResponse:
        pass

    # НАРЕЗКА
    @abstractmethod
    async def generate_video_cut(
            self,
            body: GenerateVideoCutBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def change_video_cut(
            self,
            body: ChangeVideoCutBody
    ) -> JSONResponse: pass

    @abstractmethod
    async def send_video_cut_to_moderation(
            self,
            video_cut_id: int,
    ): pass

    @abstractmethod
    async def get_video_cut_by_id(self, video_cut_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def get_video_cuts_by_organization(self, organization_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def moderate_video_cut(
            self,
            body: ModerateVideoCutBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def download_video_cut(
            self,
            video_cut_id: int
    ) -> StreamingResponse:
        pass


class IPublicationService(Protocol):
    # Публикация
    @abstractmethod
    async def generate_publication(
            self,
            organization_id: int,
            category_id: int,
            creator_id: int,
            need_images: bool,
            text_reference: str,
            time_for_publication: str = None
    ) -> int:
        pass

    @abstractmethod
    async def regenerate_publication_image(
            self,
            publication_id: int,
            prompt: str = None,
    ) -> io.BytesIO:
        pass

    @abstractmethod
    async def regenerate_publication_text(
            self,
            publication_id: int,
            prompt: str = None,
    ) -> dict:
        pass

    @abstractmethod
    async def change_publication(
            self,
            publication_id: int,
            vk_source_id: int = None,
            tg_source_id: int = None,
            name: str = None,
            text: str = None,
            tags: list[str] = None,
            time_for_publication: datetime = None,
            image: UploadFile = None,
    ) -> None: pass

    @abstractmethod
    async def publish_publication(
            self,
            publication_id: int,
    ) -> None: pass

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
    ) -> None:
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

    # РУБРИКИ
    @abstractmethod
    async def create_category(
            self,
            organization_id: int,
            prompt_for_image_style: str,
            prompt_for_text_style: str
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
            prompt_for_image_style: str = None,
            prompt_for_text_style: str = None
    ) -> None:
        pass

    @abstractmethod
    async def delete_category(self, category_id: int) -> None:
        pass

    # АВТОПОСТИНГ
    @abstractmethod
    async def create_autoposting(
            self,
            organization_id: int,
            filter_prompt: str,
            rewrite_prompt: str,
            tg_channels: list[str] = None
    ) -> int:
        pass

    @abstractmethod
    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        pass

    @abstractmethod
    async def update_autoposting(
            self,
            autoposting_id: int,
            filter_prompt: str = None,
            rewrite_prompt: str = None,
            enabled: bool = None,
            tg_channels: list[str] = None
    ) -> None:
        pass

    @abstractmethod
    async def delete_autoposting(self, autoposting_id: int) -> None:
        pass

    # НАРЕЗКА
    @abstractmethod
    async def generate_video_cut(
            self,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str,
            time_for_publication: datetime = None
    ) -> int:
        pass

    @abstractmethod
    async def change_video_cut(
            self,
            video_cut_id: int,
            name: str = None,
            description: str = None,
            tags: list[str] = None,
            time_for_publication: datetime = None
    ) -> None: pass

    @abstractmethod
    async def send_video_cut_to_moderation(
            self,
            video_cut_id: int,
    ) -> None: pass

    @abstractmethod
    async def publish_video_cut(
            self,
            video_cut_id: int,
    ) -> None: pass

    @abstractmethod
    async def get_video_cut_by_id(self, video_cut_id: int) -> model.VideoCut:
        pass

    @abstractmethod
    async def get_video_cuts_by_organization(self, organization_id: int) -> list[model.VideoCut]:
        pass

    @abstractmethod
    async def moderate_video_cut(
            self,
            video_cut_id: int,
            moderator_id: int,
            moderation_status: str,
            moderation_comment: str = ""
    ) -> None:
        pass

    @abstractmethod
    async def download_video_cut(
            self,
            video_cut_id: int
    ) -> tuple[io.BytesIO, str]:
        pass


class IPublicationRepo(Protocol):
    @abstractmethod
    async def create_publication(
            self,
            organization_id: int,
            category_id: int,
            creator_id: int,
            text_reference: str,
            name: str,
            text: str,
            tags: list[str],
            time_for_publication: datetime = None
    ) -> int:
        pass

    @abstractmethod
    async def change_publication(
            self,
            publication_id: int,
            moderator_id: int = None,
            name: str = None,
            text: str = None,
            tags: list[str] = None,
            moderation_status: str = None,
            moderation_comment: str = None,
            time_for_publication: datetime = None,
            publication_at: datetime = None,
            image_fid: str = None,
            image_name: str = None,
    ) -> None: pass

    @abstractmethod
    async def add_openai_rub_cost_to_publication(
            self,
            publication_id: int,
            amount_rub: int
    ) -> None: pass

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
            prompt_for_image_style: str,
            prompt_for_text_style: str
    ) -> int:
        pass

    @abstractmethod
    async def update_category(
            self,
            category_id: int,
            prompt_for_image_style: str = None,
            prompt_for_text_style: str = None
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

    @abstractmethod
    async def create_autoposting(
            self,
            organization_id: int,
            filter_prompt: str,
            rewrite_prompt: str,
            tg_channels: list[str] = None
    ) -> int:
        pass

    @abstractmethod
    async def update_autoposting(
            self,
            autoposting_id: int,
            filter_prompt: str = None,
            rewrite_prompt: str = None,
            enabled: bool = None,
            tg_channels: list[str] = None
    ) -> None:
        pass

    @abstractmethod
    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        pass

    @abstractmethod
    async def delete_autoposting(self, autoposting_id: int) -> None:
        pass

    # НАРЕЗКА
    @abstractmethod
    async def create_video_cut(
            self,
            project_id: int,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str,
            name: str,
            description: str,
            tags: list[str],
            time_for_publication: datetime = None
    ) -> int:
        pass

    @abstractmethod
    async def change_video_cut(
            self,
            video_cut_id: int,
            moderator_id: int = None,
            inst_source_id: int = None,
            youtube_source_id: int = None,
            name: str = None,
            description: str = None,
            tags: list[str] = None,
            moderation_status: str = None,
            moderation_comment: str = None,
            time_for_publication: datetime = None
    ) -> None: pass

    @abstractmethod
    async def add_vizard_rub_cost_to_video_cut(
            self,
            video_cut_id: int,
            amount_rub: int
    ) -> None: pass

    @abstractmethod
    async def get_video_cut_by_id(self, video_cut_id: int) -> list[model.VideoCut]:
        pass

    @abstractmethod
    async def get_video_cuts_by_organization(self, organization_id: int) -> list[model.VideoCut]: pass


class IPublicationPromptGenerator(Protocol):
    @abstractmethod
    async def get_generate_publication_text_system_prompt(
            self,
            prompt_for_text_style: str,
            publication_text_reference: str
    ) -> str:
        pass

    @abstractmethod
    async def get_regenerate_publication_text_system_prompt(
            self,
            prompt_for_text_style: str,
            publication_text: str,
            changes: str
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
