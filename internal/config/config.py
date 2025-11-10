import os


class Config:
    def __init__(self):
        # Service configuration
        self.environment = os.getenv("ENVIRONMENT", "dev")
        self.service_name = os.getenv("LOOM_CONTENT_CONTAINER_NAME", "loom-content")
        self.http_port = os.getenv("LOOM_CONTENT_PORT", "8000")
        self.service_version = os.getenv("SERVICE_VERSION", "1.0.0")
        self.root_path = os.getenv("ROOT_PATH", "/")
        self.prefix = os.getenv("LOOM_CONTENT_PREFIX", "/api/content")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        self.tg_bot_token: str = os.environ.get('LOOM_TG_BOT_TOKEN')
        self.tg_api_id: int = int(os.environ.get('LOOM_TG_API_ID'))
        self.tg_api_hash: str = os.environ.get('LOOM_TG_API_HASH')
        self.tg_session_string: str = os.environ.get('LOOM_TG_SESSION_STRING')
        self.domain: str = os.environ.get("LOOM_DOMAIN")
        self.proxy: str = os.environ.get("PROXY")

        self.interserver_secret_key = os.getenv("LOOM_INTERSERVER_SECRET_KEY")

        # PostgreSQL configuration
        self.db_host = os.getenv("LOOM_CONTENT_POSTGRES_CONTAINER_NAME", "localhost")
        self.db_port = "5432"
        self.db_name = os.getenv("LOOM_CONTENT_POSTGRES_DB_NAME", "hr_interview")
        self.db_user = os.getenv("LOOM_CONTENT_POSTGRES_USER", "postgres")
        self.db_pass = os.getenv("LOOM_CONTENT_POSTGRES_PASSWORD", "password")

        self.weed_master_host = os.getenv("LOOM_WEED_MASTER_CONTAINER_NAME", "localhost")
        self.weed_master_port = int(os.getenv("LOOM_WEED_MASTER_PORT", "9333"))

        # Настройки телеметрии
        self.alert_tg_bot_token = os.getenv("LOOM_ALERT_TG_BOT_TOKEN", "")
        self.alert_tg_chat_id = int(os.getenv("LOOM_ALERT_TG_CHAT_ID", "0"))
        self.alert_tg_chat_thread_id = int(os.getenv("LOOM_ALERT_TG_CHAT_THREAD_ID", "0"))
        self.grafana_url = os.getenv("LOOM_GRAFANA_URL", "")

        self.monitoring_redis_host = os.getenv("LOOM_MONITORING_REDIS_CONTAINER_NAME", "localhost")
        self.monitoring_redis_port = int(os.getenv("LOOM_MONITORING_REDIS_PORT", "6379"))
        self.monitoring_redis_db = int(os.getenv("LOOM_MONITORING_DEDUPLICATE_ERROR_ALERT_REDIS_DB", "0"))
        self.monitoring_redis_password = os.getenv("LOOM_MONITORING_REDIS_PASSWORD", "")

        # Настройки OpenTelemetry
        self.otlp_host = os.getenv("LOOM_OTEL_COLLECTOR_CONTAINER_NAME", "loom-otel-collector")
        self.otlp_port = int(os.getenv("LOOM_OTEL_COLLECTOR_GRPC_PORT", "4317"))

        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.neuroapi_openai_api_key = os.getenv("NEUROAPI_OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.googleai_api_key = os.getenv("GOOGLE_AI_API_KEY", "")

        # Loom Authorization service
        self.loom_authorization_host = os.getenv("LOOM_AUTHORIZATION_CONTAINER_NAME", "localhost")
        self.loom_authorization_port = os.getenv("LOOM_AUTHORIZATION_PORT", "8001")

        self.loom_employee_host = os.getenv("LOOM_EMPLOYEE_CONTAINER_NAME", "localhost")
        self.loom_employee_port = os.getenv("LOOM_EMPLOYEE_PORT", "8001")

        # Loom Organization service
        self.loom_organization_host = os.getenv("LOOM_ORGANIZATION_CONTAINER_NAME", "localhost")
        self.loom_organization_port = os.getenv("LOOM_ORGANIZATION_PORT", "8002")

        # Loom TG Bot service
        self.loom_tg_bot_host = os.getenv("LOOM_TG_BOT_CONTAINER_NAME", "localhost")
        self.loom_tg_bot_port = os.getenv("LOOM_TG_BOT_PORT", "8003")

        self.vk_app_id = os.getenv("LOOM_VK_APP_ID", "")
        self.vk_app_secret = os.getenv("LOOM_VK_APP_SECRET", "")
        self.vk_redirect_uri = f"https://{self.domain}{self.prefix}/social-network/vkontakte"

        # Vizard configuration
        self.vizard_api_key = os.getenv("VIZARD_API_KEY", "")
