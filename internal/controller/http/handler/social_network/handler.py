from opentelemetry.trace import Status, StatusCode, SpanKind

from fastapi import Request
from fastapi.responses import JSONResponse, HTMLResponse

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

    @auto_log()
    @traced_method()
    async def vk_oauth_callback(self, request: Request) -> HTMLResponse:
        query_params = dict(request.query_params)
        self.logger.info(f"VK OAuth callback received with params: {query_params}")

        # Создаем HTML для отображения параметров
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>VK OAuth Callback - Debug</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    border-bottom: 2px solid #4285f4;
                    padding-bottom: 10px;
                }
                .param {
                    margin: 15px 0;
                    padding: 10px;
                    background-color: #f8f9fa;
                    border-left: 4px solid #4285f4;
                    border-radius: 4px;
                }
                .param-name {
                    font-weight: bold;
                    color: #4285f4;
                    margin-bottom: 5px;
                }
                .param-value {
                    font-family: monospace;
                    color: #333;
                    word-break: break-all;
                }
                .empty {
                    color: #999;
                    font-style: italic;
                }
                .success {
                    color: #34a853;
                }
                .error {
                    color: #ea4335;
                    background-color: #fce8e6;
                    border-left-color: #ea4335;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>VK OAuth Callback - Полученные параметры</h1>
        """

        if not query_params:
            html_content += '<p class="empty">Параметры не получены</p>'
        else:
            # Проверяем наличие ошибки
            if 'error' in query_params:
                html_content += f'''
                <div class="param error">
                    <div class="param-name">ERROR</div>
                    <div class="param-value">{query_params.get('error', 'unknown')}</div>
                </div>
                '''
                if 'error_description' in query_params:
                    html_content += f'''
                    <div class="param error">
                        <div class="param-name">ERROR DESCRIPTION</div>
                        <div class="param-value">{query_params.get('error_description', '')}</div>
                    </div>
                    '''

            # Отображаем все параметры
            for key, value in query_params.items():
                css_class = "param"
                if key == 'code':
                    css_class += " success"

                html_content += f'''
                <div class="{css_class}">
                    <div class="param-name">{key.upper()}</div>
                    <div class="param-value">{value}</div>
                </div>
                '''

        html_content += """
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content, status_code=200)
