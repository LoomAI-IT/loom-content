import io
from datetime import datetime

from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface, model


class VideoCutService(interface.IVideoCutService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            repo: interface.IVideoCutRepo,
            storage: interface.IStorage,
            organization_client: interface.IKonturOrganizationClient,
            vizard_client: interface.IVizardClient,

    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.repo = repo
        self.storage = storage
        self.organization_client = organization_client
        self.vizard_client = vizard_client

    # НАРЕЗКА
    async def generate_vizard_video_cuts(
            self,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str,
    ) -> int:
        with self.tracer.start_as_current_span(
                "VideoCutService.generate_vizard_video_cuts",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id,
                    "creator_id": creator_id,
                    "youtube_video_reference": youtube_video_reference
                }
        ) as span:
            try:
                # Создаем проект в Vizard
                vizard_project = await self.vizard_client.create_project(
                    video_url=youtube_video_reference,
                    video_type=1,
                    lang="ru",
                    prefer_length=0,
                    ratio_of_clip=1,  # 9:16 для вертикальных видео
                    remove_silence=True,
                    max_clip_number=3,
                    subtitle_switch=True,
                    emoji_switch=True,
                    highlight_switch=True,
                    headline_switch=True,
                    project_name=f"Video cut for org {organization_id}"
                )
                print(f"{vizard_project=}", flush=True)

                await self.repo.create_vizard_project(
                    vizard_project.get("project_id"),
                    organization_id,
                    creator_id,
                    youtube_video_reference,
                )

                span.set_status(Status(StatusCode.OK))

                return vizard_project.get("project_id")

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_vizard_video_cuts(
            self,
            project_id: int,
    ):
        with self.tracer.start_as_current_span(
                "VideoCutService.create_vizard_video_cuts",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                pass
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def change_video_cut(
            self,
            video_cut_id: int,
            name: str = None,
            description: str = None,
            tags: list[str] = None,
            time_for_publication: datetime = None
    ) -> None:
        with self.tracer.start_as_current_span(
                "VideoCutService.change_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                await self.repo.change_video_cut(
                    video_cut_id=video_cut_id,
                    name=name,
                    description=description,
                    tags=tags,
                    time_for_publication=time_for_publication
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_video_cut_to_moderation(
            self,
            video_cut_id: int,
    ) -> None:
        with self.tracer.start_as_current_span(
                "VideoCutService.send_video_cut_to_moderation",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                await self.repo.change_video_cut(
                    video_cut_id=video_cut_id,
                    moderation_status=model.ModerationStatus.MODERATION.value
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def publish_video_cut(
            self,
            video_cut_id: int,
    ) -> None:
        with self.tracer.start_as_current_span(
                "VideoCutService.publish_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                # Получаем видеонарезку
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

                # Обновляем статус
                await self.repo.change_video_cut(
                    video_cut_id=video_cut_id,
                    moderation_status=model.ModerationStatus.PUBLISHED.value
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_video_cut_by_id(self, video_cut_id: int) -> model.VideoCut:
        with self.tracer.start_as_current_span(
                "VideoCutService.get_video_cut_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                video_cuts = await self.repo.get_video_cut_by_id(video_cut_id)
                if not video_cuts:
                    raise ValueError(f"Video cut {video_cut_id} not found")

                span.set_status(Status(StatusCode.OK))
                return video_cuts[0]

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_video_cuts_by_organization(self, organization_id: int) -> list[model.VideoCut]:
        with self.tracer.start_as_current_span(
                "VideoCutService.get_video_cuts_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                video_cuts = await self.repo.get_video_cuts_by_organization(organization_id)

                span.set_status(Status(StatusCode.OK))
                return video_cuts

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def moderate_video_cut(
            self,
            video_cut_id: int,
            moderator_id: int,
            moderation_status: str,
            moderation_comment: str = ""
    ) -> None:
        with self.tracer.start_as_current_span(
                "VideoCutService.moderate_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={
                    "video_cut_id": video_cut_id,
                    "moderator_id": moderator_id,
                    "moderation_status": moderation_status
                }
        ) as span:
            try:
                await self.repo.change_video_cut(
                    video_cut_id=video_cut_id,
                    moderator_id=moderator_id,
                    moderation_status=moderation_status,
                    moderation_comment=moderation_comment
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def download_video_cut(
            self,
            video_cut_id: int
    ) -> tuple[io.BytesIO, str]:
        with self.tracer.start_as_current_span(
                "VideoCutService.download_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                # Получаем видеонарезку
                video_cuts = await self.repo.get_video_cut_by_id(video_cut_id)
                if not video_cuts:
                    raise ValueError(f"Video cut {video_cut_id} not found")

                video_cut = video_cuts[0]

                if not video_cut.video_fid:
                    # Проверяем статус проекта в Vizard
                    project_status = await self.vizard_client.get_project_status(str(video_cut.project_id))

                    if project_status.get("status") == "completed":
                        # TODO: Получить URL готового видео и скачать его
                        # video_url = project_status.get("video_url")
                        # Пока возвращаем ошибку
                        raise ValueError(f"Video cut {video_cut_id} is ready but not downloaded yet")
                    else:
                        raise ValueError(
                            f"Video cut {video_cut_id} is not ready yet. Status: {project_status.get('status', 'unknown')}")

                # Скачиваем из Storage
                video_io, content_type = await self.storage.download(
                    video_cut.video_fid,
                    video_cut.video_name or "video.mp4"
                )

                span.set_status(Status(StatusCode.OK))
                return video_io, content_type

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
