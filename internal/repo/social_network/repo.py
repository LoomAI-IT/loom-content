from pkg.trace_wrapper import traced_method
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

    @traced_method()
    async def create_youtube(
            self,
            organization_id: int
    ) -> int:
        args = {'organization_id': organization_id}
        youtube_id = await self.db.insert(create_youtube, args)

        return youtube_id

    @traced_method()
    async def create_instagram(
            self,
            organization_id: int
    ) -> int:
        args = {'organization_id': organization_id}
        instagram_id = await self.db.insert(create_instagram, args)

        return instagram_id

    @traced_method()
    async def create_telegram(
            self,
            organization_id: int,
            tg_channel_username: str,
            autoselect: bool,
    ) -> int:
        args = {
            'organization_id': organization_id,
            'tg_channel_username': tg_channel_username,
            'autoselect': autoselect,
        }
        telegram_id = await self.db.insert(create_telegram, args)

        return telegram_id

    @traced_method()
    async def update_telegram(
            self,
            organization_id: int,
            tg_channel_username: str = None,
            autoselect: bool = None,
    ):
        args = {
            'organization_id': organization_id,
            'tg_channel_username': tg_channel_username,
            'autoselect': autoselect,
        }
        await self.db.update(update_telegram, args)

    @traced_method()
    async def delete_telegram(
            self,
            organization_id: int,
    ):
        args = {
            'organization_id': organization_id,
        }
        await self.db.delete(delete_telegram, args)

    @traced_method()
    async def create_vkontakte(
            self,
            organization_id: int
    ) -> int:
        args = {'organization_id': organization_id}
        vkontakte_id = await self.db.insert(create_vkontakte, args)

        return vkontakte_id

    # ПОЛУЧЕНИЕ СОЦИАЛЬНЫХ СЕТЕЙ

    @traced_method()
    async def get_youtubes_by_organization(self, organization_id: int) -> list[model.YouTube]:
        args = {'organization_id': organization_id}
        rows = await self.db.select(get_youtubes_by_organization, args)
        youtubes = model.YouTube.serialize(rows) if rows else []

        return youtubes

    @traced_method()
    async def get_instagrams_by_organization(self, organization_id: int) -> list[model.Instagram]:
        args = {'organization_id': organization_id}
        rows = await self.db.select(get_instagrams_by_organization, args)
        instagrams = model.Instagram.serialize(rows) if rows else []

        return instagrams

    @traced_method()
    async def get_telegrams_by_organization(self, organization_id: int) -> list[model.Telegram]:
        args = {'organization_id': organization_id}
        rows = await self.db.select(get_telegrams_by_organization, args)
        telegrams = model.Telegram.serialize(rows) if rows else []

        return telegrams

    @traced_method()
    async def get_vkontakte_by_organization(self, organization_id: int) -> list[model.Vkontakte]:
        args = {'organization_id': organization_id}
        rows = await self.db.select(get_vkontakte_by_organization, args)
        vkontakte = model.Vkontakte.serialize(rows) if rows else []

        return vkontakte
