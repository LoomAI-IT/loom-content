from typing import Dict, List
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface


class SocialNetworkService(interface.ISocialNetworkService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            repo: interface.ISocialNetworkRepo,
            telegram_client: interface.ITelegramClient,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.repo = repo
        self.telegram_client = telegram_client

    # СОЗДАНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    async def create_youtube(
            self,
            organization_id: int
    ) -> int:
        with self.tracer.start_as_current_span(
                "SocialNetworkService.create_youtube",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                youtube_id = await self.repo.create_youtube(organization_id=organization_id)

                span.set_status(Status(StatusCode.OK))
                return youtube_id

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def create_instagram(
            self,
            organization_id: int
    ) -> int:
        with self.tracer.start_as_current_span(
                "SocialNetworkService.create_instagram",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                instagram_id = await self.repo.create_instagram(organization_id=organization_id)

                span.set_status(Status(StatusCode.OK))
                return instagram_id

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def check_telegram_channel_permission(
            self,
            tg_channel_username: str,
    ) -> bool:
        with self.tracer.start_as_current_span(
                "SocialNetworkService.check_telegram_channel_permission",
                kind=SpanKind.INTERNAL,
                attributes={"channel": tg_channel_username}
        ) as span:
            try:
                # Проверяем доступ к каналу
                has_permission = await self.telegram_client.check_permission(tg_channel_username)

                span.set_status(Status(StatusCode.OK))
                return has_permission

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def create_telegram(
            self,
            organization_id: int,
            tg_channel_username: str,
            autoselect: bool,
    ) -> int:
        with self.tracer.start_as_current_span(
                "SocialNetworkService.create_telegram",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                telegram_id = await self.repo.create_telegram(organization_id, tg_channel_username, autoselect)

                span.set_status(Status(StatusCode.OK))
                return telegram_id

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_telegram(
            self,
            organization_id: int,
            tg_channel_username: str = None,
            autoselect: bool = None
    ):
        with self.tracer.start_as_current_span(
                "SocialNetworkService.update_telegram",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                await self.repo.update_telegram(
                    organization_id,
                    tg_channel_username,
                    autoselect
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_telegram(
            self,
            organization_id: int,
    ):
        with self.tracer.start_as_current_span(
                "SocialNetworkService.delete_telegram",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                await self.repo.delete_telegram(organization_id)

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def create_vkontakte(
            self,
            organization_id: int
    ) -> int:
        with self.tracer.start_as_current_span(
                "SocialNetworkService.create_vkontakte",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                vkontakte_id = await self.repo.create_vkontakte(organization_id=organization_id)

                span.set_status(Status(StatusCode.OK))
                return vkontakte_id

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    # ПОЛУЧЕНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    async def get_social_networks_by_organization(
            self,
            organization_id: int
    ) -> Dict[str, List]:
        with self.tracer.start_as_current_span(
                "SocialNetworkService.get_social_networks_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                # Получаем все социальные сети организации параллельно
                youtube_list = await self.repo.get_youtubes_by_organization(organization_id)
                instagram_list = await self.repo.get_instagrams_by_organization(organization_id)
                telegram_list = await self.repo.get_telegrams_by_organization(organization_id)
                vkontakte_list = await self.repo.get_vkontakte_by_organization(organization_id)

                social_networks = {
                    "youtube": youtube_list,
                    "instagram": instagram_list,
                    "telegram": telegram_list,
                    "vkontakte": vkontakte_list
                }

                span.set_status(Status(StatusCode.OK))
                return social_networks

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err