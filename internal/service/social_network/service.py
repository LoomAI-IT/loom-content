from internal import interface
from pkg.trace_wrapper import traced_method


class SocialNetworkService(interface.ISocialNetworkService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            repo: interface.ISocialNetworkRepo,
            telegram_client: interface.ITelegramClient,
            vk_client = None,
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
        await self.repo.update_vkontakte(
            organization_id=organization_id,
            access_token=access_token,
            refresh_token=refresh_token,
            device_id=device_id,
            user_id=user_id,
            vk_group_id=vk_group_id,
            vk_group_name=vk_group_name
        )

    @traced_method()
    async def process_vk_oauth_callback(
            self,
            code: str,
            device_id: str,
            state_token: str
    ) -> tuple[int, list]:
        # Получаем данные из state
        state_data = self.vk_client.get_state_data(state_token)
        if not state_data:
            raise ValueError("Invalid or expired state token")

        organization_id = state_data.get('organization_id')
        code_verifier = state_data.get('code_verifier')

        if not organization_id or not code_verifier:
            raise ValueError("Missing organization_id or code_verifier in state")

        # Обмениваем код на токены
        token_result = await self.vk_client.exchange_user_code_for_token(
            authorization_code=code,
            code_verifier=code_verifier,
            device_id=device_id,
            state=state_token
        )

        access_token = token_result.get('access_token')
        refresh_token = token_result.get('refresh_token')
        user_id = token_result.get('user_id')

        # Сохраняем токены в БД (без группы пока)
        await self.update_vkontakte(
            organization_id=organization_id,
            access_token=access_token,
            refresh_token=refresh_token,
            device_id=device_id,
            user_id=user_id
        )

        # Получаем список групп пользователя
        groups = await self.vk_client.get_user_groups(
            user_access_token=access_token,
            user_id=user_id
        )

        return organization_id, groups

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
