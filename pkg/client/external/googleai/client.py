from io import BytesIO

import httpx
from PIL import Image
import google.generativeai as genai
from google.generativeai import GenerationConfig
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

        # Настройка прокси
        transport = httpx.HTTPTransport(proxy="http://user331580:52876b@163.5.189.163:2667")
        http_client = httpx.Client(transport=transport)

        genai.configure(
            api_key=api_key,
            transport="rest",
            client_options={"http_client": http_client}
        )
        self.model_name = "gemini-2.5-flash-image"
        self.model = genai.GenerativeModel(self.model_name)

    @traced_method(SpanKind.CLIENT)
    async def edit_image(
            self,
            image_data: bytes,
            prompt: str,
            aspect_ratio: str = None,
            response_modalities: list[str] = None
    ) -> tuple[bytes, str]:
        try:
            image = Image.open(BytesIO(image_data))

            generation_config = {}
            if aspect_ratio:
                generation_config['image_config'] = {
                    'aspect_ratio': aspect_ratio
                }
            if response_modalities:
                generation_config['response_modalities'] = response_modalities

            generation_config = GenerationConfig(**generation_config) if generation_config else None
            contents = [prompt, image]

            if generation_config:
                response = self.model.generate_content(
                    contents=contents,
                    generation_config=generation_config
                )
            else:
                response = self.model.generate_content(contents=contents)

            result_image_data = None
            result_text = None

            for part in response.parts:
                if hasattr(part, 'text') and part.text:
                    result_text = part.text
                elif hasattr(part, 'inline_data') and part.inline_data:
                    result_image_data = part.inline_data.data

            if result_image_data is None:
                raise ValueError("No image data in response")

            return result_image_data, result_text

        except Exception as e:
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

            images = [Image.open(BytesIO(img_data)) for img_data in images_data]

            generation_config = {}
            if aspect_ratio:
                generation_config['image_config'] = {
                    'aspect_ratio': aspect_ratio
                }
            if response_modalities:
                generation_config['response_modalities'] = response_modalities

            contents = images + [prompt]
            generation_config = GenerationConfig(**generation_config) if generation_config else None

            if generation_config:
                response = self.model.generate_content(
                    contents=contents,
                    generation_config=generation_config
                )
            else:
                response = self.model.generate_content(contents=contents)

            result_image_data = None
            result_text = None

            for part in response.parts:
                if hasattr(part, 'text') and part.text:
                    result_text = part.text
                elif hasattr(part, 'inline_data') and part.inline_data:
                    result_image_data = part.inline_data.data

            if result_image_data is None:
                raise ValueError("No image data in response")

            return result_image_data, result_text

        except Exception as e:
            raise