from abc import abstractmethod
from typing import Protocol

from internal import model


class IKonturTgBotClient(Protocol):
    @abstractmethod
    async def notify_vizard_video_cut_generated(
            self,
            account_id: int,
            youtube_video_reference: str,
            video_count: int
    ) -> None: pass
