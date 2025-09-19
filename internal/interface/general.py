import io
from abc import abstractmethod
from typing import Protocol, Sequence, Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from opentelemetry.metrics import Meter
from opentelemetry.trace import Tracer
from starlette.responses import StreamingResponse

from internal import model


class IOtelLogger(Protocol):
    @abstractmethod
    def debug(self, message: str, fields: dict = None) -> None:
        pass

    @abstractmethod
    def info(self, message: str, fields: dict = None) -> None:
        pass

    @abstractmethod
    def warning(self, message: str, fields: dict = None) -> None:
        pass

    @abstractmethod
    def error(self, message: str, fields: dict = None) -> None:
        pass


class ITelemetry(Protocol):
    @abstractmethod
    def tracer(self) -> Tracer:
        pass

    @abstractmethod
    def meter(self) -> Meter:
        pass

    @abstractmethod
    def logger(self) -> IOtelLogger:
        pass


class IHttpMiddleware(Protocol):
    @abstractmethod
    def trace_middleware01(self, app: FastAPI): pass

    @abstractmethod
    def metrics_middleware02(self, app: FastAPI): pass

    @abstractmethod
    def logger_middleware03(self, app: FastAPI): pass

    @abstractmethod
    def authorization_middleware04(self, app: FastAPI): pass


class IRedis(Protocol):
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None) -> bool: pass

    @abstractmethod
    async def get(self, key: str, default: Any = None) -> Any: pass


class IStorage(Protocol):
    @abstractmethod
    async def delete(self, fid: str, name: str): pass

    @abstractmethod
    async def download(self, fid: str, name: str) -> tuple[io.BytesIO, str]: pass

    @abstractmethod
    async def upload(self, file: io.BytesIO, name: str) -> model.AsyncWeedOperationResponse: pass

    @abstractmethod
    async def update(self, file: io.BytesIO, fid: str, name: str): pass


class IDB(Protocol):

    @abstractmethod
    async def insert(self, query: str, query_params: dict) -> int: pass

    @abstractmethod
    async def delete(self, query: str, query_params: dict) -> None: pass

    @abstractmethod
    async def update(self, query: str, query_params: dict) -> None: pass

    @abstractmethod
    async def select(self, query: str, query_params: dict) -> Sequence[Any]: pass

    @abstractmethod
    async def multi_query(self, queries: list[str]) -> None: pass


class IVizardClient(Protocol):
    @abstractmethod
    def calculate_price(
            self,
            video_duration_minutes: float,
            clips_count: int = None
    ) -> dict: pass

    @abstractmethod
    async def get_project_status(self, project_id: str) -> dict: pass

    @abstractmethod
    async def create_project(
            self,
            video_url: str,
            video_type: str,
            lang: str = "en",
            prefer_length: int = None,
            ratio_of_clip: int = None,
            template_id: int = None,
            remove_silence: bool = False,
            max_clip_number: int = None,
            keywords: str = None,
            subtitle_switch: bool = True,
            emoji_switch: bool = False,
            highlight_switch: bool = False,
            headline_switch: bool = False,
            project_name: str = None,
            webhook_url: str = None
    ) -> dict: pass


class ILLMClient(Protocol):
    @abstractmethod
    async def generate_str(
            self,
            history: list,
            system_prompt: str,
            temperature: float,
            llm_model: str,
            pdf_file: bytes = None,
    ) -> tuple[str, model.OpenAICostInfo]: pass

    @abstractmethod
    async def generate_json(
            self,
            history: list,
            system_prompt: str,
            temperature: float,
            llm_model: str,
            pdf_file: bytes = None,
    ) -> tuple[dict, model.OpenAICostInfo]: pass

    @abstractmethod
    async def transcribe_audio(
            self,
            audio_file: bytes,
            filename: str = "audio.wav"
    ) -> tuple[str, model.OpenAITranscriptionCostInfo]: pass

    @abstractmethod
    async def text_to_speech(
            self,
            text: str,
            voice: str = "alloy",
            tts_model: str = "tts-1-hd"
    ) -> tuple[bytes, model.OpenAITTSCostInfo]: pass

    @abstractmethod
    async def generate_image(
            self,
            prompt: str,
            llm_model: str = "dall-e-3",
            size: str = "1024x1024",
            quality: str = "standard",
            style: str = "vivid",
            n: int = 1,
            response_format: str = "url",
            user: str = None
    ) -> tuple[list[str], model.OpenAIImageGenerationInfo]: pass

    @abstractmethod
    async def edit_image(
            self,
            image: bytes,
            prompt: str,
            mask: bytes = None,
            llm_model: str = "dall-e-2",
            size: str = "1024x1024",
            n: int = 1,
            response_format: str = "url",
            user: str = None
    ) -> tuple[list[str], model.OpenAIImageGenerationInfo]: pass

    @abstractmethod
    async def create_image_variation(
            self,
            image: bytes,
            llm_model: str = "dall-e-2",
            size: str = "1024x1024",
            n: int = 1,
            response_format: str = "url",
            user: str = None
    ) -> tuple[list[str], model.OpenAIImageGenerationInfo]: pass

    @abstractmethod
    async def download_image_from_url(
            self,
            image_url: str
    ) -> bytes: pass