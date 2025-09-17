import io
import uuid
from datetime import datetime

from fastapi import UploadFile
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface, model


class PublicationService(interface.IPublicationService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            repo: interface.IPublicationRepo,
            llm_client: interface.ILLMClient,
            storage: interface.IStorage,
            prompt_generator: interface.IPublicationPromptGenerator,
            organization_client: interface.IKonturOrganizationClient,
            tg_bot_client: interface.IKonturTgBotClient,
            vizard_client: interface.IVizardClient,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.repo = repo
        self.llm_client = llm_client
        self.storage = storage
        self.prompt_generator = prompt_generator
        self.organization_client = organization_client
        self.tg_bot_client = tg_bot_client
        self.vizard_client = vizard_client

    # ПУБЛИКАЦИИ
    async def generate_publication(
            self,
            organization_id: int,
            category_id: int,
            creator_id: int,
            need_images: bool,
            text_reference: str,
            time_for_publication: datetime = None
    ) -> int:
        with self.tracer.start_as_current_span(
                "PublicationService.generate_publication",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id,
                    "category_id": category_id,
                    "creator_id": creator_id,
                    "need_images": need_images
                }
        ) as span:
            try:
                # Получаем категорию для промптов
                categories = await self.repo.get_category_by_id(category_id)
                if not categories:
                    raise ValueError(f"Category {category_id} not found")

                category = categories[0]

                # Генерируем текст публикации
                text_system_prompt = await self.prompt_generator.get_generate_publication_text_system_prompt(
                    category.prompt_for_text_style,
                    text_reference
                )

                publication_data, publication_data_cost = await self.llm_client.generate_json(
                    history=[{"role": "user", "content": "Создай пост для социальной сети"}],
                    system_prompt=text_system_prompt,
                    temperature=0.7,
                    llm_model="gpt-4o"
                )

                # Парсим теги
                tags = [tag.strip().replace('#', '') for tag in publication_data["tags"].split(',')]
                tags = [f"#{tag}" for tag in tags if tag]

                # Создаем публикацию в БД
                publication_id = await self.repo.create_publication(
                    organization_id=organization_id,
                    category_id=category_id,
                    creator_id=creator_id,
                    text_reference=text_reference,
                    name=publication_data["name"].strip(),
                    text=publication_data["text"],
                    tags=tags,
                    time_for_publication=time_for_publication
                )

                # Считаем общую стоимость текста
                total_text_cost_rub = int(publication_data_cost.total_cost * 100)
                await self.repo.add_openai_rub_cost_to_publication(publication_id, total_text_cost_rub)

                # Генерируем изображение если нужно
                if need_images:
                    try:
                        image_system_prompt = await self.prompt_generator.get_generate_publication_image_system_prompt(
                            category.prompt_for_image_style,
                            publication_data["text"]
                        )

                        image_urls, image_cost = await self.llm_client.generate_image(
                            prompt=image_system_prompt,
                            llm_model="dall-e-3",
                            size="1024x1024",
                            quality="standard",
                            style="vivid"
                        )

                        if image_urls:
                            # Скачиваем изображение
                            image_bytes = await self.llm_client.download_image_from_url(image_urls[0])
                            image_io = io.BytesIO(image_bytes)

                            # Загружаем в Storage
                            image_name = f"{uuid.uuid4().hex}.png"
                            upload_response = await self.storage.upload(image_io, image_name)

                            # Обновляем публикацию с изображением
                            await self.repo.change_publication(
                                publication_id,
                                image_fid=upload_response.fid,
                                image_name=image_name,
                            )

                            # Добавляем стоимость изображения
                            image_cost_rub = int(image_cost.total_cost * 100)
                            await self.repo.add_openai_rub_cost_to_publication(publication_id, image_cost_rub)

                    except Exception as image_error:
                        self.logger.warning(
                            f"Failed to generate image for publication {publication_id}: {str(image_error)}")

                # Списываем стоимость с организации
                try:
                    await self.organization_client.debit_balance(organization_id, total_text_cost_rub)
                except Exception as billing_error:
                    self.logger.error(
                        f"Failed to debit balance for organization {organization_id}: {str(billing_error)}")

                span.set_status(Status(StatusCode.OK))
                return publication_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def regenerate_publication_image(
            self,
            publication_id: int,
            prompt: str = None,
    ) -> io.BytesIO:
        with self.tracer.start_as_current_span(
                "PublicationService.regenerate_publication_image",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                # Получаем публикацию
                publications = await self.repo.get_publication_by_id(publication_id)
                if not publications:
                    raise ValueError(f"Publication {publication_id} not found")

                publication = publications[0]

                # Получаем категорию для стиля
                categories = await self.repo.get_category_by_id(publication.category_id)
                if not categories:
                    raise ValueError(f"Category {publication.category_id} not found")

                category = categories[0]

                # Генерируем промпт для изображения
                if prompt:
                    image_system_prompt = await self.prompt_generator.get_regenerate_publication_image_system_prompt(
                        category.prompt_for_image_style,
                        publication.text,
                        prompt
                    )
                else:
                    image_system_prompt = await self.prompt_generator.get_generate_publication_image_system_prompt(
                        category.prompt_for_image_style,
                        publication.text
                    )

                # Генерируем новое изображение
                image_urls, image_cost = await self.llm_client.generate_image(
                    prompt=image_system_prompt,
                    llm_model="dall-e-3",
                    size="1024x1024",
                    quality="standard",
                    style="vivid"
                )

                if not image_urls:
                    raise ValueError("Failed to generate image")

                # Скачиваем изображение
                image_bytes = await self.llm_client.download_image_from_url(image_urls[0])
                image_io = io.BytesIO(image_bytes)

                # Удаляем старое изображение если есть
                if publication.image_fid:
                    try:
                        await self.storage.delete(publication.image_fid, publication.image_name)
                    except Exception:
                        pass  # Игнорируем ошибки удаления

                # Загружаем новое изображение
                upload_response = await self.storage.upload(image_io, "generated_image.png")

                # Обновляем публикацию
                await self.repo.change_publication(
                    publication_id=publication_id,
                    image_fid=upload_response.fid
                )

                # Добавляем стоимость
                image_cost_rub = int(image_cost.total_cost * 100)
                await self.repo.add_openai_rub_cost_to_publication(publication_id, image_cost_rub)

                # Списываем с организации
                try:
                    await self.organization_client.debit_balance(publication.organization_id, image_cost_rub)
                except Exception as billing_error:
                    self.logger.error(f"Failed to debit balance: {str(billing_error)}")

                # Возвращаем новый BytesIO для скачивания
                image_io.seek(0)
                span.set_status(Status(StatusCode.OK))
                return image_io

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def regenerate_publication_text(
            self,
            publication_id: int,
            prompt: str = None,
    ) -> dict:
        with self.tracer.start_as_current_span(
                "PublicationService.regenerate_publication_text",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                # Получаем публикацию
                publications = await self.repo.get_publication_by_id(publication_id)
                if not publications:
                    raise ValueError(f"Publication {publication_id} not found")

                publication = publications[0]

                # Получаем категорию для стиля
                categories = await self.repo.get_category_by_id(publication.category_id)
                if not categories:
                    raise ValueError(f"Category {publication.category_id} not found")

                category = categories[0]

                # Генерируем промпт для текста
                if prompt:
                    text_system_prompt = await self.prompt_generator.get_regenerate_publication_text_system_prompt(
                        category.prompt_for_text_style,
                        publication.text,
                        prompt
                    )
                else:
                    text_system_prompt = await self.prompt_generator.get_generate_publication_text_system_prompt(
                        category.prompt_for_text_style,
                        publication.text_reference
                    )

                # Генерируем новый текст
                publication_data, text_cost = await self.llm_client.generate_json(
                    history=[{"role": "user", "content": "Создай улучшенный пост для социальной сети"}],
                    system_prompt=text_system_prompt,
                    temperature=0.7,
                    llm_model="gpt-4o"
                )

                # Обновляем публикацию
                await self.repo.change_publication(
                    publication_id,
                    name=publication_data["name"].strip(),
                    text=publication_data["text"],
                    tags=publication_data["tags"],
                )

                # Добавляем стоимость
                text_cost_rub = int(text_cost.total_cost * 100)
                await self.repo.add_openai_rub_cost_to_publication(publication_id, text_cost_rub)

                # Списываем с организации
                try:
                    await self.organization_client.debit_balance(publication.organization_id, text_cost_rub)
                except Exception as billing_error:
                    self.logger.error(f"Failed to debit balance: {str(billing_error)}")

                span.set_status(Status(StatusCode.OK))
                return publication_data

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def change_publication(
            self,
            publication_id: int,
            vk_source_id: int = None,
            tg_source_id: int = None,
            name: str = None,
            text: str = None,
            tags: list[str] = None,
            time_for_publication: datetime = None,
            image: UploadFile = None,
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.change_publication",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                image_fid = None

                # Загружаем новое изображение если предоставлено
                if image:
                    # Читаем файл
                    image_content = await image.read()
                    image_io = io.BytesIO(image_content)

                    # Получаем текущую публикацию для удаления старого изображения
                    publications = await self.repo.get_publication_by_id(publication_id)
                    if publications and publications[0].image_fid:
                        try:
                            await self.storage.delete(publications[0].image_fid, publications[0].image_name)
                        except Exception:
                            pass  # Игнорируем ошибки удаления

                    # Загружаем новое изображение
                    upload_response = await self.storage.upload(image_io, image.filename or "uploaded_image.png")
                    image_fid = upload_response.fid

                # Обновляем публикацию
                await self.repo.change_publication(
                    publication_id=publication_id,
                    name=name,
                    text=text,
                    tags=tags,
                    time_for_publication=time_for_publication,
                    image_fid=image_fid
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def publish_publication(
            self,
            publication_id: int,
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.publish_publication",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                # Получаем публикацию
                publications = await self.repo.get_publication_by_id(publication_id)
                if not publications:
                    raise ValueError(f"Publication {publication_id} not found")

                publication = publications[0]

                # Проверяем статус
                if publication.moderation_status != model.ModerationStatus.APPROVED:
                    raise ValueError(f"Publication must be approved before publishing")

                # Обновляем статус и время публикации
                await self.repo.change_publication(
                    publication_id=publication_id,
                    moderation_status=model.ModerationStatus.PUBLISHED,
                    publication_at=datetime.utcnow()
                )

                # TODO: Здесь нужно добавить логику отправки в соцсети
                # Например, через VK, Instagram, YouTube клиенты

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                    raise ValueError(f"Publication {publication_id} not found")

                publication = publications[0]

                # Удаляем файл из Storage если есть
                if publication.image_fid:
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
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                    moderation_status=model.ModerationStatus.MODERATION
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def moderate_publication(
            self,
            publication_id: int,
            moderator_id: int,
            moderation_status: model.ModerationStatus,
            moderation_comment: str = ""
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.moderate_publication",
                kind=SpanKind.INTERNAL,
                attributes={
                    "publication_id": publication_id,
                    "moderator_id": moderator_id,
                    "moderation_status": moderation_status.value
                }
        ) as span:
            try:
                await self.repo.change_publication(
                    publication_id=publication_id,
                    moderator_id=moderator_id,
                    moderation_status=moderation_status,
                    moderation_comment=moderation_comment
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                    raise ValueError(f"Publication {publication_id} not found")

                span.set_status(Status(StatusCode.OK))
                return publications[0]

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                    raise ValueError(f"Publication {publication_id} not found")

                publication = publications[0]

                if not publication.image_fid:
                    raise ValueError(f"Publication {publication_id} has no image")

                # Скачиваем из Storage
                image_io, content_type = await self.storage.download(
                    publication.image_fid,
                    publication.image_name or "image.png"
                )

                span.set_status(Status(StatusCode.OK))
                return image_io, content_type

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # РУБРИКИ
    async def create_category(
            self,
            organization_id: int,
            prompt_for_image_style: str,
            prompt_for_text_style: str
    ) -> int:
        with self.tracer.start_as_current_span(
                "PublicationService.create_category",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                category_id = await self.repo.create_category(
                    organization_id=organization_id,
                    prompt_for_image_style=prompt_for_image_style,
                    prompt_for_text_style=prompt_for_text_style
                )

                span.set_status(Status(StatusCode.OK))
                return category_id

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                    raise ValueError(f"Category {category_id} not found")

                span.set_status(Status(StatusCode.OK))
                return categories[0]

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def update_category(
            self,
            category_id: int,
            prompt_for_image_style: str = None,
            prompt_for_text_style: str = None
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.update_category",
                kind=SpanKind.INTERNAL,
                attributes={"category_id": category_id}
        ) as span:
            try:
                await self.repo.update_category(
                    category_id=category_id,
                    prompt_for_image_style=prompt_for_image_style,
                    prompt_for_text_style=prompt_for_text_style
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_category(self, category_id: int) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.delete_category",
                kind=SpanKind.INTERNAL,
                attributes={"category_id": category_id}
        ) as span:
            try:
                await self.repo.delete_category(category_id)

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # АВТОПОСТИНГ
    async def create_autoposting(
            self,
            organization_id: int,
            filter_prompt: str,
            rewrite_prompt: str,
            tg_channels: list[str] = None
    ) -> int:
        with self.tracer.start_as_current_span(
                "PublicationService.create_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                autoposting_id = await self.repo.create_autoposting(
                    organization_id=organization_id,
                    filter_prompt=filter_prompt,
                    rewrite_prompt=rewrite_prompt,
                    tg_channels=tg_channels or []
                )

                span.set_status(Status(StatusCode.OK))
                return autoposting_id

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def update_autoposting(
            self,
            autoposting_id: int,
            filter_prompt: str = None,
            rewrite_prompt: str = None,
            enabled: bool = None,
            tg_channels: list[str] = None
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.update_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_id": autoposting_id}
        ) as span:
            try:
                await self.repo.update_autoposting(
                    autoposting_id=autoposting_id,
                    filter_prompt=filter_prompt,
                    rewrite_prompt=rewrite_prompt,
                    enabled=enabled,
                    tg_channels=tg_channels
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_autoposting(self, autoposting_id: int) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.delete_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_id": autoposting_id}
        ) as span:
            try:
                await self.repo.delete_autoposting(autoposting_id)

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # НАРЕЗКА
    async def generate_video_cut(
            self,
            organization_id: int,
            creator_id: int,
            youtube_video_reference: str,
            time_for_publication: datetime = None
    ) -> int:
        with self.tracer.start_as_current_span(
                "PublicationService.generate_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id,
                    "creator_id": creator_id,
                    "youtube_video_reference": youtube_video_reference
                }
        ) as span:
            try:
                # Создаем проект в Vizard
                vizard_project = await self.vizard_client.create_project(
                    video_url=youtube_video_reference,
                    video_type="youtube",
                    lang="ru",
                    prefer_length=[15, 30, 60],
                    ratio_of_clip=9,  # 9:16 для вертикальных видео
                    remove_silence=True,
                    max_clip_number=3,
                    subtitle_switch=True,
                    emoji_switch=True,
                    highlight_switch=True,
                    headline_switch=True,
                    project_name=f"Video cut for org {organization_id}"
                )

                video_cut_rub_cost = int(self.vizard_client.calculate_price(
                    5,
                    3
                )["estimated_cost"] * 100)

                project_id = vizard_project.get("project_id")
                if not project_id:
                    raise ValueError("Failed to create Vizard project")

                name = vizard_project.get("name")
                description = vizard_project.get("description")
                tags = vizard_project.get("tags")


                # Парсим теги
                tags = [tag.strip().replace('#', '') for tag in tags.split(',')]
                tags = [f"#{tag}" for tag in tags if tag]

                # Создаем запись в БД
                video_cut_id = await self.repo.create_video_cut(
                    project_id=int(project_id),
                    organization_id=organization_id,
                    creator_id=creator_id,
                    youtube_video_reference=youtube_video_reference,
                    name=name,
                    description=description,
                    tags=tags,
                    time_for_publication=time_for_publication
                )

                try:
                    await self.organization_client.debit_balance(organization_id, video_cut_rub_cost)
                except Exception as billing_error:
                    self.logger.error(
                        f"Failed to debit balance for organization {organization_id}: {str(billing_error)}")

                span.set_status(Status(StatusCode.OK))

                return video_cut_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def change_video_cut(
            self,
            video_cut_id: int,
            name: str = None,
            description: str = None,
            tags: list[str] = None,
            time_for_publication: datetime = None
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.change_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                await self.repo.change_video_cut(
                    video_cut_id=video_cut_id,
                    name=name,
                    description=description,
                    tags=tags,
                    time_for_publication=time_for_publication
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_video_cut_to_moderation(
            self,
            video_cut_id: int,
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.send_video_cut_to_moderation",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                await self.repo.change_video_cut(
                    video_cut_id=video_cut_id,
                    moderation_status=model.ModerationStatus.MODERATION
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def publish_video_cut(
            self,
            video_cut_id: int,
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.publish_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                # Получаем видеонарезку
                video_cuts = await self.repo.get_video_cut_by_id(video_cut_id)
                if not video_cuts:
                    raise ValueError(f"Video cut {video_cut_id} not found")

                video_cut = video_cuts[0]

                # Проверяем статус
                if video_cut.moderation_status != model.ModerationStatus.APPROVED:
                    raise ValueError(f"Video cut must be approved before publishing")

                try:
                    # TODO: Здесь нужно добавить логику отправки в соцсети
                    # Например, через VK, Instagram, YouTube клиенты
                    pass
                except Exception as send_error:
                    self.logger.error(f"Failed to send video cut via Telegram: {str(send_error)}")

                # Обновляем статус
                await self.repo.change_video_cut(
                    video_cut_id=video_cut_id,
                    moderation_status=model.ModerationStatus.PUBLISHED
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_video_cut_by_id(self, video_cut_id: int) -> model.VideoCut:
        with self.tracer.start_as_current_span(
                "PublicationService.get_video_cut_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                video_cuts = await self.repo.get_video_cut_by_id(video_cut_id)
                if not video_cuts:
                    raise ValueError(f"Video cut {video_cut_id} not found")

                span.set_status(Status(StatusCode.OK))
                return video_cuts[0]

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_video_cuts_by_organization(self, organization_id: int) -> list[model.VideoCut]:
        with self.tracer.start_as_current_span(
                "PublicationService.get_video_cuts_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                video_cuts = await self.repo.get_video_cuts_by_organization(organization_id)

                span.set_status(Status(StatusCode.OK))
                return video_cuts

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def moderate_video_cut(
            self,
            video_cut_id: int,
            moderator_id: int,
            moderation_status: model.ModerationStatus,
            moderation_comment: str = ""
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationService.moderate_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={
                    "video_cut_id": video_cut_id,
                    "moderator_id": moderator_id,
                    "moderation_status": moderation_status.value
                }
        ) as span:
            try:
                await self.repo.change_video_cut(
                    video_cut_id=video_cut_id,
                    moderator_id=moderator_id,
                    moderation_status=moderation_status,
                    moderation_comment=moderation_comment
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def download_video_cut(
            self,
            video_cut_id: int
    ) -> tuple[io.BytesIO, str]:
        with self.tracer.start_as_current_span(
                "PublicationService.download_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                # Получаем видеонарезку
                video_cuts = await self.repo.get_video_cut_by_id(video_cut_id)
                if not video_cuts:
                    raise ValueError(f"Video cut {video_cut_id} not found")

                video_cut = video_cuts[0]

                if not video_cut.video_fid:
                    # Проверяем статус проекта в Vizard
                    project_status = await self.vizard_client.get_project_status(str(video_cut.project_id))

                    if project_status.get("status") == "completed":
                        # TODO: Получить URL готового видео и скачать его
                        # video_url = project_status.get("video_url")
                        # Пока возвращаем ошибку
                        raise ValueError(f"Video cut {video_cut_id} is ready but not downloaded yet")
                    else:
                        raise ValueError(
                            f"Video cut {video_cut_id} is not ready yet. Status: {project_status.get('status', 'unknown')}")

                # Скачиваем из Storage
                video_io, content_type = await self.storage.download(
                    video_cut.video_fid,
                    video_cut.video_name or "video.mp4"
                )

                span.set_status(Status(StatusCode.OK))
                return video_io, content_type

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err