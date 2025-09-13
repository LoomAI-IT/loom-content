import io
import re
import json
import httpx
import pypdf
import base64
import openai
import tiktoken
from datetime import datetime
from pdf2image import convert_from_bytes

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
            http_client=httpx.AsyncClient(proxy="")
        )

        self.PRICING = {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-4-32k": {"input": 60.00, "output": 120.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "gpt-3.5-turbo-16k": {"input": 3.00, "output": 4.00},
            # Whisper
            "whisper-1": {"audio_per_minute": 0.006},
            # TTS
            "tts-1": {"per_1k_chars": 0.015},
            "tts-1-hd": {"per_1k_chars": 0.030},
        }

    async def generate_str(
            self,
            history: list,
            system_prompt: str,
            temperature: float,
            llm_model: str,
            pdf_file: bytes = None,
    ) -> tuple[str, model.OpenAICostInfo]:
        with self.tracer.start_as_current_span(
                "GPTClient.generate_str",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                if system_prompt != "":
                    system_prompt = [{"role": "system", "content": system_prompt}]

                history = [
                    *system_prompt,
                    *[
                        {"role": message.role, "content": message.text}
                        for message in history
                    ]
                ]

                if pdf_file is not None:
                    if llm_model in ["gpt-5", "gpt-4o", "gpt-4o-mini"]:
                        # Подход 1: Конвертируем PDF в изображения (для vision моделей)
                        images = self._pdf_to_images(pdf_file)

                        content = [
                            {"type": "text", "text": history[-1]["content"]}
                        ]

                        # Добавляем каждую страницу как изображение
                        for i, img_base64 in enumerate(images):
                            content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}",
                                    "detail": "high"
                                }
                            })

                        history[-1]["content"] = content
                    else:
                        # Подход 2: Извлекаем текст из PDF
                        pdf_text = self._extract_text_from_pdf(pdf_file)
                        original_text = history[-1]["content"]
                        history[-1]["content"] = f"{original_text}\n\nСодержимое PDF:\n{pdf_text}"

                input_tokens = self._count_tokens(history, llm_model)

                response = await self.client.chat.completions.create(
                    model=llm_model,
                    messages=history,
                    temperature=temperature,
                )
                llm_response = response.choices[0].message.content

                usage = response.usage
                if usage:
                    actual_input_tokens = usage.prompt_tokens
                    output_tokens = usage.completion_tokens
                else:
                    # Fallback на наши подсчеты
                    actual_input_tokens = input_tokens
                    output_tokens = len(self._get_encoder(llm_model).encode(llm_response))

                # Рассчитываем стоимость
                cost_info = self._calculate_cost(actual_input_tokens, output_tokens, llm_model)

                # Логируем информацию о стоимости
                self.logger.info("Стоимость запроса", {
                    "model": llm_model,
                    "input_tokens": cost_info.input_tokens,
                    "output_tokens": cost_info.output_tokens,
                    "total_cost_usd": round(cost_info.total_cost, 6),
                    "input_cost_usd": round(cost_info.input_cost, 6),
                    "output_cost_usd": round(cost_info.output_cost, 6)
                })

                span.set_attributes({
                    "llm.input_tokens": cost_info.input_tokens,
                    "llm.output_tokens": cost_info.output_tokens,
                    "llm.cost_usd": cost_info.total_cost,
                    "llm.model": llm_model
                })

                span.set_status(Status(StatusCode.OK))
                return llm_response, cost_info

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def generate_json(
            self,
            history: list,
            system_prompt: str,
            temperature: float,
            llm_model: str,
            pdf_file: bytes = None,
    ) -> tuple[dict, model.OpenAICostInfo]:
        with self.tracer.start_as_current_span(
                "GPTClient.generate_json",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                # Сначала получаем строковый ответ с информацией о стоимости
                llm_response_str, initial_cost = await self.generate_str(
                    history, system_prompt, temperature, llm_model, pdf_file
                )

                total_cost = initial_cost

                try:
                    llm_response_json = self.__extract_and_parse_json(llm_response_str)
                except Exception as err:
                    llm_response_json, retry_cost = await self.__retry_llm_generate(
                        history,
                        llm_model,
                        temperature,
                        llm_response_str,
                    )

                    total_cost = model.OpenAICostInfo(
                        input_tokens=initial_cost.input_tokens + retry_cost.input_tokens,
                        output_tokens=initial_cost.output_tokens + retry_cost.output_tokens,
                        input_cost=initial_cost.input_cost + retry_cost.input_cost,
                        output_cost=initial_cost.output_cost + retry_cost.output_cost,
                        total_cost=initial_cost.total_cost + retry_cost.total_cost,
                        model=llm_model
                    )

                span.set_status(Status(StatusCode.OK))
                return llm_response_json, total_cost

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def __retry_llm_generate(
            self,
            history: list,
            llm_model: str,
            temperature: float,
            llm_response_str: str,
    ) -> dict:
        self.logger.warning("LLM потребовался retry", {"llm_response": llm_response_str})
        history = [
            *history,
            {"role": "assistant", "content": llm_response_str},
            {"role": "user", "content": "Я же просил JSON формат, как в системно промпте, дай ответ в JSON формате"},
        ]
        response = await self.client.chat.completions.create(
            model=llm_model,
            messages=history,
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
                kind=SpanKind.CLIENT,
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
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                response = await self.client.audio.speech.create(
                    model=tts_model,
                    voice=voice,
                    input=text,
                    response_format="mp3",
                    speed=0.85,
                )

                audio_content = response.content

                span.set_status(Status(StatusCode.OK))
                return audio_content

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        with self.tracer.start_as_current_span(
                "GPTClient._extract_text_from_pdf",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                """Извлекает текст из PDF файла"""
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
                    # Конвертируем PIL Image в base64
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    img_data = buffer.getvalue()
                    base64_image = base64.b64encode(img_data).decode('utf-8')
                    base64_images.append(base64_image)

                return base64_images
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    def __extract_and_parse_json(self, text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)

        json_str = match.group(0)
        data = json.loads(json_str)
        return data

    def _get_encoder(self, llm_model: str):
        if llm_model not in self._encoders:
            try:

                if "gpt-4" in llm_model or "gpt-3.5" in llm_model:
                    encoding_name = "cl100k_base"
                else:
                    encoding_name = "cl100k_base"

                self._encoders[llm_model] = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                self.logger.warning(f"Не удалось загрузить энкодер для {llm_model}: {e}")
                self._encoders[llm_model] = tiktoken.get_encoding("cl100k_base")

        return self._encoders[llm_model]

    def _count_tokens(self, messages: list, llm_model: str) -> int:
        try:
            encoder = self._get_encoder(llm_model)

            # Базовый подсчет токенов для сообщений
            total_tokens = 0

            for message in messages:
                # Каждое сообщение имеет служебные токены
                total_tokens += 4  # для role, content и служебных разделителей

                if isinstance(message.get("content"), str):
                    total_tokens += len(encoder.encode(message["content"]))
                elif isinstance(message.get("content"), list):
                    # Для мультимодальных сообщений (текст + изображения)
                    for content_item in message["content"]:
                        if content_item.get("type") == "text":
                            total_tokens += len(encoder.encode(content_item["text"]))
                        elif content_item.get("type") == "image_url":
                            # Приблизительная оценка токенов для изображения
                            # Это зависит от размера и детализации
                            if content_item.get("image_url", {}).get("detail") == "high":
                                total_tokens += 765  # примерная стоимость high detail изображения
                            else:
                                total_tokens += 85  # примерная стоимость low detail изображения

                total_tokens += len(encoder.encode(message.get("role", "")))

            # Добавляем токены для ответа
            total_tokens += 2

            return total_tokens
        except Exception as e:
            self.logger.warning(f"Ошибка подсчета токенов: {e}")
            return 0

    def _calculate_cost(self, input_tokens: int, output_tokens: int, llm_model: str) -> model.OpenAICostInfo:
        if llm_model not in self.PRICING:
            self.logger.warning(f"Неизвестная модель для расчета стоимости: {llm_model}")
            return model.OpenAICostInfo(input_tokens, output_tokens, 0, 0, 0, llm_model)

        pricing = self.PRICING[llm_model]

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        return model.OpenAICostInfo(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            model=llm_model
        )
