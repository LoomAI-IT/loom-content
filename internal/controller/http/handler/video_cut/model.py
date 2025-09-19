from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


# НАРЕЗКА ВИДЕО
class GenerateVizardVideoCutsBody(BaseModel):
    organization_id: int
    creator_id: int
    youtube_video_reference: str


class CreateVizardVideoCutsBody(BaseModel):
    project_id: int


class ChangeVideoCutBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    time_for_publication: Optional[datetime] = None


class ModerateVideoCutBody(BaseModel):
    moderator_id: int
    moderation_status: str
    moderation_comment: Optional[str] = ""
