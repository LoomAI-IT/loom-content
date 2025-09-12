import asyncio

import time
from urllib.parse import urlencode

from pkg.client.client import AsyncHTTPClient
from internal import interface


class InstagramClient(interface.IInstagramClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            app_id: str,
            app_secret: str,
            redirect_uri: str
    ):
        self.logger = tel.logger()

        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri

        # API endpoints
        self.base_url = "graph.instagram.com"
        self.facebook_base_url = "graph.facebook.com/v18.0"
        self.auth_base_url = "api.instagram.com/oauth/authorize"

        self.base_client = AsyncHTTPClient(
            self.base_url,
            443,
            prefix="",
            use_tracing=True,
            logger=self.logger,
            use_https=True
        )

        self.facebook_base_client = AsyncHTTPClient(
            self.facebook_base_url,
            443,
            prefix="/v18.0",
            use_tracing=True,
            logger=self.logger,
            use_https=True
        )

        self.auth_base_url = AsyncHTTPClient(
            self.auth_base_url,
            443,
            prefix="/oauth/authorize",
            use_tracing=True,
            logger=self.logger,
            use_https=True
        )

    def get_authorization_url(self, scopes: list[str] = None) -> str:
        if scopes is None:
            scopes = [
                'instagram_basic',
                'instagram_content_publish',
                'pages_show_list',
                'pages_read_engagement'
            ]

        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': ','.join(scopes),
            'response_type': 'code'
        }

        return f"{self.auth_base_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, authorization_code: str) -> dict:
        data = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'code': authorization_code
        }

        try:
            response = await self.facebook_base_client.post("/oauth/access_token", data=data)
            token_data = response.json()

            # Получаем долгосрочный токен
            long_lived_token = await self._get_long_lived_token(token_data['access_token'])

            return {
                'access_token': long_lived_token,
                'token_type': token_data.get('token_type', 'bearer')
            }

        except Exception as e:
            raise e

    async def get_instagram_account_id(self, access_token: str) -> str:
        params = {
            'access_token': access_token
        }

        try:
            response = await self.facebook_base_client.get("/me/accounts", params=params)
            response.raise_for_status()

            pages = response.json()['data']

            # Ищем Instagram аккаунт среди страниц
            for page in pages:
                instagram_id = await self._get_instagram_id_for_page(page['id'], page['access_token'])
                if instagram_id:
                    return instagram_id

            raise Exception("Instagram аккаунт не найден")

        except Exception as e:
            raise e

    async def _get_long_lived_token(self, short_token: str) -> str:
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': short_token
        }

        try:
            response = await self.facebook_base_client.get("/oauth/access_token", params=params)
            response.raise_for_status()

            data = response.json()
            return data['access_token']

        except Exception as e:
            raise e

    async def _get_instagram_id_for_page(self, page_id: str, page_token: str) -> str | None:

        params = {
            'fields': 'instagram_business_account',
            'access_token': page_token
        }

        try:
            response = await self.facebook_base_client.get(f"/{page_id}", params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('instagram_business_account', {}).get('id')

        except Exception as e:
            return None

    async def upload_reel(
            self,
            access_token: str,
            instagram_account_id: str,
            video_url: str,
            caption: str = "",
            cover_url: str = None,
            share_to_feed: bool = True
    ) -> dict:
        try:
            # Шаг 1: Создаем контейнер для медиа
            container_id = await self._create_media_container(
                access_token,
                instagram_account_id,
                video_url,
                caption,
                cover_url,
                share_to_feed
            )

            # Шаг 2: Ждем обработки видео
            await self._wait_for_media_processing(access_token, container_id)

            # Шаг 3: Публикуем медиа
            return await self._publish_media(access_token, instagram_account_id, container_id)

        except Exception as e:
            raise e

    async def _create_media_container(
            self,
            access_token: str,
            instagram_account_id: str,
            video_url: str,
            caption: str,
            cover_url: str | None,
            share_to_feed: bool
    ) -> str:
        data: dict = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': caption,
            'share_to_feed': share_to_feed,
            'access_token': access_token
        }

        if cover_url:
            data['thumb_offset'] = 0  # Можно указать время для кадра обложки

        try:
            response = await self.base_client.post(f"/{instagram_account_id}/media", data=data)
            response.raise_for_status()

            result = response.json()
            return result['id']

        except Exception as e:
            raise e

    async def _wait_for_media_processing(self, access_token: str, container_id: str, max_wait: int = 300):

        params = {
            'fields': 'status_code',
            'access_token': access_token
        }

        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                response = await self.base_client.get(f"/{container_id}", params=params)
                response.raise_for_status()

                data = response.json()
                status = data.get('status_code')

                if status == 'FINISHED':
                    self.logger.info("Медиа обработано успешно")
                    return
                elif status == 'ERROR':
                    raise Exception("Ошибка при обработке медиа")

                self.logger.info(f"Статус обработки: {status}")
                await asyncio.sleep(10)

            except Exception as e:
                await asyncio.sleep(10)
                raise e

        raise Exception("Превышено время ожидания обработки медиа")

    async def _publish_media(
            self,
            access_token: str,
            instagram_account_id: str,
            container_id: str
    ) -> dict:
        data = {
            'creation_id': container_id,
            'access_token': access_token
        }

        try:
            response = await self.base_client.post(f"/{instagram_account_id}/media_publish", data=data)
            response.raise_for_status()

            result = response.json()
            return result

        except Exception as e:
            raise e

    async def get_media_info(self, access_token: str, media_id: str) -> dict:
        params = {
            'fields': 'id,media_type,media_url,permalink,caption,timestamp,like_count,comments_count',
            'access_token': access_token
        }

        try:
            response = await self.base_client.get(f"/{media_id}", params=params)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            raise e

# Пример использования
if __name__ == "__main__":
    # Конфигурация
    APP_ID = "your_app_id"
    APP_SECRET = "your_app_secret"
    REDIRECT_URI = "https://yourdomain.com/auth/callback"

    # Создаем клиент
    client = InstagramClient(APP_ID, APP_SECRET, REDIRECT_URI)

    # 1. Получаем URL для авторизации
    auth_url = client.get_authorization_url()
    print(f"Перейдите по ссылке для авторизации: {auth_url}")

    # 2. После авторизации получаем код и обмениваем на токен
    # authorization_code = "код_полученный_после_авторизации"
    # token_data = client.exchange_code_for_token(authorization_code)
    # access_token = token_data['access_token']

    # 3. Получаем ID Instagram аккаунта
    # instagram_id = client.get_instagram_account_id(access_token)

    # 4. Публикуем Reel
    # result = client.upload_reel(
    #     access_token=access_token,
    #     instagram_account_id=instagram_id,
    #     video_url="https://example.com/video.mp4",
    #     caption="Мой новый шорт! #shorts #video"
    # )
    #
    # print(f"Опубликовано: {result}")
