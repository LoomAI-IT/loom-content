import io
from abc import abstractmethod
from typing import Protocol

from fastapi.responses import JSONResponse, Response
from starlette.responses import StreamingResponse

from internal import model

from internal.controller.http.handler.video_cut.model import *


class IVideoCutController(Protocol):
    @abstractmethod
    async def generate_vizard_video_cuts(
            self,
            body: GenerateVizardVideoCutsBody
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def create_vizard_video_cuts(
            self,
            body: CreateVizardVideoCutsBody
    ): pass

    @abstractmethod
    async def change_video_cut(
            self,
            body: ChangeVideoCutBody
    ) -> JSONResponse: pass

    @abstractmethod
    async def delete_video_cut(self, video_cut_id: int) -> JSONResponse:
        pass

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
    ) -> Response:
        pass


class IVideoCutService(Protocol):
    @abstractmethod
    async def generate_vizard_video_cuts(
            self,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str,
    ) -> int:
        pass

    @abstractmethod
    async def create_vizard_video_cuts(
            self,
            project_id: int,
            videos: list[Video],
            credit_usage: int
    ): pass

    @abstractmethod
    async def change_video_cut(
            self,
            video_cut_id: int,
            name: str = None,
            description: str = None,
            tags: list[str] = None,
            inst_source: bool = None,
            youtube_source: bool = None,
    ) -> None: pass

    @abstractmethod
    async def delete_video_cut(self, video_cut_id: int) -> None:
        pass

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
    ) -> tuple[io.BytesIO, str, str]:
        pass


class IVideoCutRepo(Protocol):
    # НАРЕЗКА
    @abstractmethod
    async def create_vizard_project(
            self,
            project_id: int,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str,
    ) -> int: pass

    @abstractmethod
    async def create_vizard_video_cut(
            self,
            project_id: int,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str,
            name: str,
            description: str,
            transcript: str,
            tags: list[str],
            video_name: str,
            video_fid: str,
            original_url: str,
            vizard_rub_cost: int
    ) -> int: pass

    @abstractmethod
    async def change_video_cut(
            self,
            video_cut_id: int,
            moderator_id: int = None,
            inst_source: bool = None,
            youtube_source: bool = None,
            name: str = None,
            description: str = None,
            tags: list[str] = None,
            moderation_status: str = None,
            moderation_comment: str = None
    ) -> None: pass

    @abstractmethod
    async def delete_video_cut(self, video_cut_id: int) -> None:
        pass

    @abstractmethod
    async def get_video_cut_by_id(self, video_cut_id: int) -> list[model.VideoCut]:
        pass

    @abstractmethod
    async def get_video_cuts_by_project_id(self, project_id: int) -> list[model.VideoCut]: pass

    @abstractmethod
    async def get_video_cuts_by_organization(self, organization_id: int) -> list[model.VideoCut]: pass
