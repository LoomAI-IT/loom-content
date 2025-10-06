from pkg.trace_wrapper import traced_method
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
    @traced_method()
    async def create_vizard_project(
            self,
            project_id: int,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str,
    ) -> int:
        args = {
            'project_id': project_id,
            'organization_id': organization_id,
            'creator_id': creator_id,
            'youtube_video_reference': youtube_video_reference,
        }

        video_cut_id = await self.db.insert(create_vizard_project, args)
        return video_cut_id

    @traced_method()
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
            original_url: str,
            vizard_rub_cost: int
    ) -> int:
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
            'original_url': original_url,
            'vizard_rub_cost': vizard_rub_cost,
        }

        video_cut_id = await self.db.insert(create_vizard_video_cut, args)
        return video_cut_id

    @traced_method()
    async def change_video_cut(
            self,
            video_cut_id: int,
            moderator_id: int = None,
            inst_source: bool = None,
            youtube_source: bool = None,
            name: str = None,
            description: str = None,
            tags: list[str] = None,
            moderation_status: str = None,
            moderation_comment: str = None
    ) -> None:
        args = {
            'video_cut_id': video_cut_id,
            'moderator_id': moderator_id,
            'inst_source': inst_source,
            'youtube_source': youtube_source,
            'name': name,
            'description': description,
            'tags': tags,
            'moderation_status': moderation_status if moderation_status else None,
            'moderation_comment': moderation_comment
        }

        await self.db.update(change_video_cut, args)

    @traced_method()
    async def delete_video_cut(self, video_cut_id: int) -> None:
        args = {'video_cut_id': video_cut_id}
        await self.db.delete(delete_video_cut, args)

    @traced_method()
    async def get_video_cut_by_id(self, video_cut_id: int) -> list[model.VideoCut]:
        args = {'video_cut_id': video_cut_id}
        rows = await self.db.select(get_video_cut_by_id, args)
        video_cuts = model.VideoCut.serialize(rows) if rows else []

        return video_cuts

    @traced_method()
    async def get_video_cuts_by_project_id(self, project_id: int) -> list[model.VideoCut]:
        args = {'project_id': project_id}
        rows = await self.db.select(get_video_cuts_by_project_id, args)
        video_cuts = model.VideoCut.serialize(rows) if rows else []

        return video_cuts

    @traced_method()
    async def get_video_cuts_by_organization(self, organization_id: int) -> list[model.VideoCut]:
        args = {'organization_id': organization_id}
        rows = await self.db.select(get_video_cuts_by_organization, args)
        video_cuts = model.VideoCut.serialize(rows) if rows else []

        return video_cuts
