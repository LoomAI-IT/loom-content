from datetime import datetime
from opentelemetry.trace import Status, StatusCode, SpanKind

from .sql_query import *
from internal import interface, model


class VideoCutRepo(interface.IVideoCutRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB,
    ):
        self.tracer = tel.tracer()
        self.db = db

    # НАРЕЗКА
    async def create_vizard_project(
            self,
            project_id: int,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str,
    ) -> int:
        with self.tracer.start_as_current_span(
                "VideoCutRepo.create_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={
                    "project_id": project_id,
                    "organization_id": organization_id,
                    "creator_id": creator_id
                }
        ) as span:
            try:
                args = {
                    'project_id': project_id,
                    'organization_id': organization_id,
                    'creator_id': creator_id,
                    'youtube_video_reference': youtube_video_reference,
                }

                video_cut_id = await self.db.insert(create_vizard_project, args)

                span.set_status(Status(StatusCode.OK))
                return video_cut_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_vizard_video_cut(
            self,
            project_id: int,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str,
            name: str,
            description: str,
            transcript: str,
            tags: list[str],
            video_name: str,
            video_fid: str,
            vizard_rub_cost: int
    ) -> int:
        with self.tracer.start_as_current_span(
                "VideoCutRepo.create_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={
                    "project_id": project_id,
                    "organization_id": organization_id,
                    "creator_id": creator_id
                }
        ) as span:
            try:
                args = {
                    'project_id': project_id,
                    'organization_id': organization_id,
                    'creator_id': creator_id,
                    'youtube_video_reference': youtube_video_reference,
                    'name': name,
                    'description': description,
                    'transcript': transcript,
                    'tags': tags,
                    'video_name': video_name,
                    'video_fid': video_fid,
                    'vizard_rub_cost': vizard_rub_cost,
                }

                video_cut_id = await self.db.insert(create_vizard_video_cut, args)

                span.set_status(Status(StatusCode.OK))
                return video_cut_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def change_video_cut(
            self,
            video_cut_id: int,
            moderator_id: int = None,
            inst_source_id: int = None,
            youtube_source_id: int = None,
            name: str = None,
            description: str = None,
            tags: list[str] = None,
            moderation_status: str = None,
            moderation_comment: str = None,
            time_for_publication: datetime = None
    ) -> None:
        with self.tracer.start_as_current_span(
                "VideoCutRepo.change_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={
                    "video_cut_id": video_cut_id
                }
        ) as span:
            try:
                args = {
                    'video_cut_id': video_cut_id,
                    'moderator_id': moderator_id,
                    'inst_source_id': inst_source_id,
                    'youtube_source_id': youtube_source_id,
                    'name': name,
                    'description': description,
                    'tags': tags,
                    'moderation_status': moderation_status if moderation_status else None,
                    'moderation_comment': moderation_comment,
                    'time_for_publication': time_for_publication,
                }

                await self.db.update(change_video_cut, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_video_cut_by_id(self, video_cut_id: int) -> list[model.VideoCut]:
        with self.tracer.start_as_current_span(
                "VideoCutRepo.get_video_cut_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "video_cut_id": video_cut_id
                }
        ) as span:
            try:
                args = {'video_cut_id': video_cut_id}
                rows = await self.db.select(get_video_cut_by_id, args)
                video_cuts = model.VideoCut.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return video_cuts
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_video_cuts_by_project_id(self, project_id: int) -> list[model.VideoCut]:
        with self.tracer.start_as_current_span(
                "VideoCutRepo.get_video_cuts_by_project_id",
                kind=SpanKind.INTERNAL,
                attributes={"project_id": project_id}
        ) as span:
            try:
                args = {'project_id': project_id}
                rows = await self.db.select(get_video_cuts_by_project_id, args)
                video_cuts = model.VideoCut.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return video_cuts
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_video_cuts_by_organization(self, organization_id: int) -> list[model.VideoCut]:
        with self.tracer.start_as_current_span(
                "VideoCutRepo.get_video_cuts_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id
                }
        ) as span:
            try:
                args = {'organization_id': organization_id}
                rows = await self.db.select(get_video_cuts_by_organization, args)
                video_cuts = model.VideoCut.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return video_cuts
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err