from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional




@dataclass
class Organization:
    id: int

    name: str
    autoposting_moderation: bool
    video_cut_description_end_sample: str
    publication_text_end_sample: str


    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['Organization']:
        return [
            cls(
                id=row.id,
                name=row.name,
                autoposting_moderation=row.autoposting_moderation,
                created_at=row.created_at
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "autoposting_moderation": self.autoposting_moderation,
            "created_at": self.created_at.isoformat()
        }