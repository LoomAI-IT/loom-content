from pydantic import BaseModel


# МОДЕЛИ ДЛЯ СОЦИАЛЬНЫХ СЕТЕЙ
class CreateTgBody(BaseModel):
    organization_id: int
    tg_channel_username: str
    autoselect: bool

class UpdateTgBody(BaseModel):
    organization_id: int
    tg_channel_username: str | None = None
    autoselect: bool | None = None


class CreateSocialNetworkBody(BaseModel):
    organization_id: int


class VkSelectGroupBody(BaseModel):
    organization_id: int
    group_id: int
    group_name: str
