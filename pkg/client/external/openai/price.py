from dataclasses import dataclass


@dataclass
class ModelPricing:
    """Цены за 1M токенов в долларах США"""
    input_price: float  # Цена за 1M input токенов
    output_price: float  # Цена за 1M output токенов
    cached_input_price: float = None  # Цена за 1M кэшированных input токенов


# Актуальные цены на январь 2025 (в долларах за 1M токенов)
PRICING_TABLE: dict[str, ModelPricing] = {
    # GPT-5 модели (август 2025)
    'gpt-5': ModelPricing(1.25, 10.00, 0.125),
    'gpt-5-2025-08-07': ModelPricing(1.25, 10.00, 0.125),
    'gpt-5-mini': ModelPricing(0.25, 2.00, 0.025),
    'gpt-5-mini-2025-08-07': ModelPricing(0.25, 2.00, 0.025),
    'gpt-5-nano': ModelPricing(0.05, 0.40, 0.005),
    'gpt-5-nano-2025-08-07': ModelPricing(0.05, 0.40, 0.005),

    # GPT-4o модели
    'gpt-4o': ModelPricing(2.50, 10.00),
    'gpt-4o-2024-08-06': ModelPricing(2.50, 10.00),
    'gpt-4o-2024-05-13': ModelPricing(5.00, 15.00),
    'gpt-4o-mini': ModelPricing(0.15, 0.60),
    'gpt-4o-mini-2024-07-18': ModelPricing(0.15, 0.60),

    # GPT-4 модели
    'gpt-4': ModelPricing(30.00, 60.00),
    'gpt-4-turbo': ModelPricing(10.00, 30.00),
    'gpt-4-turbo-2024-04-09': ModelPricing(10.00, 30.00),
    'gpt-4-turbo-preview': ModelPricing(10.00, 30.00),

    # GPT-3.5 модели
    'gpt-3.5-turbo': ModelPricing(0.50, 1.50),
    'gpt-3.5-turbo-0125': ModelPricing(0.50, 1.50),
    'gpt-3.5-turbo-1106': ModelPricing(1.00, 2.00),

    # O-series reasoning модели (декабрь 2024 - январь 2025)
    'o3': ModelPricing(15.00, 60.00),
    'o3-mini': ModelPricing(3.00, 12.00),
    'o3-2024-12-17': ModelPricing(15.00, 60.00),
    'o3-mini-2024-12-17': ModelPricing(3.00, 12.00),
    'o1': ModelPricing(15.00, 60.00),
    'o1-2024-12-17': ModelPricing(15.00, 60.00),
    'o1-mini': ModelPricing(3.00, 12.00),
    'o1-mini-2024-09-12': ModelPricing(3.00, 12.00),
    'o1-preview': ModelPricing(15.00, 60.00),
    'o1-preview-2024-09-12': ModelPricing(15.00, 60.00),
}

TRANSCRIPTION_PRICING = {
    'whisper-1': 0.006,  # $0.006 за минуту
    'gpt-4o-transcribe': {
        'per_minute': 0.006,  # $0.006 за минуту (альтернативный способ)
        'input_tokens': 2.50,  # $2.50 за 1M токенов
        'output_tokens': 10.00  # $10.00 за 1M токенов
    },
    'gpt-4o-mini-transcribe': {
        'per_minute': 0.003,  # $0.003 за минуту
        'input_tokens': 1.25,  # $1.25 за 1M токенов
        'output_tokens': 5.00  # $5.00 за 1M токенов
    }
}

IMAGE_PRICING = {
    "dall-e-3": {
        "1024x1024": {
            "standard": 0.040,
            "hd": 0.080
        },
        "1792x1024": {
            "standard": 0.080,
            "hd": 0.120
        },
        "1024x1792": {
            "standard": 0.080,
            "hd": 0.120
        }
    },
    "gpt-image-1": {
        "1024x1024": {
            "low": 0.020,
            "medium": 0.070,
            "high": 0.190
        },
        "1024x1536": {
            "low": 0.030,
            "medium": 0.105,
            "high": 0.285
        },
        "1536x1024": {
            "low": 0.030,
            "medium": 0.105,
            "high": 0.285
        },
        # Цены для редактирования (примерные, как для high quality)
        "edit": {
            "1024x1024": 0.190,
            "1024x1536": 0.285,
            "1536x1024": 0.285
        }
    }
}
