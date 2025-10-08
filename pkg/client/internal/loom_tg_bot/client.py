from contextvars import ContextVar

from opentelemetry.trace import SpanKind

from internal import interface
from pkg.client.client import AsyncHTTPClient
from pkg.trace_wrapper import traced_method


class LoomTgBotClient(interface.ILoomTgBotClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            host: str,
            port: int,
            interserver_secret_key: str,
            log_context: ContextVar[dict],
    ):
        logger = tel.logger()
        self.client = AsyncHTTPClient(
            host,
            port,
            prefix="/api/tg-bot",
            use_tracing=True,
            logger=logger,
            log_context=log_context
        )
        self.tracer = tel.tracer()

        self.interserver_secret_key = interserver_secret_key

    @traced_method(SpanKind.CLIENT)
    async def notify_vizard_video_cut_generated(
            self,
            account_id: int,
            youtube_video_reference: str,
            video_count: int,
    ) -> None:
        body = {
            "account_id": account_id,
            "youtube_video_reference": youtube_video_reference,
            "video_count": video_count,
            "interserver_secret_key": self.interserver_secret_key,
        }
        response = await self.client.post("/video-cut/vizard/notify/generated", json=body)

    @traced_method(SpanKind.CLIENT)
    async def notify_publication_approved(
            self,
            account_id: int,
            publication_id: int,
    ) -> None:
        body = {
            "account_id": account_id,
            "publication_id": publication_id,
            "interserver_secret_key": self.interserver_secret_key,
        }
        response = await self.client.post("/notify/publication/approved", json=body)

    @traced_method(SpanKind.CLIENT)
    async def set_cache_file(
            self,
            filename: str,
            file_id: str,
    ) -> None:
        body = {
            "filename": filename,
            "file_id": file_id,
            "interserver_secret_key": self.interserver_secret_key,
        }
        response = await self.client.post("/file/cache", json=body)


