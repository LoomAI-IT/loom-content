import logging
import time
from urllib.parse import urlencode
from typing import Dict, List, Optional, Union

from pkg.client.client import AsyncHTTPClient
from internal import interface


class VkClient(interface.IVkClient):
    def __init__(self, app_id: str, app_secret: str, api_version: str = "5.131"):
        self.logger = logging.getLogger(__name__)
        self.app_id = app_id
        self.app_secret = app_secret
        self.api_version = api_version

        # Клиент для API запросов
        self.api_client = AsyncHTTPClient(
            "api.vk.com",
            443,
            prefix="/method",
            use_tracing=True,
            logger=self.logger,
            use_https=True
        )

        # Клиент для OAuth
        self.oauth_client = AsyncHTTPClient(
            "oauth.vk.com",
            443,
            prefix="",
            use_tracing=True,
            logger=self.logger,
            use_https=True
        )

    def get_auth_url_for_groups(
            self,
            redirect_uri: str,
            group_ids: List[str],
            scope: str = "wall,photos,manage"
    ) -> str:
        """
        Генерирует URL для авторизации администратора группы
        для получения токенов доступа к группам
        """
        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'group_ids': ','.join(group_ids),
            'scope': scope,
            'v': self.api_version,
            'display': 'page'
        }
        return f"https://oauth.vk.com/authorize?{urlencode(params)}"

    def get_user_auth_url(self, redirect_uri: str, scope: str = "groups") -> str:
        """
        Генерирует URL для авторизации пользователя
        для получения его токена (нужен для получения списка групп)
        """
        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'v': self.api_version,
            'display': 'page'
        }
        return f"https://oauth.vk.com/authorize?{urlencode(params)}"

    async def get_user_access_token(self, code: str, redirect_uri: str) -> Dict:
        """Получает токен пользователя по коду авторизации"""
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': redirect_uri,
            'code': code
        }

        response = await self.oauth_client.get("/access_token", params=params)

        if response.status_code != 200:
            raise Exception(f"OAuth error: {response.status_code} - {response.text}")

        result = response.json()
        if 'error' in result:
            raise Exception(f"OAuth error: {result['error']} - {result.get('error_description', '')}")

        return result

    async def get_user_groups(self, user_access_token: str) -> list[dict]:
        """
        Получает список групп, где пользователь является администратором
        """
        params = {
            'access_token': user_access_token,
            'filter': 'admin',
            'extended': 1,
            'v': self.api_version
        }

        response = await self.api_client.post("/groups.get", data=params)

        if response.status_code != 200:
            raise Exception(f"HTTP error: {response.status_code}")

        result = response.json()
        if 'error' in result:
            error = result['error']
            raise Exception(f"VK API error {error['error_code']}: {error['error_msg']}")

        return result['response']['items']

    async def get_community_tokens(self, code: str, redirect_uri: str) -> Dict:
        """
        Получает токены доступа к сообществам по промежуточному коду
        """
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': redirect_uri,
            'code': code
        }

        response = await self.oauth_client.get("/access_token", params=params)

        if response.status_code != 200:
            raise Exception(f"HTTP error: {response.status_code}")

        result = response.json()
        if 'error' in result:
            raise Exception(f"OAuth error: {result['error']} - {result.get('error_description', '')}")

        return result

    async def _api_call(self, method: str, access_token: str, params: Dict = None) -> Union[Dict, List]:
        """Выполнение API-запроса к VK"""
        if params is None:
            params = {}

        params.update({
            'access_token': access_token,
            'v': self.api_version
        })

        response = await self.api_client.post(f"/{method}", data=params)

        if response.status_code != 200:
            raise Exception(f"HTTP error: {response.status_code}")

        result = response.json()
        if 'error' in result:
            error = result['error']
            raise Exception(f"VK API error {error['error_code']}: {error['error_msg']}")

        return result['response']

    async def upload_photo_to_group(self, group_token: str, photo_path: str, group_id: str) -> str:
        """Загружает фото в группу и возвращает attachment string"""
        # Получаем URL для загрузки
        upload_server = await self._api_call(
            'photos.getWallUploadServer',
            group_token,
            {'group_id': group_id}
        )

        # Загружаем фото через обычный HTTP клиент
        import requests
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            response = requests.post(upload_server['upload_url'], files=files)

        if response.status_code != 200:
            raise Exception(f"Photo upload error: {response.text}")

        upload_result = response.json()

        # Сохраняем фото
        save_params = {
            'group_id': group_id,
            'photo': upload_result['photo'],
            'server': upload_result['server'],
            'hash': upload_result['hash']
        }

        saved_photo = await self._api_call('photos.saveWallPhoto', group_token, save_params)

        photo_info = saved_photo[0]
        return f"photo{photo_info['owner_id']}_{photo_info['id']}"

    async def post_to_group(self, group_token: str, group_id: str, message: str = "",
                            attachments: List[str] = None, photo_paths: List[str] = None,
                            publish_date: int = None) -> Dict:
        """Публикует пост в группе"""

        all_attachments = attachments or []

        # Загружаем фотографии если они указаны
        if photo_paths:
            for photo_path in photo_paths:
                photo_attachment = await self.upload_photo_to_group(group_token, photo_path, group_id)
                all_attachments.append(photo_attachment)

        params = {
            'owner_id': f"-{group_id}",  # Для группы ID указывается с минусом
            'from_group': 1
        }

        if message:
            params['message'] = message

        if all_attachments:
            params['attachments'] = ','.join(all_attachments)

        if publish_date:
            params['publish_date'] = publish_date

        return await self._api_call('wall.post', group_token, params)