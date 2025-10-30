import argparse
import asyncio
from contextvars import ContextVar

import uvicorn
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry, AlertManager
from infrastructure.weedfs.weedfs import AsyncWeed
from pkg.client.external.claude.client import AnthropicClient
from pkg.client.external.telegram.client import LTelegramClient

from pkg.client.external.vizard.client import VizardClient
from pkg.client.external.openai.client import OpenAIClient
from pkg.client.external.googleai.client import GoogleAIClient

from pkg.client.internal.loom_authorization.client import LoomAuthorizationClient
from pkg.client.internal.loom_organization.client import LoomOrganizationClient
from pkg.client.internal.loom_tg_bot.client import LoomTgBotClient
from pkg.client.internal.loom_employee.client import LoomEmployeeClient

from internal.controller.http.middlerware.middleware import HttpMiddleware
from internal.controller.http.handler.publication.handler import PublicationController
from internal.controller.http.handler.video_cut.handler import VideoCutController
from internal.controller.http.handler.social_network.handler import SocialNetworkController

from internal.service.video_cut.service import VideoCutService
from internal.service.publication.service import PublicationService
from internal.service.social_network.service import SocialNetworkService
from internal.service.publication.prompt import PublicationPromptGenerator

from internal.repo.publication.repo import PublicationRepo
from internal.repo.video_cut.repo import VideoCutRepo
from internal.repo.social_network.repo import SocialNetworkRepo

from internal.app.http.app import NewHTTP
from internal.app.autoposting.app import Autoposting

from internal.config.config import Config

parser = argparse.ArgumentParser(description="Loom Content Service")
parser.add_argument(
    "mode",
    choices=["http", "autoposting"],
    help="Режим запуска: http - HTTP сервер, autoposting - автопостинг"
)

args = parser.parse_args()

cfg = Config()
cfg.service_name = cfg.service_name if args.mode == "http" else cfg.service_name + "-autoposting"

log_context: ContextVar[dict] = ContextVar('log_context', default={})

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
    log_context,
    alert_manager
)

# Инициализация базы данных
db = PG(tel, cfg.db_user, cfg.db_pass, cfg.db_host, cfg.db_port, cfg.db_name)
storage = AsyncWeed(cfg.weed_master_host, cfg.weed_master_port)

session = AiohttpSession(api=TelegramAPIServer.from_base(f'https://{cfg.domain}/telegram-bot-api'))
bot = Bot(token=cfg.tg_bot_token, session=session)

# Инициализация клиентов
loom_authorization_client = LoomAuthorizationClient(
    tel=tel,
    host=cfg.loom_authorization_host,
    port=cfg.loom_authorization_port,
    log_context=log_context
)

loom_employee_client = LoomEmployeeClient(
    tel=tel,
    host=cfg.loom_employee_host,
    port=cfg.loom_employee_port,
    log_context=log_context
)

loom_organization_client = LoomOrganizationClient(
    tel=tel,
    host=cfg.loom_organization_host,
    port=cfg.loom_organization_port,
    interserver_secret_key=cfg.interserver_secret_key,
    log_context=log_context
)
loom_tg_bot_client = LoomTgBotClient(
    tel=tel,
    host=cfg.loom_tg_bot_host,
    port=cfg.loom_tg_bot_port,
    interserver_secret_key=cfg.interserver_secret_key,
    log_context=log_context
)

openai_client = OpenAIClient(
    tel=tel,
    api_key=cfg.openai_api_key,
    neuroapi_api_key=cfg.neuroapi_openai_api_key,
    proxy=cfg.proxy
)
anthropic_client = AnthropicClient(
    tel,
    cfg.anthropic_api_key,
    proxy=cfg.proxy
)
googleai_client = GoogleAIClient(
    tel=tel,
    api_key=cfg.googleai_api_key,
    proxy=cfg.proxy
)
vizard_client = VizardClient(
    api_key=cfg.vizard_api_key
)

telegram_client = LTelegramClient(
    cfg.tg_bot_token,
    cfg.tg_session_string,
    cfg.tg_api_id,
    cfg.tg_api_hash,
)

# Инициализация репозиториев
publication_repo = PublicationRepo(tel, db)
video_cut_repo = VideoCutRepo(tel, db)
social_network_repo = SocialNetworkRepo(tel, db)


# Инициализация генератора промптов
publication_prompt_generator = PublicationPromptGenerator()

# Инициализация сервисов
publication_service = PublicationService(
    tel=tel,
    repo=publication_repo,
    social_network_repo=social_network_repo,
    anthropic_client=anthropic_client,
    openai_client=openai_client,
    googleai_client=googleai_client,
    storage=storage,
    prompt_generator=publication_prompt_generator,
    organization_client=loom_organization_client,
    vizard_client=vizard_client,
    telegram_client=telegram_client,
    loom_tg_bot_client=loom_tg_bot_client,
    loom_domain=cfg.domain,
    environment=cfg.environment
)

video_cut_service = VideoCutService(
    tel=tel,
    repo=video_cut_repo,
    storage=storage,
    organization_client=loom_organization_client,
    loom_tg_bot_client=loom_tg_bot_client,
    vizard_client=vizard_client,
    bot=bot
)

social_network_service = SocialNetworkService(
    tel=tel,
    repo=social_network_repo,
    telegram_client=telegram_client,
)

# Инициализация контроллеров
publication_controller = PublicationController(tel, publication_service)
video_cut_controller = VideoCutController(tel, video_cut_service)
social_network_controller = SocialNetworkController(tel, social_network_service)

# Инициализация middleware
http_middleware = HttpMiddleware(tel, loom_authorization_client, cfg.prefix, log_context)

autoposting = Autoposting(
    tel=tel,
    publication_service=publication_service,
    telegram_client=telegram_client,
    openai_client=openai_client,
    prompt_generator=publication_prompt_generator,
    loom_employee_client=loom_employee_client
)

app = NewHTTP(
    db=db,
    publication_controller=publication_controller,
    video_cut_controller=video_cut_controller,
    social_network_controller=social_network_controller,
    http_middleware=http_middleware,
    prefix=cfg.prefix,
)

if __name__ == "__main__":
    if args.mode == "http":
        if cfg.environment == "prod":
            workers = 2
        else:
            workers = 1

        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=int(cfg.http_port),
            workers=workers,
            loop="uvloop",
            access_log=False,
        )

    elif args.mode == "autoposting":
        asyncio.run(
            autoposting.run()
        )
