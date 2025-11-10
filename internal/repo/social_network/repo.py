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
    async def update_vkontakte(
            self,
            organization_id: int,
            access_token: str = None,
            refresh_token: str = None,
            device_id: str = None,
            user_id: int = None,
            vk_group_id: int = None,
            vk_group_name: str = None
    ):
        args = {
            'organization_id': organization_id,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'device_id': device_id,
            'user_id': user_id,
            'vk_group_id': vk_group_id,
            'vk_group_name': vk_group_name
        }
        await self.db.update(update_vkontakte, args)

    @traced_method()
    async def get_vkontakte_by_id(self, vkontakte_id: int) -> list[model.Vkontakte]:
        args = {'vkontakte_id': vkontakte_id}
        rows = await self.db.select(get_vkontakte_by_id, args)
        if rows:
            rows = model.Vkontakte.serialize(rows)
        return rows

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
