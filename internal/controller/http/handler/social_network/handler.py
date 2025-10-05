from opentelemetry.trace import Status, StatusCode, SpanKind

from fastapi.responses import JSONResponse

from internal import interface
from internal.controller.http.handler.social_network.model import *


class SocialNetworkController(interface.ISocialNetworkController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            social_network_service: interface.ISocialNetworkService,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.social_network_service = social_network_service

    # СОЗДАНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    async def create_youtube(
            self,
            body: CreateSocialNetworkBody,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "SocialNetworkController.create_youtube",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": body.organization_id}
        ) as span:
            try:
                self.logger.info("Начало создания YouTube")

                youtube_id = await self.social_network_service.create_youtube(
                    organization_id=body.organization_id
                )

                self.logger.info("YouTube создан")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "youtube_id": youtube_id
                    }
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def create_instagram(
            self,
            body: CreateSocialNetworkBody,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "SocialNetworkController.create_instagram",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": body.organization_id}
        ) as span:
            try:
                self.logger.info("Начало создания Instagram")

                instagram_id = await self.social_network_service.create_instagram(
                    organization_id=body.organization_id
                )

                self.logger.info("Instagram создан")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "instagram_id": instagram_id
                    }
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def check_telegram_channel_permission(
            self,
            tg_channel_username: str,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "SocialNetworkController.check_telegram_channel_permission",
                kind=SpanKind.INTERNAL,
                attributes={"channel": tg_channel_username}
        ) as span:
            try:
                self.logger.info("Начало проверки прав на канал Telegram")

                has_permission = await self.social_network_service.check_telegram_channel_permission(
                    tg_channel_username=tg_channel_username
                )

                self.logger.info("Проверка прав на канал Telegram завершена")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "has_permission": has_permission,
                    }
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def create_telegram(
            self,
            body: CreateTgBody,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "SocialNetworkController.create_telegram",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": body.organization_id}
        ) as span:
            try:
                self.logger.info("Начало создания Telegram")

                telegram_id = await self.social_network_service.create_telegram(
                    organization_id=body.organization_id,
                    tg_channel_username=body.tg_channel_username,
                    autoselect=body.autoselect,
                )

                self.logger.info("Telegram создан")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "telegram_id": telegram_id
                    }
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_telegram(
            self,
            body: UpdateTgBody,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "SocialNetworkController.update_telegram",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": body.organization_id,
                }
        ) as span:
            try:
                self.logger.info("Начало обновления Telegram")

                await self.social_network_service.update_telegram(
                    organization_id=body.organization_id,
                    tg_channel_username=body.tg_channel_username,
                    autoselect=body.autoselect
                )

                self.logger.info("Telegram обновлен")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={}
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_telegram(
            self,
            organization_id: int,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "SocialNetworkController.delete_telegram",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id,
                }
        ) as span:
            try:
                self.logger.info("Начало удаления Telegram")

                await self.social_network_service.delete_telegram(
                    organization_id=organization_id,
                )

                self.logger.info("Telegram удален")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={}
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def create_vkontakte(
            self,
            body: CreateSocialNetworkBody,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "SocialNetworkController.create_vkontakte",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": body.organization_id}
        ) as span:
            try:
                self.logger.info("Начало создания VKontakte")

                vkontakte_id = await self.social_network_service.create_vkontakte(
                    organization_id=body.organization_id
                )

                self.logger.info("VKontakte создан")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "vkontakte_id": vkontakte_id
                    }
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    # ПОЛУЧЕНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    async def get_social_networks_by_organization(self, organization_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "SocialNetworkController.get_social_networks_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                self.logger.info("Начало получения соцсетей организации")

                social_networks = await self.social_network_service.get_social_networks_by_organization(organization_id)

                self.logger.info("Соцсети организации получены")

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "data": {
                            "youtube": [youtube.to_dict() for youtube in social_networks["youtube"]],
                            "instagram": [instagram.to_dict() for instagram in social_networks["instagram"]],
                            "telegram": [telegram.to_dict() for telegram in social_networks["telegram"]],
                            "vkontakte": [vkontakte.to_dict() for vkontakte in social_networks["vkontakte"]]
                        }
                    }
                )

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err