from datetime import datetime
from typing import Optional
from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi import Request, HTTPException, UploadFile, Query, Path
from fastapi.responses import JSONResponse, StreamingResponse

from internal import interface, model
from internal.controller.http.handler.publication.model import (
    GeneratePublicationBody, RegeneratePublicationImageBody, RegeneratePublicationTextBody,
    ChangePublicationBody, ModeratePublicationBody, CreateCategoryBody, UpdateCategoryBody,
    CreateAutopostingBody, UpdateAutopostingBody, GenerateVideoCutBody, ChangeVideoCutBody,
    ModerateVideoCutBody
)


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
    async def generate_publication(
            self,
             body: GeneratePublicationBody,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.generate_publication",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": body.organization_id,
                    "category_id": body.category_id,
                    "creator_id": body.creator_id,
                    "need_images": body.need_images
                }
        ) as span:
            try:
                self.logger.info("Generate publication request", {
                    "organization_id": body.organization_id,
                    "category_id": body.category_id,
                    "creator_id": body.creator_id,
                    "need_images": body.need_images
                })

                publication = await self.publication_service.generate_publication(
                    organization_id=body.organization_id,
                    category_id=body.category_id,
                    creator_id=body.creator_id,
                    need_images=body.need_images,
                    text_reference=body.text_reference,
                    time_for_publication=body.time_for_publication
                )

                self.logger.info("Publication generated successfully", {
                    "organization_id": body.organization_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content=publication.to_dict()
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def regenerate_publication_image(
            self,
            body: RegeneratePublicationImageBody,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.regenerate_publication_image",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": body.publication_id}
        ) as span:
            try:
                self.logger.info("Regenerate publication image request", {
                    "publication_id": body.publication_id
                })

                image_io = await self.publication_service.regenerate_publication_image(
                    publication_id=body.publication_id,
                    prompt=body.prompt
                )

                self.logger.info("Publication image regenerated successfully", {
                    "publication_id": body.publication_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Publication image regenerated successfully",
                        "publication_id": body.publication_id
                    }
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
                attributes={"publication_id": body.publication_id}
        ) as span:
            try:
                self.logger.info("Regenerate publication text request", {
                    "publication_id": body.publication_id
                })

                publication_data = await self.publication_service.regenerate_publication_text(
                    publication_id=body.publication_id,
                    prompt=body.prompt
                )

                self.logger.info("Publication text regenerated successfully", {
                    "publication_id": body.publication_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Publication text regenerated successfully",
                        "publication_id": body.publication_id,
                        "data": publication_data
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def change_publication(
            self,
            body: ChangePublicationBody,
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.change_publication",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": body.publication_id}
        ) as span:
            try:
                self.logger.info("Change publication request", {
                    "publication_id": body.publication_id
                })

                await self.publication_service.change_publication(
                    publication_id=body.publication_id,
                    name=body.name,
                    text=body.text,
                    tags=body.tags,
                    time_for_publication=body.time_for_publication,
                    image=body.image
                )

                self.logger.info("Publication changed successfully", {
                    "publication_id": body.publication_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Publication updated successfully",
                        "publication_id": body.publication_id
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
                self.logger.error("Delete publication image failed", {
                    "publication_id": publication_id,
                    "error": str(err)
                })
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
                self.logger.error("Send publication to moderation failed", {
                    "publication_id": publication_id,
                    "error": str(err)
                })
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
                    "moderation_status": body.moderation_status.value
                }
        ) as span:
            try:
                self.logger.info("Moderate publication request", {
                    "publication_id": body.ublication_id,
                    "moderator_id": body.moderator_id,
                    "moderation_status": body.moderation_status.value
                })

                await self.publication_service.moderate_publication(
                    publication_id=body.publication_id,
                    moderator_id=body.moderator_id,
                    moderation_status=body.moderation_status,
                    moderation_comment=body.moderation_comment
                )

                self.logger.info("Publication moderated successfully", {
                    "publication_id": body.publication_id,
                    "moderation_status": body.moderation_status.value
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Publication moderated successfully",
                        "publication_id": body.publication_id,
                        "moderation_status": body.moderation_status.value
                    }
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
                    content={
                        "message": "Publication retrieved successfully",
                        "data": publication.to_dict()
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error("Get publication by ID failed", {
                    "publication_id": publication_id,
                    "error": str(err)
                })
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
                self.logger.error("Get publications by organization failed", {
                    "organization_id": organization_id,
                    "error": str(err)
                })
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
                self.logger.error("Download publication image failed", {
                    "publication_id": publication_id,
                    "error": str(err)
                })
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
                    prompt_for_text_style=body.prompt_for_text_style
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
                    content={
                        "message": "Category retrieved successfully",
                        "data": category.to_dict()
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error("Get category by ID failed", {
                    "category_id": category_id,
                    "error": str(err)
                })
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
                self.logger.error("Get categories by organization failed", {
                    "organization_id": organization_id,
                    "error": str(err)
                })
                raise err

    async def update_category(
            self,
            body: UpdateCategoryBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.update_category",
                kind=SpanKind.INTERNAL,
                attributes={"category_id": body.category_id}
        ) as span:
            try:
                self.logger.info("Update category request", {
                    "category_id": body.category_id
                })

                await self.publication_service.update_category(
                    category_id=body.category_id,
                    name=body.name,
                    prompt_for_image_style=body.prompt_for_image_style,
                    prompt_for_text_style=body.prompt_for_text_style
                )

                self.logger.info("Category updated successfully", {
                    "category_id": body.category_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Category updated successfully",
                        "category_id": body.category_id
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
                self.logger.error("Delete category failed", {
                    "category_id": category_id,
                    "error": str(err)
                })
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
                    filter_prompt=body.filter_prompt,
                    rewrite_prompt=body.rewrite_prompt,
                    tg_channels=body.tg_channels or []
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
                        "data": [autoposting.to_dict() for autoposting in autopostings]
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error("Get autoposting by organization failed", {
                    "organization_id": organization_id,
                    "error": str(err)
                })
                raise err

    async def update_autoposting(
            self,
            body: UpdateAutopostingBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.update_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={"autoposting_id": body.autoposting_id}
        ) as span:
            try:
                self.logger.info("Update autoposting request", {
                    "autoposting_id": body.autoposting_id
                })

                await self.publication_service.update_autoposting(
                    autoposting_id=body.autoposting_id,
                    filter_prompt=body.filter_prompt,
                    rewrite_prompt=body.rewrite_prompt,
                    enabled=body.enabled,
                    tg_channels=body.tg_channels
                )

                self.logger.info("Autoposting updated successfully", {
                    "autoposting_id": body.autoposting_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Autoposting updated successfully",
                        "autoposting_id": body.autoposting_id
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
                self.logger.error("Delete autoposting failed", {
                    "autoposting_id": autoposting_id,
                    "error": str(err)
                })
                raise err

    # НАРЕЗКА
    async def generate_video_cut(
            self,
            body:  GenerateVideoCutBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.generate_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": body.organization_id,
                    "creator_id": body.creator_id,
                    "youtube_video_reference": body.youtube_video_reference
                }
        ) as span:
            try:
                self.logger.info("Generate video cut request", {
                    "organization_id": body.organization_id,
                    "creator_id": body.creator_id,
                    "youtube_video_reference": body.youtube_video_reference
                })

                video_cut_id = await self.publication_service.generate_video_cut(
                    organization_id=body.organization_id,
                    creator_id=body.creator_id,
                    youtube_video_reference=body.youtube_video_reference,
                    time_for_publication=body.time_for_publication
                )

                self.logger.info("Video cut generated successfully", {
                    "video_cut_id": video_cut_id,
                    "organization_id": body.organization_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=201,
                    content={
                        "message": "Video cut generated successfully",
                        "video_cut_id": video_cut_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def change_video_cut(
            self,
            body: ChangeVideoCutBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.change_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": body.video_cut_id}
        ) as span:
            try:
                self.logger.info("Change video cut request", {
                    "video_cut_id": body.video_cut_id
                })

                await self.publication_service.change_video_cut(
                    video_cut_id=body.video_cut_id,
                    name=body.name,
                    description=body.description,
                    tags=body.tags,
                    time_for_publication=body.time_for_publication
                )

                self.logger.info("Video cut changed successfully", {
                    "video_cut_id": body.video_cut_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Video cut updated successfully",
                        "video_cut_id": body.video_cut_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_video_cut_to_moderation(
            self,
            video_cut_id: int,
    ):
        with self.tracer.start_as_current_span(
                "PublicationController.send_video_cut_to_moderation",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                self.logger.info("Send video cut to moderation request", {
                    "video_cut_id": video_cut_id
                })

                await self.publication_service.send_video_cut_to_moderation(
                    video_cut_id=video_cut_id
                )

                self.logger.info("Video cut sent to moderation successfully", {
                    "video_cut_id": video_cut_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Video cut sent to moderation successfully",
                        "video_cut_id": video_cut_id
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error("Send video cut to moderation failed", {
                    "video_cut_id": video_cut_id,
                    "error": str(err)
                })
                raise err

    async def get_video_cut_by_id(self, video_cut_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.get_video_cut_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                self.logger.info("Get video cut by ID request", {
                    "video_cut_id": video_cut_id
                })

                video_cut = await self.publication_service.get_video_cut_by_id(video_cut_id)

                self.logger.info("Video cut retrieved successfully", {
                    "video_cut_id": video_cut_id
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Video cut retrieved successfully",
                        "data": video_cut.to_dict()
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error("Get video cut by ID failed", {
                    "video_cut_id": video_cut_id,
                    "error": str(err)
                })
                raise err

    async def get_video_cuts_by_organization(self, organization_id: int) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.get_video_cuts_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                self.logger.info("Get video cuts by organization request", {
                    "organization_id": organization_id
                })

                video_cuts = await self.publication_service.get_video_cuts_by_organization(organization_id)

                self.logger.info("Video cuts retrieved successfully", {
                    "organization_id": organization_id,
                    "count": len(video_cuts)
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=[video_cut.to_dict() for video_cut in video_cuts]
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error("Get video cuts by organization failed", {
                    "organization_id": organization_id,
                    "error": str(err)
                })
                raise err

    async def moderate_video_cut(
            self,
            body: ModerateVideoCutBody
    ) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.moderate_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={
                    "video_cut_id": body.video_cut_id,
                    "moderator_id": body.moderator_id,
                    "moderation_status": body.moderation_status.value
                }
        ) as span:
            try:
                self.logger.info("Moderate video cut request", {
                    "video_cut_id": body.video_cut_id,
                    "moderator_id": body.moderator_id,
                    "moderation_status": body.moderation_status.value
                })

                await self.publication_service.moderate_video_cut(
                    video_cut_id=body.video_cut_id,
                    moderator_id=body.moderator_id,
                    moderation_status=body.moderation_status,
                    moderation_comment=body.moderation_comment
                )

                self.logger.info("Video cut moderated successfully", {
                    "video_cut_id": body.video_cut_id,
                    "moderation_status": body.moderation_status.value
                })

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Video cut moderated successfully",
                        "video_cut_id": body.video_cut_id,
                        "moderation_status": body.moderation_status.value
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def download_video_cut(
            self,
            video_cut_id: int
    ) -> StreamingResponse:
        with self.tracer.start_as_current_span(
                "PublicationController.download_video_cut",
                kind=SpanKind.INTERNAL,
                attributes={"video_cut_id": video_cut_id}
        ) as span:
            try:
                self.logger.info("Download video cut request", {
                    "video_cut_id": video_cut_id
                })

                video_io, content_type = await self.publication_service.download_video_cut(video_cut_id)

                def iterfile():
                    try:
                        while True:
                            chunk = video_io.read(8192)
                            if not chunk:
                                break
                            yield chunk
                    finally:
                        video_io.close()

                self.logger.info("Video cut downloaded successfully", {
                    "video_cut_id": video_cut_id
                })

                span.set_status(Status(StatusCode.OK))
                return StreamingResponse(
                    iterfile(),
                    media_type=content_type or "video/mp4",
                    headers={
                        "Content-Disposition": f"attachment; filename=video_cut_{video_cut_id}.mp4"
                    }
                )

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error("Download video cut failed", {
                    "video_cut_id": video_cut_id,
                    "error": str(err)
                })
                raise err