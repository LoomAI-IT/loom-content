import requests
import time
from typing import Dict, List, Union
from urllib.parse import urlencode


class VkClient:
    """
    Клиент для работы с VK API для публикации постов в группах от лица пользователей
    """

    def __init__(self, app_id: str, app_secret: str, api_version: str = "5.131"):
        """
        Инициализация VK клиента

        Args:
            app_id: ID приложения ВКонтакте
            app_secret: Секретный ключ приложения
            api_version: Версия API ВКонтакте
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.api_version = api_version
        self.base_url = "https://api.vk.com/method/"

    def get_auth_url(self, redirect_uri: str, scope: str = "wall,groups") -> str:
        """
        Получение URL для авторизации пользователя

        Args:
            redirect_uri: URL для перенаправления после авторизации
            scope: Права доступа (wall - стена, groups - группы)

        Returns:
            URL для авторизации
        """
        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'v': self.api_version
        }

        return f"https://oauth.vk.com/authorize?{urlencode(params)}"

    def get_access_token(self, code: str, redirect_uri: str) -> Dict:
        """
        Получение access token по коду авторизации

        Args:
            code: Код авторизации из redirect URL
            redirect_uri: URL перенаправления

        Returns:
            Словарь с access_token, user_id и expires_in
        """
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': redirect_uri,
            'code': code
        }

        response = requests.get("https://oauth.vk.com/access_token", params=params)

        if response.status_code != 200:
            raise Exception(f"Ошибка получения токена: {response.text}")

        return response.json()

    def _api_call(self, method: str, access_token: str, params: Dict = None) -> dict | list:
        """
        Выполнение API запроса к ВКонтакте

        Args:
            method: Метод API
            access_token: Токен доступа пользователя
            params: Дополнительные параметры

        Returns:
            Ответ от API
        """
        if params is None:
            params = {}

        params.update({
            'access_token': access_token,
            'v': self.api_version
        })

        url = f"{self.base_url}{method}"
        response = requests.post(url, data=params)

        if response.status_code != 200:
            raise Exception(f"HTTP ошибка: {response.status_code}")

        result = response.json()

        if 'error' in result:
            error = result['error']
            raise Exception(f"VK API ошибка {error['error_code']}: {error['error_msg']}")

        return result['response']

    def get_user_info(self, access_token: str, user_ids: Union[str, List[str]] = None) -> List[Dict]:
        """
        Получение информации о пользователе

        Args:
            access_token: Токен доступа
            user_ids: ID пользователей (по умолчанию - текущий пользователь)

        Returns:
            Список с информацией о пользователях
        """
        params = {}
        if user_ids:
            if isinstance(user_ids, list):
                user_ids = ','.join(map(str, user_ids))
            params['user_ids'] = user_ids

        return self._api_call('users.get', access_token, params)

    def get_user_groups(self, access_token: str, extended: bool = True) -> Dict:
        """
        Получение списка групп пользователя, где он может публиковать

        Args:
            access_token: Токен доступа пользователя
            extended: Получить расширенную информацию о группах

        Returns:
            Информация о группах
        """
        params = {
            'extended': 1 if extended else 0,
            'filter': 'moder'  # Группы, где пользователь модератор или админ
        }

        return self._api_call('groups.get', access_token, params)

    def upload_photo(self, access_token: str, photo_path: str, group_id: str = None) -> str:
        """
        Загрузка фото для поста

        Args:
            access_token: Токен доступа
            photo_path: Путь к файлу изображения
            group_id: ID группы (если публикуем в группе)

        Returns:
            Строка с attachment для поста
        """
        # Получаем URL для загрузки
        params = {}
        if group_id:
            params['group_id'] = group_id

        upload_server = self._api_call('photos.getWallUploadServer', access_token, params)
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

        saved_photo = self._api_call('photos.saveWallPhoto', access_token, save_params)

        photo_info = saved_photo[0]
        return f"photo{photo_info['owner_id']}_{photo_info['id']}"

    def post_to_wall(self,
                     access_token: str,
                     message: str = "",
                     owner_id: str = None,
                     attachments: List[str] = None,
                     from_group: bool = False,
                     publish_date: int = None) -> Dict:
        """
        Публикация поста на стену

        Args:
            access_token: Токен доступа пользователя
            message: Текст поста
            owner_id: ID владельца стены (группы или пользователя). Для группы указывать с минусом
            attachments: Список вложений (фото, видео, ссылки)
            from_group: Публиковать от имени группы (только для групп)
            publish_date: Время публикации в Unix timestamp (для отложенного поста)

        Returns:
            Информация о созданном посте
        """
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

        return self._api_call('wall.post', access_token, params)

    def post_to_group(self,
                      access_token: str,
                      group_id: str,
                      message: str = "",
                      attachments: List[str] = None,
                      from_group: bool = True,
                      publish_date: int = None,
                      photo_paths: List[str] = None) -> Dict:
        """
        Публикация поста в группе (упрощенный метод)

        Args:
            access_token: Токен доступа пользователя
            group_id: ID группы (без минуса)
            message: Текст поста
            attachments: Список вложений
            from_group: Публиковать от имени группы
            publish_date: Время публикации для отложенного поста
            photo_paths: Пути к фотографиям для автоматической загрузки

        Returns:
            Информация о созданном посте
        """
        all_attachments = attachments or []

        # Загружаем фотографии если они указаны
        if photo_paths:
            for photo_path in photo_paths:
                photo_attachment = self.upload_photo(access_token, photo_path, group_id)
                all_attachments.append(photo_attachment)

        # Публикуем пост
        return self.post_to_wall(
            access_token=access_token,
            message=message,
            owner_id=f"-{group_id}",  # Для группы ID указывается с минусом
            attachments=all_attachments,
            from_group=from_group,
            publish_date=publish_date
        )

    def schedule_post(self,
                      access_token: str,
                      group_id: str,
                      message: str,
                      publish_datetime: time.struct_time,
                      photo_paths: List[str] = None) -> Dict:
        """
        Запланировать отложенный пост

        Args:
            access_token: Токен доступа
            group_id: ID группы
            message: Текст поста
            publish_datetime: Время публикации
            photo_paths: Пути к фотографиям

        Returns:
            Информация о запланированном посте
        """
        publish_timestamp = int(time.mktime(publish_datetime))

        return self.post_to_group(
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
        app_id="YOUR_APP_ID",
        app_secret="YOUR_APP_SECRET"
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