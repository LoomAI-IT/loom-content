import base64
import io
import random
import traceback
from datetime import datetime, timedelta
from decimal import Decimal

from internal import interface, model, common

from pkg.trace_wrapper import traced_method


class AutopostingService(interface.IAutopostingService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            autoposting_repo: interface.IAutopostingRepo,
            prompt_generator: interface.IAutopostingPromptGenerator,
            publication_service: interface.IPublicationService,

            anthropic_client: interface.IAnthropicClient,
            googleai_client: interface.GoogleAIClient,

            telegram_client: interface.ITelegramClient,

            storage: interface.IStorage,
            organization_client: interface.ILoomOrganizationClient,

            loom_domain: str,
            avg_generate_text_rub_cost: int,
            avg_generate_image_rub_cost: int,
            avg_edit_image_rub_cost: int,
            avg_transcribe_audio_rub_cost: int,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.autoposting_repo = autoposting_repo
        self.prompt_generator = prompt_generator
        self.publication_service = publication_service

        self.anthropic_client = anthropic_client
        self.googleai_client = googleai_client

        self.telegram_client = telegram_client

        self.storage = storage
        self.organization_client = organization_client

        self.loom_domain = loom_domain
        self.avg_generate_text_rub_cost = avg_generate_text_rub_cost
        self.avg_generate_image_rub_cost = avg_generate_image_rub_cost
        self.avg_edit_image_rub_cost = avg_edit_image_rub_cost
        self.avg_transcribe_audio_rub_cost = avg_transcribe_audio_rub_cost

    @traced_method()
    async def create_autoposting(
            self,
            organization_id: int,
            autoposting_category_id: int,
            period_in_hours: int,
            filter_prompt: str,
            tg_channels: list[str],
            required_moderation: bool,
            need_image: bool
    ) -> int:
        autoposting_id = await self.autoposting_repo.create_autoposting(
            organization_id=organization_id,
            autoposting_category_id=autoposting_category_id,
            period_in_hours=period_in_hours,
            filter_prompt=filter_prompt,
            tg_channels=tg_channels,
            required_moderation=required_moderation,
            need_image=need_image
        )
        return autoposting_id

    @traced_method()
    async def create_autoposting_category(
            self,
            organization_id: int,
            name: str,
            prompt_for_image_style: str,
            goal: str,
            structure_skeleton: list[str],
            structure_flex_level_min: int,
            structure_flex_level_max: int,
            structure_flex_level_comment: str,
            must_have: list[str],
            must_avoid: list[str],
            social_networks_rules: str,
            len_min: int,
            len_max: int,
            n_hashtags_min: int,
            n_hashtags_max: int,
            cta_type: str,
            tone_of_voice: list[str],
            brand_rules: list[str],
            good_samples: list[dict],
            additional_info: list[str]
    ) -> int:
        autoposting_category_id = await self.autoposting_repo.create_autoposting_category(
            organization_id=organization_id,
            name=name,
            prompt_for_image_style=prompt_for_image_style,
            goal=goal,
            structure_skeleton=structure_skeleton,
            structure_flex_level_min=structure_flex_level_min,
            structure_flex_level_max=structure_flex_level_max,
            structure_flex_level_comment=structure_flex_level_comment,
            must_have=must_have,
            must_avoid=must_avoid,
            social_networks_rules=social_networks_rules,
            len_min=len_min,
            len_max=len_max,
            n_hashtags_min=n_hashtags_min,
            n_hashtags_max=n_hashtags_max,
            cta_type=cta_type,
            tone_of_voice=tone_of_voice,
            brand_rules=brand_rules,
            good_samples=good_samples,
            additional_info=additional_info
        )

        return autoposting_category_id

    @traced_method()
    async def update_autoposting(
            self,
            autoposting_id: int,
            autoposting_category_id: int = None,
            period_in_hours: int = None,
            filter_prompt: str = None,
            enabled: bool = None,
            tg_channels: list[str] = None,
            required_moderation: bool = None,
            need_image: bool = None,
            last_active: datetime = None
    ) -> None:
        await self.autoposting_repo.update_autoposting(
            autoposting_id=autoposting_id,
            autoposting_category_id=autoposting_category_id,
            period_in_hours=period_in_hours,
            filter_prompt=filter_prompt,
            enabled=enabled,
            tg_channels=tg_channels,
            required_moderation=required_moderation,
            need_image=need_image,
            last_active=last_active
        )

    @traced_method()
    async def update_autoposting_category(
            self,
            autoposting_category_id: int,
            name: str = None,
            prompt_for_image_style: str = None,
            goal: str = None,
            structure_skeleton: list[str] = None,
            structure_flex_level_min: int = None,
            structure_flex_level_max: int = None,
            structure_flex_level_comment: str = None,
            must_have: list[str] = None,
            must_avoid: list[str] = None,
            social_networks_rules: str = None,
            len_min: int = None,
            len_max: int = None,
            n_hashtags_min: int = None,
            n_hashtags_max: int = None,
            cta_type: str = None,
            tone_of_voice: list[str] = None,
            brand_rules: list[str] = None,
            good_samples: list[dict] = None,
            additional_info: list[str] = None
    ) -> None:
        await self.autoposting_repo.update_autoposting_category(
            autoposting_category_id=autoposting_category_id,
            name=name,
            prompt_for_image_style=prompt_for_image_style,
            goal=goal,
            structure_skeleton=structure_skeleton,
            structure_flex_level_min=structure_flex_level_min,
            structure_flex_level_max=structure_flex_level_max,
            structure_flex_level_comment=structure_flex_level_comment,
            must_have=must_have,
            must_avoid=must_avoid,
            social_networks_rules=social_networks_rules,
            len_min=len_min,
            len_max=len_max,
            n_hashtags_min=n_hashtags_min,
            n_hashtags_max=n_hashtags_max,
            cta_type=cta_type,
            tone_of_voice=tone_of_voice,
            brand_rules=brand_rules,
            good_samples=good_samples,
            additional_info=additional_info
        )

    async def create_publication_from_random_suitable_post(self, autoposting: model.Autoposting, suitable_posts: list[dict]):
        if not suitable_posts:
            return

        selected_post = random.choice(suitable_posts)
        await self.autoposting_repo.create_viewed_telegram_post(
            autoposting_id=autoposting.id,
            tg_channel_username=selected_post['channel_username'],
            link=selected_post['link']
        )

        try:
            publication_data = await self._generate_autoposting_publication_text(
                autoposting_category_id=autoposting.autoposting_category_id,
                source_post_text=selected_post['text']
            )

            image_url = None
            if autoposting.need_image:
                images_url = await self._generate_autoposting_publication_image(
                    autoposting_category_id=autoposting.autoposting_category_id,
                    publication_text=publication_data['text']
                )
                image_url = images_url[0]


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

            if not autoposting.required_moderation:
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

    @traced_method()
    async def get_autoposting_category_by_id(self, autoposting_category_id: int) -> model.AutopostingCategory:
        category = (await self.autoposting_repo.get_autoposting_category_by_id(autoposting_category_id))[0]
        return category

    @traced_method()
    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        autopostings = await self.autoposting_repo.get_autoposting_by_organization(organization_id)
        return autopostings

    async def get_active_autopostings(self) -> list[model.Autoposting]:
        all_autopostings = await self.autoposting_repo.get_all_autopostings()
        now = datetime.now()
        active_autopostings = []

        for autoposting in all_autopostings:
            if not autoposting.enabled:
                continue

            if autoposting.last_active is None:
                active_autopostings.append(autoposting)
                continue

            time_since_last_active = now - autoposting.last_active
            period = timedelta(hours=autoposting.period_in_hours)

            if time_since_last_active >= period:
                active_autopostings.append(autoposting)

        return active_autopostings

    @traced_method()
    async def delete_autoposting(self, autoposting_id: int) -> None:
        autoposting = (await self.autoposting_repo.get_autoposting_by_id(autoposting_id))[0]
        await self.autoposting_repo.delete_autoposting_category(autoposting.autoposting_category_id)
        await self.autoposting_repo.delete_autoposting(autoposting_id)
        # TODO нормально удалять публикации

    async def get_suitable_posts(self, autoposting: model.Autoposting, channel_username: str) -> list[dict]:
        try:
            posts = await self._get_recent_telegram_posts(channel_username, autoposting.period_in_hours)
            viewed_post_links = await self._get_viewed_telegram_post_links(autoposting.id, channel_username)
            suitable_posts = await self._process_posts(autoposting, channel_username, posts, viewed_post_links)

            return suitable_posts

        except Exception as channel_err:
            self.logger.error(f"Ошибка при обработке канала {channel_username}: {channel_err}")
            return []

    async def _generate_autoposting_publication_text(
            self,
            autoposting_category_id: int,
            source_post_text: str
    ) -> dict:
        autoposting_category = (await self.autoposting_repo.get_autoposting_category_by_id(autoposting_category_id))[0]
        organization = await self.organization_client.get_organization_by_id(
            autoposting_category.organization_id
        )
        organization_cost_multiplier = await self.organization_client.get_cost_multiplier(organization.id)

        if self._check_balance(organization, organization_cost_multiplier, "generate_text"):
            self.logger.info("Недостаточно средств на балансе")
            raise common.ErrInsufficientBalance()

        web_search_result = ""
        text_system_prompt = await self.prompt_generator.get_generate_autoposting_text_system_prompt(
            autoposting_category,
            organization,
            source_post_text,
            web_search_result
        )

        publication_data, generate_cost = await self.anthropic_client.generate_json(
            history=[
                {
                    "role": "user",
                    "content": "Создай пост для социальной сети на основе исходного поста"
                }
            ],
            system_prompt=text_system_prompt,
            llm_model="claude-sonnet-4-5",
            max_tokens=15000,
            thinking_tokens=10000,
        )
        await self._debit_organization_balance(
            autoposting_category.organization_id,
            generate_cost["total_cost"] * organization_cost_multiplier.generate_text_cost_multiplier
        )

        return publication_data

    async def _generate_autoposting_publication_image(
            self,
            autoposting_category_id: int,
            publication_text: str
    ) -> list[str]:
        autoposting_category = (await self.autoposting_repo.get_autoposting_category_by_id(autoposting_category_id))[0]
        organization = await self.organization_client.get_organization_by_id(
            autoposting_category.organization_id
        )
        organization_cost_multiplier = await self.organization_client.get_cost_multiplier(organization.id)

        if self._check_balance(organization, organization_cost_multiplier, "generate_image"):
            self.logger.info("Недостаточно средств на балансе")
            raise common.ErrInsufficientBalance()

        image_system_prompt = await self.prompt_generator.get_generate_autoposting_image_system_prompt(
            autoposting_category.prompt_for_image_style,
            publication_text
        )

        images, generate_cost = await self.googleai_client.generate_image(
            prompt=str(image_system_prompt),
            aspect_ratio="16:9",
            model_name="gemini-3-pro-image-preview",
        )
        images = [images]

        images_url = await self._upload_images(images)

        await self._debit_organization_balance(
            autoposting_category.organization_id,
            generate_cost["total_cost"] * organization_cost_multiplier.generate_image_cost_multiplier
        )
        return images_url


    async def _get_viewed_telegram_post_links(
            self,
            autoposting_id: int,
            tg_channel_username: str
    ) -> list[str]:
        viewed_posts = await self.autoposting_repo.get_viewed_telegram_post(
            autoposting_id=autoposting_id,
            tg_channel_username=tg_channel_username
        )
        return [vp.link for vp in viewed_posts]

    async def _get_recent_telegram_posts(self, channel_username: str, period_hours: int):
        posts = await self.telegram_client.get_channel_posts(channel_id=channel_username, limit=100)

        now = datetime.now()
        period_start = now - timedelta(hours=period_hours * 3)
        recent_posts = []

        for post in posts:
            post_date = post['date']

            if post_date.tzinfo is not None:
                post_date_naive = post_date.replace(tzinfo=None)
            else:
                post_date_naive = post_date

            if post_date_naive >= period_start:
                recent_posts.append(post)

        return recent_posts

    async def _process_posts(
        self,
        autoposting: model.Autoposting,
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
                is_suitable, reason = await self._filter_post_text_with_ai(autoposting.filter_prompt, post_text)

                if is_suitable:
                    self.logger.info(f"Пост подходит: {reason}")
                    suitable_posts.append({
                        "text": post_text,
                        "channel_username": channel_username,
                        "link": post_link,
                        "date": post_date,
                    })
                    if len(suitable_posts) == 1:
                        break
                else:
                    await self.autoposting_repo.create_viewed_telegram_post(
                        autoposting_id=autoposting.id,
                        tg_channel_username=channel_username,
                        link=post_link
                    )

            except Exception as post_err:
                self.logger.error(f"Ошибка при обработке поста: {post_err}")
                continue

        self.logger.info(f"Обработано постов: {processed_count}, отобрано: {len(suitable_posts)}")

        return suitable_posts

    async def _filter_post_text_with_ai(self, filter_prompt: str, post_text: str) -> tuple[bool, str]:
        filter_system_prompt = await self.prompt_generator.get_filter_post_system_prompt(
            filter_prompt=filter_prompt,
            post_text=post_text
        )

        filter_result, _ = await self.anthropic_client.generate_json(
            history=[{"role": "user", "content": "Проанализируй этот пост"}],
            system_prompt=filter_system_prompt,
            max_tokens=20000,
            thinking_tokens=15000,
            llm_model="claude-sonnet-4-5",
        )

        is_suitable = filter_result.get("is_suitable", False)
        reason = filter_result.get("reason", "не указана")

        return is_suitable, reason

    async def _upload_images(self, images: list[str | bytes]) -> list[str]:
        images_url = []
        for image in images:
            if isinstance(image, str):
                image_bytes = base64.b64decode(image)
            else:
                image_bytes = image
            image_name = "autoposting_image.png"

            upload_response = await self.storage.upload(io.BytesIO(image_bytes), image_name)

            image_url = f"https://{self.loom_domain}/api/content/image/{upload_response.fid}/{image_name}"
            images_url.append(image_url)
        return images_url

    def _check_balance(
            self,
            organization: model.Organization,
            organization_cost_multiplier: model.CostMultiplier,
            operation: str
    ) -> bool:
        if operation == "generate_text":
            return float(
                organization.rub_balance) < organization_cost_multiplier.generate_text_cost_multiplier * self.avg_generate_text_rub_cost
        elif operation == "generate_image":
            return float(
                organization.rub_balance) < organization_cost_multiplier.generate_image_cost_multiplier * self.avg_generate_image_rub_cost
        elif operation == "edit_image":
            return float(
                organization.rub_balance) < organization_cost_multiplier.generate_image_cost_multiplier * self.avg_edit_image_rub_cost
        elif operation == "transcribe_audio":
            return float(
                organization.rub_balance) < organization_cost_multiplier.transcribe_audio_cost_multiplier * self.avg_transcribe_audio_rub_cost
        return True

    async def _debit_organization_balance(self, organization_id: int, usd_cost: float):
        usd_cost = Decimal(str(usd_cost))
        usd_to_rub_rate = Decimal("90.00")
        rub_amount_str = str((usd_cost * usd_to_rub_rate).quantize(Decimal("0.01")))
        await self.organization_client.debit_balance(organization_id, rub_amount_str)
