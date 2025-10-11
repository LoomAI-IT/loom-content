from dataclasses import dataclass


@dataclass
class Organization:
    id: int
    name: str
    rub_balance: str
    video_cut_description_end_sample: str
    publication_text_end_sample: str
    tone_of_voice: list[str]
    brand_rules: list[str]
    compliance_rules: list[str]
    audience_insights: list[str]
    products: list[dict]
    locale: dict
    additional_info: list[str]
    created_at: str

@dataclass
class CostMultiplier:
    id: int
    organization_id: int
    generate_text_cost_multiplier: float
    transcribe_audio_cost_multiplier: float
    generate_image_cost_multiplier: float
    generate_vizard_video_cut_cost_multiplier: float
    created_at: str