import asyncio
from datetime import datetime, timedelta

from internal import interface


async def Autoposting(
        tel: interface.ITelemetry,
        publication_service: interface.IPublicationService,
        telegram_client: interface.ITelegramClient,
        openai_client: interface.IOpenAIClient,
        prompt_generator: interface.IPublicationPromptGenerator,
):
    logger = tel.logger()

    logger.info("🚀 Сервис автопостинга запущен и готов к работе")

    while True:
        try:
            logger.info("🔄 Начата новая итерация автопостинга")

            # 1. Получаем все автопостинги
            logger.info("📋 Запрос всех автопостингов из базы данных...")
            all_autopostings = await publication_service.get_all_autopostings()
            logger.info(f"✅ Получено {len(all_autopostings)} автопостингов из базы данных")

            # 2. Фильтруем автопостинги по enabled и last_active
            logger.info("🔍 Фильтрация автопостингов по статусу и времени последней активности...")
            now = datetime.now()
            active_autopostings = []
            disabled_count = 0
            not_ready_count = 0

            for autoposting in all_autopostings:
                # Проверяем enabled
                if not autoposting.enabled:
                    disabled_count += 1
                    logger.debug(f"⏸️  Автопостинг {autoposting.id} (орг: {autoposting.organization_id}) отключен, пропускаем")
                    continue

                # Проверяем last_active
                if autoposting.last_active is None:
                    # Если last_active еще не установлен, добавляем
                    logger.info(f"🆕 Автопостинг {autoposting.id} (орг: {autoposting.organization_id}) - первый запуск, добавлен в очередь")
                    active_autopostings.append(autoposting)
                else:
                    # Проверяем, прошло ли достаточно времени с последней активности
                    time_since_last_active = now - autoposting.last_active
                    period = timedelta(hours=autoposting.period_in_hours)

                    if time_since_last_active >= period:
                        logger.info(f"⏰ Автопостинг {autoposting.id} (орг: {autoposting.organization_id}) - прошло {time_since_last_active}, период {period}, добавлен в очередь")
                        active_autopostings.append(autoposting)
                    else:
                        not_ready_count += 1
                        remaining_time = period - time_since_last_active
                        logger.debug(f"⏳ Автопостинг {autoposting.id} (орг: {autoposting.organization_id}) - еще не готов, осталось ждать {remaining_time}")

            logger.info(f"📊 Статистика фильтрации: всего={len(all_autopostings)}, активных={len(active_autopostings)}, отключенных={disabled_count}, не готовых={not_ready_count}")

            if len(active_autopostings) == 0:
                logger.info("💤 Нет автопостингов для обработки, переход в режим ожидания")

            # 3. Обрабатываем каждый активный автопостинг
            for autoposting in active_autopostings:
                try:
                    logger.info("─" * 60)
                    logger.info(f"🔧 Обработка автопостинга ID={autoposting.id}, организация={autoposting.organization_id}")
                    logger.info(f"📝 Каналов для мониторинга: {len(autoposting.tg_channels)}, период: {autoposting.period_in_hours} часов")

                    suitable_posts = []

                    # Обрабатываем каждый канал
                    for channel_username in autoposting.tg_channels:
                        try:
                            logger.info(f"📡 Загрузка постов из канала @{channel_username}...")

                            # 3. Получаем последние ~100 постов
                            posts = await telegram_client.get_channel_posts(
                                channel_id=channel_username,
                                limit=100
                            )

                            logger.info(f"✅ Загружено {len(posts)} постов из @{channel_username}")

                            # 4. Фильтруем посты за период автопостинга
                            period_start = now - timedelta(hours=autoposting.period_in_hours)
                            recent_posts = [
                                post for post in posts
                                if post['date'] >= period_start
                            ]

                            logger.info(f"🕒 Найдено {len(recent_posts)} постов за последние {autoposting.period_in_hours} часов в @{channel_username}")

                            # Получаем уже просмотренные посты
                            logger.info(f"🔎 Проверка просмотренных постов для @{channel_username}...")
                            viewed_posts = await publication_service.get_viewed_telegram_post(
                                autoposting_id=autoposting.id,
                                tg_channel_username=channel_username
                            )
                            viewed_post_dates = {vp.created_at for vp in viewed_posts}
                            logger.info(f"📌 Найдено {len(viewed_post_dates)} просмотренных постов для @{channel_username}")

                            # Обрабатываем каждый пост
                            empty_posts_count = 0
                            already_viewed_count = 0
                            processed_count = 0

                            for post in recent_posts:
                                try:
                                    post_text = post['text']
                                    post_date = post['date']

                                    # Пропускаем пустые посты
                                    if not post_text or not post_text.strip():
                                        empty_posts_count += 1
                                        continue

                                    # 5. Помечаем пост просмотренным
                                    await publication_service.create_viewed_telegram_post(
                                        autoposting_id=autoposting.id,
                                        tg_channel_username=channel_username
                                    )

                                    # Пропускаем уже просмотренные посты
                                    if post_date in viewed_post_dates:
                                        already_viewed_count += 1
                                        continue

                                    processed_count += 1
                                    logger.info(f"🤖 Анализ поста #{processed_count} из @{channel_username} через OpenAI...")

                                    # 6. Фильтруем через OpenAI
                                    filter_system_prompt = await prompt_generator.get_filter_post_system_prompt(
                                        filter_prompt=autoposting.filter_prompt,
                                        post_text=post_text
                                    )

                                    filter_result, _ = await openai_client.generate_json(
                                        history=[{"role": "user", "content": "Проанализируй этот пост"}],
                                        system_prompt=filter_system_prompt,
                                        temperature=0.3,
                                        llm_model="gpt-4o-mini"
                                    )

                                    # Проверяем результат фильтрации
                                    if filter_result.get("is_suitable", False):
                                        suitable_posts.append({
                                            "text": post_text,
                                            "channel": channel_username,
                                            "link": post.get("link", ""),
                                            "date": post_date
                                        })
                                        logger.info(f"✅ Пост из @{channel_username} прошел фильтр! Причина: {filter_result.get('reason', 'не указана')}")
                                    else:
                                        logger.info(f"❌ Пост из @{channel_username} не прошел фильтр. Причина: {filter_result.get('reason', 'не указана')}")

                                except Exception as post_err:
                                    logger.error(f"❗ Ошибка при обработке поста из @{channel_username}: {str(post_err)}")
                                    continue

                            logger.info(f"📈 Итоги обработки @{channel_username}: обработано={processed_count}, пустых={empty_posts_count}, уже просмотрено={already_viewed_count}")

                        except Exception as channel_err:
                            logger.error(f"❗ Ошибка при обработке канала @{channel_username}: {str(channel_err)}")
                            continue

                    logger.info(f"🎯 Итого найдено {len(suitable_posts)} подходящих постов для автопостинга {autoposting.id}")

                    # Обновляем last_active после успешной обработки всех постов
                    logger.info(f"💾 Обновление времени последней активности для автопостинга {autoposting.id}...")
                    await publication_service.update_autoposting(
                        autoposting_id=autoposting.id,
                        last_active=datetime.now()
                    )

                    logger.info(f"✅ Автопостинг {autoposting.id} успешно обработан, last_active обновлен")

                except Exception as autoposting_err:
                    logger.error(f"❗❗ Критическая ошибка при обработке автопостинга {autoposting.id}: {str(autoposting_err)}")
                    continue

            logger.info(f"✅ Итерация автопостинга завершена. Обработано {len(active_autopostings)} автопостингов")
            logger.info("😴 Переход в режим ожидания на 30 минут...")

            # Спим 30 минут
            await asyncio.sleep(30 * 60)

        except Exception as err:
            logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА в главном цикле автопостинга: {str(err)}")
            logger.error("🔄 Повторная попытка через 5 минут...")
            # В случае ошибки спим 5 минут перед повторной попыткой
            await asyncio.sleep(5 * 60)