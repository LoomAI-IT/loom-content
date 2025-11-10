import io

from abc import abstractmethod
from typing import Protocol, Dict, List

from fastapi.responses import JSONResponse, HTMLResponse
from fastapi import Request

from internal import model
from internal.controller.http.handler.social_network.model import *


class ISocialNetworkController(Protocol):
    # СОЗДАНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    @abstractmethod
    async def create_youtube(
            self,
            body: CreateSocialNetworkBody,
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def create_instagram(
            self,
            body: CreateSocialNetworkBody,
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def check_telegram_channel_permission(
            self,
            tg_channel_username: str,
    ) -> JSONResponse: pass

    @abstractmethod
    async def create_telegram(
            self,
            body: CreateTgBody,
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def update_telegram(
            self,
            body: UpdateTgBody
    ) -> JSONResponse: pass

    @abstractmethod
    async def delete_telegram(
            self,
            organization_id: int,
    ) -> JSONResponse: pass

    @abstractmethod
    async def vk_select_group(
            self,
            body: 'VkSelectGroupBody',
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def get_vk_auth_url(
            self,
            organization_id: int
    ) -> JSONResponse:
        pass

    # ПОЛУЧЕНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    @abstractmethod
    async def get_social_networks_by_organization(self, organization_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def vk_oauth_callback(self, request: Request) -> HTMLResponse: pass


class ISocialNetworkService(Protocol):
    # СОЗДАНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    @abstractmethod
    async def create_youtube(
            self,
            organization_id: int
    ) -> int:
        pass

    @abstractmethod
    async def create_instagram(
            self,
            organization_id: int
    ) -> int:
        pass

    @abstractmethod
    async def check_telegram_channel_permission(
            self,
            tg_channel_username: str,
    ) -> bool: pass

    @abstractmethod
    async def create_telegram(
            self,
            organization_id: int,
            tg_channel_username: str,
            autoselect: bool,
    ) -> int:
        pass

    @abstractmethod
    async def update_telegram(
            self,
            organization_id: int,
            tg_channel_username: str = None,
            autoselect: bool = None
    ): pass

    @abstractmethod
    async def delete_telegram(
            self,
            organization_id: int,
    ): pass

    @abstractmethod
    async def create_vkontakte(
            self,
            organization_id: int,
            access_token: str,
            refresh_token: str,
            device_id: str,
            user_id: int
    ) -> int:
        pass

    @abstractmethod
    async def update_vkontakte(
            self,
            organization_id: int,
            access_token: str = None,
            refresh_token: str = None,
            device_id: str = None,
            user_id: int = None,
            vk_group_id: int = None,
            vk_group_name: str = None
    ):
        pass

    @abstractmethod
    async def process_vk_oauth_callback(
            self,
            code: str,
            device_id: str,
            state_token: str
    ) -> tuple[int, list]:
        pass

    @abstractmethod
    async def get_vk_auth_url(
            self,
            organization_id: int
    ) -> str:
        pass

    # ПОЛУЧЕНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    @abstractmethod
    async def get_social_networks_by_organization(
            self,
            organization_id: int
    ) -> Dict[str, List]:
        pass


class ISocialNetworkRepo(Protocol):
    # СОЗДАНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    @abstractmethod
    async def create_youtube(
            self,
            organization_id: int
    ) -> int:
        pass

    @abstractmethod
    async def create_instagram(
            self,
            organization_id: int
    ) -> int:
        pass

    @abstractmethod
    async def create_telegram(
            self,
            organization_id: int,
            tg_channel_username: str,
            autoselect: bool
    ) -> int:
        pass

    @abstractmethod
    async def create_vkontakte(
            self,
            organization_id: int,
            access_token: str,
            refresh_token: str,
            device_id: str,
            user_id: int,
            autoselect: bool = True
    ) -> int:
        pass

    @abstractmethod
    async def update_telegram(
            self,
            organization_id: int,
            tg_channel_username: str = None,
            autoselect: bool = None,
    ): pass

    @abstractmethod
    async def delete_telegram(
            self,
            organization_id: int,
    ): pass

    @abstractmethod
    async def update_vkontakte(
            self,
            organization_id: int,
            access_token: str = None,
            refresh_token: str = None,
            device_id: str = None,
            user_id: int = None,
            vk_group_id: int = None,
            vk_group_name: str = None
    ):
        pass

    @abstractmethod
    async def get_vkontakte_by_id(self, vkontakte_id: int) -> list[model.Vkontakte]:
        pass

    # ПОЛУЧЕНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    @abstractmethod
    async def get_youtubes_by_organization(self, organization_id: int) -> List[model.YouTube]:
        pass

    @abstractmethod
    async def get_instagrams_by_organization(self, organization_id: int) -> List[model.Instagram]:
        pass

    @abstractmethod
    async def get_telegrams_by_organization(self, organization_id: int) -> List[model.Telegram]:
        pass

    @abstractmethod
    async def get_vkontakte_by_organization(self, organization_id: int) -> List[model.Vkontakte]:
        pass


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


class ITelegramClient(Protocol):
    @abstractmethod
    async def send_text_message(
            self,
            channel_id: str | int,
            text: str,
    ) -> str: pass

    @abstractmethod
    async def send_photo(
            self,
            channel_id: str | int,
            photo: bytes,
            caption: str = None,
    ) -> str: pass

    @abstractmethod
    async def check_permission(
            self,
            channel_id: str | int,
    ) -> bool: pass

    @abstractmethod
    async def get_channel_posts(
            self,
            channel_id: str,
            limit: int = None
    ) -> list[dict]: pass


class IVkClient(Protocol):
    @abstractmethod
    def get_auth_url(self, redirect_uri: str, scope: str = "wall,groups") -> str: pass

    @abstractmethod
    async def get_access_token(self, code: str, redirect_uri: str) -> dict: pass

    @abstractmethod
    async def get_user_info(self, access_token: str, user_ids: str | list[str] = None) -> list[dict]: pass

    @abstractmethod
    def get_auth_url_for_groups(
            self,
            redirect_uri: str,
            group_ids: list[str],
            scope: str = "wall,photos,manage"
    ) -> str: pass

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
