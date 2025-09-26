from pydantic import BaseModel


# МОДЕЛИ ДЛЯ СОЦИАЛЬНЫХ СЕТЕЙ
class CreateTgBody(BaseModel):
    organization_id: int
    tg_channel_username: str
    autoselect: bool

class UpdateTgBody(BaseModel):
    organization_id: int
    tg_channel_username: str = None
    autoselect: bool = None


class CreateSocialNetworkBody(BaseModel):
    organization_id: int
