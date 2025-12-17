from fastapi.responses import JSONResponse

from internal import interface
from internal.controller.http.handler.autoposting.model import *
from pkg.log_wrapper import auto_log
from pkg.trace_wrapper import traced_method


class AutopostingController(interface.IAutopostingController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            autoposting_service: interface.IAutopostingService,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.autoposting_service = autoposting_service

    @auto_log()
    @traced_method()
    async def create_autoposting(
            self,
            body: CreateAutopostingBody
    ) -> JSONResponse:
        autoposting_id = await self.autoposting_service.create_autoposting(
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

    # РУБРИКИ ДЛЯ АВТОПОСТИНГА
    @auto_log()
    @traced_method()
    async def create_autoposting_category(
            self,
            body: CreateAutopostingCategoryBody,
    ) -> JSONResponse:
        autoposting_category_id = await self.autoposting_service.create_autoposting_category(
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
    async def update_autoposting(
            self,
            autoposting_id: int,
            body: UpdateAutopostingBody
    ) -> JSONResponse:
        await self.autoposting_service.update_autoposting(
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
    async def update_autoposting_category(
            self,
            autoposting_category_id: int,
            body: UpdateAutopostingCategoryBody
    ) -> JSONResponse:
        await self.autoposting_service.update_autoposting_category(
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

    @auto_log()
    @traced_method()
    async def get_autoposting_by_organization(self, organization_id: int) -> JSONResponse:
        autopostings = await self.autoposting_service.get_autoposting_by_organization(organization_id)
        return JSONResponse(
            status_code=200,
            content={
                "autopostings": [autoposting.to_dict() for autoposting in autopostings]
            }
        )

    @auto_log()
    @traced_method()
    async def get_autoposting_category_by_id(self, autoposting_category_id: int) -> JSONResponse:
        category = await self.autoposting_service.get_autoposting_category_by_id(autoposting_category_id)
        return JSONResponse(
            status_code=200,
            content=category.to_dict()
        )

    @auto_log()
    @traced_method()
    async def delete_autoposting(self, autoposting_id: int) -> JSONResponse:
        await self.autoposting_service.delete_autoposting(autoposting_id)
        return JSONResponse(
            status_code=200,
            content={
                "autoposting_id": autoposting_id
            }
        )