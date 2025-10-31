def get_login_vk_html(organization_id: int, domain: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход через VK ID</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}

        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 60px 40px;
            max-width: 450px;
            width: 100%;
            text-align: center;
        }}

        .logo {{
            margin-bottom: 30px;
        }}

        .logo h1 {{
            font-size: 32px;
            color: #333;
            margin-bottom: 10px;
        }}

        .logo p {{
            color: #666;
            font-size: 16px;
        }}

        .login-section {{
            margin-top: 40px;
        }}

        .divider {{
            margin: 30px 0;
            text-align: center;
            position: relative;
        }}

        .divider::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: #e0e0e0;
        }}

        .divider span {{
            background: white;
            padding: 0 15px;
            color: #999;
            font-size: 14px;
            position: relative;
            z-index: 1;
        }}

        .info {{
            margin-top: 30px;
            font-size: 14px;
            color: #999;
        }}

        .info a {{
            color: #667eea;
            text-decoration: none;
        }}

        .info a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 480px) {{
            .container {{
                padding: 40px 30px;
            }}

            .logo h1 {{
                font-size: 28px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>Loom AI</h1>
            <p>Войдите, чтобы продолжить</p>
        </div>

        <div class="login-section">
            <div id="vk-button">
                <script src="https://unpkg.com/@vkid/sdk@<3.0.0/dist-sdk/umd/index.js"></script>
                <script type="text/javascript">
                    if ('VKIDSDK' in window) {{
                        const VKID = window.VKIDSDK;
                        VKID.Config.init({{
                            app: 54287509,
                            redirectUrl: 'https://{domain}/api/content/vk/select-group-page',
                            responseMode: VKID.ConfigResponseMode.Callback,
                            source: VKID.ConfigSource.LOWCODE,
                            scope: 'wall,groups,offline', // wall - публикация постов, groups - доступ к группам, offline - постоянный токен
                        }});
                        const oneTap = new VKID.OneTap();
                        oneTap.render({{
                            container: document.currentScript.parentElement,
                            showAlternativeLogin: true
                        }})
                        .on(VKID.WidgetEvents.ERROR, vkidOnError)
                        .on(VKID.OneTapInternalEvents.LOGIN_SUCCESS, function (payload) {{
                            const code = payload.code;
                            const deviceId = payload.device_id;
                            VKID.Auth.exchangeCode(code, deviceId)
                                .then(vkidOnSuccess)
                                .catch(vkidOnError);
                        }});

                        function vkidOnSuccess(data) {{
                            // Обработка полученного результата
                            console.log('Успешная авторизация:', data);

                            // Отправляем access_token на ваш сервер
                            fetch('https://{domain}/api/content/social-network/vkontakte', {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/json',
                                }},
                                body: JSON.stringify({{
                                    access_token: data.access_token,
                                    organization_id: {organization_id},
                                }})
                            }})
                            .then(response => response.json())
                            .catch(error => {{
                                console.error('Ошибка сохранения токена:', error);
                                alert('Ошибка при сохранении данных. Попробуйте еще раз.');
                            }});
                        }}

                        function vkidOnError(error) {{
                            // Обработка ошибки
                            console.error('Ошибка авторизации:', error);
                            alert('Произошла ошибка при авторизации. Попробуйте еще раз.');
                        }}
                    }}
                </script>
            </div>
        </div>

        <div class="info">
            Нажимая "Войти", вы соглашаетесь с <a href="#">условиями использования</a> и <a href="#">политикой конфиденциальности</a>
        </div>
    </div>
</body>
</html>
"""