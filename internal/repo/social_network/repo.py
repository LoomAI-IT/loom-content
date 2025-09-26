from typing import List
from opentelemetry.trace import Status, StatusCode, SpanKind

from .sql_query import *
from internal import interface, model


class SocialNetworkRepo(interface.ISocialNetworkRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB,
    ):
        self.tracer = tel.tracer()
        self.db = db

    # СОЗДАНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    async def create_youtube(
            self,
            organization_id: int
    ) -> int:
        with self.tracer.start_as_current_span(
                "SocialNetworkRepo.create_youtube",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                args = {'organization_id': organization_id}
                youtube_id = await self.db.insert(create_youtube, args)

                span.set_status(Status(StatusCode.OK))
                return youtube_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_instagram(
            self,
            organization_id: int
    ) -> int:
        with self.tracer.start_as_current_span(
                "SocialNetworkRepo.create_instagram",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                args = {'organization_id': organization_id}
                instagram_id = await self.db.insert(create_instagram, args)

                span.set_status(Status(StatusCode.OK))
                return instagram_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_telegram(
            self,
            organization_id: int,
            channel_username: str,
    ) -> int:
        with self.tracer.start_as_current_span(
                "SocialNetworkRepo.create_telegram",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                args = {
                    'organization_id': organization_id,
                    'channel_username': channel_username,
                }
                telegram_id = await self.db.insert(create_telegram, args)

                span.set_status(Status(StatusCode.OK))
                return telegram_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_vkontakte(
            self,
            organization_id: int
    ) -> int:
        with self.tracer.start_as_current_span(
                "SocialNetworkRepo.create_vkontakte",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                args = {'organization_id': organization_id}
                vkontakte_id = await self.db.insert(create_vkontakte, args)

                span.set_status(Status(StatusCode.OK))
                return vkontakte_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # ПОЛУЧЕНИЕ СОЦИАЛЬНЫХ СЕТЕЙ
    async def get_youtubes_by_organization(self, organization_id: int) -> List[model.YouTube]:
        with self.tracer.start_as_current_span(
                "SocialNetworkRepo.get_youtubes_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                args = {'organization_id': organization_id}
                rows = await self.db.select(get_youtubes_by_organization, args)
                youtubes = model.YouTube.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return youtubes
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_instagrams_by_organization(self, organization_id: int) -> List[model.Instagram]:
        with self.tracer.start_as_current_span(
                "SocialNetworkRepo.get_instagrams_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                args = {'organization_id': organization_id}
                rows = await self.db.select(get_instagrams_by_organization, args)
                instagrams = model.Instagram.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return instagrams
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_telegrams_by_organization(self, organization_id: int) -> List[model.Telegram]:
        with self.tracer.start_as_current_span(
                "SocialNetworkRepo.get_telegrams_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                args = {'organization_id': organization_id}
                rows = await self.db.select(get_telegrams_by_organization, args)
                telegrams = model.Telegram.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return telegrams
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_vkontakte_by_organization(self, organization_id: int) -> List[model.Vkontakte]:
        with self.tracer.start_as_current_span(
                "SocialNetworkRepo.get_vkontakte_by_organization",
                kind=SpanKind.INTERNAL,
                attributes={"organization_id": organization_id}
        ) as span:
            try:
                args = {'organization_id': organization_id}
                rows = await self.db.select(get_vkontakte_by_organization, args)
                vkontakte = model.Vkontakte.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                return vkontakte
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err