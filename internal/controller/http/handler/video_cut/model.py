from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# НАРЕЗКА ВИДЕО
class GenerateVizardVideoCutsBody(BaseModel):
    organization_id: int
    creator_id: int
    youtube_video_reference: str


class Video(BaseModel):
    viralScore: str
    relatedTopic: str
    transcript: str
    videoUrl: str
    clipEditorUrl: str
    videoMsDuration: int
    videoId: int
    title: str
    viralReason: str


class CreateVizardVideoCutsBody(BaseModel):
    code: int
    videos: list[Video]
    projectId: int
    creditsUsed: int


class ChangeVideoCutBody(BaseModel):
    video_cut_id: int
    name: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    inst_source: bool | None = None
    youtube_source: bool | None = None


class ModerateVideoCutBody(BaseModel):
    moderator_id: int
    moderation_status: str
    moderation_comment: Optional[str] = ""
