from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model
from internal import interface
from pkg.client.client import AsyncHTTPClient


class KonturTgBotClient(interface.IKonturTgBotClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            host: str,
            port: int,
            interserver_secret_key: str,
    ):
        logger = tel.logger()
        self.client = AsyncHTTPClient(
            host,
            port,
            prefix="/api/tg-bot",
            use_tracing=True,
            logger=logger,
        )
        self.tracer = tel.tracer()

        self.interserver_secret_key = interserver_secret_key

    async def notify_vizard_video_cut_generated(
            self,
            account_id: int,
            youtube_video_reference: str,
            video_count: int,
    ) -> None:
        with self.tracer.start_as_current_span(
                "KonturTgBotClient.notify_vizard_video_cut_generated",
                kind=SpanKind.CLIENT
        ) as span:
            try:
                body = {
                    "account_id": account_id,
                    "youtube_video_reference": youtube_video_reference,
                    "video_count": video_count,
                    "interserver_secret_key": self.interserver_secret_key,
                }
                response = await self.client.post("/video-cut/vizard/notify/generated", json=body)

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def set_cache_file(
            self,
            filename: str,
            file_id: str,
    ) -> None:
        with self.tracer.start_as_current_span(
                "KonturTgBotClient.set_cache_file",
                kind=SpanKind.CLIENT
        ) as span:
            try:
                body = {
                    "filename": filename,
                    "file_id": file_id
                }
                response = await self.client.post("/file/cache", json=body)

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise