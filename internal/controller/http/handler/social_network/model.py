from pydantic import BaseModel


# МОДЕЛИ ДЛЯ СОЦИАЛЬНЫХ СЕТЕЙ
class CreateSocialNetworkBody(BaseModel):
    organization_id: int
    channel_username: str