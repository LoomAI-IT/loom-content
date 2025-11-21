import base64
import io
import uuid
from datetime import datetime
from decimal import Decimal

from fastapi import UploadFile

from internal import interface, model, common

from pkg.trace_wrapper import traced_method


class PublicationService(interface.IPublicationService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            repo: interface.IPublicationRepo,
            social_network_repo: interface.ISocialNetworkRepo,
            openai_client: interface.IOpenAIClient,
            anthropic_client: interface.IAnthropicClient,
            googleai_client: interface.GoogleAIClient,
            storage: interface.IStorage,
            prompt_generator: interface.IPublicationPromptGenerator,
            organization_client: interface.ILoomOrganizationClient,
            vizard_client: interface.IVizardClient,
            telegram_client: interface.ITelegramClient,
            loom_tg_bot_client: interface.ILoomTgBotClient,
            loom_domain: str,
            environment: str,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.repo = repo
        self.social_network_repo = social_network_repo
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
        self.googleai_client = googleai_client
        self.storage = storage
        self.prompt_generator = prompt_generator
        self.organization_client = organization_client
        self.vizard_client = vizard_client
        self.telegram_client = telegram_client
        self.loom_tg_bot_client = loom_tg_bot_client
        self.loom_domain = loom_domain
        self.environment = environment
        self.avg_generate_text_rub_cost = 3
        self.avg_generate_image_rub_cost = 25
        self.avg_edit_image_rub_cost = 5
        self.avg_transcribe_audio_rub_cost = 1

    # ПУБЛИКАЦИИ

    @traced_method()
    async def generate_publication_text(
            self,
            category_id: int,
            text_reference: str
    ) -> dict:
        category = (await self.repo.get_category_by_id(category_id))[0]
        organization = await self.organization_client.get_organization_by_id(category.organization_id)
        organization_cost_multiplier = await self.organization_client.get_cost_multiplier(organization.id)

        if self._check_balance(organization, organization_cost_multiplier, "generate_text"):
            self.logger.info("Недостаточно средств на балансе")
            raise common.ErrInsufficientBalance()

        text_system_prompt = await self.prompt_generator.get_generate_publication_text_system_prompt(
            text_reference,
            category,
            organization
        )

        publication_data, generate_cost = await self.anthropic_client.generate_json(
            history=[
                {
                    "role": "user",
                    "content": """
<system>
Очень хорошо подумай, чтобы соответсовать всему что промпте, ты должен учесть все что относится к рубрике и организации
Обрати внимание на каждый XML тег и проанализуй данные в нем
Большое внимание на <good_samples> и <bad_samples>

ultrathink
<system/>

<user>
Создай текст для поста
</user>
                        """
                }
            ],
            system_prompt=text_system_prompt,
            max_tokens=20000,
            thinking_tokens=15000,
            llm_model="claude-sonnet-4-5",
        )
        publication_data["text"] = publication_data["text"].replace("\n", "<br>")

        await self._debit_organization_balance(
            category.organization_id,
            generate_cost["total_cost"] * organization_cost_multiplier.generate_text_cost_multiplier
        )

        return publication_data

    @traced_method()
    async def test_generate_publication_text(
            self,
            text_reference: str,
            organization_id: int,
            name: str,
            hint: str,
            goal: str,
            tone_of_voice: list[str],
            brand_rules: list[str],
            creativity_level: int,
            audience_segment: str,
            len_min: int,
            len_max: int,
            n_hashtags_min: int,
            n_hashtags_max: int,
            cta_type: str,
            cta_strategy: dict,
            good_samples: list[dict],
            bad_samples: list[dict],
            additional_info: list[dict],
            prompt_for_image_style: str
    ) -> dict:
        category = model.Category(
            id=-1,
            organization_id=organization_id,
            name=name,
            hint=hint,
            goal=goal,
            tone_of_voice=tone_of_voice,
            brand_rules=brand_rules,
            creativity_level=creativity_level,
            audience_segment=audience_segment,
            len_min=len_min,
            len_max=len_max,
            n_hashtags_min=n_hashtags_min,
            n_hashtags_max=n_hashtags_max,
            cta_type=cta_type,
            cta_strategy=cta_strategy,
            good_samples=good_samples,
            bad_samples=bad_samples,
            additional_info=additional_info,
            prompt_for_image_style=prompt_for_image_style,
            created_at=datetime.now()
        )

        organization = await self.organization_client.get_organization_by_id(category.organization_id)

        text_system_prompt = await self.prompt_generator.get_generate_publication_text_system_prompt(
            text_reference,
            category,
            organization
        )

        publication_data, generate_cost = await self.anthropic_client.generate_json(
            history=[
                {
                    "role": "user",
                    "content": """
<system>
Очень хорошо подумай, чтобы соответсовать всему что промпте, ты должен учесть все что относится к рубрике и организации
Обрати внимание на каждый XML тег и проанализуй данные в нем
Большое внимание на <good_samples> и <bad_samples>

ultrathink
<system/>

<user>
Создай текст для поста
</user>
                        """
                }
            ],
            system_prompt=text_system_prompt,
            max_tokens=20000,
            thinking_tokens=15000,
            llm_model="claude-sonnet-4-5",
        )
        publication_data["text"] = publication_data["text"].replace("\n", "<br>")
        return publication_data

    @traced_method()
    async def regenerate_publication_text(
            self,
            category_id: int,
            publication_text: str,
            prompt: str = None
    ) -> dict:
        category = (await self.repo.get_category_by_id(category_id))[0]
        organization = await self.organization_client.get_organization_by_id(category.organization_id)
        organization_cost_multiplier = await self.organization_client.get_cost_multiplier(organization.id)

        if self._check_balance(organization, organization_cost_multiplier, "generate_text"):
            self.logger.info("Недостаточно средств на балансе")
            raise common.ErrInsufficientBalance()

        if prompt:
            self.logger.info("Регенерация текста публикации с промптом")
            text_system_prompt = await self.prompt_generator.get_regenerate_publication_text_system_prompt(
                category,
                organization,
                publication_text,
                prompt,
            )
            publication_data, generate_cost = await self.anthropic_client.generate_json(
                history=[
                    {
                        "role": "user",
                        "content": """
<system>
Очень хорошо подумай, чтобы соответсовать всему что промпте, ты должен учесть все что относится к рубрике и организации
Обрати внимание на каждый XML тег и проанализуй данные в нем
Большое внимание на <good_samples> и <bad_samples>

ultrathink
<system/>

<user>
Следуй инструкциям перегенерации
</user>
                        """
                    }
                ],
                system_prompt=text_system_prompt,
                llm_model="claude-sonnet-4-5",
                max_tokens=20000,
                thinking_tokens=15000,
            )
        else:
            self.logger.info("Регенерация текста публикации без промпта")
            text_system_prompt = await self.prompt_generator.get_regenerate_publication_text_system_prompt(
                category,
                organization,
                publication_text,
                "",
            )
            publication_data, generate_cost = await self.anthropic_client.generate_json(
                history=[
                    {
                        "role": "user",
                        "content": """
<system>
Очень хорошо подумай, чтобы соответсовать всему что промпте, ты должен учесть все что относится к рубрике и организации
Обрати внимание на каждый XML тег и проанализуй данные в нем
Большое внимание на <good_samples> и <bad_samples>

ultrathink
<system/>

<user>
Следуй инструкциям перегенерации
</user>
                        """
                    }
                ],
                system_prompt=text_system_prompt,
                llm_model="claude-sonnet-4-5",
                max_tokens=20000,
                thinking_tokens=15000,
            )

        await self._debit_organization_balance(
            category.organization_id,
            generate_cost["total_cost"] * organization_cost_multiplier.generate_text_cost_multiplier
        )
        publication_data["text"] = publication_data["text"].replace("\n", "<br>")
        return publication_data

    @traced_method()
    async def generate_publication_image(
            self,
            category_id: int,
            publication_text: str,
            text_reference: str,
            prompt: str = None,
            image_file: UploadFile = None
    ) -> list[str]:
        category = (await self.repo.get_category_by_id(category_id))[0]
        organization = await self.organization_client.get_organization_by_id(category.organization_id)
        organization_cost_multiplier = await self.organization_client.get_cost_multiplier(organization.id)

        if self._check_balance(organization, organization_cost_multiplier, "generate_image"):
            self.logger.info("Недостаточно средств на балансе")
            raise common.ErrInsufficientBalance()

        if prompt:
            if image_file:
                self.logger.info("Генерация изображения с промптом и файлом")
                generate_image_system_prompt = await self.prompt_generator.get_generate_image_with_user_prompt_system(
                    prompt,
                    category.prompt_for_image_style,
                    publication_text,
                    category,
                    organization,
                )
                image_content = await image_file.read()
                generate_image_prompt, generate_prompt_cost = await self.anthropic_client.generate_json(
                    history=[
                        {
                            "role": "user",
                            "content": """
<system>
ultrathink
<system/>

<user>
Сделай JSON-промпт для генерации картинки
</user>
"""
                        }
                    ],
                    system_prompt=generate_image_system_prompt,
                    llm_model="claude-sonnet-4-5",
                    max_tokens=20000,
                    thinking_tokens=15000,
                    images=[image_content]
                )

                images, generate_cost = await self.googleai_client.edit_image(
                    prompt=str(generate_image_prompt),
                    image_data=image_content,
                    aspect_ratio="16:9",
                    model_name="gemini-3-pro-image-preview",
                )
                images = [images]
            else:
                self.logger.info("Генерация изображения с промптом")
                generate_image_system_prompt = await self.prompt_generator.get_generate_image_with_user_prompt_system(
                    prompt,
                    category.prompt_for_image_style,
                    publication_text,
                    category,
                    organization,
                    True
                )

                generate_image_prompt, generate_prompt_cost = await self.anthropic_client.generate_json(
                    history=[
                        {
                            "role": "user",
                            "content": """
<system>
ultrathink
<system/>

<user>
Сделай JSON-промпт для генерации картинки
</user>
"""
                        }
                    ],
                    system_prompt=generate_image_system_prompt,
                    llm_model="claude-sonnet-4-5",
                    max_tokens=20000,
                    thinking_tokens=15000,
                )

                images, generate_cost = await self.googleai_client.generate_image(
                    prompt=str(generate_image_prompt),
                    aspect_ratio="16:9",
                    model_name="gemini-3-pro-image-preview",
                )
                images = [images]

        else:
            self.logger.info("Генерация изображения без промпта")
            generate_image_system_prompt = await self.prompt_generator.get_generate_image_prompt_system(
                category.prompt_for_image_style,
                publication_text,
                category,
                organization
            )

            generate_image_prompt, generate_prompt_cost = await self.anthropic_client.generate_json(
                history=[
                    {
                        "role": "user",
                        "content": """
<system>
ultrathink
<system/>

<user>
Сделай JSON-промпт для генерации картинки
</user>
"""
                    }
                ],
                system_prompt=generate_image_system_prompt,
                llm_model="claude-sonnet-4-5",
                max_tokens=20000,
                thinking_tokens=15000,
            )

            images, generate_cost = await self.googleai_client.generate_image(
                prompt=str(generate_image_prompt),
                aspect_ratio="16:9",
                model_name="gemini-3-pro-image-preview",
            )
            images = [images]

        images_url = await self._upload_images(images)

        await self._debit_organization_balance(
            category.organization_id,
            generate_prompt_cost["total_cost"] * organization_cost_multiplier.generate_text_cost_multiplier
        )

        await self._debit_organization_balance(
            category.organization_id,
            generate_cost["total_cost"] * organization_cost_multiplier.generate_image_cost_multiplier
        )
        return images_url

    @traced_method()
    async def create_publication(
            self,
            organization_id: int,
            category_id: int,
            creator_id: int,
            text_reference: str,
            text: str,
            moderation_status: str,
            image_url: str = None,
            image_file: UploadFile = None,
    ) -> int:
        publication_id = await self.repo.create_publication(
            organization_id=organization_id,
            category_id=category_id,
            creator_id=creator_id,
            text_reference=text_reference,
            text=text,
            moderation_status=moderation_status
        )

        # Обрабатываем изображение
        if image_file and image_file.filename:
            self.logger.info("Загрузка изображения из файла")

            image_content = await image_file.read()
            image_io = io.BytesIO(image_content)
            image_name = image_file.filename

            upload_response = await self.storage.upload(image_io, image_name)

            await self.repo.change_publication(
                publication_id=publication_id,
                image_fid=upload_response.fid,
                image_name=image_name
            )

        elif image_url:
            self.logger.info("Загрузка изображения по URL")

            image_content = await self.openai_client.download_image_from_url(image_url)
            image_io = io.BytesIO(image_content)
            image_name = f"{uuid.uuid4().hex}.png"

            upload_response = await self.storage.upload(image_io, image_name)

            await self.repo.change_publication(
                publication_id=publication_id,
                image_fid=upload_response.fid,
                image_name=image_name
            )

        return publication_id

    @traced_method()
    async def change_publication(
            self,
            publication_id: int,
            vk_source: bool = None,
            tg_source: bool = None,
            vk_link: str = None,
            tg_link: str = None,
            text: str = None,
            image_url: str = None,
            image_file: UploadFile = None,
    ) -> None:
        image_fid = None
        image_name = None

        if image_file and image_file.filename:
            self.logger.info("Загрузка нового изображения из файла")

            image_content = await image_file.read()
            image_io = io.BytesIO(image_content)
            image_name = image_file.filename

            upload_response = await self.storage.upload(image_io, image_name)
            image_fid = upload_response.fid

        elif image_url:
            self.logger.info("Загрузка нового изображения по URL")

            image_content = await self.openai_client.download_image_from_url(image_url)
            image_io = io.BytesIO(image_content)
            image_name = f"{uuid.uuid4().hex}.png"

            upload_response = await self.storage.upload(image_io, image_name)
            image_fid = upload_response.fid

        old_publication = (await self.repo.get_publication_by_id(publication_id))[0]
        await self.repo.change_publication(
            publication_id=publication_id,
            vk_source=vk_source,
            tg_source=tg_source,
            vk_link=vk_link,
            tg_link=tg_link,
            text=text,
            image_fid=image_fid,
            image_name=image_name,
        )

        if image_file or image_url:
            if old_publication.image_fid:
                self.logger.info("Безопасное удаление старой картинки")
                await self.storage.delete(
                    old_publication.image_fid,
                    old_publication.image_name
                )

    @traced_method()
    async def delete_publication(
            self,
            publication_id: int,
    ) -> None:
        publication = (await self.repo.get_publication_by_id(publication_id))[0]

        if publication.image_fid and publication.image_name:
            self.logger.info("Удаление изображения публикации")
            await self.storage.delete(publication.image_fid, publication.image_name)

        await self.repo.delete_publication(publication_id)

    @traced_method()
    async def delete_publication_image(
            self,
            publication_id: int,
    ) -> None:
        publication = (await self.repo.get_publication_by_id(publication_id))[0]
        if publication.image_fid:
            self.logger.info("Удаление изображения из хранилища")
            await self.storage.delete(publication.image_fid, publication.image_name)

        await self.repo.change_publication(
            publication_id=publication_id,
            image_fid="",
            image_name=""
        )

    @traced_method()
    async def send_publication_to_moderation(
            self,
            publication_id: int,
    ) -> None:
        await self.repo.change_publication(
            publication_id=publication_id,
            moderation_status=model.ModerationStatus.MODERATION.value
        )

    @traced_method()
    async def moderate_publication(
            self,
            publication_id: int,
            moderator_id: int,
            moderation_status: str,
            moderation_comment: str = ""
    ) -> dict:
        await self.repo.change_publication(
            publication_id=publication_id,
            moderator_id=moderator_id,
            moderation_status=moderation_status,
            moderation_comment=moderation_comment
        )
        post_links = {}
        publication = (await self.repo.get_publication_by_id(publication_id))[0]
        if moderation_status == model.ModerationStatus.APPROVED.value:
            self.logger.info("Публикация одобрена, публикуем в соцсети")

            if publication.tg_source:
                self.logger.info("Публикация в Telegram")
                tg_post_link = await self._publish_to_telegram(publication)
                await self.repo.change_publication(
                    publication_id=publication_id,
                    tg_link=tg_post_link,
                )
                post_links["telegram"] = tg_post_link

            await self.loom_tg_bot_client.notify_publication_approved(
                account_id=publication.creator_id,
                publication_id=publication_id,
            )
        if moderation_status == model.ModerationStatus.REJECTED.value:
            self.logger.info("Отправляем уведомление об отклоненной публикации")
            await self.loom_tg_bot_client.notify_publication_rejected(
                account_id=publication.creator_id,
                publication_id=publication_id,
            )

        return post_links

    @traced_method()
    async def get_publication_by_id(self, publication_id: int) -> model.Publication:
        publication = (await self.repo.get_publication_by_id(publication_id))[0]
        return publication

    @traced_method()
    async def get_publications_by_organization(self, organization_id: int) -> list[model.Publication]:
        publications = await self.repo.get_publications_by_organization(organization_id)
        return publications

    @traced_method()
    async def download_publication_image(
            self,
            publication_id: int
    ) -> tuple[io.BytesIO, str]:
        publication = (await self.repo.get_publication_by_id(publication_id))[0]

        image_io, content_type = await self.storage.download(
            publication.image_fid,
            publication.image_name
        )

        return image_io, content_type

    @traced_method()
    async def download_other_image(
            self,
            image_fid: str,
            image_name: str
    ) -> tuple[io.BytesIO, str]:
        image_io, content_type = await self.storage.download(
            image_fid,
            "open_ai_image.png"
        )

        return image_io, content_type

    # РУБРИКИ
    @traced_method()
    async def create_category(
            self,
            organization_id: int,
            name: str,
            hint: str,
            goal: str,
            tone_of_voice: list[str],
            brand_rules: list[str],
            creativity_level: int,
            audience_segment: str,
            len_min: int,
            len_max: int,
            n_hashtags_min: int,
            n_hashtags_max: int,
            cta_type: str,
            cta_strategy: dict,
            good_samples: list[dict],
            bad_samples: list[dict],
            additional_info: list[dict],
            prompt_for_image_style: str
    ) -> int:
        category_id = await self.repo.create_category(
            organization_id=organization_id,
            name=name,
            hint=hint,
            goal=goal,
            tone_of_voice=tone_of_voice,
            brand_rules=brand_rules,
            creativity_level=creativity_level,
            audience_segment=audience_segment,
            len_min=len_min,
            len_max=len_max,
            n_hashtags_min=n_hashtags_min,
            n_hashtags_max=n_hashtags_max,
            cta_type=cta_type,
            cta_strategy=cta_strategy,
            good_samples=good_samples,
            bad_samples=bad_samples,
            additional_info=additional_info,
            prompt_for_image_style=prompt_for_image_style
        )
        return category_id

    @traced_method()
    async def get_category_by_id(self, category_id: int) -> model.Category:
        category = (await self.repo.get_category_by_id(category_id))[0]
        return category

    @traced_method()
    async def get_categories_by_organization(self, organization_id: int) -> list[model.Category]:
        categories = await self.repo.get_categories_by_organization(organization_id)
        return categories

    @traced_method()
    async def update_category(
            self,
            category_id: int,
            name: str = None,
            hint: str = None,
            goal: str = None,
            tone_of_voice: list[str] = None,
            brand_rules: list[str] = None,
            creativity_level: int = None,
            audience_segment: str = None,
            len_min: int = None,
            len_max: int = None,
            n_hashtags_min: int = None,
            n_hashtags_max: int = None,
            cta_type: str = None,
            cta_strategy: dict = None,
            good_samples: list[dict] = None,
            bad_samples: list[dict] = None,
            additional_info: list[dict] = None,
            prompt_for_image_style: str = None
    ) -> None:
        await self.repo.update_category(
            category_id=category_id,
            name=name,
            hint=hint,
            goal=goal,
            tone_of_voice=tone_of_voice,
            brand_rules=brand_rules,
            creativity_level=creativity_level,
            audience_segment=audience_segment,
            len_min=len_min,
            len_max=len_max,
            n_hashtags_min=n_hashtags_min,
            n_hashtags_max=n_hashtags_max,
            cta_type=cta_type,
            cta_strategy=cta_strategy,
            good_samples=good_samples,
            bad_samples=bad_samples,
            additional_info=additional_info,
            prompt_for_image_style=prompt_for_image_style
        )

    @traced_method()
    async def delete_category(self, category_id: int) -> None:
        await self.repo.delete_category(category_id)
        # TODO сделать сервис для удаления всех публикаци по категории
        await self.repo.delete_publication_by_category_id(category_id)

    @traced_method()
    async def generate_categories(
            self,
            organization_id: int
    ) -> list[dict]:
        organization = await self.organization_client.get_organization_by_id(organization_id)

        system_prompt = await self.prompt_generator.get_generate_categories_system_prompt(organization)

        categories_data, generate_cost = await self.anthropic_client.generate_json(
            history=[
                {
                    "role": "user",
                    "content": """
<system>
Очень хорошо проанализируй организацию, используй web_search для изучения ниши
Создай 2 профессиональные рубрики с учетом всех требований из промпта

ultrathink
</system>

<user>
Создай 2 рубрики для организации
</user>
                    """
                }
            ],
            system_prompt=system_prompt,
            max_tokens=25000,
            thinking_tokens=20000,
            llm_model="claude-sonnet-4-5",
            enable_web_search=True
        )

        created_categories = []
        for category in categories_data["categories"]:
            category_id = await self.create_category(
                organization_id=organization_id,
                name=category["name"],
                hint=category["hint"],
                goal=category["goal"],
                tone_of_voice=category["tone_of_voice"],
                brand_rules=category["brand_rules"],
                creativity_level=category["creativity_level"],
                audience_segment=category["audience_segment"],
                len_min=category["len_min"],
                len_max=category["len_max"],
                n_hashtags_min=category["n_hashtags_min"],
                n_hashtags_max=category["n_hashtags_max"],
                cta_type=category["cta_type"],
                cta_strategy=category["cta_strategy"],
                good_samples=category["good_samples"],
                bad_samples=category["bad_samples"],
                additional_info=category["additional_info"],
                prompt_for_image_style=category["prompt_for_image_style"]
            )
            category["id"] = category_id
            created_categories.append(category)

        return created_categories

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
        autoposting_category_id = await self.repo.create_autoposting_category(
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
    async def get_autoposting_category_by_id(self, autoposting_category_id: int) -> model.AutopostingCategory:
        category = (await self.repo.get_autoposting_category_by_id(autoposting_category_id))[0]
        return category

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
        await self.repo.update_autoposting_category(
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

    # АВТОПОСТИНГ

    @traced_method()
    async def generate_autoposting_publication_text(
            self,
            autoposting_category_id: int,
            source_post_text: str
    ) -> dict:
        autoposting_category = (await self.repo.get_autoposting_category_by_id(autoposting_category_id))[0]
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

    @traced_method()
    async def generate_autoposting_publication_image(
            self,
            autoposting_category_id: int,
            publication_text: str
    ) -> list[str]:
        autoposting_category = (await self.repo.get_autoposting_category_by_id(autoposting_category_id))[0]
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
        autoposting_id = await self.repo.create_autoposting(
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
        await self.repo.update_autoposting(
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
    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        autopostings = await self.repo.get_autoposting_by_organization(organization_id)
        return autopostings

    @traced_method()
    async def get_all_autopostings(self) -> list[model.Autoposting]:
        autopostings = await self.repo.get_all_autopostings()
        return autopostings

    @traced_method()
    async def delete_autoposting(self, autoposting_id: int) -> None:
        autoposting = (await self.repo.get_autoposting_by_id(autoposting_id))[0]
        await self.repo.delete_publication_by_category_id(autoposting.autoposting_category_id)
        await self.repo.delete_autoposting_category(autoposting.autoposting_category_id)
        await self.repo.delete_autoposting(autoposting_id)
        # TODO нормально удалять публикации

    # ПРОСМОТРЕННЫЕ TELEGRAM ПОСТЫ
    @traced_method()
    async def create_viewed_telegram_post(
            self,
            autoposting_id: int,
            tg_channel_username: str,
            link: str
    ) -> int:
        viewed_post_id = await self.repo.create_viewed_telegram_post(
            autoposting_id=autoposting_id,
            tg_channel_username=tg_channel_username,
            link=link
        )

        return viewed_post_id

    @traced_method()
    async def get_viewed_telegram_post(
            self,
            autoposting_id: int,
            tg_channel_username: str
    ) -> list[model.ViewedTelegramPost]:
        viewed_posts = await self.repo.get_viewed_telegram_post(
            autoposting_id=autoposting_id,
            tg_channel_username=tg_channel_username
        )

        return viewed_posts

    @traced_method()
    async def transcribe_audio(
            self,
            audio_file: UploadFile,
            organization_id: int,
    ) -> str:
        if organization_id == -1:
            audio_content = await audio_file.read()
            transcribed_text, generate_cost = await self.openai_client.transcribe_audio(
                audio_content,
                audio_file.filename,
                "whisper-1",
                "ru"
            )
            return transcribed_text

        organization = await self.organization_client.get_organization_by_id(organization_id)
        organization_cost_multiplier = await self.organization_client.get_cost_multiplier(organization.id)

        if self._check_balance(organization, organization_cost_multiplier, "transcribe_audio"):
            self.logger.info("Недостаточно средств на балансе")
            raise common.ErrInsufficientBalance()

        audio_content = await audio_file.read()
        transcribed_text, generate_cost = await self.openai_client.transcribe_audio(
            audio_content,
            audio_file.filename,
            "whisper-1",
            "ru"
        )
        await self._debit_organization_balance(
            organization_id,
            generate_cost["total_cost"] * organization_cost_multiplier.transcribe_audio_cost_multiplier,
        )

        return transcribed_text

    @traced_method()
    async def edit_image(
            self,
            organization_id: int,
            image_file: UploadFile,
            prompt: str,
    ) -> list[str]:
        organization = await self.organization_client.get_organization_by_id(organization_id)
        organization_cost_multiplier = await self.organization_client.get_cost_multiplier(organization.id)

        if self._check_balance(organization, organization_cost_multiplier, "edit_image"):
            self.logger.info("Недостаточно средств на балансе")
            raise common.ErrInsufficientBalance()

        self.logger.info("Редактирование изображения через GoogleAI")
        image_content = await image_file.read()

        result_image_data, generate_cost = await self.googleai_client.edit_image(
            image_data=image_content,
            model_name="gemini-3-pro-image-preview",
            prompt=prompt,
            aspect_ratio="16:9",
        )

        result_image_base64 = base64.b64encode(result_image_data).decode('utf-8')
        images_url = await self._upload_images([result_image_base64])

        await self._debit_organization_balance(
            organization_id,
            generate_cost["total_cost"] * organization_cost_multiplier.generate_image_cost_multiplier
        )

        return images_url

    @traced_method()
    async def combine_images(
            self,
            organization_id: int,
            category_id: int,
            images_files: list[UploadFile],
            prompt: str,
    ) -> list[str]:
        organization = await self.organization_client.get_organization_by_id(organization_id)
        organization_cost_multiplier = await self.organization_client.get_cost_multiplier(organization.id)

        if self._check_balance(organization, organization_cost_multiplier, "edit_image"):
            self.logger.info("Недостаточно средств на балансе")
            raise common.ErrInsufficientBalance()

        images_data = []
        for image_file in images_files:
            image_content = await image_file.read()
            images_data.append(image_content)

        result_image_data, generate_cost = await self.googleai_client.combine_images(
            images_data=images_data,
            prompt=prompt,
            model_name="gemini-3-pro-image-preview",
            aspect_ratio="16:9",
        )

        result_image_base64 = base64.b64encode(result_image_data).decode('utf-8')
        images_url = await self._upload_images([result_image_base64])

        await self._debit_organization_balance(
            organization_id,
            generate_cost["total_cost"] * organization_cost_multiplier.generate_image_cost_multiplier
        )

        return images_url

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

    async def _publish_to_telegram(self, publication: model.Publication) -> str:
        telegram_account = (await self.social_network_repo.get_telegrams_by_organization(
            publication.organization_id
        ))[0]

        if publication.image_fid:
            self.logger.info("Публикация с изображением")
            photo_io, _ = await self.storage.download(publication.image_fid, publication.image_name)
            tg_post_link = await self.telegram_client.send_photo(
                telegram_account.tg_channel_username,
                photo=photo_io.read(),
                caption=publication.text,
            )
        else:
            self.logger.info("Публикация без изображения")
            tg_post_link = await self.telegram_client.send_text_message(
                telegram_account.tg_channel_username,
                text=publication.text,
            )
        return tg_post_link
