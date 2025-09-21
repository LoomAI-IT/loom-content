import base64
import io
import uuid

from fastapi import UploadFile
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface, model


class PublicationService(interface.IPublicationService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            repo: interface.IPublicationRepo,
            openai_client: interface.IOpenAIClient,
            storage: interface.IStorage,
            prompt_generator: interface.IPublicationPromptGenerator,
            organization_client: interface.IKonturOrganizationClient,
            vizard_client: interface.IVizardClient,
            kontur_domain: str

    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.repo = repo
        self.openai_client = openai_client
        self.storage = storage
        self.prompt_generator = prompt_generator
        self.organization_client = organization_client
        self.vizard_client = vizard_client
        self.kontur_domain = kontur_domain

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
                    raise ValueError(f"Category {category_id} not found")

                category = categories[0]

                # Генерируем текст публикации
                text_system_prompt = await self.prompt_generator.get_generate_publication_text_system_prompt(
                    category.prompt_for_text_style,
                    text_reference
                )

                publication_data, generate_cost = await self.openai_client.generate_json(
                    history=[{"role": "user", "content": "Создай пост для социальной сети"}],
                    system_prompt=text_system_prompt,
                    temperature=1,
                    llm_model="gpt-5"
                )
                usd_cost = generate_cost["total_cost"]
                await self.organization_client.debit_balance(category.organization_id, int(usd_cost * 90.0))

                span.set_status(Status(StatusCode.OK))
                return publication_data

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                    raise ValueError(f"Category {category_id} not found")

                category = categories[0]

                # Генерируем промпт для текста
                if prompt:
                    text_system_prompt = await self.prompt_generator.get_regenerate_publication_text_system_prompt(
                        category.prompt_for_text_style,
                        publication_text,
                        prompt
                    )
                else:
                    text_system_prompt = await self.prompt_generator.get_generate_publication_text_system_prompt(
                        category.prompt_for_text_style,
                        publication_text
                    )

                # Генерируем новый текст
                publication_data, generate_cost = await self.openai_client.generate_json(
                    history=[{"role": "user", "content": "Создай улучшенный пост для социальной сети"}],
                    system_prompt=text_system_prompt,
                    temperature=1,
                    llm_model="gpt-5"
                )

                usd_cost = generate_cost["total_cost"]
                await self.organization_client.debit_balance(category.organization_id, int(usd_cost * 90.0))

                span.set_status(Status(StatusCode.OK))
                return publication_data

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                    raise ValueError(f"Category {category_id} not found")

                category = categories[0]

                # Генерируем промпт для изображения
                if prompt:
                    if image_file:
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
                            size="1024x1024",
                            quality="low",
                            n=1
                        )
                    else:
                        image_system_prompt = await self.prompt_generator.get_regenerate_publication_image_system_prompt(
                            category.prompt_for_image_style,
                            publication_text,
                            prompt
                        )
                        images, generate_cost = await self.openai_client.generate_image(
                            prompt=image_system_prompt,
                            image_model="gpt-image-1",
                            size="1024x1024",
                            quality="low",
                            n=1,
                        )

                else:
                    image_system_prompt = await self.prompt_generator.get_generate_publication_image_system_prompt(
                        category.prompt_for_image_style,
                        publication_text
                    )

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
                    image_name = "open_ai_image.png"

                    upload_response = await self.storage.upload(io.BytesIO(image_bytes), image_name)

                    image_url = f"https://{self.kontur_domain}/api/content/image/{upload_response.fid}/{image_name}"
                    images_url.append(image_url)

                usd_cost = generate_cost["total_cost"]
                await self.organization_client.debit_balance(category.organization_id, int(usd_cost * 90.0))

                return images_url


            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_publication(
            self,
            organization_id: int,
            category_id: int,
            creator_id: int,
            text_reference: str,
            name: str,
            text: str,
            tags: list[str],
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
                    name=name,
                    text=text,
                    tags=tags,
                    moderation_status=moderation_status
                )

                # Обрабатываем изображение
                if image_file and image_file.filename:
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
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def change_publication(
            self,
            publication_id: int,
            vk_source: bool = None,
            tg_source: bool = None,
            name: str = None,
            text: str = None,
            tags: list[str] = None,
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
                    # Получаем текущую публикацию для проверки старого изображения
                    publications = await self.repo.get_publication_by_id(publication_id)
                    if publications and publications[0].image_fid:
                        old_publication = publications[0]
                        # Удаляем старый файл из Storage
                        try:
                            await self.storage.delete(
                                old_publication.image_fid,
                                old_publication.image_name
                            )
                            self.logger.info(f"Deleted old image: {old_publication.image_fid}")
                        except Exception as delete_error:
                            self.logger.warning(
                                f"Failed to delete old image: {str(delete_error)}"
                            )

                if image_file and image_file.filename:
                    # Загружаем файл изображения
                    image_content = await image_file.read()
                    image_io = io.BytesIO(image_content)
                    image_name = image_file.filename

                    # Загружаем в Storage
                    upload_response = await self.storage.upload(image_io, image_name)
                    image_fid = upload_response.fid

                elif image_url:
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
                    name=name,
                    text=text,
                    tags=tags,
                    image_fid=image_fid,
                    image_name=image_name,
                )

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
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
                    raise ValueError(f"Publication {publication_id} not found")

                publication = publications[0]

                # Удаляем файл изображения из Storage если есть
                if publication.image_fid and publication.image_name:
                    try:
                        await self.storage.delete(publication.image_fid, publication.image_name)
                        self.logger.info(f"Deleted image file for publication {publication_id}", {
                            "image_fid": publication.image_fid,
                            "image_name": publication.image_name
                        })
                    except Exception as delete_error:
                        self.logger.warning(f"Failed to delete image file: {str(delete_error)}", {
                            "publication_id": publication_id,
                            "image_fid": publication.image_fid
                        })

                # Удаляем публикацию из БД
                await self.repo.delete_publication(publication_id)

                self.logger.info(f"Publication {publication_id} deleted successfully")
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
                    moderation_status=model.ModerationStatus.MODERATION.value
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
            moderation_status: str,
            moderation_comment: str = ""
    ) -> None:
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
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # РУБРИКИ
    async def create_category(
            self,
            organization_id: int,
            name: str,
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
                    name=name,
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
            name: str = None,
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
                    name=name,
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
                usd_cost = generate_cost["total_cost"]

                await self.organization_client.debit_balance(organization_id, int(usd_cost * 90.0))

                return transcribed_text

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
