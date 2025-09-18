import io
import re
import json
import httpx
import pypdf
import base64
import openai
import tiktoken
import subprocess
from pdf2image import convert_from_bytes
from pathlib import Path

from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import model


class GPTClient(interface.ILLMClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            api_key: str
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self._encoders = {}

        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            http_client=httpx.AsyncClient(proxy="http://32uLYMeQ:jLaDv4WK@193.160.72.227:62940")
        )

    async def generate_str(
            self,
            history: list,
            system_prompt: str,
            temperature: float,
            llm_model: str,
            pdf_file: bytes = None,
    ) -> str:
        with self.tracer.start_as_current_span(
                "GPTClient.generate_str",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                messages = self._prepare_messages(history, system_prompt, pdf_file, llm_model)

                response = await self.client.chat.completions.create(
                    model=llm_model,
                    messages=messages,
                    temperature=temperature,
                )
                print(f"Generate text response: {response=}", flush=True)

                llm_response = response.choices[0].message.content

                span.set_status(Status(StatusCode.OK))
                return llm_response

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    def _prepare_messages(self, history: list, system_prompt: str, pdf_file: bytes, llm_model: str) -> list:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.extend([
            {"role": message["role"], "content": message["content"]}
            for message in history
        ])

        if pdf_file:
            if llm_model in ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4-turbo-preview"]:
                # Vision модели - конвертируем в изображения
                images = self._pdf_to_images(pdf_file)
                content = [{"type": "text", "text": messages[-1]["content"]}]

                for img_base64 in images:
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}",
                            "detail": "high"
                        }
                    })

                messages[-1]["content"] = content
            else:
                # Текстовые модели - извлекаем текст
                pdf_text = self._extract_text_from_pdf(pdf_file)
                messages[-1]["content"] += f"\n\nСодержимое PDF:\n{pdf_text}"

        return messages

    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        with self.tracer.start_as_current_span(
                "GPTClient._extract_text_from_pdf",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    def _pdf_to_images(self, pdf_bytes: bytes) -> list[str]:
        with self.tracer.start_as_current_span(
                "GPTClient._pdf_to_images",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                images = convert_from_bytes(pdf_bytes, dpi=200)
                base64_images = []

                for img in images:
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    img_data = buffer.getvalue()
                    base64_image = base64.b64encode(img_data).decode('utf-8')
                    base64_images.append(base64_image)

                return base64_images
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    def _get_encoder(self, llm_model: str):
        if llm_model not in self._encoders:
            try:
                # Используем cl100k_base для всех современных моделей
                encoding_name = "cl100k_base"
                self._encoders[llm_model] = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                self.logger.warning(f"Не удалось загрузить энкодер для {llm_model}: {e}")
                self._encoders[llm_model] = tiktoken.get_encoding("cl100k_base")

        return self._encoders[llm_model]

    async def generate_json(
            self,
            history: list,
            system_prompt: str,
            temperature: float,
            llm_model: str,
            pdf_file: bytes = None,
    ) -> dict:
        with self.tracer.start_as_current_span(
                "GPTClient.generate_json",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                llm_response_str = await self.generate_str(
                    history, system_prompt, temperature, llm_model, pdf_file
                )

                try:
                    llm_response_json = self.__extract_and_parse_json(llm_response_str)
                except Exception:
                    llm_response_json, retry_cost = await self.__retry_llm_generate(
                        history, llm_model, temperature, llm_response_str
                    )

                span.set_status(Status(StatusCode.OK))
                self.logger.info("Ответ от LLM", {"llm_response_str": llm_response_str})
                return llm_response_json

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    def __extract_and_parse_json(self, text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        json_str = match.group(0)
        data = json.loads(json_str)
        return data

    async def __retry_llm_generate(
            self,
            history: list,
            llm_model: str,
            temperature: float,
            llm_response_str: str,
    ) -> dict:
        self.logger.warning("LLM потребовался retry", {"llm_response": llm_response_str})

        retry_messages = [
            *[{"role": msg["role"], "content": msg["content"]} for msg in history],
            {"role": "assistant", "content": llm_response_str},
            {"role": "user", "content": "Я же просил JSON формат, как в системном промпте, дай ответ в JSON формате"},
        ]

        response = await self.client.chat.completions.create(
            model=llm_model,
            messages=retry_messages,
            temperature=temperature,
        )

        llm_response_str = response.choices[0].message.content
        llm_response_json = self.__extract_and_parse_json(llm_response_str)

        return llm_response_json

    async def transcribe_audio(
            self,
            audio_file: bytes,
            filename: str = "audio.wav"
    ) -> str:
        with self.tracer.start_as_current_span(
                "GPTClient.transcribe_audio",
                kind=SpanKind.CLIENT
        ) as span:
            try:
                audio_buffer = io.BytesIO(audio_file)
                audio_buffer.name = filename

                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_buffer,
                    response_format="text"
                )

                span.set_status(Status(StatusCode.OK))
                return transcript

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def text_to_speech(
            self,
            text: str,
            voice: str = "alloy",
            tts_model: str = "tts-1-hd"
    ) -> bytes:
        with self.tracer.start_as_current_span(
                "GPTClient.text_to_speech",
                kind=SpanKind.CLIENT
        ) as span:
            try:
                response = await self.client.audio.speech.create(
                    model=tts_model,
                    voice=voice,
                    input=text,
                    response_format="mp3",
                    speed=0.85,
                )
                print(f"Generate text fron audio response: {response=}")
                audio_content = response.content
                span.set_status(Status(StatusCode.OK))
                return audio_content

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def generate_image(
            self,
            prompt: str,
            llm_model: str = "dall-e-3",
            size: str = "1024x1024",
            quality: str = "high",
            style: str= "vivid",
            n: int = 1,
            response_format: str = "url",
            user: str = None
    ) -> list[str]:
        with self.tracer.start_as_current_span(
                "GPTClient.generate_image",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                # Валидация параметров
                if llm_model == "dall-e-3":
                    if n != 1:
                        self.logger.warning(
                            "DALL-E 3 поддерживает только n=1. Устанавливаем n=1"
                        )
                        n = 1
                    if size not in ["1024x1024", "1024x1792", "1792x1024"]:
                        raise ValueError(
                            f"Размер {size} не поддерживается для DALL-E 3. "
                            "Используйте: 1024x1024, 1024x1792, 1792x1024"
                        )
                elif llm_model == "dall-e-2":
                    if size not in ["256x256", "512x512", "1024x1024"]:
                        raise ValueError(
                            f"Размер {size} не поддерживается для DALL-E 2. "
                            "Используйте: 256x256, 512x512, 1024x1024"
                        )
                    if n > 10:
                        raise ValueError("DALL-E 2 поддерживает максимум 10 изображений за раз")
                    # DALL-E 2 не поддерживает quality и style
                    quality = None
                    style = None

                # Подготовка параметров запроса
                params = {
                    "model": llm_model,
                    "prompt": prompt,
                    "size": size,
                    "n": n,
                    "response_format": response_format
                }

                if model == "dall-e-3":
                    params["quality"] = quality
                    params["style"] = style
                if model == "gpt-image-1":
                    params["quality"] = style
                if user:
                    params["user"] = user

                # Выполнение запроса
                response = await self.client.images.generate(**params)
                print(f"Image generation response: {response=}", flush=True)

                # Извлечение результатов
                if response_format == "url":
                    images = [img.url for img in response.data]
                else:  # b64_json
                    images = [img.b64_json for img in response.data]

                span.set_status(Status(StatusCode.OK))

                return images

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка при генерации изображения: {err}")
                raise


    async def download_image_from_url(
            self,
            image_url: str
    ) -> bytes:
        with self.tracer.start_as_current_span(
                "GPTClient.download_image_from_url",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url)
                    response.raise_for_status()

                span.set_status(Status(StatusCode.OK))
                return response.content

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise