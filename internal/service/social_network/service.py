from internal import interface
from pkg.trace_wrapper import traced_method


class SocialNetworkService(interface.ISocialNetworkService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            repo: interface.ISocialNetworkRepo,
            telegram_client: interface.ITelegramClient,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.repo = repo
        self.telegram_client = telegram_client

    @traced_method()
    async def create_youtube(
            self,
            organization_id: int
    ) -> int:
        youtube_id = await self.repo.create_youtube(organization_id=organization_id)
        return youtube_id

    @traced_method()
    async def create_instagram(
            self,
            organization_id: int
    ) -> int:
        instagram_id = await self.repo.create_instagram(organization_id=organization_id)
        return instagram_id

    @traced_method()
    async def check_telegram_channel_permission(
            self,
            tg_channel_username: str,
    ) -> bool:
        has_permission = await self.telegram_client.check_permission(tg_channel_username)
        return has_permission

    @traced_method()
    async def create_telegram(
            self,
            organization_id: int,
            tg_channel_username: str,
            autoselect: bool,
    ) -> int:
        telegram_id = await self.repo.create_telegram(organization_id, tg_channel_username, autoselect)
        return telegram_id

    @traced_method()
    async def update_telegram(
            self,
            organization_id: int,
            tg_channel_username: str = None,
            autoselect: bool = None
    ):
        await self.repo.update_telegram(
            organization_id,
            tg_channel_username,
            autoselect
        )

    @traced_method()
    async def delete_telegram(
            self,
            organization_id: int,
    ):
        await self.repo.delete_telegram(organization_id)

    @traced_method()
    async def create_vkontakte(
            self,
            organization_id: int
    ) -> int:
        vkontakte_id = await self.repo.create_vkontakte(organization_id=organization_id)
        return vkontakte_id

    @traced_method()
    async def get_social_networks_by_organization(
            self,
            organization_id: int
    ) -> dict[str, list]:
        youtube_list = await self.repo.get_youtubes_by_organization(organization_id)
        instagram_list = await self.repo.get_instagrams_by_organization(organization_id)
        telegram_list = await self.repo.get_telegrams_by_organization(organization_id)
        vkontakte_list = await self.repo.get_vkontakte_by_organization(organization_id)

        social_networks = {
            "youtube": youtube_list,
            "instagram": instagram_list,
            "telegram": telegram_list,
            "vkontakte": vkontakte_list
        }

        return social_networks
