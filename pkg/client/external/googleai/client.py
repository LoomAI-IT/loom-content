from io import BytesIO
import base64
from typing import Optional

import httpx
from PIL import Image
from opentelemetry.trace import SpanKind

from internal import interface
from internal.common.error import ErrNoImageData
from pkg.trace_wrapper import traced_method


class GoogleAIClient(interface.GoogleAIClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            api_key: str,
            proxy: str = None,
    ):
        self.logger = tel.logger()
        self.tracer = tel.tracer()
        self.api_key = api_key

        if proxy:
            transport = httpx.AsyncHTTPTransport(proxy=proxy)
            self.http_client = httpx.AsyncClient(
                transport=transport,
                timeout=900,
                headers={
                    "Content-Type": "application/json"
                }
            )
        else:
            self.http_client = httpx.AsyncClient(
                timeout=900,
                headers={
                    "Content-Type": "application/json"
                }
            )

        self.model_name = "gemini-3-pro-image-preview"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def close(self):
        """Закрытие HTTP клиента"""
        await self.http_client.aclose()

    def _image_to_base64(self, image_data: bytes) -> tuple[str, str]:
        """Конвертация изображения в base64 и определение mime-type"""
        image = Image.open(BytesIO(image_data))

        format_to_mime = {
            'PNG': 'image/png',
            'JPEG': 'image/jpeg',
            'JPG': 'image/jpeg',
            'WEBP': 'image/webp',
            'GIF': 'image/gif'
        }
        mime_type = format_to_mime.get(image.format, 'image/jpeg')
        base64_image = base64.b64encode(image_data).decode('utf-8')

        return base64_image, mime_type

    def _calculate_cost(self, result: dict, input_images_count: int = 0) -> dict:
        usage = result.get('usageMetadata', {})
        self.logger.debug("Gemini usage", {"usage": str(usage)})

        # Input text: $2/1M tokens
        input_text_tokens = 0
        for detail in usage.get('promptTokensDetails', []):
            if detail.get('modality') == 'TEXT':
                input_text_tokens = detail.get('tokenCount', 0)
        input_text_cost = input_text_tokens / 1_000_000 * 2.00

        # Input images: $0.067/image
        input_images_cost = input_images_count * 0.067

        # Output text/thinking: $12/1M tokens
        thoughts_tokens = usage.get('thoughtsTokenCount', 0)
        output_text_cost = thoughts_tokens / 1_000_000 * 12.00

        output_images_cost = 0.134

        total_cost = round(input_text_cost + input_images_cost + output_text_cost + output_images_cost, 6)
        self.logger.debug("Gemini cost", {"total_cost": f"${total_cost}"})

        return {"total_cost": total_cost}

    async def _generate_content(
            self,
            parts: list,
            aspect_ratio: Optional[str] = None,
            response_modalities: Optional[list[str]] = None,
            input_images_count: int = 0
    ) -> tuple[bytes, dict]:
        """Базовый метод для генерации контента"""
        payload: dict = {
            "contents": [{"parts": parts}]
        }

        config = {}
        if aspect_ratio:
            config['imageConfig'] = {
                'aspectRatio': aspect_ratio,
                "imageSize": "2K"
            }
        if response_modalities:
            config['responseModalities'] = response_modalities
        if config:
            payload['generationConfig'] = config

        url = f"{self.base_url}/models/{self.model_name}:generateContent"
        response = await self.http_client.post(
            url,
            json=payload,
            headers={"x-goog-api-key": self.api_key}
        )
        response.raise_for_status()

        result = response.json()

        result_image_data = None

        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                for part in candidate['content']['parts']:
                    if 'inlineData' in part:
                        result_image_data = base64.b64decode(part['inlineData']['data'])
                        break

        if result_image_data is None:
            self.logger.warning("Ответ Gemini без изображения", result)
            raise ErrNoImageData()

        return result_image_data, self._calculate_cost(result, input_images_count)

    @traced_method(SpanKind.CLIENT)
    async def edit_image(
            self,
            image_data: bytes,
            prompt: str,
            aspect_ratio: str = None,
            response_modalities: list[str] = None
    ) -> tuple[bytes, dict]:
        base64_image, mime_type = self._image_to_base64(image_data)
        parts = [
            {"text": prompt},
            {"inline_data": {"mime_type": mime_type, "data": base64_image}}
        ]
        return await self._generate_content(parts, aspect_ratio, response_modalities, input_images_count=1)

    @traced_method(SpanKind.CLIENT)
    async def combine_images(
            self,
            images_data: list[bytes],
            prompt: str,
            aspect_ratio: str = None,
            response_modalities: list[str] = None
    ) -> tuple[bytes, dict]:
        if len(images_data) > 14:
            raise ValueError("Maximum 14 images supported for best performance")

        parts: list = [{"text": prompt}]
        for img_data in images_data:
            base64_image, mime_type = self._image_to_base64(img_data)
            parts.append({"inline_data": {"mime_type": mime_type, "data": base64_image}})

        return await self._generate_content(parts, aspect_ratio, response_modalities, input_images_count=len(images_data))

    @traced_method(SpanKind.CLIENT)
    async def generate_image(
            self,
            prompt: str,
            aspect_ratio: str = None,
            response_modalities: list[str] = None
    ) -> tuple[bytes, dict]:
        parts = [{"text": prompt}]
        return await self._generate_content(
            parts,
            aspect_ratio,
            response_modalities or ["TEXT", "IMAGE"]
        )
