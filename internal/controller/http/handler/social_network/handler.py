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
                self.logger.info("Create YouTube request", {
                    "organization_id": body.organization_id
                })

                youtube_id = await self.social_network_service.create_youtube(
                    organization_id=body.organization_id
                )

                self.logger.info("YouTube created successfully", {
                    "youtube_id": youtube_id,
                    "organization_id": body.organization_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "message": "YouTube created successfully",
                        "youtube_id": youtube_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                self.logger.info("Create Instagram request", {
                    "organization_id": body.organization_id
                })

                instagram_id = await self.social_network_service.create_instagram(
                    organization_id=body.organization_id
                )

                self.logger.info("Instagram created successfully", {
                    "instagram_id": instagram_id,
                    "organization_id": body.organization_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "message": "Instagram created successfully",
                        "instagram_id": instagram_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                self.logger.info("Check Telegram channel permission request", {
                    "channel": tg_channel_username
                })

                has_permission = await self.social_network_service.check_telegram_channel_permission(
                    tg_channel_username=tg_channel_username
                )

                self.logger.info("Telegram channel permission check completed", {
                    "channel": tg_channel_username,
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Telegram channel permission check completed",
                        "has_permission": has_permission,
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                self.logger.info("Create Telegram request", {
                    "organization_id": body.organization_id
                })

                telegram_id = await self.social_network_service.create_telegram(
                    organization_id=body.organization_id,
                    tg_channel_username=body.tg_channel_username,
                    autoselect=body.autoselect,
                )

                self.logger.info("Telegram created successfully", {
                    "telegram_id": telegram_id,
                    "organization_id": body.organization_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "message": "Telegram created successfully",
                        "telegram_id": telegram_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                self.logger.info("Update Telegram request", {
                    "organization_id": body.organization_id,
                })

                await self.social_network_service.update_telegram(
                    organization_id=body.organization_id,
                    tg_channel_username=body.tg_channel_username,
                    autoselect=body.autoselect
                )

                self.logger.info("Telegram updated successfully", {
                    "organization_id": body.organization_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Telegram updated successfully",
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                self.logger.info("Delete Telegram request", {
                    "organization_id": organization_id,
                })

                await self.social_network_service.delete_telegram(
                    organization_id=organization_id,
                )

                self.logger.info("Telegram deleted successfully", {

                    "organization_id": organization_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Telegram deleted successfully",
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                self.logger.info("Create Vkontakte request", {
                    "organization_id": body.organization_id
                })

                vkontakte_id = await self.social_network_service.create_vkontakte(
                    organization_id=body.organization_id
                )

                self.logger.info("Vkontakte created successfully", {
                    "vkontakte_id": vkontakte_id,
                    "organization_id": body.organization_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "message": "Vkontakte created successfully",
                        "vkontakte_id": vkontakte_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # ПОЛУЧЕНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    async def get_social_networks_by_organization(self, organization_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "SocialNetworkController.get_social_networks_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                self.logger.info("Get social networks by organization request", {
                    "organization_id": organization_id
                })

                social_networks = await self.social_network_service.get_social_networks_by_organization(organization_id)

                self.logger.info("Social networks retrieved successfully", {
                    "organization_id": organization_id,
                    "youtube_count": len(social_networks["youtube"]),
                    "instagram_count": len(social_networks["instagram"]),
                    "telegram_count": len(social_networks["telegram"]),
                    "vkontakte_count": len(social_networks["vkontakte"])
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Social networks retrieved successfully",
                        "data": {
                            "youtube": [youtube.to_dict() for youtube in social_networks["youtube"]],
                            "instagram": [instagram.to_dict() for instagram in social_networks["instagram"]],
                            "telegram": [telegram.to_dict() for telegram in social_networks["telegram"]],
                            "vkontakte": [vkontakte.to_dict() for vkontakte in social_networks["vkontakte"]]
                        }
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err