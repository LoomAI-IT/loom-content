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

        try:
            code = query_params.get('code')
            device_id = query_params.get('device_id')
            state_token = query_params.get('state')

            if not code or not device_id or not state_token:
                return self._render_error_page("Missing required parameters: code, device_id, or state")

            if 'error' in query_params:
                error_msg = f"{query_params.get('error', 'unknown')}: {query_params.get('error_description', '')}"
                return self._render_error_page(error_msg)

            organization_id, groups = await self.social_network_service.process_vk_oauth_callback(
                code=code,
                device_id=device_id,
                state_token=state_token
            )

            # Рендерим страницу с выбором группы
            return self._render_group_selection_page(organization_id, groups)

        except ValueError as e:
            # Ошибки валидации (невалидный state, отсутствуют данные)
            self.logger.warning(f"Validation error in VK OAuth callback: {str(e)}")
            return self._render_error_page(str(e))
        except Exception as e:
            # Неожиданные ошибки
            self.logger.error(f"Error in VK OAuth callback: {str(e)}")
            return self._render_error_page(f"Error during authorization: {str(e)}")

    @auto_log()
    @traced_method()
    async def vk_select_group(self, body: VkSelectGroupBody) -> JSONResponse:
        await self.social_network_service.update_vkontakte(
            organization_id=body.organization_id,
            vk_group_id=body.group_id,
            vk_group_name=body.group_name
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Group '{body.group_name}' successfully selected",
                "group_id": body.group_id,
                "group_name": body.group_name
            }
        )

    def _render_group_selection_page(self, organization_id: int, groups: list) -> HTMLResponse:
        """Рендерит страницу выбора группы VK"""
        groups_html = ""
        for group in groups:
            group_id = group.get('id')
            group_name = group.get('name')
            group_screen_name = group.get('screen_name', '')
            group_photo = group.get('photo_100', '')

            groups_html += f'''
            <div class="group-item">
                <label class="group-label">
                    <input type="radio" name="group" value="{group_id}"
                           data-name="{group_name}" required>
                    <div class="group-info">
                        {f'<img src="{group_photo}" class="group-photo" alt="">' if group_photo else ''}
                        <div class="group-details">
                            <div class="group-name">{group_name}</div>
                            {f'<div class="group-screen-name">@{group_screen_name}</div>' if group_screen_name else ''}
                        </div>
                    </div>
                </label>
            </div>
            '''

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Выберите группу ВКонтакте</title>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    background-color: white;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                }}
                h1 {{
                    color: #333;
                    margin-top: 0;
                    margin-bottom: 10px;
                    font-size: 24px;
                }}
                .subtitle {{
                    color: #666;
                    margin-bottom: 30px;
                    font-size: 14px;
                }}
                .group-item {{
                    margin-bottom: 12px;
                }}
                .group-label {{
                    display: block;
                    padding: 16px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s;
                }}
                .group-label:hover {{
                    border-color: #667eea;
                    background-color: #f8f9ff;
                }}
                .group-label input[type="radio"] {{
                    margin-right: 12px;
                    cursor: pointer;
                }}
                .group-label input[type="radio"]:checked + .group-info {{
                    color: #667eea;
                }}
                input[type="radio"]:checked ~ .group-label {{
                    border-color: #667eea;
                    background-color: #f8f9ff;
                }}
                .group-info {{
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }}
                .group-photo {{
                    width: 48px;
                    height: 48px;
                    border-radius: 50%;
                    object-fit: cover;
                }}
                .group-details {{
                    flex: 1;
                }}
                .group-name {{
                    font-weight: 600;
                    color: #333;
                    margin-bottom: 4px;
                }}
                .group-screen-name {{
                    color: #999;
                    font-size: 13px;
                }}
                .submit-btn {{
                    width: 100%;
                    padding: 14px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    margin-top: 24px;
                    transition: transform 0.2s, box-shadow 0.2s;
                }}
                .submit-btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
                }}
                .submit-btn:active {{
                    transform: translateY(0);
                }}
                .submit-btn:disabled {{
                    opacity: 0.6;
                    cursor: not-allowed;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Выберите группу ВКонтакте</h1>
                <div class="subtitle">Выберите группу, в которую будут публиковаться посты</div>

                <div id="errorMessage" style="display: none; background-color: #fee; border: 1px solid #fcc; padding: 12px; border-radius: 8px; margin-bottom: 16px; color: #c00;"></div>
                <div id="successMessage" style="display: none; background-color: #efe; border: 1px solid #cfc; padding: 12px; border-radius: 8px; margin-bottom: 16px; color: #060;"></div>

                <form id="groupForm">
                    <input type="hidden" id="organization_id" value="{organization_id}">

                    {groups_html}

                    <button type="submit" class="submit-btn" id="submitBtn">Подтвердить выбор</button>
                </form>
            </div>

            <script>
                document.getElementById('groupForm').addEventListener('submit', async function(e) {{
                    e.preventDefault();

                    const selectedRadio = document.querySelector('input[name="group"]:checked');
                    if (!selectedRadio) {{
                        showError('Пожалуйста, выберите группу');
                        return;
                    }}

                    const submitBtn = document.getElementById('submitBtn');
                    const organizationId = parseInt(document.getElementById('organization_id').value);
                    const groupId = parseInt(selectedRadio.value);
                    const groupName = selectedRadio.getAttribute('data-name');

                    // Отключаем кнопку и показываем загрузку
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Сохранение...';

                    try {{
                        const response = await fetch('/api/content/social-network/vkontakte/select-group', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                organization_id: organizationId,
                                group_id: groupId,
                                group_name: groupName
                            }})
                        }});

                        const data = await response.json();

                        if (response.ok) {{
                            showSuccess(`Группа "${{groupName}}" успешно выбрана! Вы можете закрыть это окно.`);
                            // Опционально: можно закрыть окно автоматически через несколько секунд
                            setTimeout(() => {{
                                window.close();
                            }}, 2000);
                        }} else {{
                            showError(data.message || 'Произошла ошибка при сохранении');
                            submitBtn.disabled = false;
                            submitBtn.textContent = 'Подтвердить выбор';
                        }}
                    }} catch (error) {{
                        showError('Ошибка соединения с сервером');
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Подтвердить выбор';
                    }}
                }});

                function showError(message) {{
                    const errorDiv = document.getElementById('errorMessage');
                    const successDiv = document.getElementById('successMessage');
                    successDiv.style.display = 'none';
                    errorDiv.textContent = message;
                    errorDiv.style.display = 'block';
                }}

                function showSuccess(message) {{
                    const errorDiv = document.getElementById('errorMessage');
                    const successDiv = document.getElementById('successMessage');
                    errorDiv.style.display = 'none';
                    successDiv.textContent = message;
                    successDiv.style.display = 'block';
                }}
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)

    def _render_error_page(self, error_message: str) -> HTMLResponse:
        """Рендерит страницу ошибки"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ошибка</title>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                }}
                .container {{
                    background-color: white;
                    border-radius: 12px;
                    padding: 60px 40px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }}
                .error-icon {{
                    width: 80px;
                    height: 80px;
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 24px;
                    font-size: 48px;
                }}
                h1 {{
                    color: #333;
                    margin: 0 0 16px 0;
                    font-size: 28px;
                }}
                .message {{
                    color: #666;
                    font-size: 16px;
                    line-height: 1.6;
                }}
                .error-details {{
                    background-color: #fff5f5;
                    border-left: 4px solid #f5576c;
                    padding: 16px;
                    margin-top: 24px;
                    border-radius: 4px;
                    text-align: left;
                    color: #c53030;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">✕</div>
                <h1>Произошла ошибка</h1>
                <div class="message">
                    Не удалось завершить настройку ВКонтакте.
                </div>
                <div class="error-details">
                    {error_message}
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=400)
