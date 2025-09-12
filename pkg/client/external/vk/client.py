import logging

import requests
import time
from urllib.parse import urlencode

from pkg.client.client import AsyncHTTPClient
from internal import interface


class VkClient(interface.IVkClient):
    def __init__(
            self,
            # tel: interface.ITelemetry,
            app_id: str,
            app_secret: str,
            api_version: str = "5.131"
    ):
        self.logger = logging.getLogger(__name__)

        self.app_id = app_id
        self.app_secret = app_secret
        self.api_version = api_version
        self.base_url = "https://api.vk.com/method"

        self.base_client = AsyncHTTPClient(
            "api.vk.com",
            443,
            prefix="/method",
            use_tracing=True,
            logger=self.logger,
            use_https=True
        )

        self.auth_client = AsyncHTTPClient(
            "oauth.vk.com",
            443,
            prefix="/method",
            use_tracing=True,
            logger=self.logger,
            use_https=True
        )

    def get_auth_url(self, redirect_uri: str, scope: str = "wall,groups") -> str:
        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'v': self.api_version
        }

        return f"https://oauth.vk.com/authorize?{urlencode(params)}"

    async def get_access_token(self, code: str, redirect_uri: str) -> dict:
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': redirect_uri,
            'code': code
        }

        response = await self.auth_client.get("/access_token", params=params)

        if response.status_code != 200:
            raise Exception(f"Ошибка получения токена: {response.text}")

        return response.json()

    async def _api_call(self, method: str, access_token: str, params: dict = None) -> dict | list:
        if params is None:
            params = {}

        params.update({
            'access_token': access_token,
            'v': self.api_version
        })

        url = f"{self.base_url}{method}"
        response = await self.base_client.post(url, data=params)

        if response.status_code != 200:
            raise Exception(f"HTTP ошибка: {response.status_code}")

        result = response.json()

        if 'error' in result:
            error = result['error']
            raise Exception(f"VK API ошибка {error['error_code']}: {error['error_msg']}")

        return result['response']

    async def get_user_info(self, access_token: str, user_ids: str | list[str] = None) -> list[dict]:

        params = {}
        if user_ids:
            if isinstance(user_ids, list):
                user_ids = ','.join(map(str, user_ids))
            params['user_ids'] = user_ids

        return await self._api_call('users.get', access_token, params)

    async def get_user_groups(self, access_token: str, extended: bool = True) -> dict:
        params = {
            'extended': 1 if extended else 0,
            'filter': 'moder'  # Группы, где пользователь модератор или админ
        }

        return await self._api_call('groups.get', access_token, params)

    async def upload_photo(self, access_token: str, photo_path: str, group_id: str = None) -> str:
        params = {}
        if group_id:
            params['group_id'] = group_id

        upload_server = await self._api_call('photos.getWallUploadServer', access_token, params)
        upload_url = upload_server['upload_url']

        # Загружаем фото
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            response = requests.post(upload_url, files=files)

        if response.status_code != 200:
            raise Exception(f"Ошибка загрузки фото: {response.text}")

        upload_result = response.json()

        # Сохраняем фото
        save_params = {
            'photo': upload_result['photo'],
            'server': upload_result['server'],
            'hash': upload_result['hash']
        }
        if group_id:
            save_params['group_id'] = group_id

        saved_photo = await self._api_call('photos.saveWallPhoto', access_token, save_params)

        photo_info = saved_photo[0]
        return f"photo{photo_info['owner_id']}_{photo_info['id']}"

    async def post_to_wall(
            self,
            access_token: str,
            message: str = "",
            owner_id: str = None,
            attachments: list[str] = None,
            from_group: bool = False,
            publish_date: int = None
    ) -> dict:
        params = {}

        if message:
            params['message'] = message

        if owner_id:
            params['owner_id'] = owner_id

        if attachments:
            params['attachments'] = ','.join(attachments)

        if from_group:
            params['from_group'] = 1

        if publish_date:
            params['publish_date'] = publish_date

        return await self._api_call('wall.post', access_token, params)

    async def post_to_group(
            self,
            access_token: str,
            group_id: str,
            message: str = "",
            attachments: list[str] = None,
            from_group: bool = True,
            publish_date: int = None,
            photo_paths: list[str] = None
    ) -> dict:

        all_attachments = attachments or []

        # Загружаем фотографии если они указаны
        if photo_paths:
            for photo_path in photo_paths:
                photo_attachment = await self.upload_photo(access_token, photo_path, group_id)
                all_attachments.append(photo_attachment)

        # Публикуем пост
        return await self.post_to_wall(
            access_token=access_token,
            message=message,
            owner_id=f"-{group_id}",  # Для группы ID указывается с минусом
            attachments=all_attachments,
            from_group=from_group,
            publish_date=publish_date
        )

    async def schedule_post(
            self,
            access_token: str,
            group_id: str,
            message: str,
            publish_datetime: time.struct_time,
            photo_paths: list[str] = None
    ) -> dict:
        publish_timestamp = int(time.mktime(publish_datetime))

        return await self.post_to_group(
            access_token=access_token,
            group_id=group_id,
            message=message,
            publish_date=publish_timestamp,
            photo_paths=photo_paths
        )


# Пример использования
if __name__ == "__main__":
    # Инициализация клиента
    vk_client = VkClient(
        app_id="54141090",
        app_secret="leGJ3pNlIYW77A11fGI0"
    )

    # Получение URL для авторизации
    auth_url = vk_client.get_auth_url("http://your-site.com/vk/callback")
    print(f"URL для авторизации: {auth_url}")

    # После получения кода от пользователя
    # code = "код_из_callback_url"
    # token_info = vk_client.get_access_token(code, "http://your-site.com/vk/callback")
    # access_token = token_info['access_token']

    # Публикация поста в группе
    # post_result = vk_client.post_to_group(
    #     access_token=access_token,
    #     group_id="123456789",
    #     message="Тестовый пост из Python!",
    #     photo_paths=["path/to/image.jpg"]
    # )
    # print(f"Пост опубликован: {post_result}")
