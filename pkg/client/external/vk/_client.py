import hashlib
import logging
import secrets
import base64
import time
from urllib.parse import urlencode
from typing import Dict, List, Optional, Union

from pkg.client.client import AsyncHTTPClient
from internal import interface
import requests


class VkClient:

    def __init__(self, app_id: str, app_secret: str, redirect_uri: str, api_version: str = "5.199"):
        
        self.logger = logging.getLogger(__name__)
        self.app_id = app_id
        self.app_secret = app_secret
        self.api_version = api_version
        self.redirect_uri = redirect_uri

        # базовый клиент для запросов авторизации vk_outhv2
        self.id_vk_client = AsyncHTTPClient(
            "id.vk.com",
            443,
            prefix="",
            use_tracing=True,
            logger=self.logger,
            use_https=True
        )

        self.api_client = AsyncHTTPClient(
            "api.vk.ru",
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

    def get_user_auth_url(self, scope: str = "groups") -> tuple[str, str]:

        """
        Генерирует URL для авторизации пользователя
        
        Args:
            scope: Какие права мы хотим получать от пользователя

        Returns:
            Ссылка для авторизации пользователя, code_verifier (индентификатор высокой энтропии)
        """

        # записываем сгенерированные code_verifier и code_challenge
        code_verifier, code_challenge = self._generate_pkce_pair()

        # записываем сгенерированный state
        state = self._generate_state(48)

        # тело запроса
        request_body = {
            'response_type': 'code',
            'client_id': self.app_id,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'scope': scope,
            'redirect_uri': self.redirect_uri,
            'state': state,
        }

        # возвразаем code_verifier т.к. он нужен при каждом обмене данными
        return f"https://id.vk.ru/authorize?{urlencode(request_body)}", code_verifier
    
    def _generate_state(self, min_len: int = 32) -> str:

        """
        Генерирует state из допустимых символов [a-zA-Z0-9_-], длиной >= min_len.

        Args:
            min_len: Минимальная длинна 

        Returns:
            state (случайно сгенерированная строчка\n
                   Нужна для защиты от подмены ответа (CSRF)
        """
    
        state = ""


        while len(state) < min_len:
            # собираем случайную строку, которая является криптографически стойкой. генерируем по 16 байт (примерно по 22 символа) чтобы сильно не перескакивать по длине.
            state += secrets.token_urlsafe(16)
        
        # если слишком длинная последовательность - обрезаем
        return state[:max(min_len, 32)]

    def _generate_pkce_pair(self) -> tuple[str, str]:

        """
        Генерирует два значения: code_verifier и code_challenge для использования PKCE

        Returns:
            code_verifier, code_challenge
        """

        # Разрешенные значения дляя code_verifier и code_challange
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        
        # Генерируем code_verififer в длинну 64 при использовании криптографически стойкого генератора.
        code_verifier = "".join(secrets.choice(allowed) for _ in range(64))

        # Генерируем code_challange из code_verifier по sha256
        digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
        code_challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

        # Эти два значения нужны в PKCE (Proof Key for Code Exchange)
        # Это расширение протокола OAuth 2.0, которое повышает безопасность потока с кодом авторизации, защищая от атак с перехватом кода.
        # Работает так: при авторизации отправляем code_challenge, а уже на шаге обмена кода на токен отправляем code_verifier, сервер дешифрует verifier и должен получить challenge.
        # Иначен токены не будут отправлены
        return code_verifier, code_challenge

    async def exchange_user_code_for_token(self, authorization_code: str, code_verifier: str, device_id: str, state: str) -> Dict:
        
        """
        Меняем код на токены пользователя.

        Args:
            authorization_code: код авторизации
            code_verifier: один из компонентов PKCE
            device_id: уникальный индентификатор устройства
            state: случайная строчка с прошлых этапов

        Returns:
            access_tokens, user_id, state, scope
        """
        
        request_body = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "code_verifier": code_verifier,
            "client_id": self.app_id,
            "device_id": device_id,
            "redirect_uri": self.redirect_uri,
            "state": state
        }
        
        request_headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = await self.id_vk_client.post("/oauth2/auth", data=request_body, headers=request_headers)

        if response.status_code != 200:
            raise Exception(f"OAuth error: {response.status_code} - {response.text}")

        result = response.json()
        if 'error' in result:
            raise Exception(f"OAuth error: {result['error']} - {result.get('error_description', '')}")

        return result

    async def refresh_access_token(self, refresh_token: str, device_id: str, state: str) -> dict:

        """
        Меняем refresh_token на новый access_token.

        Args:
            refresh_token: токен обновления
            device_id: уникальный индентификатор устройства
            state: случайная строчка с прошлых этапов

        Returns:
            access_tokens
        """

        request_body = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.app_id,
            "device_id": device_id,
            "state": state
        }
        
        request_headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = await self.id_vk_client.post("/oauth2/auth", data=request_body, headers=request_headers)
        
        try:
            response = await self.id_vk_client.post("oauth2/auth", data=request_body, headers=request_headers)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            raise

    async def get_user_groups(self, user_access_token: str, user_id: str) -> list[dict]:
        """
        Получает список групп где пользователь может выкладывать посты

        Args:
            user_access_token: токен пользователя
            user_id: уникальный индентификатор пользователя (получаем на шаге с обменом кода)

        Returns:
            список групп
        """

        request_body = {
            'access_token': user_access_token,
            'user_id': user_id,
            'extended': 1,
            'filter': 'moder',
            'v': self.api_version
        }

        response = await self.api_client.post("/groups.get", data=request_body)

        if response.status_code != 200:
            raise Exception(f"HTTP error: {response.status_code}")

        result = response.json()
        if 'error' in result:
            error = result['error']
            raise Exception(f"VK API error {error['error_code']}: {error['error_msg']}")

        return result['response']['items']

    def get_auth_url_for_groups(self, redirect_uri: str, group_ids: List[str], scope: str = "stories,wall,photos,manage") -> str:
        
        """
        Генерирует URL для авторизации администратора группы
        для получения токенов доступа к группам
        """

        request_body = {
            'client_id': self.app_id,
            'group_ids': ','.join(group_ids),
            'v': self.api_version,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': scope,
            'display': 'page'
        }
        return f"https://oauth.vk.com/authorize?{urlencode(request_body)}"

    async def get_community_tokens(self, code: str, redirect_uri: str) -> Dict:
        """
        Получает токены доступа к сообществам по промежуточному коду
        """
        request_body = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': redirect_uri,
            'code': code
        }

        response = await self.oauth_client.get("/access_token", params=request_body)

        if response.status_code != 200:
            raise Exception(f"HTTP error: {response.status_code}")

        result = response.json()
        if 'error' in result:
            raise Exception(f"OAuth error: {result['error']} - {result.get('error_description', '')}")

        return result

    async def _api_call(self, method: str, access_token: str, request_body: Optional[Dict] = None) -> Union[Dict, List]:
        """Выполнение API-запроса к VK"""
        if request_body is None:
            request_body = {}

        request_body.update({
            'access_token': access_token,
            'v': self.api_version
        })

        response = await self.api_client.post(f"/{method}", data=request_body)

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
                            attachments: Optional[List[str]] = None, photo_paths: Optional[List[str]] = None,
                            publish_date: Optional[int] = None) -> Dict:
        """Публикует пост в группе"""

        all_attachments = attachments or []

        # Загружаем фотографии если они указаны
        if photo_paths:
            for photo_path in photo_paths:
                photo_attachment = await self.upload_photo_to_group(group_token, photo_path, group_id)
                all_attachments.append(photo_attachment)

        request_body = {
            'owner_id': f"-{group_id}",  # Для группы ID указывается с минусом
            'from_group': 1
        }

        if message:
            request_body['message'] = message

        if all_attachments:
            request_body['attachments'] = ','.join(all_attachments)

        if publish_date:
            request_body['publish_date'] = publish_date

        return await self._api_call('wall.post', group_token, request_body)


# Пример использования
if __name__ == "__main__":
    import asyncio

    CLIENT_ID = "53783668"
    CLIENT_SECRET = "MnZYrcexCNrMxsGgskr5"
    REDIRECT_URI = "https://dev3.loom-ai.ru/api/content/social-network/vkontakte"

    async def main():
        client = VkClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

        # Формируем ссылку на регистрацию пользователя
        auth_url, code_verifier = client.get_user_auth_url()
        print("\nAUTH URL:\n", auth_url, "\n")

        # Обмениваем нужные данные на код
        authorization_code = input("Paste code: ").strip()
        device_id = input("Device ID: ").strip()
        state = input("State: ").strip()

        print("-----------------------------------------------------------------\n")

        # 3) Обмен на токены
        tokens = await client.exchange_user_code_for_token(authorization_code=authorization_code, code_verifier=code_verifier, device_id=device_id, state=state)
        print("\nTOKENS:", tokens, "\n")

        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token")
        print("ACCESS_TOKEN:", access_token)
        print("REFRESH_TOKEN:", refresh_token)

        # 3. Обновляем токен при необходимости
        if refresh_token:
            new_tokens = await client.refresh_access_token(refresh_token=refresh_token, device_id=device_id, state=state)
            access_token = new_tokens['access_token']
            print(f"\nNEW_ACCESS_TOKEN: {access_token}\n")
        
        user_id = tokens['user_id']

        print(f"\nUser ID: {user_id}")
        print(f"\nScope:{tokens['scope']}\n")

        print("-----------------------------------------------------------------\n")



    asyncio.run(main())
