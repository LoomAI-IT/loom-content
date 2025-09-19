import uvicorn

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry, AlertManager
from infrastructure.weedfs.weedfs import AsyncWeed


from pkg.client.external.vizard.client import VizardClient
from pkg.client.external.openai.client import GPTClient

from pkg.client.internal.kontur_authorization.client import KonturAuthorizationClient
from pkg.client.internal.kontur_organization.client import KonturOrganizationClient
from pkg.client.internal.kontur_tg_bot.client import KonturTgBotClient

from internal.controller.http.middlerware.middleware import HttpMiddleware
from internal.controller.http.handler.publication.handler import PublicationController
from internal.controller.http.handler.video_cut.handler import VideoCutController

from internal.service.video_cut.service import VideoCutService
from internal.service.publication.service import PublicationService
from internal.service.publication.prompt import PublicationPromptGenerator

from internal.repo.publication.repo import PublicationRepo
from internal.repo.video_cut.repo import VideoCutRepo

from internal.app.http.app import NewHTTP

from internal.config.config import Config

cfg = Config()

alert_manager = AlertManager(
    cfg.alert_tg_bot_token,
    cfg.service_name,
    cfg.alert_tg_chat_id,
    cfg.alert_tg_chat_thread_id,
    cfg.grafana_url,
    cfg.monitoring_redis_host,
    cfg.monitoring_redis_port,
    cfg.monitoring_redis_db,
    cfg.monitoring_redis_password,
)

tel = Telemetry(
    cfg.log_level,
    cfg.root_path,
    cfg.environment,
    cfg.service_name,
    cfg.service_version,
    cfg.otlp_host,
    cfg.otlp_port,
    alert_manager
)

# Инициализация базы данных
db = PG(tel, cfg.db_user, cfg.db_pass, cfg.db_host, cfg.db_port, cfg.db_name)
storage = AsyncWeed(cfg.weed_master_host, cfg.weed_master_port)

# Инициализация клиентов
kontur_authorization_client = KonturAuthorizationClient(
    tel=tel,
    host=cfg.kontur_authorization_host,
    port=cfg.kontur_authorization_port,
)

kontur_organization_client = KonturOrganizationClient(
    tel=tel,
    host=cfg.kontur_organization_host,
    port=cfg.kontur_organization_port,
    interserver_secret_key=cfg.interserver_secret_key
)
kontur_tg_bot_client = KonturTgBotClient(
    tel=tel,
    host=cfg.kontur_tg_bot_host,
    port=cfg.kontur_tg_bot_port,
    interserver_secret_key=cfg.interserver_secret_key
)

openai_client = GPTClient(
    tel=tel,
    api_key=cfg.openai_api_key
)
vizard_client = VizardClient(
    api_key=cfg.vizard_api_key
)

# Инициализация репозиториев
publication_repo = PublicationRepo(tel, db)
video_cut_repo = VideoCutRepo(tel, db)

# Инициализация генератора промптов
publication_prompt_generator = PublicationPromptGenerator()

# Инициализация сервисов
publication_service = PublicationService(
    tel=tel,
    repo=publication_repo,
    llm_client=openai_client,
    storage=storage,
    prompt_generator=publication_prompt_generator,
    organization_client=kontur_organization_client,
    vizard_client=vizard_client,
)

video_cut_service = VideoCutService(
    tel=tel,
    repo=video_cut_repo,
    storage=storage,
    organization_client=kontur_organization_client,
    vizard_client=vizard_client,
)

# Инициализация контроллеров
publication_controller = PublicationController(tel, publication_service)
video_cut_controller = VideoCutController(tel, video_cut_service)

# Инициализация middleware
http_middleware = HttpMiddleware(tel, cfg.prefix, kontur_authorization_client)

if __name__ == "__main__":
    app = NewHTTP(
        db=db,
        publication_controller=publication_controller,
        video_cut_controller=video_cut_controller,
        http_middleware=http_middleware,
        prefix=cfg.prefix,
    )
    uvicorn.run(app, host="0.0.0.0", port=int(cfg.http_port), access_log=False)