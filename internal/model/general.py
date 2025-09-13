from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel


@dataclass
class OpenAICostInfo:
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    model: str


@dataclass
class OpenAITranscriptionCostInfo:
    duration_minutes: float
    cost_per_minute: float
    total_cost: float
    model: str


@dataclass
class OpenAITTSCostInfo:
    character_count: int
    cost_per_1k_chars: float
    total_cost: float
    model: str
    voice: str


@dataclass
class OpenAIImageGenerationInfo:
    model: str
    size: str
    quality: str
    style: str
    cost_per_image: float
    total_cost: float
    image_count: int


@dataclass
class AsyncWeedOperationResponse:
    status_code: int
    content: bytes
    content_type: str
    headers: dict
    fid: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None


class AuthorizationData(BaseModel):
    account_id: int
    message: str
    code: int


class JWTTokens(BaseModel):
    access_token: str
    refresh_token: str
