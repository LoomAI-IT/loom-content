from abc import abstractmethod
from typing import Protocol

from internal import model


class IKonturTgBotClient(Protocol):
    @abstractmethod
    async def send_generated_video_cut(
            self,
            video_cut_id: int,
            name: str,
            description: str,
            tags: str,

    ) -> None: pass
