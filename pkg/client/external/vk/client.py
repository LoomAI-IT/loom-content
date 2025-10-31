from pkg.client.client import AsyncHTTPClient
from internal import interface


class VkClient(interface.IVkClient):
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.api_version = "5.131"

        self.api_client = AsyncHTTPClient(
            "api.vk.com",
            443,
            prefix="/method",
            use_tracing=True,
            use_https=True
        )

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