from opentelemetry.trace import Status, StatusCode, SpanKind

from fastapi.responses import JSONResponse

from internal import interface
from internal.controller.http.handler.social_network.model import *
from pkg.log_wrapper import auto_log
from pkg.trace_wrapper import traced_method


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
    @auto_log()
    @traced_method()
    async def create_youtube(
            self,
            body: CreateSocialNetworkBody,
    ) -> JSONResponse:
        youtube_id = await self.social_network_service.create_youtube(
            organization_id=body.organization_id
        )
        return JSONResponse(
            status_code=201,
            content={
                "youtube_id": youtube_id
            }
        )

    @auto_log()
    @traced_method()
    async def create_instagram(
            self,
            body: CreateSocialNetworkBody,
    ) -> JSONResponse:
        instagram_id = await self.social_network_service.create_instagram(
            organization_id=body.organization_id
        )
        return JSONResponse(
            status_code=201,
            content={
                "instagram_id": instagram_id
            }
        )

    @auto_log()
    @traced_method()
    async def check_telegram_channel_permission(
            self,
            tg_channel_username: str,
    ) -> JSONResponse:
        has_permission = await self.social_network_service.check_telegram_channel_permission(
            tg_channel_username=tg_channel_username
        )
        return JSONResponse(
            status_code=200,
            content={
                "has_permission": has_permission,
            }
        )

    @auto_log()
    @traced_method()
    async def create_telegram(
            self,
            body: CreateTgBody,
    ) -> JSONResponse:
        telegram_id = await self.social_network_service.create_telegram(
            organization_id=body.organization_id,
            tg_channel_username=body.tg_channel_username,
            autoselect=body.autoselect,
        )
        return JSONResponse(
            status_code=201,
            content={
                "telegram_id": telegram_id
            }
        )

    @auto_log()
    @traced_method()
    async def update_telegram(
            self,
            body: UpdateTgBody,
    ) -> JSONResponse:
        await self.social_network_service.update_telegram(
            organization_id=body.organization_id,
            tg_channel_username=body.tg_channel_username,
            autoselect=body.autoselect
        )
        return JSONResponse(
            status_code=200,
            content={}
        )

    @auto_log()
    @traced_method()
    async def delete_telegram(
            self,
            organization_id: int,
    ) -> JSONResponse:
        await self.social_network_service.delete_telegram(
            organization_id=organization_id,
        )
        return JSONResponse(
            status_code=200,
            content={}
        )

    @auto_log()
    @traced_method()
    async def create_vkontakte(
            self,
            body: CreateSocialNetworkBody,
    ) -> JSONResponse:
        vkontakte_id = await self.social_network_service.create_vkontakte(
            organization_id=body.organization_id
        )
        return JSONResponse(
            status_code=201,
            content={
                "vkontakte_id": vkontakte_id
            }
        )

    # ПОЛУЧЕНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    @auto_log()
    @traced_method()
    async def get_social_networks_by_organization(self, organization_id: int) -> JSONResponse:
        social_networks = await self.social_network_service.get_social_networks_by_organization(organization_id)
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
