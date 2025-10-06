import base64
import io
import uuid
from datetime import datetime
from decimal import Decimal

from fastapi import UploadFile
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface, model


class PublicationService(interface.IPublicationService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            repo: interface.IPublicationRepo,
            social_network_repo: interface.ISocialNetworkRepo,
            openai_client: interface.IOpenAIClient,
            storage: interface.IStorage,
            prompt_generator: interface.IPublicationPromptGenerator,
            organization_client: interface.ILoomOrganizationClient,
            vizard_client: interface.IVizardClient,
            telegram_client: interface.ITelegramClient,
            loom_domain: str,
            environment: str,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.repo = repo
        self.social_network_repo = social_network_repo
        self.openai_client = openai_client
        self.storage = storage
        self.prompt_generator = prompt_generator
        self.organization_client = organization_client
        self.vizard_client = vizard_client
        self.telegram_client = telegram_client
        self.loom_domain = loom_domain
        self.environment = environment

    # ПУБЛИКАЦИИ
    async def generate_publication_text(
            self,
            category_id: int,
            text_reference: str
    ) -> dict:
        with self.tracer.start_as_current_span(
                "PublicationService.generate_publication_text",
                kind=SpanKind.INTERNAL,
                attributes={"category_id": category_id}
        ) as span:
            try:
                # Получаем категорию для промптов
                categories = await self.repo.get_category_by_id(category_id)
                if not categories:
                    self.logger.info("Категория не найдена")
                    raise ValueError(f"Category {category_id} not found")

                category = categories[0]

                # Получаем организацию
                organization = await self.organization_client.get_organization_by_id(category.organization_id)

                # Генерируем текст публикации
                text_system_prompt = await self.prompt_generator.get_generate_publication_text_system_prompt(
                    category,
                    organization
                )

                publication_data, generate_cost = await self.openai_client.generate_json(
                    history=[{"role": "user",
                              "content": f"Создай пост для социальной сети, вот мой запрос: {text_reference}"}],
                    system_prompt=text_system_prompt,
                    temperature=1,
                    llm_model="gpt-5"
                )
                await self._debit_organization_balance(category.organization_id, generate_cost["total_cost"])

                span.set_status(Status(StatusCode.OK))
                return publication_data

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def regenerate_publication_text(
            self,
            category_id: int,
            publication_text: str,
            prompt: str = None
    ) -> dict:
        with self.tracer.start_as_current_span(
                "PublicationService.regenerate_publication_text_standalone",
                kind=SpanKind.INTERNAL,
                attributes={"category_id": category_id}
        ) as span:
            try:
                # Получаем категорию для стиля
                categories = await self.repo.get_category_by_id(category_id)
                if not categories:
                    self.logger.info("Категория не найдена")
                    raise ValueError(f"Category {category_id} not found")

                category = categories[0]

                # Получаем организацию
                organization = await self.organization_client.get_organization_by_id(category.organization_id)

                # Генерируем промпт для текста
                if prompt:
                    self.logger.info("Регенерация текста публикации с промптом")
                    text_system_prompt = await self.prompt_generator.get_regenerate_publication_text_system_prompt(
                        category,
                        organization,
                        publication_text,
                    )
                    publication_data, generate_cost = await self.openai_client.generate_json(
                        history=[
                            {
                                "role": "user",
                                "content": f"Создай улучшенный пост для социальной сети c этими правками: {prompt}"
                            }
                        ],
                        system_prompt=text_system_prompt,
                        temperature=1,
                        llm_model="gpt-5"
                    )
                else:
                    self.logger.info("Регенерация текста публикации без промпта")
                    text_system_prompt = await self.prompt_generator.get_regenerate_publication_text_system_prompt(
                        category,
                        organization,
                        publication_text,
                    )
                    publication_data, generate_cost = await self.openai_client.generate_json(
                        history=[
                            {
                                "role": "user",
                                "content": f"Создай улучшенный пост для социальной сети"
                            }
                        ],
                        system_prompt=text_system_prompt,
                        temperature=1,
                        llm_model="gpt-5"
                    )

                # Генерируем новый текст

                await self._debit_organization_balance(category.organization_id, generate_cost["total_cost"])

                span.set_status(Status(StatusCode.OK))
                return publication_data

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def generate_publication_image(
            self,
            category_id: int,
            publication_text: str,
            text_reference: str,
            prompt: str = None,
            image_file: UploadFile = None
    ) -> list[str]:
        with self.tracer.start_as_current_span(
                "PublicationService.generate_publication_image_standalone",
                kind=SpanKind.INTERNAL,
                attributes={"category_id": category_id}
        ) as span:
            try:
                # Получаем категорию для стиля
                categories = await self.repo.get_category_by_id(category_id)
                if not categories:
                    self.logger.info("Категория не найдена")
                    raise ValueError(f"Category {category_id} not found")

                category = categories[0]

                if self.environment == "prod":
                    size = "1536x1024"
                    quality = "high"
                else:
                    size = "1024x1024"
                    quality = "low"

                # Генерируем промпт для изображения
                if prompt:
                    if image_file:
                        self.logger.info("Редактирование изображения с промптом и файлом")
                        image_system_prompt = await self.prompt_generator.get_regenerate_publication_image_system_prompt(
                            category.prompt_for_image_style,
                            publication_text,
                            prompt
                        )
                        image_content = await image_file.read()
                        images, generate_cost = await self.openai_client.edit_image(
                            image=image_content,
                            prompt=image_system_prompt,
                            image_model="gpt-image-1",
                            size=size,
                            quality=quality,
                            n=1
                        )
                    else:
                        self.logger.info("Генерация изображения с промптом")
                        image_system_prompt = await self.prompt_generator.get_regenerate_publication_image_system_prompt(
                            category.prompt_for_image_style,
                            publication_text,
                            prompt
                        )
                        images, generate_cost = await self.openai_client.generate_image(
                            prompt=image_system_prompt,
                            image_model="gpt-image-1",
                            size=size,
                            quality=quality,
                            n=1,
                        )

                else:
                    self.logger.info("Генерация изображения без промпта")
                    image_system_prompt = await self.prompt_generator.get_generate_publication_image_system_prompt(
                        category.prompt_for_image_style,
                        publication_text
                    )

                    images, generate_cost = await self.openai_client.generate_image(
                        prompt=image_system_prompt,
                        image_model="gpt-image-1",
                        size=size,
                        quality=quality,
                        n=1,
                    )

                images_url = []
                for image in images:
                    image_bytes = base64.b64decode(image)
                    image_name = "open_ai_image.png"

                    upload_response = await self.storage.upload(io.BytesIO(image_bytes), image_name)

                    image_url = f"https://{self.loom_domain}/api/content/image/{upload_response.fid}/{image_name}"
                    images_url.append(image_url)

                await self._debit_organization_balance(category.organization_id, generate_cost["total_cost"])

                return images_url


            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

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
        with self.tracer.start_as_current_span(
                "PublicationService.create_publication",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id,
                    "category_id": category_id,
                    "creator_id": creator_id
                }
        ) as span:
            try:
                # Создаем публикацию в БД
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
                    # Загружаем файл изображения
                    image_content = await image_file.read()
                    image_io = io.BytesIO(image_content)
                    image_name = image_file.filename

                    # Загружаем в Storage
                    upload_response = await self.storage.upload(image_io, image_name)

                    # Обновляем публикацию с изображением
                    await self.repo.change_publication(
                        publication_id=publication_id,
                        image_fid=upload_response.fid,
                        image_name=image_name
                    )

                elif image_url:
                    self.logger.info("Загрузка изображения по URL")
                    # Загружаем изображение по URL (старая логика)
                    image_content = await self.openai_client.download_image_from_url(image_url)
                    image_io = io.BytesIO(image_content)
                    image_name = f"{uuid.uuid4().hex}.png"

                    # Загружаем в Storage
                    upload_response = await self.storage.upload(image_io, image_name)

                    # Обновляем публикацию с изображением
                    await self.repo.change_publication(
                        publication_id=publication_id,
                        image_fid=upload_response.fid,
                        image_name=image_name
                    )

                span.set_status(Status(StatusCode.OK))
                return publication_id

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def change_publication(
            self,
            publication_id: int,
            vk_source: bool = None,
            tg_source: bool = None,
            text: str = None,
            image_url: str = None,
            image_file: UploadFile = None,
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.change_publication",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                image_fid = None
                image_name = None

                # Если загружается новое изображение, сначала удаляем старое
                if image_file or image_url:
                    self.logger.info("Удаление старого изображения перед загрузкой нового")
                    # Получаем текущую публикацию для проверки старого изображения
                    publications = await self.repo.get_publication_by_id(publication_id)
                    if publications and publications[0].image_fid:
                        self.logger.info("Старое изображение найдено, удаление")
                        old_publication = publications[0]
                        # Удаляем старый файл из Storage
                        try:
                            await self.storage.delete(
                                old_publication.image_fid,
                                old_publication.image_name
                            )
                        except Exception as delete_error:
                            self.logger.warning(
                                f"Failed to delete old image: {str(delete_error)}"
                            )

                if image_file and image_file.filename:
                    self.logger.info("Загрузка нового изображения из файла")
                    # Загружаем файл изображения
                    image_content = await image_file.read()
                    image_io = io.BytesIO(image_content)
                    image_name = image_file.filename

                    # Загружаем в Storage
                    upload_response = await self.storage.upload(image_io, image_name)
                    image_fid = upload_response.fid

                elif image_url:
                    self.logger.info("Загрузка нового изображения по URL")
                    # Загружаем изображение по URL
                    image_content = await self.openai_client.download_image_from_url(image_url)
                    image_io = io.BytesIO(image_content)
                    image_name = f"{uuid.uuid4().hex}.png"

                    # Загружаем в Storage
                    upload_response = await self.storage.upload(image_io, image_name)
                    image_fid = upload_response.fid

                # Обновляем публикацию
                await self.repo.change_publication(
                    publication_id=publication_id,
                    vk_source=vk_source,
                    tg_source=tg_source,
                    text=text,
                    image_fid=image_fid,
                    image_name=image_name,
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_publication(
            self,
            publication_id: int,
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.delete_publication",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                # Получаем публикацию для проверки существования и получения информации о файле
                publications = await self.repo.get_publication_by_id(publication_id)
                if not publications:
                    self.logger.info("Публикация не найдена")
                    raise ValueError(f"Publication {publication_id} not found")

                publication = publications[0]

                # Удаляем файл изображения из Storage если есть
                if publication.image_fid and publication.image_name:
                    self.logger.info("Удаление изображения публикации")
                    try:
                        await self.storage.delete(publication.image_fid, publication.image_name)
                    except Exception as delete_error:
                        self.logger.warning(f"Failed to delete image file: {str(delete_error)}", {
                            "publication_id": publication_id,
                            "image_fid": publication.image_fid
                        })

                # Удаляем публикацию из БД
                await self.repo.delete_publication(publication_id)
                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_publication_image(
            self,
            publication_id: int,
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.delete_publication_image",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                # Получаем публикацию
                publications = await self.repo.get_publication_by_id(publication_id)
                if not publications:
                    self.logger.info("Публикация не найдена")
                    raise ValueError(f"Publication {publication_id} not found")

                publication = publications[0]

                # Удаляем файл из Storage если есть
                if publication.image_fid:
                    self.logger.info("Удаление изображения из хранилища")
                    try:
                        await self.storage.delete(publication.image_fid, publication.image_name)
                    except Exception as delete_error:
                        self.logger.warning(f"Failed to delete image file: {str(delete_error)}")

                # Очищаем поля изображения в БД
                await self.repo.change_publication(
                    publication_id=publication_id,
                    image_fid=""
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def send_publication_to_moderation(
            self,
            publication_id: int,
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.send_publication_to_moderation",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                await self.repo.change_publication(
                    publication_id=publication_id,
                    moderation_status=model.ModerationStatus.MODERATION.value
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def moderate_publication(
            self,
            publication_id: int,
            moderator_id: int,
            moderation_status: str,
            moderation_comment: str = ""
    ) -> dict:
        with self.tracer.start_as_current_span(
                "PublicationService.moderate_publication",
                kind=SpanKind.INTERNAL,
                attributes={
                    "publication_id": publication_id,
                    "moderator_id": moderator_id,
                    "moderation_status": moderation_status
                }
        ) as span:
            try:
                await self.repo.change_publication(
                    publication_id=publication_id,
                    moderator_id=moderator_id,
                    moderation_status=moderation_status,
                    moderation_comment=moderation_comment
                )
                post_links = {}
                if moderation_status == model.ModerationStatus.APPROVED.value:
                    self.logger.info("Публикация одобрена, публикуем в соцсети")
                    publication = (await self.repo.get_publication_by_id(publication_id))[0]

                    if publication.tg_source:
                        self.logger.info("Публикация в Telegram")
                        tg_post_link = await self._publish_to_telegram(publication)
                        post_links["telegram"] = tg_post_link

                span.set_status(Status(StatusCode.OK))
                return post_links

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_publication_by_id(self, publication_id: int) -> model.Publication:
        with self.tracer.start_as_current_span(
                "PublicationService.get_publication_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                publications = await self.repo.get_publication_by_id(publication_id)
                if not publications:
                    self.logger.info("Публикация не найдена")
                    raise ValueError(f"Publication {publication_id} not found")

                span.set_status(Status(StatusCode.OK))
                return publications[0]

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_publications_by_organization(self, organization_id: int) -> list[model.Publication]:
        with self.tracer.start_as_current_span(
                "PublicationService.get_publications_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                publications = await self.repo.get_publications_by_organization(organization_id)

                span.set_status(Status(StatusCode.OK))
                return publications

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def download_publication_image(
            self,
            publication_id: int
    ) -> tuple[io.BytesIO, str]:
        with self.tracer.start_as_current_span(
                "PublicationService.download_publication_image",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                # Получаем публикацию
                publications = await self.repo.get_publication_by_id(publication_id)
                if not publications:
                    self.logger.info("Публикация не найдена")
                    raise ValueError(f"Publication {publication_id} not found")

                publication = publications[0]

                if not publication.image_fid:
                    self.logger.info("У публикации нет изображения")
                    raise ValueError(f"Publication {publication_id} has no image")

                # Скачиваем из Storage
                image_io, content_type = await self.storage.download(
                    publication.image_fid,
                    publication.image_name or "image.png"
                )

                span.set_status(Status(StatusCode.OK))
                return image_io, content_type

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def download_other_image(
            self,
            image_fid: str,
            image_name: str
    ) -> tuple[io.BytesIO, str]:
        with self.tracer.start_as_current_span(
                "PublicationService.download_other_image",
                kind=SpanKind.INTERNAL,
                attributes={"image_fid": image_fid}
        ) as span:
            try:

                # Скачиваем из Storage
                image_io, content_type = await self.storage.download(
                    image_fid,
                    "open_ai_image.png"
                )

                span.set_status(Status(StatusCode.OK))
                return image_io, content_type

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    # РУБРИКИ
    async def create_category(
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
        with self.tracer.start_as_current_span(
                "PublicationService.create_category",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                category_id = await self.repo.create_category(
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

                span.set_status(Status(StatusCode.OK))
                return category_id

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_category_by_id(self, category_id: int) -> model.Category:
        with self.tracer.start_as_current_span(
                "PublicationService.get_category_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"category_id": category_id}
        ) as span:
            try:
                categories = await self.repo.get_category_by_id(category_id)
                if not categories:
                    self.logger.info("Категория не найдена")
                    raise ValueError(f"Category {category_id} not found")

                span.set_status(Status(StatusCode.OK))
                return categories[0]

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_categories_by_organization(self, organization_id: int) -> list[model.Category]:
        with self.tracer.start_as_current_span(
                "PublicationService.get_categories_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                categories = await self.repo.get_categories_by_organization(organization_id)

                span.set_status(Status(StatusCode.OK))
                return categories

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_category(
            self,
            category_id: int,
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
        with self.tracer.start_as_current_span(
                "PublicationService.update_category",
                kind=SpanKind.INTERNAL,
                attributes={"category_id": category_id}
        ) as span:
            try:
                await self.repo.update_category(
                    category_id=category_id,
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

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_category(self, category_id: int) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.delete_category",
                kind=SpanKind.INTERNAL,
                attributes={"category_id": category_id}
        ) as span:
            try:
                await self.repo.delete_category(category_id)
                await self.repo.delete_publication_by_category_id(category_id)
                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    # РУБРИКИ ДЛЯ АВТОПОСТИНГА
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
        with self.tracer.start_as_current_span(
                "PublicationService.create_autoposting_category",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
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

                span.set_status(Status(StatusCode.OK))
                return autoposting_category_id

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_autoposting_category_by_id(self, autoposting_category_id: int) -> model.AutopostingCategory:
        with self.tracer.start_as_current_span(
                "PublicationService.get_autoposting_category_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_category_id": autoposting_category_id}
        ) as span:
            try:
                categories = await self.repo.get_autoposting_category_by_id(autoposting_category_id)

                if not categories:
                    self.logger.info("Категория автопостинга не найдена")
                    raise ValueError(f"Autoposting category with id {autoposting_category_id} not found")

                span.set_status(Status(StatusCode.OK))
                return categories[0]

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

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
        with self.tracer.start_as_current_span(
                "PublicationService.update_autoposting_category",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_category_id": autoposting_category_id}
        ) as span:
            try:
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

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    # АВТОПОСТИНГ
    async def generate_autoposting_publication_text(
            self,
            autoposting_category_id: int,
            source_post_text: str
    ) -> dict:
        with self.tracer.start_as_current_span(
                "PublicationService.generate_autoposting_publication_text",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_category_id": autoposting_category_id}
        ) as span:
            try:
                # Получаем категорию автопостинга
                categories = await self.repo.get_autoposting_category_by_id(autoposting_category_id)
                if not categories:
                    self.logger.info("Категория автопостинга не найдена")
                    raise ValueError(f"Autoposting category {autoposting_category_id} not found")

                autoposting_category = categories[0]

                # Получаем организацию
                organization = await self.organization_client.get_organization_by_id(
                    autoposting_category.organization_id)

                # Генерируем промпт для автопостинга
                text_system_prompt = await self.prompt_generator.get_generate_autoposting_text_system_prompt(
                    autoposting_category,
                    organization,
                    source_post_text
                )

                # Генерируем текст публикации
                publication_data, generate_cost = await self.openai_client.generate_json(
                    history=[{"role": "user", "content": "Создай пост для социальной сети на основе исходного поста"}],
                    system_prompt=text_system_prompt,
                    temperature=1,
                    llm_model="gpt-5"
                )
                await self._debit_organization_balance(autoposting_category.organization_id,
                                                       generate_cost["total_cost"])

                span.set_status(Status(StatusCode.OK))
                return publication_data

            except Exception as err:

                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def generate_autoposting_publication_image(
            self,
            autoposting_category_id: int,
            publication_text: str
    ) -> list[str]:
        with self.tracer.start_as_current_span(
                "PublicationService.generate_autoposting_publication_image",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_category_id": autoposting_category_id}
        ) as span:
            try:
                # Получаем категорию автопостинга
                categories = await self.repo.get_autoposting_category_by_id(autoposting_category_id)
                if not categories:
                    self.logger.info("Категория автопостинга не найдена")
                    raise ValueError(f"Autoposting category {autoposting_category_id} not found")

                autoposting_category = categories[0]

                # Генерируем промпт для изображения
                image_system_prompt = await self.prompt_generator.get_generate_autoposting_image_system_prompt(
                    autoposting_category.prompt_for_image_style,
                    publication_text
                )

                # Генерируем изображение
                images, generate_cost = await self.openai_client.generate_image(
                    prompt=image_system_prompt,
                    image_model="gpt-image-1",
                    size="1024x1024",
                    quality="low",
                    n=1,
                )

                images_url = []
                for image in images:
                    image_bytes = base64.b64decode(image)
                    image_name = "autoposting_image.png"

                    upload_response = await self.storage.upload(io.BytesIO(image_bytes), image_name)

                    image_url = f"https://{self.loom_domain}/api/content/image/{upload_response.fid}/{image_name}"
                    images_url.append(image_url)

                await self._debit_organization_balance(autoposting_category.organization_id,
                                                       generate_cost["total_cost"])

                span.set_status(Status(StatusCode.OK))
                return images_url

            except Exception as err:

                span.set_status(StatusCode.ERROR, str(err))
                raise err

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
        with self.tracer.start_as_current_span(
                "PublicationService.create_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                autoposting_id = await self.repo.create_autoposting(
                    organization_id=organization_id,
                    autoposting_category_id=autoposting_category_id,
                    period_in_hours=period_in_hours,
                    filter_prompt=filter_prompt,
                    tg_channels=tg_channels,
                    required_moderation=required_moderation,
                    need_image=need_image
                )

                span.set_status(Status(StatusCode.OK))
                return autoposting_id

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

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
        with self.tracer.start_as_current_span(
                "PublicationService.update_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_id": autoposting_id}
        ) as span:
            try:
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

                span.set_status(Status(StatusCode.OK))

            except Exception as err:

                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        with self.tracer.start_as_current_span(
                "PublicationService.get_autoposting_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                autopostings = await self.repo.get_autoposting_by_organization(organization_id)

                span.set_status(Status(StatusCode.OK))
                return autopostings

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_all_autopostings(self) -> list[model.Autoposting]:
        with self.tracer.start_as_current_span(
                "PublicationService.get_all_autopostings",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                autopostings = await self.repo.get_all_autopostings()

                span.set_status(Status(StatusCode.OK))
                return autopostings

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_autoposting(self, autoposting_id: int) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.delete_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_id": autoposting_id}
        ) as span:
            try:
                autoposting = (await self.repo.get_autoposting_by_id(autoposting_id))[0]
                await self.repo.delete_publication_by_category_id(autoposting.autoposting_category_id)
                await self.repo.delete_autoposting_category(autoposting.autoposting_category_id)
                await self.repo.delete_autoposting(autoposting_id)

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    # ПРОСМОТРЕННЫЕ TELEGRAM ПОСТЫ
    async def create_viewed_telegram_post(
            self,
            autoposting_id: int,
            tg_channel_username: str,
            link: str
    ) -> int:
        with self.tracer.start_as_current_span(
                "PublicationService.create_viewed_telegram_post",
                kind=SpanKind.INTERNAL,
                attributes={
                    "autoposting_id": autoposting_id,
                    "tg_channel_username": tg_channel_username,
                    "link": link
                }
        ) as span:
            try:
                viewed_post_id = await self.repo.create_viewed_telegram_post(
                    autoposting_id=autoposting_id,
                    tg_channel_username=tg_channel_username,
                    link=link
                )

                span.set_status(Status(StatusCode.OK))
                return viewed_post_id

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_viewed_telegram_post(
            self,
            autoposting_id: int,
            tg_channel_username: str
    ) -> list[model.ViewedTelegramPost]:
        with self.tracer.start_as_current_span(
                "PublicationService.get_viewed_telegram_post",
                kind=SpanKind.INTERNAL,
                attributes={
                    "autoposting_id": autoposting_id,
                    "tg_channel_username": tg_channel_username
                }
        ) as span:
            try:
                viewed_posts = await self.repo.get_viewed_telegram_post(
                    autoposting_id=autoposting_id,
                    tg_channel_username=tg_channel_username
                )

                span.set_status(Status(StatusCode.OK))
                return viewed_posts

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def transcribe_audio(
            self,
            audio_file: UploadFile,
            organization_id: int,
    ) -> str:
        with self.tracer.start_as_current_span(
                "PublicationService.transcribe_audio",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                audio_content = await audio_file.read()
                transcribed_text, generate_cost = await self.openai_client.transcribe_audio(
                    audio_content,
                    audio_file.filename,
                    "whisper-1",
                    "ru"
                )
                await self._debit_organization_balance(organization_id, generate_cost["total_cost"])

                return transcribed_text

            except Exception as err:
                
                span.set_status(StatusCode.ERROR, str(err))
                raise err

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
