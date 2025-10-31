from pkg.client.client import AsyncHTTPClient
from internal import interface


class VkClient(interface.IVkClient):
    def __init__(self, app_id: str):
        self.app_id = app_id

        self.api_client = AsyncHTTPClient(
            "api.vk.com",
            443,
            prefix="/method",
            use_tracing=True,
            use_https=True
        )