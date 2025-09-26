from dataclasses import dataclass
from datetime import datetime


@dataclass
class YouTube:
    id: int
    organization_id: int
    autoselect: bool

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list['YouTube']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
                autoselect=row.autoselect,
                created_at=row.created_at,
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "autoselect": self.autoselect,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class Instagram:
    id: int
    organization_id: int
    autoselect: bool

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list['Instagram']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
                autoselect=row.autoselect,
                created_at=row.created_at,
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "autoselect": self.autoselect,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class Telegram:
    id: int
    organization_id: int
    autoselect: bool
    tg_channel_username: str

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list['Telegram']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
                autoselect=row.autoselect,
                tg_channel_username=row.tg_channel_username,
                created_at=row.created_at,
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "autoselect": self.autoselect,
            "tg_channel_username": self.tg_channel_username,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class Vkontakte:
    id: int
    organization_id: int
    autoselect: bool

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list['Vkontakte']:
        return [
            cls(
                id=row.id,
                organization_id=row.organization_id,
                autoselect=row.autoselect,
                created_at=row.created_at,
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "autoselect": self.autoselect,
            "created_at": self.created_at.isoformat()
        }