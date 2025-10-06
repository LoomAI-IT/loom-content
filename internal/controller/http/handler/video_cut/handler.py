import io

from fastapi.responses import JSONResponse, StreamingResponse

from internal import interface
from internal.controller.http.handler.video_cut.model import *
from pkg.trace_wrapper import traced_method


class VideoCutController(interface.IVideoCutController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            video_cut_service: interface.IVideoCutService,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.video_cut_service = video_cut_service

    # НАРЕЗКА

    @traced_method()
    async def generate_vizard_video_cuts(
            self,
            body: GenerateVizardVideoCutsBody
    ) -> JSONResponse:
        self.logger.info("Начало генерации нарезки видео")

        project_id = await self.video_cut_service.generate_vizard_video_cuts(
            organization_id=body.organization_id,
            creator_id=body.creator_id,
            youtube_video_reference=body.youtube_video_reference,
        )

        self.logger.info("Нарезка видео сгенерирована")
        return JSONResponse(
            status_code=201,
            content={
                "project_id": project_id
            }
        )

    @traced_method()
    async def create_vizard_video_cuts(
            self,
            body: CreateVizardVideoCutsBody
    ) -> JSONResponse:
        await self.video_cut_service.create_vizard_video_cuts(
            body.projectId,
            body.videos,
            body.creditsUsed
        )

        return JSONResponse(
            content={},
            status_code=201,
        )

    @traced_method()
    async def change_video_cut(
            self,
            body: ChangeVideoCutBody
    ) -> JSONResponse:
        self.logger.info("Начало изменения нарезки видео")

        await self.video_cut_service.change_video_cut(
            video_cut_id=body.video_cut_id,
            name=body.name,
            description=body.description,
            tags=body.tags,
            inst_source=body.inst_source,
            youtube_source=body.youtube_source
        )

        self.logger.info("Нарезка видео изменена")
        return JSONResponse(
            status_code=200,
            content={
                "video_cut_id": body.video_cut_id
            }
        )

    @traced_method()
    async def delete_video_cut(self, video_cut_id: int) -> JSONResponse:
        self.logger.info("Начало удаления нарезки видео")

        await self.video_cut_service.delete_video_cut(video_cut_id)

        self.logger.info("Нарезка видео удалена")
        return JSONResponse(
            status_code=200,
            content={
                "video_cut_id": video_cut_id
            }
        )

    @traced_method()
    async def send_video_cut_to_moderation(
            self,
            video_cut_id: int,
    ):
        self.logger.info("Начало отправки нарезки видео на модерацию")

        await self.video_cut_service.send_video_cut_to_moderation(
            video_cut_id=video_cut_id
        )

        self.logger.info("Нарезка видео отправлена на модерацию")
        return JSONResponse(
            status_code=200,
            content={
                "video_cut_id": video_cut_id
            }
        )

    @traced_method()
    async def get_video_cut_by_id(self, video_cut_id: int) -> JSONResponse:
        self.logger.info("Начало получения нарезки видео")

        video_cut = await self.video_cut_service.get_video_cut_by_id(video_cut_id)

        self.logger.info("Нарезка видео получена")
        return JSONResponse(
            status_code=200,
            content={
                "data": video_cut.to_dict()
            }
        )

    @traced_method()
    async def get_video_cuts_by_organization(self, organization_id: int) -> JSONResponse:
        self.logger.info("Начало получения нарезок видео организации")

        video_cuts = await self.video_cut_service.get_video_cuts_by_organization(organization_id)

        self.logger.info("Нарезки видео организации получены")
        return JSONResponse(
            status_code=200,
            content=[video_cut.to_dict() for video_cut in video_cuts]
        )

    @traced_method()
    async def moderate_video_cut(
            self,
            body: ModerateVideoCutBody
    ) -> JSONResponse:
        self.logger.info("Начало модерации нарезки видео")

        await self.video_cut_service.moderate_video_cut(
            video_cut_id=body.video_cut_id,
            moderator_id=body.moderator_id,
            moderation_status=body.moderation_status,
            moderation_comment=body.moderation_comment
        )

        self.logger.info("Нарезка видео промодерирована")
        return JSONResponse(
            status_code=200,
            content={
                "video_cut_id": body.video_cut_id,
                "moderation_status": body.moderation_status
            }
        )

    @traced_method()
    async def download_video_cut(
            self,
            video_cut_id: int
    ) -> StreamingResponse:
        self.logger.info("Начало скачивания нарезки видео")

        video_io, content_type, video_name = await self.video_cut_service.download_video_cut(video_cut_id)

        video_content = video_io.read()
        file_size = len(video_content)
        video_io = io.BytesIO(video_content)

        def iterfile():
            try:
                while True:
                    chunk = video_io.read(8192)
                    if not chunk:
                        break
                    yield chunk
            finally:
                video_io.close()

        self.logger.info("Нарезка видео скачана")
        return StreamingResponse(
            iterfile(),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename={video_name}",
                "Content-Type": "video/mp4",
                "Accept-Ranges": "bytes",  # Важно для видео
                "Content-Length": str(file_size)  # Если знаете размер
            }
        )
