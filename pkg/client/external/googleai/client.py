from io import BytesIO
import base64
from typing import Optional

import httpx
from PIL import Image
from opentelemetry.trace import SpanKind

from internal import interface
from pkg.trace_wrapper import traced_method


class GoogleAIClient(interface.GoogleAIClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            api_key: str,
    ):
        self.logger = tel.logger()
        self.tracer = tel.tracer()
        self.api_key = api_key

        # Настройка прокси
        transport = httpx.AsyncHTTPTransport(proxy="http://user331580:52876b@163.5.189.163:2667")
        self.http_client = httpx.AsyncClient(
            transport=transport,
            timeout=120.0,
            headers={
                "Content-Type": "application/json"
            }
        )

        self.model_name = "gemini-2.5-flash-image"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def close(self):
        """Закрытие HTTP клиента"""
        await self.http_client.aclose()

    def _image_to_base64(self, image_data: bytes) -> tuple[str, str]:
        """Конвертация изображения в base64 и определение mime-type"""
        image = Image.open(BytesIO(image_data))

        # Определяем mime-type
        format_to_mime = {
            'PNG': 'image/png',
            'JPEG': 'image/jpeg',
            'JPG': 'image/jpeg',
            'WEBP': 'image/webp',
            'GIF': 'image/gif'
        }
        mime_type = format_to_mime.get(image.format, 'image/jpeg')

        # Конвертируем в base64
        base64_image = base64.b64encode(image_data).decode('utf-8')

        return base64_image, mime_type

    def _build_generation_config(
            self,
            aspect_ratio: Optional[str] = None,
            response_modalities: Optional[list[str]] = None
    ) -> dict:
        """Построение конфигурации генерации"""
        config = {}

        if aspect_ratio:
            config['imageConfig'] = {
                'aspectRatio': aspect_ratio
            }

        if response_modalities:
            config['responseModalities'] = response_modalities

        return config

    @traced_method(SpanKind.CLIENT)
    async def edit_image(
            self,
            image_data: bytes,
            prompt: str,
            aspect_ratio: str = None,
            response_modalities: list[str] = None
    ) -> tuple[bytes, str]:
        try:
            # Конвертируем изображение в base64
            base64_image, mime_type = self._image_to_base64(image_data)

            # Формируем запрос (сначала текст, потом изображение)
            parts = [
                {
                    "text": prompt
                },
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64_image
                    }
                }
            ]

            payload: dict = {
                "contents": [
                    {
                        "parts": parts
                    }
                ]
            }

            # Добавляем конфигурацию генерации если есть
            generation_config = self._build_generation_config(aspect_ratio, response_modalities)
            if generation_config:
                payload['generationConfig'] = generation_config

            # Отправляем запрос
            url = f"{self.base_url}/models/{self.model_name}:generateContent"
            response = await self.http_client.post(
                url,
                json=payload,
                headers={
                    "x-goog-api-key": self.api_key
                }
            )
            response.raise_for_status()

            # Парсим ответ
            result = response.json()

            result_image_data = None
            result_text = None

            # Извлекаем данные из ответа
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    for part in candidate['content']['parts']:
                        if 'text' in part:
                            result_text = part['text']
                        elif 'inlineData' in part:
                            result_image_data = base64.b64decode(part['inlineData']['data'])

            if result_image_data is None:
                self.logger.warning("Ответ Gemini", result)
                result_image_data = image_data

            return result_image_data, result_text

        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Error in edit_image: {str(e)}")
            raise

    @traced_method(SpanKind.CLIENT)
    async def combine_images(
            self,
            images_data: list[bytes],
            prompt: str,
            aspect_ratio: str = None,
            response_modalities: list[str] = None
    ) -> tuple[bytes, str]:
        try:
            if len(images_data) > 3:
                raise ValueError("Maximum 3 images supported for best performance")

            # Сначала добавляем текстовый промпт
            parts: list = [
                {
                    "text": prompt
                }
            ]

            # Затем добавляем все изображения
            for img_data in images_data:
                base64_image, mime_type = self._image_to_base64(img_data)
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64_image
                    }
                })

            payload: dict = {
                "contents": [
                    {
                        "parts": parts
                    }
                ]
            }

            # Добавляем конфигурацию генерации если есть
            generation_config = self._build_generation_config(aspect_ratio, response_modalities)
            if generation_config:
                payload['generationConfig'] = generation_config

            # Отправляем запрос
            url = f"{self.base_url}/models/{self.model_name}:generateContent"
            response = await self.http_client.post(
                url,
                json=payload,
                headers={
                    "x-goog-api-key": self.api_key
                }
            )
            response.raise_for_status()

            # Парсим ответ
            result = response.json()

            result_image_data = None
            result_text = None

            # Извлекаем данные из ответа
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    for part in candidate['content']['parts']:
                        if 'text' in part:
                            result_text = part['text']
                        elif 'inlineData' in part:
                            result_image_data = base64.b64decode(part['inlineData']['data'])

            if result_image_data is None:
                self.logger.warning("Ответ Gemini", result)
                result_image_data = images_data[0]

            return result_image_data, result_text

        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Error in combine_images: {str(e)}")
            raise