from fastapi import Form, UploadFile, File
from opentelemetry.trace import Status, StatusCode, SpanKind

from fastapi.responses import JSONResponse, StreamingResponse

from internal import interface
from internal.controller.http.handler.publication.model import *


class PublicationController(interface.IPublicationController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            publication_service: interface.IPublicationService,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.publication_service = publication_service

    # ПУБЛИКАЦИИ
    async def generate_publication_text(
            self,
            body: GeneratePublicationTextBody,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.generate_publication_text",
                kind=SpanKind.INTERNAL,
                attributes={
                    "category_id": body.category_id
                }
        ) as span:
            try:
                self.logger.info("Generate publication text request", {
                    "category_id": body.category_id
                })

                text_data = await self.publication_service.generate_publication_text(
                    category_id=body.category_id,
                    text_reference=body.text_reference
                )

                self.logger.info("Publication text generated successfully", {
                    "category_id": body.category_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=text_data
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def regenerate_publication_text(
            self,
            body: RegeneratePublicationTextBody,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.regenerate_publication_text",
                kind=SpanKind.INTERNAL,
                attributes={
                    "category_id": body.category_id
                }
        ) as span:
            try:
                self.logger.info("Regenerate publication text request", {
                    "category_id": body.category_id
                })

                text_data = await self.publication_service.regenerate_publication_text(
                    category_id=body.category_id,
                    publication_text=body.publication_text,
                    prompt=body.prompt
                )

                self.logger.info("Publication text regenerated successfully", {
                    "category_id": body.category_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=text_data
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def generate_publication_image(
            self,
            category_id: int = Form(...),
            publication_text: str = Form(...),
            text_reference: str = Form(...),
            prompt: str | None = Form(None),
            image_file: UploadFile = File(None),
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.generate_publication_image",
                kind=SpanKind.INTERNAL,
                attributes={
                    "category_id": category_id
                }
        ) as span:
            try:
                self.logger.info("Generate publication image request", {
                    "category_id": category_id
                })

                images_url = await self.publication_service.generate_publication_image(
                    category_id=category_id,
                    publication_text=publication_text,
                    text_reference=text_reference,
                    prompt=prompt,
                    image_file=image_file,
                )

                self.logger.info("Publication image generated successfully", {
                    "category_id": category_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=images_url
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_publication(
            self,
            organization_id: int = Form(...),
            category_id: int = Form(...),
            creator_id: int = Form(...),
            text_reference: str = Form(...),
            text: str = Form(...),
            moderation_status: str = Form(...),
            image_url: str = Form(None),
            image_file: UploadFile = File(None),
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.create_publication",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id,
                    "category_id": category_id,
                    "creator_id": creator_id
                }
        ) as span:
            try:
                self.logger.info("Create publication request", {
                    "organization_id": organization_id,
                    "category_id": category_id,
                    "creator_id": creator_id
                })

                publication_id = await self.publication_service.create_publication(
                    organization_id=organization_id,
                    category_id=category_id,
                    creator_id=creator_id,
                    text_reference=text_reference,
                    text=text,
                    moderation_status=moderation_status,
                    image_url=image_url,
                    image_file=image_file
                )

                self.logger.info("Publication created successfully", {
                    "publication_id": publication_id,
                    "organization_id": organization_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "message": "Publication created successfully",
                        "publication_id": publication_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def change_publication(
            self,
            publication_id: int,
            vk_source: bool = Form(None),
            tg_source: bool = Form(None),
            text: str = Form(None),
            image_url: str = Form(None),
            image_file: UploadFile = File(None),
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.change_publication",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                self.logger.info("Change publication request", {
                    "publication_id": publication_id
                })

                await self.publication_service.change_publication(
                    publication_id=publication_id,
                    vk_source=vk_source,
                    tg_source=tg_source,
                    text=text,
                    image_url=image_url,
                    image_file=image_file,
                )

                self.logger.info("Publication changed successfully", {
                    "publication_id": publication_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Publication updated successfully",
                        "publication_id": publication_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_publication_image(
            self,
            publication_id: int,
    ):
        with self.tracer.start_as_current_span(
                "PublicationController.delete_publication_image",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                self.logger.info("Delete publication image request", {
                    "publication_id": publication_id
                })

                await self.publication_service.delete_publication_image(
                    publication_id=publication_id
                )

                self.logger.info("Publication image deleted successfully", {
                    "publication_id": publication_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Publication image deleted successfully",
                        "publication_id": publication_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_publication_to_moderation(
            self,
            publication_id: int,
    ):
        with self.tracer.start_as_current_span(
                "PublicationController.send_publication_to_moderation",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                self.logger.info("Send publication to moderation request", {
                    "publication_id": publication_id
                })

                await self.publication_service.send_publication_to_moderation(
                    publication_id=publication_id
                )

                self.logger.info("Publication sent to moderation successfully", {
                    "publication_id": publication_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Publication sent to moderation successfully",
                        "publication_id": publication_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def moderate_publication(
            self,
            body: ModeratePublicationBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.moderate_publication",
                kind=SpanKind.INTERNAL,
                attributes={
                    "publication_id": body.publication_id,
                    "moderator_id": body.moderator_id,
                    "moderation_status": body.moderation_status
                }
        ) as span:
            try:
                self.logger.info("Moderate publication request", {
                    "publication_id": body.publication_id,
                    "moderator_id": body.moderator_id,
                    "moderation_status": body.moderation_status
                })

                post_links = await self.publication_service.moderate_publication(
                    publication_id=body.publication_id,
                    moderator_id=body.moderator_id,
                    moderation_status=body.moderation_status,
                    moderation_comment=body.moderation_comment
                )

                self.logger.info("Publication moderated successfully", {
                    "publication_id": body.publication_id,
                    "moderation_status": body.moderation_status
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=post_links
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_publication_by_id(self, publication_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.get_publication_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                self.logger.info("Get publication by ID request", {
                    "publication_id": publication_id
                })

                publication = await self.publication_service.get_publication_by_id(publication_id)

                self.logger.info("Publication retrieved successfully", {
                    "publication_id": publication_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=publication.to_dict()
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_publications_by_organization(self, organization_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.get_publications_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                self.logger.info("Get publications by organization request", {
                    "organization_id": organization_id
                })

                publications = await self.publication_service.get_publications_by_organization(organization_id)

                self.logger.info("Publications retrieved successfully", {
                    "organization_id": organization_id,
                    "count": len(publications)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=[publication.to_dict() for publication in publications]
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def download_publication_image(
            self,
            publication_id: int
    ) -> StreamingResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.download_publication_image",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                self.logger.info("Download publication image request", {
                    "publication_id": publication_id
                })

                image_io, content_type = await self.publication_service.download_publication_image(publication_id)

                def iterfile():
                    try:
                        while True:
                            chunk = image_io.read(8192)
                            if not chunk:
                                break
                            yield chunk
                    finally:
                        image_io.close()

                self.logger.info("Publication image downloaded successfully", {
                    "publication_id": publication_id
                })

                span.set_status(Status(StatusCode.OK))
                return StreamingResponse(
                    iterfile(),
                    media_type=content_type or "image/png",
                    headers={
                        "Content-Disposition": f"attachment; filename=publication_{publication_id}_image.png"
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def download_other_image(
            self,
            image_fid: str,
            image_name: str
    ) -> StreamingResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.download_other_image",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                self.logger.info("Download other image request", {
                    "image_fid": image_fid
                })

                image_io, content_type = await self.publication_service.download_other_image(image_fid, image_name)

                def iterfile():
                    try:
                        while True:
                            chunk = image_io.read(8192)
                            if not chunk:
                                break
                            yield chunk
                    finally:
                        image_io.close()

                self.logger.info("Other image downloaded successfully", {
                    "image_fid": image_fid
                })

                span.set_status(Status(StatusCode.OK))
                return StreamingResponse(
                    iterfile(),
                    media_type=content_type or "image/png",
                    headers={
                        "Content-Disposition": f"attachment; filename={image_name}"
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_publication(
            self,
            publication_id: int,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.delete_publication",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                self.logger.info("Delete publication request", {
                    "publication_id": publication_id
                })

                await self.publication_service.delete_publication(
                    publication_id=publication_id
                )

                self.logger.info("Publication deleted successfully", {
                    "publication_id": publication_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Publication deleted successfully",
                        "publication_id": publication_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # РУБРИКИ
    async def create_category(
            self,
            body: CreateCategoryBody,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.create_category",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": body.organization_id}
        ) as span:
            try:
                self.logger.info("Create category request", {
                    "organization_id": body.organization_id
                })

                category_id = await self.publication_service.create_category(
                    organization_id=body.organization_id,
                    name=body.name,
                    prompt_for_image_style=body.prompt_for_image_style,
                    goal=body.goal,
                    structure_skeleton=body.structure_skeleton,
                    structure_flex_level_min=body.structure_flex_level_min,
                    structure_flex_level_max=body.structure_flex_level_max,
                    structure_flex_level_comment=body.structure_flex_level_comment,
                    must_have=body.must_have,
                    must_avoid=body.must_avoid,
                    social_networks_rules=body.social_networks_rules,
                    len_min=body.len_min,
                    len_max=body.len_max,
                    n_hashtags_min=body.n_hashtags_min,
                    n_hashtags_max=body.n_hashtags_max,
                    cta_type=body.cta_type,
                    tone_of_voice=body.tone_of_voice,
                    brand_rules=body.brand_rules,
                    good_samples=body.good_samples,
                    additional_info=body.additional_info
                )

                self.logger.info("Category created successfully", {
                    "category_id": category_id,
                    "organization_id": body.organization_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "message": "Category created successfully",
                        "category_id": category_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_category_by_id(self, category_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.get_category_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"category_id": category_id}
        ) as span:
            try:
                self.logger.info("Get category by ID request", {
                    "category_id": category_id
                })

                category = await self.publication_service.get_category_by_id(category_id)

                self.logger.info("Category retrieved successfully", {
                    "category_id": category_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=category.to_dict()
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_categories_by_organization(self, organization_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.get_categories_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                self.logger.info("Get categories by organization request", {
                    "organization_id": organization_id
                })

                categories = await self.publication_service.get_categories_by_organization(organization_id)

                self.logger.info("Categories retrieved successfully", {
                    "organization_id": organization_id,
                    "count": len(categories)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=[category.to_dict() for category in categories]
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def update_category(
            self,
            category_id: int,
            body: UpdateCategoryBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.update_category",
                kind=SpanKind.INTERNAL,
                attributes={"category_id": category_id}
        ) as span:
            try:
                self.logger.info("Update category request", {
                    "category_id": category_id
                })

                await self.publication_service.update_category(
                    category_id=category_id,
                    name=body.name,
                    prompt_for_image_style=body.prompt_for_image_style,
                    goal=body.goal,
                    structure_skeleton=body.structure_skeleton,
                    structure_flex_level_min=body.structure_flex_level_min,
                    structure_flex_level_max=body.structure_flex_level_max,
                    structure_flex_level_comment=body.structure_flex_level_comment,
                    must_have=body.must_have,
                    must_avoid=body.must_avoid,
                    social_networks_rules=body.social_networks_rules,
                    len_min=body.len_min,
                    len_max=body.len_max,
                    n_hashtags_min=body.n_hashtags_min,
                    n_hashtags_max=body.n_hashtags_max,
                    cta_type=body.cta_type,
                    tone_of_voice=body.tone_of_voice,
                    brand_rules=body.brand_rules,
                    good_samples=body.good_samples,
                    additional_info=body.additional_info
                )

                self.logger.info("Category updated successfully", {
                    "category_id": category_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Category updated successfully",
                        "category_id": category_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_category(self, category_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.delete_category",
                kind=SpanKind.INTERNAL,
                attributes={"category_id": category_id}
        ) as span:
            try:
                self.logger.info("Delete category request", {
                    "category_id": category_id
                })

                await self.publication_service.delete_category(category_id)

                self.logger.info("Category deleted successfully", {
                    "category_id": category_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Category deleted successfully",
                        "category_id": category_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # РУБРИКИ ДЛЯ АВТОПОСТИНГА
    async def create_autoposting_category(
            self,
            body: CreateAutopostingCategoryBody,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.create_autoposting_category",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": body.organization_id}
        ) as span:
            try:
                self.logger.info("Create autoposting category request", {
                    "organization_id": body.organization_id
                })

                autoposting_category_id = await self.publication_service.create_autoposting_category(
                    organization_id=body.organization_id,
                    name=body.name,
                    prompt_for_image_style=body.prompt_for_image_style,
                    goal=body.goal,
                    structure_skeleton=body.structure_skeleton,
                    structure_flex_level_min=body.structure_flex_level_min,
                    structure_flex_level_max=body.structure_flex_level_max,
                    structure_flex_level_comment=body.structure_flex_level_comment,
                    must_have=body.must_have,
                    must_avoid=body.must_avoid,
                    social_networks_rules=body.social_networks_rules,
                    len_min=body.len_min,
                    len_max=body.len_max,
                    n_hashtags_min=body.n_hashtags_min,
                    n_hashtags_max=body.n_hashtags_max,
                    cta_type=body.cta_type,
                    tone_of_voice=body.tone_of_voice,
                    brand_rules=body.brand_rules,
                    good_samples=body.good_samples,
                    additional_info=body.additional_info
                )

                self.logger.info("Autoposting category created successfully", {
                    "autoposting_category_id": autoposting_category_id,
                    "organization_id": body.organization_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "message": "Autoposting category created successfully",
                        "autoposting_category_id": autoposting_category_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_autoposting_category_by_id(self, autoposting_category_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.get_autoposting_category_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_category_id": autoposting_category_id}
        ) as span:
            try:
                self.logger.info("Get autoposting category by ID request", {
                    "autoposting_category_id": autoposting_category_id
                })

                category = await self.publication_service.get_autoposting_category_by_id(autoposting_category_id)

                self.logger.info("Autoposting category retrieved successfully", {
                    "autoposting_category_id": autoposting_category_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=category.to_dict()
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def update_autoposting_category(
            self,
            autoposting_category_id: int,
            body: UpdateAutopostingCategoryBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.update_autoposting_category",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_category_id": autoposting_category_id}
        ) as span:
            try:
                self.logger.info("Update autoposting category request", {
                    "autoposting_category_id": autoposting_category_id
                })

                await self.publication_service.update_autoposting_category(
                    autoposting_category_id=autoposting_category_id,
                    name=body.name,
                    prompt_for_image_style=body.prompt_for_image_style,
                    goal=body.goal,
                    structure_skeleton=body.structure_skeleton,
                    structure_flex_level_min=body.structure_flex_level_min,
                    structure_flex_level_max=body.structure_flex_level_max,
                    structure_flex_level_comment=body.structure_flex_level_comment,
                    must_have=body.must_have,
                    must_avoid=body.must_avoid,
                    social_networks_rules=body.social_networks_rules,
                    len_min=body.len_min,
                    len_max=body.len_max,
                    n_hashtags_min=body.n_hashtags_min,
                    n_hashtags_max=body.n_hashtags_max,
                    cta_type=body.cta_type,
                    tone_of_voice=body.tone_of_voice,
                    brand_rules=body.brand_rules,
                    good_samples=body.good_samples,
                    additional_info=body.additional_info
                )

                self.logger.info("Autoposting category updated successfully", {
                    "autoposting_category_id": autoposting_category_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Autoposting category updated successfully",
                        "autoposting_category_id": autoposting_category_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_autoposting_category(self, autoposting_category_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.delete_autoposting_category",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_category_id": autoposting_category_id}
        ) as span:
            try:
                self.logger.info("Delete autoposting category request", {
                    "autoposting_category_id": autoposting_category_id
                })

                await self.publication_service.delete_autoposting_category(autoposting_category_id)

                self.logger.info("Autoposting category deleted successfully", {
                    "autoposting_category_id": autoposting_category_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Autoposting category deleted successfully",
                        "autoposting_category_id": autoposting_category_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # АВТОПОСТИНГ
    async def create_autoposting(
            self,
            body: CreateAutopostingBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.create_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": body.organization_id}
        ) as span:
            try:
                self.logger.info("Create autoposting request", {
                    "organization_id": body.organization_id
                })

                autoposting_id = await self.publication_service.create_autoposting(
                    organization_id=body.organization_id,
                    autoposting_category_id=body.autoposting_category_id,
                    period_in_hours=body.period_in_hours,
                    filter_prompt=body.filter_prompt,
                    tg_channels=body.tg_channels or [],
                    required_moderation=body.required_moderation,
                    need_image=body.need_image
                )

                self.logger.info("Autoposting created successfully", {
                    "autoposting_id": autoposting_id,
                    "organization_id": body.organization_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "message": "Autoposting created successfully",
                        "autoposting_id": autoposting_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_autoposting_by_organization(self, organization_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.get_autoposting_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                self.logger.info("Get autoposting by organization request", {
                    "organization_id": organization_id
                })

                autopostings = await self.publication_service.get_autoposting_by_organization(organization_id)

                self.logger.info("Autopostings retrieved successfully", {
                    "organization_id": organization_id,
                    "count": len(autopostings)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Autopostings retrieved successfully",
                        "autopostings": [autoposting.to_dict() for autoposting in autopostings]
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def update_autoposting(
            self,
            autoposting_id: int,
            body: UpdateAutopostingBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.update_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_id": autoposting_id}
        ) as span:
            try:
                self.logger.info("Update autoposting request", {
                    "autoposting_id": autoposting_id
                })

                await self.publication_service.update_autoposting(
                    autoposting_id=autoposting_id,
                    autoposting_category_id=body.autoposting_category_id,
                    period_in_hours=body.period_in_hours,
                    filter_prompt=body.filter_prompt,
                    enabled=body.enabled,
                    tg_channels=body.tg_channels,
                    required_moderation=body.required_moderation,
                    need_image=body.need_image
                )

                self.logger.info("Autoposting updated successfully", {
                    "autoposting_id": autoposting_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Autoposting updated successfully",
                        "autoposting_id": autoposting_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_autoposting(self, autoposting_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.delete_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_id": autoposting_id}
        ) as span:
            try:
                self.logger.info("Delete autoposting request", {
                    "autoposting_id": autoposting_id
                })

                await self.publication_service.delete_autoposting(autoposting_id)

                self.logger.info("Autoposting deleted successfully", {
                    "autoposting_id": autoposting_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Autoposting deleted successfully",
                        "autoposting_id": autoposting_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def transcribe_audio(
            self,
            organization_id: int = Form(...),
            audio_file: UploadFile = File(...),
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.transcribe_audio",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                text = await self.publication_service.transcribe_audio(audio_file, organization_id)

                return JSONResponse(
                    content={"text": text},
                    status_code=200
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
