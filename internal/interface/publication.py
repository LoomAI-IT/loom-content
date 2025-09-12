import io
from abc import abstractmethod
from typing import Protocol
from datetime import datetime

from fastapi import UploadFile
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse

from internal import model


class IPublicationController(Protocol):
    @abstractmethod
    async def create_publication(
            self,
            organization_id: int,
            category_id: int,
            creator_id: int,
            text_reference: str,
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def create_video_cut(
            self,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def get_publication_by_id(self, publication_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def get_video_cut_by_id(self, video_cut_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def get_publications_by_organization(self, organization_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def get_video_cuts_by_organization(self, organization_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def moderate_publication(
            self,
            publication_id: int,
            moderator_id: int,
            status: model.ModerationStatus,
            comment: str = ""
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def moderate_video_cut(
            self,
            video_cut_id: int,
            moderator_id: int,
            status: model.ModerationStatus,
            comment: str = ""
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def upload_publication_image(
            self,
            publication_id: int,
            image_file: UploadFile
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def upload_video_cut_file(
            self,
            video_cut_id: int,
            video_file: UploadFile
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def download_publication_image(
            self,
            publication_id: int
    ) -> StreamingResponse:
        pass

    @abstractmethod
    async def download_video_cut(
            self,
            video_cut_id: int
    ) -> StreamingResponse:
        pass

    @abstractmethod
    async def create_autoposting(
            self,
            organization_id: int,
            filter_prompt: str,
            rewrite_prompt: str,
            tg_channels: list[str] = None
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def get_autoposting_by_organization(self, organization_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def update_autoposting(
            self,
            autoposting_id: int,
            filter_prompt: str = None,
            rewrite_prompt: str = None,
            tg_channels: list[str] = None
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def delete_autoposting(self, autoposting_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def create_category(
            self,
            organization_id: int,
            prompt_for_image_style: str,
            prompt_for_text_style: str
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
            prompt_for_image_style: str = None,
            prompt_for_text_style: str = None
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def delete_category(self, category_id: int) -> JSONResponse:
        pass


class IPublicationService(Protocol):
    @abstractmethod
    async def create_publication(
            self,
            organization_id: int,
            category_id: int,
            creator_id: int,
            text_reference: str,
            name: str,
            text: str,
            text_end_sample: str = None,
            time_for_publication: datetime = None
    ) -> int:
        pass

    @abstractmethod
    async def create_video_cut(
            self,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str
    ) -> int:
        pass

    @abstractmethod
    async def get_publication_by_id(self, publication_id: int) -> model.Publication:
        pass

    @abstractmethod
    async def get_video_cut_by_id(self, video_cut_id: int) -> model.VideoCut:
        pass

    @abstractmethod
    async def get_publications_by_organization(self, organization_id: int) -> list[model.Publication]:
        pass

    @abstractmethod
    async def get_video_cuts_by_organization(self, organization_id: int) -> list[model.VideoCut]:
        pass

    @abstractmethod
    async def get_publications_for_moderation(self, organization_id: int) -> list[model.Publication]:
        pass

    @abstractmethod
    async def get_video_cuts_for_moderation(self, organization_id: int) -> list[model.VideoCut]:
        pass

    @abstractmethod
    async def moderate_publication(
            self,
            publication_id: int,
            moderator_id: int,
            status: model.ModerationStatus,
            comment: str = ""
    ) -> None:
        pass

    @abstractmethod
    async def moderate_video_cut(
            self,
            video_cut_id: int,
            moderator_id: int,
            status: model.ModerationStatus,
            comment: str = ""
    ) -> None:
        pass

    @abstractmethod
    async def upload_publication_image(
            self,
            publication_id: int,
            image_file: UploadFile
    ) -> str:
        pass

    @abstractmethod
    async def upload_video_cut_file(
            self,
            video_cut_id: int,
            video_file: UploadFile
    ) -> str:
        pass

    @abstractmethod
    async def download_publication_image(
            self,
            publication_id: int
    ) -> tuple[io.BytesIO, str]:
        pass

    @abstractmethod
    async def download_video_cut(
            self,
            video_cut_id: int
    ) -> tuple[io.BytesIO, str]:
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
    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        pass

    @abstractmethod
    async def update_autoposting(
            self,
            autoposting_id: int,
            filter_prompt: str = None,
            rewrite_prompt: str = None,
            tg_channels: list[str] = None
    ) -> None:
        pass

    @abstractmethod
    async def delete_autoposting(self, autoposting_id: int) -> None:
        pass

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
            text_end_sample: str = None,
            time_for_publication: datetime = None
    ) -> int:
        pass

    @abstractmethod
    async def create_video_cut(
            self,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str,
    ) -> int:
        pass

    @abstractmethod
    async def get_publication_by_id(self, publication_id: int) -> list[model.Publication]:
        pass

    @abstractmethod
    async def get_video_cut_by_id(self, video_cut_id: int) -> list[model.VideoCut]:
        pass

    @abstractmethod
    async def get_publications_by_organization(self, organization_id: int) -> list[model.Publication]:
        pass

    @abstractmethod
    async def get_video_cuts_by_organization(self, organization_id: int) -> list[model.VideoCut]:
        pass

    @abstractmethod
    async def get_publications_by_status(
            self,
            organization_id: int,
            status: model.ModerationStatus
    ) -> list[model.Publication]:
        pass

    @abstractmethod
    async def get_video_cuts_by_status(
            self,
            organization_id: int,
            status: model.ModerationStatus
    ) -> list[model.VideoCut]:
        pass

    @abstractmethod
    async def update_publication_moderation(
            self,
            publication_id: int,
            moderator_id: int,
            status: model.ModerationStatus,
            comment: str = ""
    ) -> None:
        pass

    @abstractmethod
    async def update_video_cut_moderation(
            self,
            video_cut_id: int,
            moderator_id: int,
            status: model.ModerationStatus,
            comment: str = ""
    ) -> None:
        pass

    @abstractmethod
    async def update_publication_image(
            self,
            publication_id: int,
            image_fid: str
    ) -> None:
        pass

    @abstractmethod
    async def update_video_cut_file(
            self,
            video_cut_id: int,
            video_fid: str
    ) -> None:
        pass

    @abstractmethod
    async def set_publication_published(
            self,
            publication_id: int,
            publication_at: datetime
    ) -> None:
        pass

    @abstractmethod
    async def set_video_cut_published(
            self,
            video_cut_id: int,
            publication_at: datetime
    ) -> None:
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
    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        pass

    @abstractmethod
    async def update_autoposting(
            self,
            autoposting_id: int,
            filter_prompt: str = None,
            rewrite_prompt: str = None,
            tg_channels: list[str] = None
    ) -> None:
        pass

    @abstractmethod
    async def delete_autoposting(self, autoposting_id: int) -> None:
        pass

    @abstractmethod
    async def create_category(
            self,
            organization_id: int,
            prompt_for_image_style: str,
            prompt_for_text_style: str
    ) -> int:
        pass

    @abstractmethod
    async def get_category_by_id(self, category_id: int) -> list[model.Category]:
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