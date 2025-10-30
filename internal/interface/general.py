import io
from abc import abstractmethod
from typing import Protocol, Sequence, Any, Literal

from fastapi import FastAPI
from opentelemetry.metrics import Meter
from opentelemetry.trace import Tracer

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
    def logger_middleware02(self, app: FastAPI): pass

    @abstractmethod
    def authorization_middleware03(self, app: FastAPI): pass


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


class GoogleAIClient(Protocol):
    @abstractmethod
    async def edit_image(
            self,
            image_data: bytes,
            prompt: str,
            aspect_ratio: str = None,
            response_modalities: list[str] = None
    ) -> tuple[bytes, str]: pass

    @abstractmethod
    async def combine_images(
            self,
            images_data: list[bytes],
            prompt: str,
            aspect_ratio: str = None,
            response_modalities: list[str] = None
    ) -> tuple[bytes, str]: pass


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
            video_type: int,
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


class IAnthropicClient(Protocol):
    @abstractmethod
    async def generate_str(
            self,
            history: list,
            system_prompt: str,
            temperature: float = 1.0,
            llm_model: str = "claude-haiku-4-5",
            max_tokens: int = 4096,
            thinking_tokens: int = None,
            enable_caching: bool = True,
            cache_ttl: str = "5m",
            enable_web_search: bool = True,
            max_searches: int = 5,
            images: list[bytes] = None,
    ) -> tuple[str, dict]: pass

    @abstractmethod
    async def generate_json(
            self,
            history: list,
            system_prompt: str,
            temperature: float = 1.0,
            llm_model: str = "claude-haiku-4-5",
            max_tokens: int = 4096,
            thinking_tokens: int = None,
            enable_caching: bool = True,
            cache_ttl: str = "5m",
            enable_web_search: bool = True,
            max_searches: int = 5,
            images: list[bytes] = None,
    ) -> tuple[dict, dict]: pass


class IOpenAIClient(Protocol):
    @abstractmethod
    async def generate_str(
            self,
            history: list,
            system_prompt: str,
            temperature: float,
            llm_model: str,
            pdf_file: bytes = None,
    ) -> tuple[str, dict]: pass

    @abstractmethod
    async def generate_json(
            self,
            history: list,
            system_prompt: str,
            temperature: float,
            llm_model: str,
            pdf_file: bytes = None,
    ) -> tuple[dict, dict]: pass

    @abstractmethod
    async def web_search(
            self,
            query: str,
    ) -> str: pass

    @abstractmethod
    async def transcribe_audio(
            self,
            audio_file: bytes,
            filename: str,
            audio_model: str,
            language: str = None,
            prompt: str = None,
            response_format: Literal["json", "text", "srt", "verbose_json", "vtt"] = "verbose_json",
            temperature: float = None,
            timestamp_granularities: list[Literal["word", "segment"]] = None
    ) -> tuple[str, dict]: pass

    @abstractmethod
    async def generate_image(
            self,
            prompt: str,
            image_model: Literal["dall-e-3", "gpt-image-1"] = "gpt-image-1",
            size: str = None,
            quality: str = None,
            style: Literal["vivid", "natural"] = None,
            n: int = 1,
    ) -> tuple[list[str], dict]: pass

    @abstractmethod
    async def edit_image(
            self,
            image: bytes,
            prompt: str,
            mask: bytes = None,
            quality: str = None,
            image_model: Literal["gpt-image-1"] = "gpt-image-1",
            size: str = None,
            n: int = 1,
    ) -> tuple[list[str], dict]: pass

    @abstractmethod
    async def download_image_from_url(
            self,
            image_url: str
    ) -> bytes: pass
