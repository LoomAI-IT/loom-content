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
from typing import Any
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

        self.PRICING = {
            # GPT-4o серия
            "gpt-4o": {"input": 2.50, "output": 10.00, "cached_input": 1.25},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60, "cached_input": 0.075},

            # GPT-4 классические
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-4-32k": {"input": 60.00, "output": 120.00},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "gpt-4-turbo-preview": {"input": 10.00, "output": 30.00},

            # GPT-3.5
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "gpt-3.5-turbo-16k": {"input": 3.00, "output": 4.00},

            # O1 reasoning models
            "o1": {"input": 15.00, "output": 60.00, "cached_input": 7.50},
            "o1-preview": {"input": 15.00, "output": 60.00, "cached_input": 7.50},
            "o1-mini": {"input": 3.00, "output": 12.00, "cached_input": 1.50},

            # O3 серия
            "o3": {"input": 20.00, "output": 80.00, "cached_input": 10.00},
            "o3-mini": {"input": 5.00, "output": 20.00, "cached_input": 2.50},
            "gpt-5": {"input": 20.00, "output": 80.00, "cached_input": 10.00},

            # Audio models - цены в долларах
            "whisper-1": {"per_minute": 0.006},  # $0.006 за минуту
            "tts-1": {"per_1k_chars": 0.015},  # $0.015 за 1000 символов
            "tts-1-hd": {"per_1k_chars": 0.030},  # $0.030 за 1000 символов
            "dall-e-3": {
                "standard": {
                    "1024x1024": 0.040,
                    "1024x1792": 0.080,
                    "1792x1024": 0.080,
                },
                "hd": {
                    "1024x1024": 0.080,
                    "1024x1792": 0.120,
                    "1792x1024": 0.120,
                }
            },
            "gpt-image-1": {
                "input": 5.00,
                "image_input": 10.00,
                "output": 40.00
            },
            # DALL-E 2 pricing (per image)
            "dall-e-2": {
                "1024x1024": 0.020,
                "512x512": 0.018,
                "256x256": 0.016,
            }
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
                messages = self._prepare_messages(history, system_prompt, pdf_file, llm_model)

                response = await self.client.chat.completions.create(
                    model=llm_model,
                    messages=messages,
                    temperature=temperature,
                )

                llm_response = response.choices[0].message.content
                usage_info = response.usage

                cost_info = self._calculate_cost_from_usage(usage_info, llm_model)

                span.set_attributes({
                    "llm.input_tokens": cost_info.input_tokens,
                    "llm.output_tokens": cost_info.output_tokens,
                    "llm.cached_tokens": getattr(cost_info, 'cached_tokens', 0),
                    "llm.reasoning_tokens": getattr(cost_info, 'reasoning_tokens', 0),
                    "llm.cost_usd": cost_info.total_cost,
                    "llm.model": llm_model
                })

                span.set_status(Status(StatusCode.OK))
                return llm_response, cost_info

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

    def _calculate_cost_from_usage(
            self,
            usage: Any,
            llm_model: str
    ) -> model.OpenAICostInfo:
        """
        Расчет стоимости на основе данных usage из API
        Учитывает обычные, кэшированные и reasoning токены
        """
        if not usage:
            return model.OpenAICostInfo(0, 0, 0, 0, 0, llm_model)

        # Извлекаем все типы токенов из response.usage
        input_tokens = getattr(usage, 'prompt_tokens', 0) or getattr(usage, 'input_tokens', 0)
        output_tokens = getattr(usage, 'completion_tokens', 0) or getattr(usage, 'output_tokens', 0)

        # Новые поля для продвинутых моделей
        cached_tokens = 0
        reasoning_tokens = 0

        # Проверяем наличие детальной информации о токенах
        if hasattr(usage, 'input_tokens_details'):
            details = usage.input_tokens_details
            cached_tokens = getattr(details, 'cached_tokens', 0)

        if hasattr(usage, 'output_tokens_details'):
            details = usage.output_tokens_details
            reasoning_tokens = getattr(details, 'reasoning_tokens', 0)

        # Альтернативные названия полей (для совместимости)
        cached_tokens = cached_tokens or getattr(usage, 'input_cached_tokens', 0)

        # Получаем цены для модели
        if llm_model not in self.PRICING:
            self.logger.warning(f"Неизвестная модель для расчета стоимости: {llm_model}")
            return model.OpenAICostInfo(input_tokens, output_tokens, 0, 0, 0, llm_model)

        pricing = self.PRICING[llm_model]

        # Расчет стоимости с учетом кэшированных токенов
        regular_input_tokens = input_tokens - cached_tokens

        input_cost = 0
        if regular_input_tokens > 0:
            input_cost += (regular_input_tokens / 1_000_000) * pricing["input"]

        if cached_tokens > 0 and "cached_input" in pricing:
            # Кэшированные токены со скидкой (обычно 50% для GPT-4o и больше для O1)
            input_cost += (cached_tokens / 1_000_000) * pricing["cached_input"]
        elif cached_tokens > 0:
            # Если нет специальной цены для кэша, используем обычную
            input_cost += (cached_tokens / 1_000_000) * pricing["input"]

        # Output включает reasoning токены (они оплачиваются по той же ставке)
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        total_cost = input_cost + output_cost

        # Создаем расширенный объект с информацией о всех типах токенов
        cost_info = model.OpenAICostInfo(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            model=llm_model
        )

        return cost_info

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
    ) -> tuple[dict, model.OpenAICostInfo]:
        with self.tracer.start_as_current_span(
                "GPTClient.generate_json",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                llm_response_str, initial_cost = await self.generate_str(
                    history, system_prompt, temperature, llm_model, pdf_file
                )

                total_cost = initial_cost

                try:
                    llm_response_json = self.__extract_and_parse_json(llm_response_str)
                except Exception:
                    llm_response_json, retry_cost = await self.__retry_llm_generate(
                        history, llm_model, temperature, llm_response_str
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
    ) -> tuple[dict, model.OpenAICostInfo]:
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

        retry_cost = self._calculate_cost_from_usage(response.usage, llm_model)

        return llm_response_json, retry_cost

    async def transcribe_audio(
            self,
            audio_file: bytes,
            filename: str = "audio.wav"
    ) -> tuple[str, model.OpenAITranscriptionCostInfo]:
        with self.tracer.start_as_current_span(
                "GPTClient.transcribe_audio",
                kind=SpanKind.CLIENT
        ) as span:
            try:
                # Определяем длительность аудио для расчета стоимости
                duration_minutes = self._get_audio_duration(audio_file, filename)

                audio_buffer = io.BytesIO(audio_file)
                audio_buffer.name = filename

                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_buffer,
                    response_format="text"
                )

                cost_per_minute = self.PRICING["whisper-1"]["per_minute"]
                total_cost = duration_minutes * cost_per_minute

                cost_info = model.OpenAITranscriptionCostInfo(
                    duration_minutes=duration_minutes,
                    cost_per_minute=cost_per_minute,
                    total_cost=total_cost,
                    model="whisper-1"
                )

                span.set_attributes({
                    "audio.duration_minutes": duration_minutes,
                    "audio.cost_per_minute": cost_per_minute,
                    "audio.total_cost": total_cost,
                    "audio.model": "whisper-1"
                })

                span.set_status(Status(StatusCode.OK))
                return transcript, cost_info

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    def _get_audio_duration(self, audio_file: bytes, filename: str) -> float:
        try:
            # Вариант 1: Использование ffmpeg через subprocess (если установлен)

            import tempfile

            with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as tmp_file:
                tmp_file.write(audio_file)
                tmp_file_path = tmp_file.name

            try:
                result = subprocess.run(
                    [
                        'ffprobe',
                        '-v', 'error',
                        '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1',
                        tmp_file_path
                    ],
                    capture_output=True,
                    text=True,
                    check=True
                )
                duration_seconds = float(result.stdout.strip())
                return duration_seconds / 60.0

            finally:
                # Удаляем временный файл
                import os
                os.unlink(tmp_file_path)

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Вариант 2: Использование pydub (если ffmpeg недоступен)
            try:
                from pydub import AudioSegment
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_file))
                duration_seconds = len(audio_segment) / 1000.0
                return duration_seconds / 60.0

            except ImportError:
                # Вариант 3: Приблизительная оценка на основе размера файла
                # Предполагаем средний битрейт 128 kbps для MP3
                self.logger.warning(
                    "Не удалось точно определить длительность аудио. "
                    "Используется приблизительная оценка на основе размера файла."
                )

                # Размер файла в килобайтах
                file_size_kb = len(audio_file) / 1024

                # Приблизительная оценка для разных форматов
                if filename.lower().endswith('.mp3'):
                    # MP3: ~128 kbps = 16 KB/s = 0.96 MB/min
                    estimated_minutes = file_size_kb / (16 * 60)
                elif filename.lower().endswith('.wav'):
                    # WAV: ~1411 kbps = 176 KB/s = 10.6 MB/min
                    estimated_minutes = file_size_kb / (176 * 60)
                elif filename.lower().endswith('.m4a'):
                    # M4A: ~256 kbps = 32 KB/s = 1.92 MB/min
                    estimated_minutes = file_size_kb / (32 * 60)
                else:
                    # По умолчанию используем оценку для MP3
                    estimated_minutes = file_size_kb / (16 * 60)

                return estimated_minutes

    async def text_to_speech(
            self,
            text: str,
            voice: str = "alloy",
            tts_model: str = "tts-1-hd"
    ) -> tuple[bytes, model.OpenAITTSCostInfo]:
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
                audio_content = response.content

                char_count = len(text)
                cost_per_1k_chars = self.PRICING[tts_model]["per_1k_chars"]
                total_cost = (char_count / 1000) * cost_per_1k_chars

                cost_info = model.OpenAITTSCostInfo(
                    character_count=char_count,
                    cost_per_1k_chars=cost_per_1k_chars,
                    total_cost=total_cost,
                    model=tts_model,
                    voice=voice
                )

                span.set_attributes({
                    "tts.character_count": char_count,
                    "tts.cost_per_1k_chars": cost_per_1k_chars,
                    "tts.total_cost": total_cost,
                    "tts.model": tts_model,
                    "tts.voice": voice
                })

                span.set_status(Status(StatusCode.OK))
                return audio_content, cost_info

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
    ) -> tuple[list[str], model.OpenAIImageGenerationInfo]:
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

                # Извлечение результатов
                if response_format == "url":
                    images = [img.url for img in response.data]
                else:  # b64_json
                    images = [img.b64_json for img in response.data]

                # Расчет стоимости
                cost_info = self._calculate_image_generation_cost(
                    llm_model=llm_model,
                    size=size,
                    quality=quality,
                    style=style,
                    image_count=n
                )

                # Логирование метрик
                span.set_attributes({
                    "dalle.model": llm_model,
                    "dalle.size": size,
                    "dalle.quality": quality or "N/A",
                    "dalle.style": style or "N/A",
                    "dalle.image_count": n,
                    "dalle.cost_per_image": cost_info.cost_per_image,
                    "dalle.total_cost": cost_info.total_cost,
                    "dalle.response_format": response_format
                })

                span.set_status(Status(StatusCode.OK))

                self.logger.info(
                    f"Сгенерировано {n} изображение(й) с помощью {llm_model}",
                    {
                        "model": llm_model,
                        "size": size,
                        "quality": quality,
                        "total_cost": cost_info.total_cost
                    }
                )

                return images, cost_info

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка при генерации изображения: {err}")
                raise

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
    ) -> tuple[list[str], model.OpenAIImageGenerationInfo]:
        with self.tracer.start_as_current_span(
                "GPTClient.edit_image",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                if llm_model != "dall-e-2":
                    raise ValueError("Только DALL-E 2 поддерживает редактирование изображений")

                if n > 10:
                    raise ValueError("Максимум 10 изображений за раз")

                # Подготовка файлов
                image_file = io.BytesIO(image)
                image_file.name = "image.png"

                params = {
                    "image": image_file,
                    "prompt": prompt,
                    "size": size,
                    "n": n,
                    "response_format": response_format
                }

                if mask:
                    mask_file = io.BytesIO(mask)
                    mask_file.name = "mask.png"
                    params["mask"] = mask_file

                if user:
                    params["user"] = user

                # Выполнение запроса
                response = await self.client.images.edit(**params)

                # Извлечение результатов
                if response_format == "url":
                    images = [img.url for img in response.data]
                else:
                    images = [img.b64_json for img in response.data]

                # Расчет стоимости
                cost_info = self._calculate_image_generation_cost(
                    llm_model=llm_model,
                    size=size,
                    quality=None,
                    style=None,
                    image_count=n
                )

                span.set_attributes({
                    "dalle.operation": "edit",
                    "dalle.model": llm_model,
                    "dalle.size": size,
                    "dalle.image_count": n,
                    "dalle.total_cost": cost_info.total_cost,
                    "dalle.has_mask": mask is not None
                })

                span.set_status(Status(StatusCode.OK))
                return images, cost_info

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def create_image_variation(
            self,
            image: bytes,
            llm_model: str = "dall-e-2",
            size: str = "1024x1024",
            n: int = 1,
            response_format: str = "url",
            user: str = None
    ) -> tuple[list[str], model.OpenAIImageGenerationInfo]:
        with self.tracer.start_as_current_span(
                "GPTClient.create_image_variation",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                if llm_model != "dall-e-2":
                    raise ValueError("Только DALL-E 2 поддерживает создание вариаций")

                if n > 10:
                    raise ValueError("Максимум 10 изображений за раз")

                # Подготовка файла
                image_file = io.BytesIO(image)
                image_file.name = "image.png"

                params = {
                    "image": image_file,
                    "size": size,
                    "n": n,
                    "response_format": response_format
                }

                if user:
                    params["user"] = user

                # Выполнение запроса
                response = await self.client.images.create_variation(**params)

                # Извлечение результатов
                if response_format == "url":
                    images = [img.url for img in response.data]
                else:
                    images = [img.b64_json for img in response.data]

                # Расчет стоимости
                cost_info = self._calculate_image_generation_cost(
                    llm_model=llm_model,
                    size=size,
                    quality=None,
                    style=None,
                    image_count=n
                )

                span.set_attributes({
                    "dalle.operation": "variation",
                    "dalle.model": llm_model,
                    "dalle.size": size,
                    "dalle.image_count": n,
                    "dalle.total_cost": cost_info.total_cost
                })

                span.set_status(Status(StatusCode.OK))
                return images, cost_info

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    def _calculate_image_generation_cost(
            self,
            llm_model: str,
            size: str,
            quality: str ,
            style: str,
            image_count: int
    ) -> model.OpenAIImageGenerationInfo:
        if llm_model == "dall-e-3":
            # Для DALL-E 3 используем quality для определения цены
            pricing_key = quality or "standard"
            if pricing_key in self.PRICING["dall-e-3"] and size in self.PRICING["dall-e-3"][pricing_key]:
                cost_per_image = self.PRICING["dall-e-3"][pricing_key][size]
            else:
                # Fallback на стандартную цену если не найдено
                self.logger.warning(
                    f"Цена не найдена для {llm_model} {quality} {size}, используем стандартную"
                )
                cost_per_image = 0.040
        elif model == "dall-e-2":
            # Для DALL-E 2 цена зависит только от размера
            if size in self.PRICING["dall-e-2"]:
                cost_per_image = self.PRICING["dall-e-2"][size]
            else:
                # Fallback
                self.logger.warning(
                    f"Цена не найдена для {model} {size}, используем стандартную"
                )
                cost_per_image = 0.020
        else:
            self.logger.warning(f"Неизвестная модель {model}")
            cost_per_image = 0.040

        total_cost = cost_per_image * image_count

        return model.OpenAIImageGenerationInfo(
            model=llm_model,
            size=size,
            quality=quality or "N/A",
            style=style or "N/A",
            cost_per_image=cost_per_image,
            total_cost=total_cost,
            image_count=image_count
        )

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