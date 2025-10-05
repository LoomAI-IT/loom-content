import asyncio
import random
import traceback
from datetime import datetime, timedelta

from internal import interface, model


class Autoposting:
    def __init__(
        self,
        tel: interface.ITelemetry,
        publication_service: interface.IPublicationService,
        telegram_client: interface.ITelegramClient,
        openai_client: interface.IOpenAIClient,
        prompt_generator: interface.IPublicationPromptGenerator,
        loom_employee_client: interface.ILoomEmployeeClient,
    ):
        self.tel = tel
        self.logger = tel.logger()
        self.publication_service = publication_service
        self.telegram_client = telegram_client
        self.openai_client = openai_client
        self.prompt_generator = prompt_generator
        self.loom_employee_client = loom_employee_client

    async def run(self):
        self.logger.info("Сервис автопостинга запущен")

        while True:
            try:
                await self._process_iteration()
                await self._sleep_until_next_iteration()
            except Exception as err:
                await self._handle_critical_error(err)

    async def _process_iteration(self):
        self.logger.info("Начата новая итерация автопостинга")

        active_autopostings = await self._get_active_autopostings()

        if not active_autopostings:
            self.logger.info("Нет автопостингов для обработки")
            return

        for autoposting in active_autopostings:
            await self._process_autoposting(autoposting)

        self.logger.info(f"Итерация завершена, обработано автопостингов: {len(active_autopostings)}")

    async def _get_active_autopostings(self) -> list:
        all_autopostings = await self.publication_service.get_all_autopostings()

        now = datetime.now()
        active_autopostings = []

        for autoposting in all_autopostings:
            if not autoposting.enabled:
                continue

            if self._should_process_autoposting(autoposting, now):
                active_autopostings.append(autoposting)

        return active_autopostings

    def _should_process_autoposting(self, autoposting: model.Autoposting, now: datetime) -> bool:
        if autoposting.last_active is None:
            return True

        time_since_last_active = now - autoposting.last_active
        period = timedelta(hours=autoposting.period_in_hours)

        return time_since_last_active >= period

    async def _process_autoposting(self, autoposting: model.Autoposting):
        try:
            self.logger.info(f"Обработка автопостинга {autoposting.id}, организация {autoposting.organization_id}, каналов {len(autoposting.tg_channels)}")

            suitable_posts = []

            for channel_username in autoposting.tg_channels:
                channel_suitable_posts = await self._process_channel(autoposting, channel_username)
                suitable_posts.extend(channel_suitable_posts)
                if len(channel_suitable_posts) == 1:
                    break

            self.logger.info(f"Найдено подходящих постов: {len(suitable_posts)}")

            await self._process_suitable_posts(autoposting, suitable_posts)
            await self._update_last_active(autoposting.id)

        except Exception as autoposting_err:
            self.logger.error(f"Ошибка при обработке автопостинга {autoposting.id}: {autoposting_err}")

    async def _process_channel(self, autoposting: model.Autoposting, channel_username: str) -> list[dict]:
        try:
            posts = await self._fetch_channel_posts(channel_username)
            recent_posts = self._filter_posts_by_time(posts, autoposting.period_in_hours)
            self.logger.info(f"Канал {channel_username}: постов за {autoposting.period_in_hours}ч - {len(recent_posts)}")

            viewed_post_links = await self._get_viewed_post_links(autoposting.id, channel_username)
            suitable_posts = await self._process_posts(autoposting, channel_username, recent_posts, viewed_post_links)

            return suitable_posts

        except Exception as channel_err:
            self.logger.error(f"Ошибка при обработке канала {channel_username}: {channel_err}")
            return []

    async def _fetch_channel_posts(self, channel_username: str) -> list[dict]:
        posts = await self.telegram_client.get_channel_posts(channel_id=channel_username, limit=100)
        return posts

    def _filter_posts_by_time(self, posts: list[dict], period_hours: int) -> list[dict]:
        now = datetime.now()
        period_start = now - timedelta(hours=period_hours*3)
        recent_posts = []

        for post in posts:
            post_date = post['date']
            # Приводим даты к naive формату для сравнения
            if post_date.tzinfo is not None:
                post_date_naive = post_date.replace(tzinfo=None)
            else:
                post_date_naive = post_date

            if post_date_naive >= period_start:
                recent_posts.append(post)

        return recent_posts

    async def _get_viewed_post_links(self, autoposting_id: int, channel_username: str) -> list[str]:
        viewed_posts = await self.publication_service.get_viewed_telegram_post(
            autoposting_id=autoposting_id,
            tg_channel_username=channel_username
        )
        return [vp.link for vp in viewed_posts]

    async def _process_posts(
        self,
        autoposting,
        channel_username: str,
        recent_posts: list[dict],
        viewed_post_links: list[str],
    ) -> list[dict]:

        suitable_posts = []
        processed_count = 0

        for post in recent_posts:
            try:
                post_text = post['text']
                post_date = post['date']
                post_link = post['link']

                if not post_text or not post_text.strip():
                    continue

                if post_link in viewed_post_links:
                    continue

                processed_count += 1
                is_suitable, reason = await self._filter_post_with_ai(autoposting.filter_prompt, post_text)

                if is_suitable:
                    self.logger.info(f"Пост подходит: {reason}")
                    suitable_posts.append({
                        "text": post_text,
                        "channel_username": channel_username,
                        "link": post.get("link", ""),
                        "date": post_date,
                    })
                    if len(suitable_posts) == 1:
                        break
                else:
                    await self._mark_post_as_viewed(autoposting.id, channel_username, post_link)

            except Exception as post_err:
                self.logger.error(f"Ошибка при обработке поста: {post_err}")
                continue

        self.logger.info(f"Обработано постов: {processed_count}, отобрано: {len(suitable_posts)}")

        return suitable_posts

    async def _mark_post_as_viewed(self, autoposting_id: int, channel_username: str, link: str):
        await self.publication_service.create_viewed_telegram_post(
            autoposting_id=autoposting_id,
            tg_channel_username=channel_username,
            link=link
        )

    async def _filter_post_with_ai(self, filter_prompt: str, post_text: str) -> tuple[bool, str]:
        filter_system_prompt = await self.prompt_generator.get_filter_post_system_prompt(
            filter_prompt=filter_prompt,
            post_text=post_text
        )

        filter_result, _ = await self.openai_client.generate_json(
            history=[{"role": "user", "content": "Проанализируй этот пост"}],
            system_prompt=filter_system_prompt,
            temperature=1,
            llm_model="gpt-5",
        )

        is_suitable = filter_result.get("is_suitable", False)
        reason = filter_result.get("reason", "не указана")

        return is_suitable, reason

    async def _process_suitable_posts(self, autoposting: model.Autoposting, suitable_posts: list[dict]):
        if not suitable_posts:
            return

        selected_post = random.choice(suitable_posts)
        self.logger.info(f"Выбран пост для публикации: {selected_post['link']}")
        await self._mark_post_as_viewed(autoposting.id, selected_post['channel_username'], selected_post['link'])

        try:
            publication_data = await self.publication_service.generate_autoposting_publication_text(
                autoposting_category_id=autoposting.autoposting_category_id,
                source_post_text=selected_post['text']
            )

            image_url = None
            if autoposting.need_image:
                images_url = await self.publication_service.generate_autoposting_publication_image(
                    autoposting_category_id=autoposting.autoposting_category_id,
                    publication_text=publication_data['text']
                )
                image_url = images_url[0]

            employees = await self.loom_employee_client.get_employees_by_organization(autoposting.organization_id)
            moderators = [employee for employee in employees if employee.role == "moderator"]

            publication_id = await self.publication_service.create_publication(
                organization_id=autoposting.organization_id,
                category_id=autoposting.autoposting_category_id,
                creator_id=0,
                text_reference=selected_post['text'],
                text=publication_data['text'],
                moderation_status="moderation",
                image_url=image_url
            )

            await self.publication_service.change_publication(
                publication_id=publication_id,
                tg_source=True
            )

            if not moderators:
                await self.publication_service.moderate_publication(
                    publication_id=publication_id,
                    moderator_id=0,
                    moderation_status="approved",
                    moderation_comment=""
                )

            self.logger.info(f"Публикация создана: {publication_id}")

        except Exception as gen_err:
            self.logger.error(f"Ошибка при генерации публикации: {gen_err}")
            self.logger.error(traceback.format_exc())

    async def _update_last_active(self, autoposting_id: int):
        await self.publication_service.update_autoposting(
            autoposting_id=autoposting_id,
            last_active=datetime.now()
        )

    async def _sleep_until_next_iteration(self):
        await asyncio.sleep(1 * 60)

    async def _handle_critical_error(self, err: Exception):
        self.logger.error(f"Критическая ошибка в главном цикле: {err}")
        self.logger.error(traceback.format_exc())
        await asyncio.sleep(1 * 60)
