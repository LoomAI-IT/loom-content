def get_select_vk_group_html(organization_id: int, domain: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Выбор группы - Loom AI</title>
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
            padding: 20px;
        }}

        .container {{
            max-width: 800px;
            margin: 40px auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
        }}

        h1 {{
            font-size: 28px;
            color: #333;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #666;
            margin-bottom: 30px;
        }}

        .loading {{
            text-align: center;
            padding: 40px;
            color: #666;
        }}

        .groups-list {{
            display: none;
        }}

        .groups-list.active {{
            display: block;
        }}

        .group-item {{
            display: flex;
            align-items: center;
            padding: 20px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .group-item:hover {{
            border-color: #667eea;
            background: #f8f9ff;
        }}

        .group-item.selected {{
            border-color: #667eea;
            background: #f0f3ff;
        }}

        .group-avatar {{
            width: 60px;
            height: 60px;
            border-radius: 12px;
            margin-right: 20px;
            object-fit: cover;
        }}

        .group-info {{
            flex: 1;
        }}

        .group-name {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }}

        .group-members {{
            color: #999;
            font-size: 14px;
        }}

        .group-check {{
            width: 24px;
            height: 24px;
            border: 2px solid #ddd;
            border-radius: 50%;
            position: relative;
        }}

        .group-item.selected .group-check {{
            background: #667eea;
            border-color: #667eea;
        }}

        .group-item.selected .group-check::after {{
            content: '✓';
            color: white;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 14px;
        }}

        .submit-btn {{
            width: 100%;
            padding: 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
            transition: background 0.3s;
        }}

        .submit-btn:hover {{
            background: #5568d3;
        }}

        .submit-btn:disabled {{
            background: #ccc;
            cursor: not-allowed;
        }}

        .error {{
            color: #e74c3c;
            padding: 20px;
            text-align: center;
            background: #fee;
            border-radius: 12px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Выберите группу для публикации</h1>
        <p class="subtitle">Выберите группу, в которую Loom AI сможет публиковать посты</p>

        <div id="error" class="error" style="display: none;"></div>

        <div id="loading" class="loading">
            <p>⏳ Загружаем ваши группы...</p>
        </div>

        <div id="groups-list" class="groups-list">
            <!-- Группы будут загружены сюда -->
        </div>

        <button id="submit-btn" class="submit-btn" disabled>
            Подтвердить выбор
        </button>
    </div>

    <script>
        let selectedGroupId = null;
        const submitBtn = document.getElementById('submit-btn');
        const groupsList = document.getElementById('groups-list');
        const loading = document.getElementById('loading');
        const errorDiv = document.getElementById('error');

        // Загружаем группы пользователя через сервер (токен на сервере, запрос с IP сервера)
        async function loadGroups() {{
            try {{
                const response = await fetch('https://{domain}/api/content/social-network/vkontakte/get-groups/{organization_id}');
                const data = await response.json();

                if (data.error) {{
                    showError(data.error);
                    return;
                }}

                loading.style.display = 'none';
                groupsList.classList.add('active');

                if (data.groups.length === 0) {{
                    groupsList.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">У вас нет групп, где вы являетесь администратором</p>';
                    return;
                }}

                // Отображаем группы
                data.groups.forEach(group => {{
                    const groupItem = document.createElement('div');
                    groupItem.className = 'group-item';
                    groupItem.dataset.groupId = group.id;

                    groupItem.innerHTML = `
                        <img src="${{group.photo_100}}" alt="${{group.name}}" class="group-avatar">
                        <div class="group-info">
                            <div class="group-name">${{group.name}}</div>
                            <div class="group-members">${{group.members_count.toLocaleString('ru-RU')}} подписчиков</div>
                        </div>
                        <div class="group-check"></div>
                    `;

                    groupItem.addEventListener('click', () => selectGroup(groupItem, group.id, group.name));
                    groupsList.appendChild(groupItem);
                }});

            }} catch (error) {{
                showError('Ошибка загрузки групп: ' + error.message);
            }}
        }}

        let selectedGroupName = null;

        function selectGroup(element, groupId, groupName) {{
            // Убираем выделение с других групп
            document.querySelectorAll('.group-item').forEach(item => {{
                item.classList.remove('selected');
            }});

            // Выделяем выбранную группу
            element.classList.add('selected');
            selectedGroupId = groupId;
            selectedGroupName = groupName;
            submitBtn.disabled = false;
        }}

        function showError(message) {{
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            loading.style.display = 'none';
        }}

        // Отправка выбранной группы
        submitBtn.addEventListener('click', async () => {{
            if (!selectedGroupId) return;

            submitBtn.disabled = true;
            submitBtn.textContent = 'Сохранение...';

            try {{
                const response = await fetch('https://{domain}/api/content/social-network/vkontakte/select-group', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        organization_id: {organization_id},
                        vk_group_id: selectedGroupId,
                        vk_group_name: selectedGroupName
                    }})
                }});

                const data = await response.json();

                if (data.success) {{
                    window.location.href = '/dashboard';
                }} else {{
                    showError(data.error || 'Ошибка при сохранении группы');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Подтвердить выбор';
                }}
            }} catch (error) {{
                showError('Ошибка: ' + error.message);
                submitBtn.disabled = false;
                submitBtn.textContent = 'Подтвердить выбор';
            }}
        }});

        // Загружаем группы при загрузке страницы
        loadGroups();
    </script>
</body>
</html>
"""