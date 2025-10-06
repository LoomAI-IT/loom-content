import io
import json

import aiohttp
from aiogram import Bot
from aiogram.types import BufferedInputFile

from internal import interface, model

from internal.controller.http.handler.video_cut.model import *
from pkg.trace_wrapper import traced_method


class VideoCutService(interface.IVideoCutService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            repo: interface.IVideoCutRepo,
            storage: interface.IStorage,
            organization_client: interface.ILoomOrganizationClient,
            loom_tg_bot_client: interface.ILoomTgBotClient,
            vizard_client: interface.IVizardClient,
            bot: Bot

    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.repo = repo
        self.storage = storage
        self.organization_client = organization_client
        self.loom_tg_bot_client = loom_tg_bot_client
        self.vizard_client = vizard_client
        self.bot = bot

    @traced_method()
    async def generate_vizard_video_cuts(
            self,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str,
    ) -> int:
        vizard_project = await self.vizard_client.create_project(
            video_url=youtube_video_reference,
            video_type=2,
            lang="ru",
            prefer_length=0,
            ratio_of_clip=1,
            remove_silence=True,
            max_clip_number=2,
            subtitle_switch=True,
            emoji_switch=True,
            highlight_switch=True,
            headline_switch=True,
            project_name=youtube_video_reference
        )

        project_id = vizard_project["projectId"]

        await self.repo.create_vizard_project(
            project_id,
            organization_id,
            creator_id,
            youtube_video_reference,
        )

        return project_id

    @traced_method()
    async def create_vizard_video_cuts(
            self,
            project_id: int,
            videos: list[Video],
            credit_usage: int
    ):
        vizard_project = await self.repo.get_video_cuts_by_project_id(project_id)
        if not vizard_project:
            return

        vizard_project = vizard_project[0]

        rub_cost_per_credit = 10
        total_rub_cost = credit_usage * rub_cost_per_credit
        rub_cost_per_video = total_rub_cost // len(videos)

        for video in videos:
            video_content, content_type = await self._download_video_from_url(video.videoUrl)
            video_io = io.BytesIO(video_content)

            extension = ".mp4"
            video_name = f"video_cut_{video.videoId}_{project_id}{extension}"

            upload_response = await self.storage.upload(video_io, video_name)

            tags = json.loads(video.relatedTopic)

            video_cut_id = await self.repo.create_vizard_video_cut(
                project_id=project_id,
                organization_id=vizard_project.organization_id,
                creator_id=vizard_project.creator_id,
                youtube_video_reference=vizard_project.youtube_video_reference,
                name=video.title or f"Video Cut #{video.videoId}",
                description=video.viralReason or "",
                transcript=video.transcript or "",
                tags=tags,
                video_name=video_name,
                original_url=video.videoUrl,
                video_fid=upload_response.fid,
                vizard_rub_cost=rub_cost_per_video
            )
            resp = await self.bot.send_video(
                7529376518,
                video=BufferedInputFile(video_content, filename=video_name)
            )
            await self.loom_tg_bot_client.set_cache_file(
                video_name,
                resp.video.file_id
            )

        await self.loom_tg_bot_client.notify_vizard_video_cut_generated(
            vizard_project.creator_id,
            vizard_project.youtube_video_reference,
            len(videos),
        )

    @traced_method()
    async def change_video_cut(
            self,
            video_cut_id: int,
            name: str = None,
            description: str = None,
            tags: list[str] = None,
            inst_source: bool = None,
            youtube_source: bool = None,
    ) -> None:
        await self.repo.change_video_cut(
            video_cut_id=video_cut_id,
            name=name,
            description=description,
            tags=tags,
            inst_source=inst_source,
            youtube_source=youtube_source,
        )

    @traced_method()
    async def delete_video_cut(self, video_cut_id: int) -> None:
        video_cut = (await self.repo.get_video_cut_by_id(video_cut_id))[0]

        if video_cut.video_fid and video_cut.video_name:
            await self.storage.delete(video_cut.video_fid, video_cut.video_name)

        await self.repo.delete_video_cut(video_cut_id)

        self.logger.info(f"Video cut {video_cut_id} deleted successfully")

    @traced_method()
    async def send_video_cut_to_moderation(
            self,
            video_cut_id: int,
    ) -> None:
        await self.repo.change_video_cut(
            video_cut_id=video_cut_id,
            moderation_status=model.ModerationStatus.MODERATION.value
        )

    @traced_method()
    async def publish_video_cut(
            self,
            video_cut_id: int,
    ) -> None:
        video_cuts = await self.repo.get_video_cut_by_id(video_cut_id)
        if not video_cuts:
            raise ValueError(f"Video cut {video_cut_id} not found")

        video_cut = video_cuts[0]

        # Проверяем статус
        if video_cut.moderation_status != model.ModerationStatus.APPROVED:
            raise ValueError(f"Video cut must be approved before publishing")

        try:
            # TODO: Здесь нужно добавить логику отправки в соцсети
            # Например, через VK, Instagram, YouTube клиенты
            pass
        except Exception as send_error:
            self.logger.error(f"Failed to send video cut via Telegram: {str(send_error)}")

        await self.repo.change_video_cut(
            video_cut_id=video_cut_id,
            moderation_status=model.ModerationStatus.PUBLISHED.value
        )

    @traced_method()
    async def get_video_cut_by_id(self, video_cut_id: int) -> model.VideoCut:
        video_cut = (await self.repo.get_video_cut_by_id(video_cut_id))[0]
        return video_cut

    @traced_method()
    async def get_video_cuts_by_organization(self, organization_id: int) -> list[model.VideoCut]:
        video_cuts = await self.repo.get_video_cuts_by_organization(organization_id)
        return video_cuts

    @traced_method()
    async def moderate_video_cut(
            self,
            video_cut_id: int,
            moderator_id: int,
            moderation_status: str,
            moderation_comment: str = ""
    ) -> None:
        await self.repo.change_video_cut(
            video_cut_id=video_cut_id,
            moderator_id=moderator_id,
            moderation_status=moderation_status,
            moderation_comment=moderation_comment
        )

    @traced_method()
    async def download_video_cut(
            self,
            video_cut_id: int
    ) -> tuple[io.BytesIO, str, str]:
        video_cut = (await self.repo.get_video_cut_by_id(video_cut_id))[0]

        video_io, content_type = await self.storage.download(
            video_cut.video_fid,
            video_cut.video_name
        )

        return video_io, content_type, video_cut.video_name

    async def _download_video_from_url(self, video_url: str) -> tuple[bytes, str]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', 'video/mp4')
                        content = await response.read()
                        return content, content_type
                    else:
                        raise Exception(f"Failed to download video: HTTP {response.status}")
        except Exception as err:
            raise err
