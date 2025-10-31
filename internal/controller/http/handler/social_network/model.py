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

# VK МОДЕЛИ
class CreateVkTokenBody(BaseModel):
    access_token: str
    organization_id: int

class SelectVkGroupBody(BaseModel):
    organization_id: int
    vk_group_id: str
    vk_group_name: str

class UpdateVkBody(BaseModel):
    organization_id: int
    vk_group_id: str | None = None
    vk_access_token: str | None = None
    vk_group_name: str | None = None
    vk_group_photo: str | None = None
    autoselect: bool | None = None
