from internal import interface
from pkg.trace_wrapper import traced_method


class SocialNetworkService(interface.ISocialNetworkService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            repo: interface.ISocialNetworkRepo,
            telegram_client: interface.ITelegramClient,
            vk_client: interface.IVkClient,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.repo = repo
        self.telegram_client = telegram_client
        self.vk_client = vk_client

    @traced_method()
    async def create_youtube(
            self,
            organization_id: int
    ) -> int:
        youtube_id = await self.repo.create_youtube(organization_id=organization_id)
        return youtube_id

    @traced_method()
    async def create_vkontakte(
            self,
            organization_id: int,
            access_token: str,
    ) -> None:
        await self.repo.create_vkontakte(
            organization_id,
            access_token,
        )

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
    async def update_vkontakte(
            self,
            organization_id: int,
            vk_group_id: str = None,
            vk_access_token: str = None,
            vk_group_name: str = None,
            autoselect: bool = None
    ) -> None:
        await self.repo.update_vkontakte(
            organization_id=organization_id,
            vk_group_id=vk_group_id,
            vk_access_token=vk_access_token,
            vk_group_name=vk_group_name,
            autoselect=autoselect
        )

    @traced_method()
    async def delete_telegram(
            self,
            organization_id: int,
    ):
        await self.repo.delete_telegram(organization_id)

    @traced_method()
    async def get_vk_groups(
            self,
            organization_id: int
    ) -> list[dict]:
        vkontakte = (await self.repo.get_vkontakte_by_organization(organization_id))[0]

        groups = await self.vk_client.get_user_groups(vkontakte.vk_access_token)

        return groups

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
