import requests
import json
import time
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
import logging


class InstagramClient:
    """
    Клиент для работы с Instagram Basic Display API и Instagram Graph API
    для авторизации пользователей и публикации Reels (шортов)
    """

    def __init__(self, app_id: str, app_secret: str, redirect_uri: str):
        """
        Инициализация клиента

        Args:
            app_id: ID приложения Facebook/Instagram
            app_secret: Секретный ключ приложения
            redirect_uri: URI для перенаправления после авторизации
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri

        # API endpoints
        self.base_url = "https://graph.instagram.com"
        self.facebook_base_url = "https://graph.facebook.com/v18.0"
        self.auth_base_url = "https://api.instagram.com/oauth/authorize"

        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_authorization_url(self, scopes: List[str] = None) -> str:
        """
        Генерирует URL для авторизации пользователя

        Args:
            scopes: Список разрешений. По умолчанию для публикации контента

        Returns:
            URL для авторизации
        """
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

    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Обменивает код авторизации на токен доступа

        Args:
            authorization_code: Код, полученный после авторизации

        Returns:
            Словарь с токеном доступа и информацией о пользователе
        """
        url = f"{self.facebook_base_url}/oauth/access_token"

        data = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'code': authorization_code
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()

            token_data = response.json()

            # Получаем долгосрочный токен
            long_lived_token = self._get_long_lived_token(token_data['access_token'])

            return {
                'access_token': long_lived_token,
                'token_type': token_data.get('token_type', 'bearer')
            }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при обмене кода на токен: {e}")
            raise

    def _get_long_lived_token(self, short_token: str) -> str:
        """
        Получает долгосрочный токен доступа

        Args:
            short_token: Краткосрочный токен

        Returns:
            Долгосрочный токен доступа
        """
        url = f"{self.facebook_base_url}/oauth/access_token"

        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': short_token
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data['access_token']

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при получении долгосрочного токена: {e}")
            return short_token

    def get_instagram_account_id(self, access_token: str) -> str:
        """
        Получает ID Instagram аккаунта пользователя

        Args:
            access_token: Токен доступа

        Returns:
            ID Instagram аккаунта
        """
        # Сначала получаем Facebook страницы
        url = f"{self.facebook_base_url}/me/accounts"

        params = {
            'access_token': access_token
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            pages = response.json()['data']

            # Ищем Instagram аккаунт среди страниц
            for page in pages:
                instagram_id = self._get_instagram_id_for_page(page['id'], page['access_token'])
                if instagram_id:
                    return instagram_id

            raise Exception("Instagram аккаунт не найден")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при получении ID аккаунта: {e}")
            raise

    def _get_instagram_id_for_page(self, page_id: str, page_token: str) -> Optional[str]:
        """
        Получает Instagram ID для Facebook страницы
        """
        url = f"{self.facebook_base_url}/{page_id}"

        params = {
            'fields': 'instagram_business_account',
            'access_token': page_token
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('instagram_business_account', {}).get('id')

        except:
            return None

    def upload_reel(self,
                    access_token: str,
                    instagram_account_id: str,
                    video_url: str,
                    caption: str = "",
                    cover_url: Optional[str] = None,
                    share_to_feed: bool = True) -> Dict[str, Any]:
        """
        Загружает и публикует Reel (шорт)

        Args:
            access_token: Токен доступа
            instagram_account_id: ID Instagram аккаунта
            video_url: URL видеофайла (должен быть доступен публично)
            caption: Описание к видео
            cover_url: URL обложки видео (опционально)
            share_to_feed: Поделиться ли в основной ленте

        Returns:
            Результат публикации
        """

        # Шаг 1: Создаем контейнер для медиа
        container_id = self._create_media_container(
            access_token,
            instagram_account_id,
            video_url,
            caption,
            cover_url,
            share_to_feed
        )

        # Шаг 2: Ждем обработки видео
        self._wait_for_media_processing(access_token, container_id)

        # Шаг 3: Публикуем медиа
        return self._publish_media(access_token, instagram_account_id, container_id)

    def _create_media_container(
            self,
            access_token: str,
            instagram_account_id: str,
            video_url: str,
            caption: str,
            cover_url: Optional[str],
            share_to_feed: bool
    ) -> str:
        """
        Создает контейнер для медиа
        """
        url = f"{self.base_url}/{instagram_account_id}/media"

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
            response = requests.post(url, data=data)
            response.raise_for_status()

            result = response.json()
            return result['id']

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при создании контейнера медиа: {e}")
            raise

    def _wait_for_media_processing(self, access_token: str, container_id: str, max_wait: int = 300):
        """
        Ожидает завершения обработки медиа

        Args:
            access_token: Токен доступа
            container_id: ID контейнера медиа
            max_wait: Максимальное время ожидания в секундах
        """
        url = f"{self.base_url}/{container_id}"

        params = {
            'fields': 'status_code',
            'access_token': access_token
        }

        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                status = data.get('status_code')

                if status == 'FINISHED':
                    self.logger.info("Медиа обработано успешно")
                    return
                elif status == 'ERROR':
                    raise Exception("Ошибка при обработке медиа")

                self.logger.info(f"Статус обработки: {status}")
                time.sleep(10)

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Ошибка при проверке статуса: {e}")
                time.sleep(10)

        raise Exception("Превышено время ожидания обработки медиа")

    def _publish_media(self, access_token: str, instagram_account_id: str, container_id: str) -> Dict[str, Any]:
        """
        Публикует медиа
        """
        url = f"{self.base_url}/{instagram_account_id}/media_publish"

        data = {
            'creation_id': container_id,
            'access_token': access_token
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()

            result = response.json()
            self.logger.info(f"Медиа опубликовано с ID: {result['id']}")
            return result

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при публикации медиа: {e}")
            raise

    def get_media_info(self, access_token: str, media_id: str) -> Dict[str, Any]:
        """
        Получает информацию о опубликованном медиа

        Args:
            access_token: Токен доступа
            media_id: ID медиа

        Returns:
            Информация о медиа
        """
        url = f"{self.base_url}/{media_id}"

        params = {
            'fields': 'id,media_type,media_url,permalink,caption,timestamp,like_count,comments_count',
            'access_token': access_token
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при получении информации о медиа: {e}")
            raise

    def delete_media(self, access_token: str, media_id: str) -> bool:
        """
        Удаляет медиа (работает только для некоторых типов контента)

        Args:
            access_token: Токен доступа
            media_id: ID медиа

        Returns:
            True если удаление прошло успешно
        """
        url = f"{self.base_url}/{media_id}"

        params = {
            'access_token': access_token
        }

        try:
            response = requests.delete(url, params=params)
            response.raise_for_status()

            return response.json().get('success', False)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при удалении медиа: {e}")
            return False


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
