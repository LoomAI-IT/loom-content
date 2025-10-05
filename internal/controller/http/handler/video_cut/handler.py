import io

from opentelemetry.trace import Status, StatusCode, SpanKind

from fastapi.responses import JSONResponse, StreamingResponse

from internal import interface
from internal.controller.http.handler.video_cut.model import *


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
    async def generate_vizard_video_cuts(
            self,
            body: GenerateVizardVideoCutsBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VideoCutController.generate_vizard_video_cuts",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": body.organization_id,
                    "creator_id": body.creator_id,
                    "youtube_video_reference": body.youtube_video_reference
                }
        ) as span:
            try:
                self.logger.info("Начало генерации нарезки видео")

                project_id = await self.video_cut_service.generate_vizard_video_cuts(
                    organization_id=body.organization_id,
                    creator_id=body.creator_id,
                    youtube_video_reference=body.youtube_video_reference,
                )

                self.logger.info("Нарезка видео сгенерирована")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "project_id": project_id
                    }
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def create_vizard_video_cuts(
            self,
            body: CreateVizardVideoCutsBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VideoCutController.create_vizard_video_cuts",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.video_cut_service.create_vizard_video_cuts(
                    body.projectId,
                    body.videos,
                    body.creditsUsed
                )

                return JSONResponse(
                    content={},
                    status_code=201,
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def change_video_cut(
            self,
            body: ChangeVideoCutBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VideoCutController.change_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": body.video_cut_id}
        ) as span:
            try:
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

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "video_cut_id": body.video_cut_id
                    }
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_video_cut(self, video_cut_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VideoCutController.delete_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                self.logger.info("Начало удаления нарезки видео")

                await self.video_cut_service.delete_video_cut(video_cut_id)

                self.logger.info("Нарезка видео удалена")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "video_cut_id": video_cut_id
                    }
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def send_video_cut_to_moderation(
            self,
            video_cut_id: int,
    ):
        with self.tracer.start_as_current_span(
                "VideoCutController.send_video_cut_to_moderation",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                self.logger.info("Начало отправки нарезки видео на модерацию")

                await self.video_cut_service.send_video_cut_to_moderation(
                    video_cut_id=video_cut_id
                )

                self.logger.info("Нарезка видео отправлена на модерацию")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "video_cut_id": video_cut_id
                    }
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_video_cut_by_id(self, video_cut_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VideoCutController.get_video_cut_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                self.logger.info("Начало получения нарезки видео")

                video_cut = await self.video_cut_service.get_video_cut_by_id(video_cut_id)

                self.logger.info("Нарезка видео получена")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "data": video_cut.to_dict()
                    }
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_video_cuts_by_organization(self, organization_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VideoCutController.get_video_cuts_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                self.logger.info("Начало получения нарезок видео организации")

                video_cuts = await self.video_cut_service.get_video_cuts_by_organization(organization_id)

                self.logger.info("Нарезки видео организации получены")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=[video_cut.to_dict() for video_cut in video_cuts]
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def moderate_video_cut(
            self,
            body: ModerateVideoCutBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "VideoCutController.moderate_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={
                    "video_cut_id": body.video_cut_id,
                    "moderator_id": body.moderator_id,
                    "moderation_status": body.moderation_status
                }
        ) as span:
            try:
                self.logger.info("Начало модерации нарезки видео")

                await self.video_cut_service.moderate_video_cut(
                    video_cut_id=body.video_cut_id,
                    moderator_id=body.moderator_id,
                    moderation_status=body.moderation_status,
                    moderation_comment=body.moderation_comment
                )

                self.logger.info("Нарезка видео промодерирована")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "video_cut_id": body.video_cut_id,
                        "moderation_status": body.moderation_status
                    }
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def download_video_cut(
            self,
            video_cut_id: int
    ) -> StreamingResponse:
        with self.tracer.start_as_current_span(
                "VideoCutController.download_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
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

                span.set_status(Status(StatusCode.OK))
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

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err
