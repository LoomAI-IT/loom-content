from enum import Enum

from pkg.client.client import AsyncHTTPClient
from internal import interface


class VideoType(Enum):
    """Типы источников видео"""
    REMOTE_FILE = 1  # Прямая ссылка на видеофайл (.mp4, .mov)
    YOUTUBE = 2  # YouTube видео
    GOOGLE_DRIVE = 3  # Google Drive видео
    VIMEO = 4  # Vimeo видео
    STREAMYARD = 5  # StreamYard видео


class AspectRatio(Enum):
    """Соотношения сторон для клипов"""
    VERTICAL = 1  # 9:16 - для TikTok, YouTube Shorts
    SQUARE = 2  # 1:1 - для Instagram, Facebook
    HORIZONTAL = 4  # 16:9 - для YouTube, Twitter


class ClipLength(Enum):
    """Длительность клипов в секундах"""
    AUTO = 0  # Автоматический выбор
    SEC_15 = 15  # 15 секунд
    SEC_30 = 30  # 30 секунд
    SEC_60 = 60  # 60 секунд
    SEC_90 = 90  # 90 секунд


class PricingPlan(Enum):
    """Тарифные планы Vizard"""
    FREE = "free"
    CREATOR = "creator"
    BUSINESS = "business"


class VizardClient(interface.IVizardClient):
    BASE_URL = "https://elb-api.vizard.ai/hvizard-server-front/open-api/v1"

    # Цены и лимиты планов (в минутах)
    PRICING = {
        PricingPlan.FREE: {
            "monthly_minutes": 60,
            "price_per_month": 0,
            "max_upload_length": 60,  # минут
            "max_upload_size": 1,  # GB
            "max_upload_quality": "1080p",
            "max_export_quality": "720p",
            "watermark": True,
            "api_access": False
        },
        PricingPlan.CREATOR: {
            "monthly_minutes": 600,
            "price_per_month": 16,  # USD при годовой оплате
            "max_upload_length": 600,
            "max_upload_size": 10,
            "max_upload_quality": "4K",
            "max_export_quality": "4K",
            "watermark": False,
            "api_access": True
        },
        PricingPlan.BUSINESS: {
            "monthly_minutes": 600,  # базовый пакет
            "price_per_month": 60,  # USD при годовой оплате, базовый пакет
            "max_upload_length": 600,
            "max_upload_size": 10,
            "max_upload_quality": "4K",
            "max_export_quality": "4K",
            "watermark": False,
            "api_access": True
        }
    }

    def __init__(
            self,
            api_key: str,
            plan: PricingPlan = PricingPlan.CREATOR
    ):

        self.api_key = api_key
        self.plan = plan
        self.headers = {
            "Content-Type": "application/json",
            "VIZARDAI_API_KEY": self.api_key
        }
        self.used_minutes = 0
        self.api_client = AsyncHTTPClient(
            "elb-api.vizard.ai",
            443,
            prefix="/hvizard-server-front/open-api/v1",
            use_tracing=True,
            use_https=True
        )

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
    ) -> dict:
        """
        Создание проекта и отправка видео на обработку

        Args:
            video_url: URL видео
            video_type: Тип источника видео
            lang: Язык видео (en, es, fr, de, it, pt, ru, zh, ja, ko и др.)
            prefer_length: Предпочтительная длительность клипов
            ratio_of_clip: Соотношение сторон клипов
            template_id: ID кастомного шаблона
            remove_silence: Удалять паузы и слова-паразиты
            max_clip_number: Максимальное количество клипов (1-100)
            keywords: Ключевые слова через запятую
            subtitle_switch: Включить субтитры
            emoji_switch: Включить автоэмодзи в субтитрах
            highlight_switch: Выделять ключевые слова в субтитрах
            headline_switch: Добавить заголовок в начале клипа
            project_name: Название проекта
            webhook_url: URL для webhook уведомлений

        Returns:
            Ответ API с project_id
        """
        # Подготовка данных запроса
        data: dict = {
            "lang": lang,
            "videoUrl": video_url,
            "videoType": video_type,
            "preferLength": [prefer_length]
        }

        # Опциональные параметры
        if ratio_of_clip:
            data["ratioOfClip"] = ratio_of_clip
        if template_id:
            data["templateId"] = template_id
        if remove_silence:
            data["removeSilenceSwitch"] = 1
        else:
            data["removeSilenceSwitch"] = 0
        if max_clip_number:
            data["maxClipNumber"] = min(max(1, max_clip_number), 100)
        if keywords:
            data["keyword"] = keywords
        data["subtitleSwitch"] = 1 if subtitle_switch else 0
        data["emojiSwitch"] = 1 if emoji_switch else 0
        data["highlightSwitch"] = 1 if highlight_switch else 0
        data["headlineSwitch"] = 1 if headline_switch else 0
        if project_name:
            data["projectName"] = project_name
        if webhook_url:
            data["webhookUrl"] = webhook_url

        # Отправка запроса
        try:
            response = await self.api_client.post(
                f"/project/create",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()

            response_json = response.json()

            return response_json

        except Exception as e:
            raise e

    async def get_project_status(self, project_id: str) -> dict:
        try:
            response = await self.api_client.get(
                f"/project/query/{project_id}",
                headers={"VIZARDAI_API_KEY": self.api_key}
            )
            response.raise_for_status()

            response_json = response.json()

            # Обновление счетчика использованных минут
            if response_json.get("status") == "completed":
                video_duration = response_json.get("videoDuration", 0) / 60  # в минутах
                self.used_minutes += video_duration

            return response_json

        except Exception as e:
            raise e

    def calculate_price(
            self,
            video_duration_minutes: float,
            clips_count: int = None
    ) -> dict:
        plan_info = self.PRICING[self.plan]

        # Проверка лимитов
        if video_duration_minutes > plan_info["max_upload_length"]:
            return {
                "error": f"Видео превышает максимальную длительность для плана {self.plan.value}: "
                         f"{plan_info['max_upload_length']} минут"
            }

        # Расчет стоимости
        monthly_minutes = plan_info["monthly_minutes"]
        monthly_price = plan_info["price_per_month"]

        # Стоимость за минуту
        if monthly_price > 0:
            price_per_minute = monthly_price / monthly_minutes
        else:
            price_per_minute = 0

        video_cost = video_duration_minutes * price_per_minute

        # Проверка доступных минут
        remaining_minutes = monthly_minutes - self.used_minutes
        minutes_needed = video_duration_minutes
        additional_minutes_needed = max(0, int(minutes_needed - remaining_minutes))

        price_info = {
            "plan": self.plan.value,
            "video_duration_minutes": video_duration_minutes,
            "monthly_minutes_limit": monthly_minutes,
            "used_minutes": self.used_minutes,
            "remaining_minutes": remaining_minutes,
            "minutes_needed": minutes_needed,
            "additional_minutes_needed": additional_minutes_needed,
            "price_per_minute": round(price_per_minute, 4),
            "estimated_cost": round(video_cost, 2),
            "currency": "USD",
            "notes": []
        }

        # Добавление заметок
        if additional_minutes_needed > 0:
            price_info["notes"].append(
                f"Недостаточно минут! Нужно еще {additional_minutes_needed:.1f} минут. "
                "Необходимо обновить план или докупить минуты."
            )

        if self.plan == PricingPlan.FREE:
            price_info["notes"].append("API недоступен на бесплатном плане!")

        if clips_count:
            price_info["clips_count"] = clips_count
            if clips_count > 100:
                price_info["notes"].append("Максимум 100 клипов за один запрос")

        return price_info


import asyncio


async def basic_example():
    """Базовый пример создания проекта"""

    # Инициализация клиента
    client = VizardClient(
        api_key="61be2e491cbd416099ada26810de0fb9",
        plan=PricingPlan.CREATOR
    )

    vizard_project = await client.create_project(
        video_url="https://www.youtube.com/watch?v=M3eE7J_Ul3s",
        video_type=2,
        lang="ru",
        prefer_length=0,
        ratio_of_clip=1,  # 9:16 для вертикальных видео
        remove_silence=True,
        max_clip_number=2,
        subtitle_switch=True,
        emoji_switch=True,
        highlight_switch=True,
        headline_switch=True,
        project_name=f"Yrrj"
    )
    print(f"{vizard_project=}", flush=True)




# Запуск примеров
if __name__ == "__main__":
    print("=== Базовый пример ===")
    asyncio.run(basic_example())