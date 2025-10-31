def get_login_vk_html(oauth_url: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход через VK</title>
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

        .vk-button {{
            display: inline-block;
            margin-top: 40px;
            padding: 16px 40px;
            background: #0077FF;
            color: white;
            text-decoration: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            transition: background 0.3s;
        }}

        .vk-button:hover {{
            background: #0066DD;
        }}

        .info {{
            margin-top: 30px;
            font-size: 14px;
            color: #999;
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
            <p>Подключите VK для публикации постов</p>
        </div>

        <a href="{oauth_url}" class="vk-button">
            Войти через VK
        </a>

        <div class="info">
            Вы будете перенаправлены на страницу авторизации VK
        </div>
    </div>
</body>
</html>
"""