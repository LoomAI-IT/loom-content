from fastapi import Form, UploadFile, File

from fastapi.responses import JSONResponse, StreamingResponse

from internal import interface, common
from internal.controller.http.handler.publication.model import *
from pkg.log_wrapper import auto_log
from pkg.trace_wrapper import traced_method


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

    @auto_log()
    @traced_method()
    async def generate_publication_text(
            self,
            body: GeneratePublicationTextBody,
    ) -> JSONResponse:
        try:
            text_data = await self.publication_service.generate_publication_text(
                category_id=body.category_id,
                text_reference=body.text_reference
            )
            return JSONResponse(
                status_code=200,
                content=text_data
            )
        except common.ErrInsufficientBalance:
            return JSONResponse(
                status_code=400,
                content={
                    "status_code": common.StatusCode.InsufficientBalance,
                }
            )

    @auto_log()
    @traced_method()
    async def regenerate_publication_text(
            self,
            body: RegeneratePublicationTextBody,
    ) -> JSONResponse:
        try:
            text_data = await self.publication_service.regenerate_publication_text(
                category_id=body.category_id,
                publication_text=body.publication_text,
                prompt=body.prompt
            )

            return JSONResponse(
                status_code=200,
                content=text_data
            )
        except common.ErrInsufficientBalance:
            return JSONResponse(
                status_code=400,
                content={
                    "status_code": common.StatusCode.InsufficientBalance,
                }
            )

    @auto_log()
    @traced_method()
    async def generate_publication_image(
            self,
            category_id: int = Form(...),
            publication_text: str = Form(...),
            text_reference: str = Form(...),
            prompt: str | None = Form(None),
            image_file: UploadFile = File(None),
    ) -> JSONResponse:
        try:
            images_url = await self.publication_service.generate_publication_image(
                category_id=category_id,
                publication_text=publication_text,
                text_reference=text_reference,
                prompt=prompt,
                image_file=image_file,
            )

            return JSONResponse(
                status_code=200,
                content=images_url
            )
        except common.ErrInsufficientBalance:
            return JSONResponse(
                status_code=400,
                content={
                    "status_code": common.StatusCode.InsufficientBalance,
                }
            )

    @auto_log()
    @traced_method()
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
        return JSONResponse(
            status_code=201,
            content={
                "publication_id": publication_id
            }
        )

    @auto_log()
    @traced_method()
    async def change_publication(
            self,
            publication_id: int,
            vk_source: bool = Form(None),
            tg_source: bool = Form(None),
            text: str = Form(None),
            image_url: str = Form(None),
            image_file: UploadFile = File(None),
    ) -> JSONResponse:
        await self.publication_service.change_publication(
            publication_id=publication_id,
            vk_source=vk_source,
            tg_source=tg_source,
            text=text,
            image_url=image_url,
            image_file=image_file,
        )

        return JSONResponse(
            status_code=200,
            content={
                "publication_id": publication_id
            }
        )

    @auto_log()
    @traced_method()
    async def delete_publication_image(
            self,
            publication_id: int,
    ):
        await self.publication_service.delete_publication_image(
            publication_id=publication_id
        )
        return JSONResponse(
            status_code=200,
            content={
                "publication_id": publication_id
            }
        )

    @auto_log()
    @traced_method()
    async def send_publication_to_moderation(
            self,
            publication_id: int,
    ):
        await self.publication_service.send_publication_to_moderation(
            publication_id=publication_id
        )
        return JSONResponse(
            status_code=200,
            content={
                "publication_id": publication_id
            }
        )

    @auto_log()
    @traced_method()
    async def moderate_publication(
            self,
            body: ModeratePublicationBody
    ) -> JSONResponse:
        post_links = await self.publication_service.moderate_publication(
            publication_id=body.publication_id,
            moderator_id=body.moderator_id,
            moderation_status=body.moderation_status,
            moderation_comment=body.moderation_comment
        )
        return JSONResponse(
            status_code=200,
            content=post_links
        )

    @auto_log()
    @traced_method()
    async def get_publication_by_id(self, publication_id: int) -> JSONResponse:
        publication = await self.publication_service.get_publication_by_id(publication_id)
        return JSONResponse(
            status_code=200,
            content=publication.to_dict()
        )

    @auto_log()
    @traced_method()
    async def get_publications_by_organization(self, organization_id: int) -> JSONResponse:
        publications = await self.publication_service.get_publications_by_organization(organization_id)
        return JSONResponse(
            status_code=200,
            content=[publication.to_dict() for publication in publications]
        )

    @auto_log()
    @traced_method()
    async def download_publication_image(
            self,
            publication_id: int
    ) -> StreamingResponse:
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

        return StreamingResponse(
            iterfile(),
            media_type=content_type or "image/png",
            headers={
                "Content-Disposition": f"attachment; filename=publication_{publication_id}_image.png"
            }
        )

    @auto_log()
    @traced_method()
    async def download_other_image(
            self,
            image_fid: str,
            image_name: str
    ) -> StreamingResponse:
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

        return StreamingResponse(
            iterfile(),
            media_type=content_type or "image/png",
            headers={
                "Content-Disposition": f"attachment; filename={image_name}"
            }
        )

    @auto_log()
    @traced_method()
    async def delete_publication(
            self,
            publication_id: int,
    ) -> JSONResponse:
        await self.publication_service.delete_publication(
            publication_id=publication_id
        )

        return JSONResponse(
            status_code=200,
            content={
                "publication_id": publication_id
            }
        )

    # РУБРИКИ

    @auto_log()
    @traced_method()
    async def create_category(
            self,
            body: CreateCategoryBody,
    ) -> JSONResponse:
        category_id = await self.publication_service.create_category(
            organization_id=body.organization_id,
            name=body.name,
            goal=body.goal,
            tone_of_voice=body.tone_of_voice,
            brand_rules=body.brand_rules,
            structure_variations=body.structure_variations,
            creativity_level=body.creativity_level,
            audience_segments=body.audience_segments,
            len_min=body.len_min,
            len_max=body.len_max,
            n_hashtags_min=body.n_hashtags_min,
            n_hashtags_max=body.n_hashtags_max,
            cta_type=body.cta_type,
            cta_strategy=body.cta_strategy,
            good_samples=body.good_samples,
            bad_samples=body.bad_samples,
            additional_info=body.additional_info,
            prompt_for_image_style=body.prompt_for_image_style
        )
        return JSONResponse(
            status_code=201,
            content={
                "category_id": category_id
            }
        )

    @auto_log()
    @traced_method()
    async def get_category_by_id(self, category_id: int) -> JSONResponse:
        category = await self.publication_service.get_category_by_id(category_id)
        return JSONResponse(
            status_code=200,
            content=category.to_dict()
        )

    @auto_log()
    @traced_method()
    async def get_categories_by_organization(self, organization_id: int) -> JSONResponse:
        categories = await self.publication_service.get_categories_by_organization(organization_id)
        return JSONResponse(
            status_code=200,
            content=[category.to_dict() for category in categories]
        )

    @auto_log()
    @traced_method()
    async def update_category(
            self,
            category_id: int,
            body: UpdateCategoryBody
    ) -> JSONResponse:
        await self.publication_service.update_category(
            category_id=category_id,
            name=body.name,
            goal=body.goal,
            tone_of_voice=body.tone_of_voice,
            brand_rules=body.brand_rules,
            structure_variations=body.structure_variations,
            creativity_level=body.creativity_level,
            audience_segments=body.audience_segments,
            len_min=body.len_min,
            len_max=body.len_max,
            n_hashtags_min=body.n_hashtags_min,
            n_hashtags_max=body.n_hashtags_max,
            cta_type=body.cta_type,
            cta_strategy=body.cta_strategy,
            good_samples=body.good_samples,
            bad_samples=body.bad_samples,
            additional_info=body.additional_info,
            prompt_for_image_style=body.prompt_for_image_style
        )
        return JSONResponse(
            status_code=200,
            content={
                "category_id": category_id
            }
        )

    @auto_log()
    @traced_method()
    async def delete_category(self, category_id: int) -> JSONResponse:
        await self.publication_service.delete_category(category_id)
        return JSONResponse(
            status_code=200,
            content={
                "category_id": category_id
            }
        )

    # РУБРИКИ ДЛЯ АВТОПОСТИНГА
    @auto_log()
    @traced_method()
    async def create_autoposting_category(
            self,
            body: CreateAutopostingCategoryBody,
    ) -> JSONResponse:
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

        return JSONResponse(
            status_code=201,
            content={
                "autoposting_category_id": autoposting_category_id
            }
        )

    @auto_log()
    @traced_method()
    async def get_autoposting_category_by_id(self, autoposting_category_id: int) -> JSONResponse:
        category = await self.publication_service.get_autoposting_category_by_id(autoposting_category_id)
        return JSONResponse(
            status_code=200,
            content=category.to_dict()
        )

    @auto_log()
    @traced_method()
    async def update_autoposting_category(
            self,
            autoposting_category_id: int,
            body: UpdateAutopostingCategoryBody
    ) -> JSONResponse:
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
        return JSONResponse(
            status_code=200,
            content={
                "autoposting_category_id": autoposting_category_id
            }
        )

    # АВТОПОСТИНГ

    @auto_log()
    @traced_method()
    async def create_autoposting(
            self,
            body: CreateAutopostingBody
    ) -> JSONResponse:
        autoposting_id = await self.publication_service.create_autoposting(
            organization_id=body.organization_id,
            autoposting_category_id=body.autoposting_category_id,
            period_in_hours=body.period_in_hours,
            filter_prompt=body.filter_prompt,
            tg_channels=body.tg_channels or [],
            required_moderation=body.required_moderation,
            need_image=body.need_image
        )
        return JSONResponse(
            status_code=201,
            content={
                "autoposting_id": autoposting_id
            }
        )

    @auto_log()
    @traced_method()
    async def get_autoposting_by_organization(self, organization_id: int) -> JSONResponse:
        autopostings = await self.publication_service.get_autoposting_by_organization(organization_id)
        return JSONResponse(
            status_code=200,
            content={
                "autopostings": [autoposting.to_dict() for autoposting in autopostings]
            }
        )

    @auto_log()
    @traced_method()
    async def update_autoposting(
            self,
            autoposting_id: int,
            body: UpdateAutopostingBody
    ) -> JSONResponse:
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
        return JSONResponse(
            status_code=200,
            content={
                "autoposting_id": autoposting_id
            }
        )

    @auto_log()
    @traced_method()
    async def delete_autoposting(self, autoposting_id: int) -> JSONResponse:
        await self.publication_service.delete_autoposting(autoposting_id)
        return JSONResponse(
            status_code=200,
            content={
                "autoposting_id": autoposting_id
            }
        )

    @auto_log()
    @traced_method()
    async def transcribe_audio(
            self,
            organization_id: int = Form(...),
            audio_file: UploadFile = File(...),
    ) -> JSONResponse:
        try:
            text = await self.publication_service.transcribe_audio(audio_file, organization_id)

            return JSONResponse(
                content={"text": text},
                status_code=200
            )
        except common.ErrInsufficientBalance:
            return JSONResponse(
                status_code=400,
                content={
                    "status_code": common.StatusCode.InsufficientBalance,
                }
            )
