import io

from fastapi.responses import JSONResponse, StreamingResponse

from internal import interface
from internal.controller.http.handler.video_cut.model import *
from pkg.log_wrapper import auto_log
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
    @auto_log()
    @traced_method()
    async def generate_vizard_video_cuts(
            self,
            body: GenerateVizardVideoCutsBody
    ) -> JSONResponse:
        project_id = await self.video_cut_service.generate_vizard_video_cuts(
            organization_id=body.organization_id,
            creator_id=body.creator_id,
            youtube_video_reference=body.youtube_video_reference,
        )
        return JSONResponse(
            status_code=201,
            content={
                "project_id": project_id
            }
        )

    @auto_log()
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

    @auto_log()
    @traced_method()
    async def change_video_cut(
            self,
            body: ChangeVideoCutBody
    ) -> JSONResponse:
        await self.video_cut_service.change_video_cut(
            video_cut_id=body.video_cut_id,
            name=body.name,
            description=body.description,
            tags=body.tags,
            inst_source=body.inst_source,
            youtube_source=body.youtube_source
        )
        return JSONResponse(
            status_code=200,
            content={
                "video_cut_id": body.video_cut_id
            }
        )

    @auto_log()
    @traced_method()
    async def delete_video_cut(self, video_cut_id: int) -> JSONResponse:
        await self.video_cut_service.delete_video_cut(video_cut_id)
        return JSONResponse(
            status_code=200,
            content={
                "video_cut_id": video_cut_id
            }
        )

    @auto_log()
    @traced_method()
    async def send_video_cut_to_moderation(
            self,
            video_cut_id: int,
    ):
        await self.video_cut_service.send_video_cut_to_moderation(
            video_cut_id=video_cut_id
        )
        return JSONResponse(
            status_code=200,
            content={
                "video_cut_id": video_cut_id
            }
        )

    @auto_log()
    @traced_method()
    async def get_video_cut_by_id(self, video_cut_id: int) -> JSONResponse:
        video_cut = await self.video_cut_service.get_video_cut_by_id(video_cut_id)
        return JSONResponse(
            status_code=200,
            content={
                "data": video_cut.to_dict()
            }
        )

    @auto_log()
    @traced_method()
    async def get_video_cuts_by_organization(self, organization_id: int) -> JSONResponse:
        video_cuts = await self.video_cut_service.get_video_cuts_by_organization(organization_id)
        return JSONResponse(
            status_code=200,
            content=[video_cut.to_dict() for video_cut in video_cuts]
        )

    @auto_log()
    @traced_method()
    async def moderate_video_cut(
            self,
            body: ModerateVideoCutBody
    ) -> JSONResponse:
        await self.video_cut_service.moderate_video_cut(
            video_cut_id=body.video_cut_id,
            moderator_id=body.moderator_id,
            moderation_status=body.moderation_status,
            moderation_comment=body.moderation_comment
        )
        return JSONResponse(
            status_code=200,
            content={
                "video_cut_id": body.video_cut_id,
                "moderation_status": body.moderation_status
            }
        )

    @auto_log()
    @traced_method()
    async def download_video_cut(
            self,
            video_cut_id: int
    ) -> StreamingResponse:
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
