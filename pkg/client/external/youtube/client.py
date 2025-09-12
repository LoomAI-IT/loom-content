import requests
from typing import Optional, Dict, Any, List, Union
from urllib.parse import urlencode
from io import BytesIO
import mimetypes

from internal import interface


class YouTubeClient:
    def __init__(
            self,
            tel: interface.ITelemetry,
            client_id: str,
            client_secret: str,
            redirect_uri: str
    ):
        """
        Инициализация клиента

        Args:
            client_id: Client ID из Google Cloud Console
            client_secret: Client Secret из Google Cloud Console
            redirect_uri: URI для перенаправления после авторизации
        """
        self.logger = tel.logger()

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        # API endpoints
        self.auth_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.api_base_url = "https://www.googleapis.com/youtube/v3"
        self.upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"

    def get_authorization_url(self, scopes: list[str] = None, state: str = None) -> str:

        """
        Генерирует URL для авторизации пользователя

        Args:
            scopes: Список разрешений. По умолчанию для загрузки видео
            state: Параметр состояния для защиты от CSRF

        Returns:
            URL для авторизации
        """
        if scopes is None:
            scopes = [
                'https://www.googleapis.com/auth/youtube.upload',
                'https://www.googleapis.com/auth/youtube',
                'https://www.googleapis.com/auth/youtube.readonly'
            ]

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(scopes),
            'response_type': 'code',
            'access_type': 'offline',  # Для получения refresh token
            'prompt': 'consent'
        }

        if state:
            params['state'] = state

        return f"{self.auth_base_url}?{urlencode(params)}"

    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Обменивает код авторизации на токены доступа

        Args:
            authorization_code: Код, полученный после авторизации

        Returns:
            Словарь с токенами доступа
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }

        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Обновляет токен доступа используя refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            Новые токены доступа
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise

    def get_channel_info(self, access_token: str) -> Dict[str, Any]:
        """
        Получает информацию о канале пользователя

        Args:
            access_token: Токен доступа

        Returns:
            Информация о канале
        """
        url = f"{self.api_base_url}/channels"

        params = {
            'part': 'snippet,statistics,status',
            'mine': 'true'
        }

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            if data['items']:
                return data['items'][0]
            else:
                raise Exception("Канал не найден")

        except requests.exceptions.RequestException as e:
            raise

    def upload_short(
            self,
            access_token: str,
            video_file: Union[str, bytes, BytesIO],
            title: str,
            description: str = "",
            tags: List[str] = None,
            category_id: str = "22",  # People & Blogs
            privacy_status: str = "public",
            made_for_kids: bool = False,
            thumbnail_file: Optional[Union[str, bytes, BytesIO]] = None
    ) -> Dict[str, Any]:
        """
        Загружает YouTube Short

        Args:
            access_token: Токен доступа
            video_file: Путь к файлу, байты или BytesIO объект
            title: Заголовок видео
            description: Описание видео
            tags: Теги видео
            category_id: ID категории видео
            privacy_status: Приватность (public, private, unlisted)
            made_for_kids: Предназначено ли для детей
            thumbnail_file: Файл превью (опционально)

        Returns:
            Информация о загруженном видео
        """

        # Подготавливаем метаданные
        snippet: dict = {
            'title': title,
            'description': description,
            'categoryId': category_id
        }

        if tags:
            snippet['tags'] = tags

        # Добавляем #Shorts в описание для определения как Short
        if '#Shorts' not in description and '#shorts' not in description:
            snippet['description'] = f"{description}\n\n#Shorts" if description else "#Shorts"

        video_metadata = {
            'snippet': snippet,
            'status': {
                'privacyStatus': privacy_status,
                'madeForKids': made_for_kids,
                'selfDeclaredMadeForKids': made_for_kids
            }
        }

        # Загружаем видео
        video_id = self._upload_video_file(access_token, video_file, video_metadata)

        # Загружаем превью, если предоставлено
        if thumbnail_file and video_id:
            self._upload_thumbnail(access_token, video_id, thumbnail_file)

        # Получаем информацию о загруженном видео
        return self.get_video_info(access_token, video_id)

    def _upload_video_file(
            self,
            access_token: str,
            video_file: Union[str, bytes, BytesIO],
            metadata: Dict[str, Any]
    ) -> str:
        """
        Загружает видеофайл на YouTube
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Upload-Content-Type': 'video/*'
        }

        params = {
            'part': 'snippet,status',
            'uploadType': 'resumable'
        }

        # Инициируем загрузку
        try:
            response = requests.post(
                self.upload_url,
                params=params,
                headers=headers,
                json=metadata
            )
            response.raise_for_status()

            upload_url = response.headers.get('Location')
            if not upload_url:
                raise Exception("Не получен URL для загрузки")

            # Получаем данные файла
            if isinstance(video_file, str):
                # Путь к файлу
                with open(video_file, 'rb') as f:
                    file_data = f.read()
                content_type = mimetypes.guess_type(video_file)[0] or 'video/mp4'
            elif isinstance(video_file, bytes):
                file_data = video_file
                content_type = 'video/mp4'
            elif isinstance(video_file, BytesIO):
                file_data = video_file.getvalue()
                content_type = 'video/mp4'
            else:
                raise ValueError("Неподдерживаемый тип файла")

            # Загружаем файл
            upload_headers = {
                'Content-Type': content_type,
                'Content-Length': str(len(file_data))
            }

            self.logger.info(f"Начинаем загрузку видео размером {len(file_data)} байт")

            upload_response = requests.put(upload_url, data=file_data, headers=upload_headers)
            upload_response.raise_for_status()

            result = upload_response.json()
            video_id = result['id']

            self.logger.info(f"Видео успешно загружено с ID: {video_id}")
            return video_id

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при загрузке видео: {e}")
            raise

    def _upload_thumbnail(
            self,
            access_token: str,
            video_id: str,
            thumbnail_file: Union[str, bytes, BytesIO]
    ):
        """
        Загружает превью для видео
        """
        url = f"{self.api_base_url}/thumbnails/set"

        params = {
            'videoId': video_id
        }

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        try:
            # Получаем данные файла превью
            if isinstance(thumbnail_file, str):
                with open(thumbnail_file, 'rb') as f:
                    file_data = f.read()
                content_type = mimetypes.guess_type(thumbnail_file)[0] or 'image/jpeg'
            elif isinstance(thumbnail_file, bytes):
                file_data = thumbnail_file
                content_type = 'image/jpeg'
            elif isinstance(thumbnail_file, BytesIO):
                file_data = thumbnail_file.getvalue()
                content_type = 'image/jpeg'
            else:
                raise ValueError("Неподдерживаемый тип файла превью")

            headers['Content-Type'] = content_type

            response = requests.post(url, params=params, headers=headers, data=file_data)
            response.raise_for_status()

            self.logger.info(f"Превью успешно загружено для видео {video_id}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при загрузке превью: {e}")
            # Не прерываем процесс, если превью не загрузилось

    def get_video_info(self, access_token: str, video_id: str) -> Dict[str, Any]:
        """
        Получает информацию о видео

        Args:
            access_token: Токен доступа
            video_id: ID видео

        Returns:
            Информация о видео
        """
        url = f"{self.api_base_url}/videos"

        params = {
            'part': 'snippet,statistics,status,contentDetails',
            'id': video_id
        }

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            if data['items']:
                return data['items'][0]
            else:
                raise Exception("Видео не найдено")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при получении информации о видео: {e}")
            raise

    def update_video(
            self,
            access_token: str,
            video_id: str,
            title: Optional[str] = None,
            description: Optional[str] = None,
            tags: Optional[List[str]] = None,
            privacy_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Обновляет информацию о видео

        Args:
            access_token: Токен доступа
            video_id: ID видео
            title: Новый заголовок
            description: Новое описание
            tags: Новые теги
            privacy_status: Новая приватность

        Returns:
            Обновленная информация о видео
        """
        # Получаем текущую информацию о видео
        current_video = self.get_video_info(access_token, video_id)

        url = f"{self.api_base_url}/videos"

        # Подготавливаем данные для обновления
        snippet = current_video['snippet'].copy()
        status = current_video['status'].copy()

        if title is not None:
            snippet['title'] = title
        if description is not None:
            snippet['description'] = description
        if tags is not None:
            snippet['tags'] = tags
        if privacy_status is not None:
            status['privacyStatus'] = privacy_status

        data = {
            'id': video_id,
            'snippet': snippet,
            'status': status
        }

        params = {
            'part': 'snippet,status'
        }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.put(url, params=params, headers=headers, json=data)
            response.raise_for_status()

            self.logger.info(f"Видео {video_id} успешно обновлено")
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при обновлении видео: {e}")
            raise

    def delete_video(self, access_token: str, video_id: str) -> bool:
        """
        Удаляет видео

        Args:
            access_token: Токен доступа
            video_id: ID видео

        Returns:
            True если удаление прошло успешно
        """
        url = f"{self.api_base_url}/videos"

        params = {
            'id': video_id
        }

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        try:
            response = requests.delete(url, params=params, headers=headers)
            response.raise_for_status()

            self.logger.info(f"Видео {video_id} успешно удалено")
            return True

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при удалении видео: {e}")
            return False

    def get_my_videos(self,
                      access_token: str,
                      max_results: int = 25,
                      order: str = "date") -> List[Dict[str, Any]]:
        """
        Получает список видео канала

        Args:
            access_token: Токен доступа
            max_results: Максимальное количество результатов
            order: Порядок сортировки (date, rating, relevance, title, viewCount)

        Returns:
            Список видео
        """
        # Сначала получаем ID канала
        channel_info = self.get_channel_info(access_token)
        channel_id = channel_info['id']

        url = f"{self.api_base_url}/search"

        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'maxResults': max_results,
            'order': order,
            'type': 'video'
        }

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            return data.get('items', [])

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при получении списка видео: {e}")
            raise


# Пример использования
if __name__ == "__main__":
    # Конфигурация
    CLIENT_ID = "your_client_id.googleusercontent.com"
    CLIENT_SECRET = "your_client_secret"
    REDIRECT_URI = "http://localhost:8080/auth/callback"

    # Создаем клиент
    client = YouTubeClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

    # 1. Получаем URL для авторизации
    auth_url = client.get_authorization_url()
    print(f"Перейдите по ссылке для авторизации: {auth_url}")

    # 2. После авторизации получаем код и обмениваем на токены
    # authorization_code = "код_полученный_после_авторизации"
    # tokens = client.exchange_code_for_token(authorization_code)
    # access_token = tokens['access_token']
    # refresh_token = tokens.get('refresh_token')

    # 3. Получаем информацию о канале
    # channel_info = client.get_channel_info(access_token)
    # print(f"Канал: {channel_info['snippet']['title']}")

    # 4. Загружаем Short
    # result = client.upload_short(
    #     access_token=access_token,
    #     video_file="/path/to/video.mp4",
    #     title="Мой новый Short!",
    #     description="Описание моего короткого видео",
    #     tags=["shorts", "youtube", "видео"]
    # )
    #
    # print(f"Видео загружено: https://youtu.be/{result['id']}")

    # 5. Обновляем токен при необходимости
    # if refresh_token:
    #     new_tokens = client.refresh_access_token(refresh_token)
    #     access_token = new_tokens['access_token']
