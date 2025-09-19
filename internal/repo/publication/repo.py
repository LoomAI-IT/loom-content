from datetime import datetime
from opentelemetry.trace import Status, StatusCode, SpanKind

from .sql_query import *
from internal import interface, model


class PublicationRepo(interface.IPublicationRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB,
    ):
        self.tracer = tel.tracer()
        self.db = db

    # ПУБЛИКАЦИИ
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
    ) -> int:
        with self.tracer.start_as_current_span(
                "PublicationRepo.create_publication",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id,
                    "category_id": category_id,
                    "creator_id": creator_id
                }
        ) as span:
            try:
                args = {
                    'organization_id': organization_id,
                    'category_id': category_id,
                    'creator_id': creator_id,
                    'text_reference': text_reference,
                    'name': name,
                    'text': text,
                    'tags': tags,
                    'moderation_status': moderation_status,
                }

                publication_id = await self.db.insert(create_publication, args)

                span.set_status(Status(StatusCode.OK))
                return publication_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def change_publication(
            self,
            publication_id: int,
            moderator_id: int = None,
            vk_source: bool = None,
            tg_source: bool = None,
            name: str = None,
            text: str = None,
            tags: list[str] = None,
            moderation_status: str = None,
            moderation_comment: str = None,
            time_for_publication: datetime = None,
            publication_at: datetime = None,
            image_fid: str = None,
            image_name: str = None,
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationRepo.change_publication",
                kind=SpanKind.INTERNAL,
                attributes={
                    "publication_id": publication_id
                }
        ) as span:
            try:
                args = {
                    'publication_id': publication_id,
                    'moderator_id': moderator_id,
                    'vk_source': vk_source,
                    'tg_source': tg_source,
                    'name': name,
                    'text': text,
                    'tags': tags,
                    'moderation_status': moderation_status if moderation_status else None,
                    'moderation_comment': moderation_comment,
                    'time_for_publication': time_for_publication,
                    'publication_at': publication_at,
                    'image_fid': image_fid,
                    'image_name': image_name,
                }

                await self.db.update(change_publication, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_publication(self, publication_id: int) -> None:
        with self.tracer.start_as_current_span(
                "PublicationRepo.delete_publication",
                kind=SpanKind.INTERNAL,
                attributes={"publication_id": publication_id}
        ) as span:
            try:
                args = {'publication_id': publication_id}
                await self.db.delete(delete_publication, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def add_openai_rub_cost_to_publication(
            self,
            publication_id: int,
            amount_rub: int
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationRepo.add_openai_rub_cost_to_publication",
                kind=SpanKind.INTERNAL,
                attributes={
                    "publication_id": publication_id,
                    "amount_rub": amount_rub
                }
        ) as span:
            try:
                args = {
                    'publication_id': publication_id,
                    'amount_rub': amount_rub,
                }

                await self.db.update(add_openai_rub_cost_to_publication, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_publication_by_id(self, publication_id: int) -> list[model.Publication]:
        with self.tracer.start_as_current_span(
                "PublicationRepo.get_publication_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "publication_id": publication_id
                }
        ) as span:
            try:
                args = {'publication_id': publication_id}
                rows = await self.db.select(get_publication_by_id, args)
                publications = model.Publication.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return publications
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_publications_by_organization(self, organization_id: int) -> list[model.Publication]:
        with self.tracer.start_as_current_span(
                "PublicationRepo.get_publications_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id
                }
        ) as span:
            try:
                args = {'organization_id': organization_id}
                rows = await self.db.select(get_publications_by_organization, args)
                publications = model.Publication.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return publications
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
                "PublicationRepo.create_category",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id
                }
        ) as span:
            try:
                args = {
                    'organization_id': organization_id,
                    'name': name,
                    'prompt_for_image_style': prompt_for_image_style,
                    'prompt_for_text_style': prompt_for_text_style,
                }

                category_id = await self.db.insert(create_category, args)

                span.set_status(Status(StatusCode.OK))
                return category_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def update_category(
            self,
            category_id: int,
            name: str = None,
            prompt_for_image_style: str = None,
            prompt_for_text_style: str = None
    ) -> None:
        with self.tracer.start_as_current_span(
                "PublicationRepo.update_category",
                kind=SpanKind.INTERNAL,
                attributes={
                    "category_id": category_id
                }
        ) as span:
            try:
                args = {
                    'category_id': category_id,
                    'name': name,
                    'prompt_for_image_style': prompt_for_image_style,
                    'prompt_for_text_style': prompt_for_text_style,
                }

                await self.db.update(update_category, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_category_by_id(self, category_id: int) -> list[model.Category]:
        with self.tracer.start_as_current_span(
                "PublicationRepo.get_category_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "category_id": category_id
                }
        ) as span:
            try:
                args = {'category_id': category_id}
                rows = await self.db.select(get_category_by_id, args)
                categories = model.Category.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return categories
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_categories_by_organization(self, organization_id: int) -> list[model.Category]:
        with self.tracer.start_as_current_span(
                "PublicationRepo.get_categories_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id
                }
        ) as span:
            try:
                args = {'organization_id': organization_id}
                rows = await self.db.select(get_categories_by_organization, args)
                categories = model.Category.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return categories
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_category(self, category_id: int) -> None:
        with self.tracer.start_as_current_span(
                "PublicationRepo.delete_category",
                kind=SpanKind.INTERNAL,
                attributes={
                    "category_id": category_id
                }
        ) as span:
            try:
                args = {'category_id': category_id}
                await self.db.delete(delete_category, args)

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
                "PublicationRepo.create_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id
                }
        ) as span:
            try:
                args = {
                    'organization_id': organization_id,
                    'filter_prompt': filter_prompt,
                    'rewrite_prompt': rewrite_prompt,
                    'tg_channels': tg_channels or [],
                }

                autoposting_id = await self.db.insert(create_autoposting, args)

                span.set_status(Status(StatusCode.OK))
                return autoposting_id
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
                "PublicationRepo.update_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={
                    "autoposting_id": autoposting_id
                }
        ) as span:
            try:
                args = {
                    'autoposting_id': autoposting_id,
                    'filter_prompt': filter_prompt,
                    'rewrite_prompt': rewrite_prompt,
                    'enabled': enabled,
                    'tg_channels': tg_channels,
                }

                await self.db.update(update_autoposting, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_autoposting_by_organization(self, organization_id: int) -> list[model.Autoposting]:
        with self.tracer.start_as_current_span(
                "PublicationRepo.get_autoposting_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={
                    "organization_id": organization_id
                }
        ) as span:
            try:
                args = {'organization_id': organization_id}
                rows = await self.db.select(get_autoposting_by_organization, args)
                autopostings = model.Autoposting.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return autopostings
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_autoposting(self, autoposting_id: int) -> None:
        with self.tracer.start_as_current_span(
                "PublicationRepo.delete_autoposting",
                kind=SpanKind.INTERNAL,
                attributes={
                    "autoposting_id": autoposting_id
                }
        ) as span:
            try:
                args = {'autoposting_id': autoposting_id}
                await self.db.delete(delete_autoposting, args)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err