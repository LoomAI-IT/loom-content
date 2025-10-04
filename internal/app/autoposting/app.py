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

    logger.info("Autoposting service started")

    while True:
        try:
            logger.info("Starting autoposting iteration")

            # 1. Получаем все автопостинги
            all_autopostings = await publication_service.get_all_autopostings()
            logger.info(f"Found {len(all_autopostings)} total autopostings")

            # 2. Фильтруем автопостинги по enabled и last_active
            now = datetime.now()
            active_autopostings = []

            for autoposting in all_autopostings:
                # Проверяем enabled
                if not autoposting.enabled:
                    continue

                # Проверяем last_active
                if autoposting.last_active is None:
                    # Если last_active еще не установлен, добавляем
                    active_autopostings.append(autoposting)
                else:
                    # Проверяем, прошло ли достаточно времени с последней активности
                    time_since_last_active = now - autoposting.last_active
                    period = timedelta(hours=autoposting.period_in_hours)

                    if time_since_last_active >= period:
                        active_autopostings.append(autoposting)

            logger.info(f"Found {len(active_autopostings)} active autopostings to process")

            # 3. Обрабатываем каждый активный автопостинг
            for autoposting in active_autopostings:
                try:
                    logger.info(f"Processing autoposting {autoposting.id} for organization {autoposting.organization_id}")

                    suitable_posts = []

                    # Обрабатываем каждый канал
                    for channel_username in autoposting.tg_channels:
                        try:
                            logger.info(f"Fetching posts from channel {channel_username}")

                            # 3. Получаем последние ~100 постов
                            posts = await telegram_client.get_channel_posts(
                                channel_id=channel_username,
                                limit=100
                            )

                            logger.info(f"Fetched {len(posts)} posts from {channel_username}")

                            # 4. Фильтруем посты за период автопостинга
                            period_start = now - timedelta(hours=autoposting.period_in_hours)
                            recent_posts = [
                                post for post in posts
                                if post['date'] >= period_start
                            ]

                            logger.info(f"Found {len(recent_posts)} posts from last {autoposting.period_in_hours} hours in {channel_username}")

                            # Получаем уже просмотренные посты
                            viewed_posts = await publication_service.get_viewed_telegram_post(
                                autoposting_id=autoposting.id,
                                tg_channel_username=channel_username
                            )
                            viewed_post_dates = {vp.created_at for vp in viewed_posts}

                            # Обрабатываем каждый пост
                            for post in recent_posts:
                                try:
                                    post_text = post['text']
                                    post_date = post['date']

                                    # Пропускаем пустые посты
                                    if not post_text or not post_text.strip():
                                        continue

                                    # 5. Помечаем пост просмотренным
                                    await publication_service.create_viewed_telegram_post(
                                        autoposting_id=autoposting.id,
                                        tg_channel_username=channel_username
                                    )

                                    # Пропускаем уже просмотренные посты
                                    if post_date in viewed_post_dates:
                                        continue

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
                                        logger.info(f"Post from {channel_username} passed filter")

                                except Exception as post_err:
                                    logger.error(f"Error processing post from {channel_username}: {str(post_err)}")
                                    continue

                        except Exception as channel_err:
                            logger.error(f"Error processing channel {channel_username}: {str(channel_err)}")
                            continue

                    logger.info(f"Found {len(suitable_posts)} suitable posts for autoposting {autoposting.id}")

                    # Обновляем last_active после успешной обработки всех постов
                    await publication_service.update_autoposting(
                        autoposting_id=autoposting.id,
                        last_active=datetime.now()
                    )

                    logger.info(f"Successfully processed autoposting {autoposting.id}, updated last_active")

                except Exception as autoposting_err:
                    logger.error(f"Error processing autoposting {autoposting.id}: {str(autoposting_err)}")
                    continue

            logger.info("Autoposting iteration completed, sleeping for 30 minutes")

            # Спим 30 минут
            await asyncio.sleep(30 * 60)

        except Exception as err:
            logger.error(f"Error in autoposting main loop: {str(err)}")
            # В случае ошибки спим 5 минут перед повторной попыткой
            await asyncio.sleep(5 * 60)