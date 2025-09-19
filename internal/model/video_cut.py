from datetime import datetime
from dataclasses import dataclass
from typing import List

@dataclass
class VideoCut:
    id: int
    project_id: int
    organization_id: int
    creator_id: int
    moderator_id: int

    inst_source_id: int
    youtube_source_id: int

    youtube_video_reference: str
    name: str
    description: str
    tags: list[str]
    video_fid: str
    video_name: str

    vizard_rub_cost: int
    moderation_status: str
    moderation_comment: str

    time_for_publication: datetime
    publication_at: datetime
    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['VideoCut']:
        return [
            cls(
                id=row.id,
                project_id=row.project_id,
                organization_id=row.organization_id,
                creator_id=row.creator_id,
                moderator_id=row.moderator_id,
                inst_source_id=row.inst_source_id,
                youtube_source_id=row.youtube_source_id,
                youtube_video_reference=row.youtube_video_reference,
                name=row.name,
                description=row.description,
                tags=row.tags,
                video_fid=row.video_fid,
                video_name=row.video_name,
                vizard_rub_cost=row.vizard_rub_cost,
                moderation_status=ModerationStatus(row.moderation_status),
                moderation_comment=row.moderation_comment,
                time_for_publication=row.time_for_publication,
                publication_at=row.publication_at,
                created_at=row.created_at
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "organization_id": self.organization_id,
            "creator_id": self.creator_id,
            "moderator_id": self.moderator_id,
            "inst_source_id": self.inst_source_id,
            "youtube_source_id": self.youtube_source_id,
            "youtube_video_reference": self.youtube_video_reference,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "video_fid": self.video_fid,
            "video_name": self.video_name,
            "vizard_rub_cost": self.vizard_rub_cost,
            "moderation_status": self.moderation_status.value,
            "moderation_comment": self.moderation_comment,
            "time_for_publication": self.time_for_publication.isoformat() if self.time_for_publication else None,
            "publication_at": self.publication_at.isoformat() if self.publication_at else None,
            "created_at": self.created_at.isoformat()
        }