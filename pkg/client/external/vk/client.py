from pkg.client.client import AsyncHTTPClient
from internal import interface


class VkClient(interface.IVkClient):
    def __init__(self, client_id: str, client_secret: str, redirect_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.api_version = "5.131"

        self.api_client = AsyncHTTPClient(
            "api.vk.com",
            443,
            prefix="/method",
            use_tracing=True,
            use_https=True
        )

    def get_oauth_url(self, state) -> str:
        scope = "wall,groups,offline"
        oauth_url = f"https://oauth.vk.com/authorize?client_id={self.client_id}&redirect_uri={self.redirect_url}&scope={scope}&response_type=code&state={state}&display=page"
        return oauth_url

    async def get_user_groups(self, access_token: str) -> list[dict]:
        """
        Получить список групп пользователя VK, где он является администратором

        Args:
            access_token: VK access token пользователя

        Returns:
            Список словарей с информацией о группах
        """
        params = {
            "access_token": access_token,
            "filter": "admin,editor,moder",  # только группы где пользователь администратор
            "extended": 1,  # получить полную информацию
            "v": self.api_version
        }

        response = await self.api_client.get(
            "/groups.get",
            params=params
        )
        response_json = response.json()

        if "error" in response_json:
            error_msg = response_json["error"].get("error_msg", "Unknown error")
            raise Exception(f"VK API error: {error_msg}")

        # VK API возвращает данные в формате {"response": {"count": N, "items": [...]}}
        items = response_json.get("response", {}).get("items", [])

        # Форматируем данные для удобного использования
        groups = []
        for group in items:
            groups.append({
                "id": group.get("id"),
                "name": group.get("name"),
                "screen_name": group.get("screen_name"),
                "photo_100": group.get("photo_100"),
                "members_count": group.get("members_count", 0)
            })

        return groups

    async def exchange_code_for_token(self, authorization_code: str) -> dict:
        oauth_client = AsyncHTTPClient(
            "oauth.vk.com",
            443,
            prefix="",
            use_tracing=True,
            use_https=True
        )

        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_url,
            "code": authorization_code
        }

        response = await oauth_client.get(
            "/access_token",
            params=params
        )
        response_json = response.json()

        if "error" in response_json:
            error_msg = response_json.get("error_description", response_json.get("error", "Unknown error"))
            raise Exception(f"VK OAuth error: {error_msg}")

        return response_json

    async def publish_post(
            self,
            access_token: str,
            owner_id: int,
            message: str,
            attachments: str = None
    ) -> dict:
        """
        Опубликовать пост на стене группы VK

        Args:
            access_token: VK access token пользователя с правами wall и groups
            owner_id: ID группы (отрицательное число, например -123456)
            message: Текст поста
            attachments: Вложения (опционально, например "photo123_456")

        Returns:
            Словарь с информацией о созданном посте:
            {
                "post_id": int
            }

        Raises:
            Exception: Если произошла ошибка при публикации
        """
        params = {
            "access_token": access_token,
            "owner_id": owner_id,  # отрицательный ID группы
            "from_group": 1,  # публиковать от имени группы
            "message": message,
            "v": self.api_version
        }

        if attachments:
            params["attachments"] = attachments

        response = await self.api_client.get(
            "/wall.post",
            params=params
        )
        response_json = response.json()

        if "error" in response_json:
            error_msg = response_json["error"].get("error_msg", "Unknown error")
            error_code = response_json["error"].get("error_code", 0)
            raise Exception(f"VK API error [{error_code}]: {error_msg}")

        post_id = response_json.get("response", {}).get("post_id")
        if not post_id:
            raise Exception("Failed to publish post: no post_id in response")

        return {
            "post_id": post_id,
            "owner_id": owner_id
        }