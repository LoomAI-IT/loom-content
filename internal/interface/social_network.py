import io
from abc import abstractmethod
from typing import Protocol, Sequence, Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from opentelemetry.metrics import Meter
from opentelemetry.trace import Tracer
from starlette.responses import StreamingResponse

from internal import model


class IInstagramClient(Protocol):
    @abstractmethod
    def get_authorization_url(self, scopes: list[str] = None) -> str: pass

    @abstractmethod
    async def exchange_code_for_token(self, authorization_code: str) -> dict: pass

    @abstractmethod
    async def get_instagram_account_id(self, access_token: str) -> str: pass

    @abstractmethod
    async def upload_reel(
            self,
            access_token: str,
            instagram_account_id: str,
            video_url: str,
            caption: str = "",
            cover_url: str = None,
            share_to_feed: bool = True
    ) -> dict: pass

class IYouTubeClient(Protocol):
    @abstractmethod
    def get_authorization_url(self, scopes: list[str] = None, state: str = None) -> str: pass

    @abstractmethod
    async def exchange_code_for_token(self, authorization_code: str) -> dict: pass

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> dict: pass

    @abstractmethod
    async def get_channel_info(self, access_token: str) -> dict: pass

    @abstractmethod
    async def upload_short(
            self,
            access_token: str,
            video_file: io.BytesIO,
            title: str,
            description: str = "",
            tags: list[str] = None,
            category_id: str = "22",  # People & Blogs
            privacy_status: str = "public",
            made_for_kids: bool = False,
            thumbnail_file: io.BytesIO = None
    ) -> dict: pass

    @abstractmethod
    async def get_video_info(self, access_token: str, video_id: str) -> dict: pass

class IVkClient(Protocol):
    @abstractmethod
    def get_auth_url(self, redirect_uri: str, scope: str = "wall,groups") -> str: pass

    @abstractmethod
    async def get_access_token(self, code: str, redirect_uri: str) -> dict: pass

    @abstractmethod
    async def get_user_info(self, access_token: str, user_ids: str | list[str] = None) -> list[dict]: pass

    @abstractmethod
    async def get_user_groups(self, access_token: str, extended: bool = True) -> dict: pass

    @abstractmethod
    async def upload_photo(self, access_token: str, photo_path: str, group_id: str = None) -> str: pass

    @abstractmethod
    async def post_to_wall(
            self,
            access_token: str,
            message: str = "",
            owner_id: str = None,
            attachments: list[str] = None,
            from_group: bool = False,
            publish_date: int = None
    ) -> dict: pass

    @abstractmethod
    async def post_to_group(
            self,
            access_token: str,
            group_id: str,
            message: str = "",
            attachments: list[str] = None,
            from_group: bool = True,
            publish_date: int = None,
            photo_paths: list[str] = None
    ) -> dict: pass
