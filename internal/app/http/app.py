from fastapi import FastAPI
from starlette.responses import StreamingResponse

from internal import model, interface
from internal.controller.http.handler.publication.model import *


def NewHTTP(
        db: interface.IDB,
        publication_controller: interface.IPublicationController,
        video_cut_controller: interface.IVideoCutController,
        social_network_controller: interface.ISocialNetworkController,
        http_middleware: interface.IHttpMiddleware,
        prefix: str
):
    app = FastAPI(
        openapi_url=prefix + "/openapi.json",
        docs_url=prefix + "/docs",
        redoc_url=prefix + "/redoc",
    )
    include_middleware(app, http_middleware)
    include_db_handler(app, db, prefix)

    include_publication_handlers(app, publication_controller, prefix)
    include_video_cut_handlers(app, video_cut_controller, prefix)
    include_social_network_handlers(app, social_network_controller, prefix)

    return app


def include_middleware(
        app: FastAPI,
        http_middleware: interface.IHttpMiddleware,
):
    http_middleware.authorization_middleware03(app)
    http_middleware.logger_middleware02(app)
    http_middleware.trace_middleware01(app)


def include_publication_handlers(
        app: FastAPI,
        publication_controller: interface.IPublicationController,
        prefix: str
):
    # Генерация публикации
    app.add_api_route(
        prefix + "/publication/text/generate",
        publication_controller.generate_publication_text,
        methods=["POST"],
        tags=["Publication"],
    )

    # Тестовая генерация публикации (без сохранения категории в БД)
    app.add_api_route(
        prefix + "/publication/text/test-generate",
        publication_controller.test_generate_publication_text,
        methods=["POST"],
        tags=["Publication"],
    )

    # Регенерация изображения публикации
    app.add_api_route(
        prefix + "/publication/text/regenerate",
        publication_controller.regenerate_publication_text,
        methods=["POST"],
        tags=["Publication"],
    )
    app.add_api_route(
        prefix + "/publication/image/generate",
        publication_controller.generate_publication_image,
        methods=["POST"],
        tags=["Publication"],
    )

    # Регенерация изображения публикации
    app.add_api_route(
        prefix + "/publication/create",
        publication_controller.create_publication,
        methods=["POST"],
        tags=["Publication"],
    )

    # Изменение публикации
    app.add_api_route(
        prefix + "/publication/{publication_id}",
        publication_controller.change_publication,
        methods=["PUT"],
        tags=["Publication"]
    )

    # Удаление изображения публикации
    app.add_api_route(
        prefix + "/publication/{publication_id}/image",
        publication_controller.delete_publication_image,
        methods=["DELETE"],
        tags=["Publication"]
    )

    # Отправка публикации на модерацию
    app.add_api_route(
        prefix + "/publication/{publication_id}/moderation/send",
        publication_controller.send_publication_to_moderation,
        methods=["POST"],
        tags=["Publication"]
    )

    # Модерация публикации
    app.add_api_route(
        prefix + "/publication/moderate",
        publication_controller.moderate_publication,
        methods=["POST"],
        tags=["Publication"]
    )

    # Получение публикации по ID
    app.add_api_route(
        prefix + "/publication/{publication_id}",
        publication_controller.get_publication_by_id,
        methods=["GET"],
        tags=["Publication"],
        response_model=model.Publication,
    )

    # Получение публикаций по организации
    app.add_api_route(
        prefix + "/publication/organization/{organization_id}/publications",
        publication_controller.get_publications_by_organization,
        methods=["GET"],
        tags=["Publication"],
        response_model=list[model.Publication],
    )

    # Скачивание изображения публикации
    app.add_api_route(
        prefix + "/publication/{publication_id}/image/download",
        publication_controller.download_publication_image,
        methods=["GET"],
        tags=["Publication"],
        response_class=StreamingResponse,
    )

    app.add_api_route(
        prefix + "/image/{image_fid}/{image_name}",
        publication_controller.download_other_image,
        methods=["GET"],
        tags=["Publication"],
        response_class=StreamingResponse,
    )

    app.add_api_route(
        prefix + "/publication/{publication_id}",
        publication_controller.delete_publication,
        methods=["DELETE"],
        tags=["Publication"]
    )

    # РУБРИКИ
    # Создание рубрики
    app.add_api_route(
        prefix + "/publication/category",
        publication_controller.create_category,
        methods=["POST"],
        tags=["Category"]
    )

    # Получение рубрики по ID
    app.add_api_route(
        prefix + "/publication/category/{category_id}",
        publication_controller.get_category_by_id,
        methods=["GET"],
        tags=["Category"]
    )

    # Получение рубрик по организации
    app.add_api_route(
        prefix + "/publication/organization/{organization_id}/categories",
        publication_controller.get_categories_by_organization,
        methods=["GET"],
        tags=["Category"],
        response_model=list[model.Category],
    )

    # Обновление рубрики
    app.add_api_route(
        prefix + "/publication/category/{category_id}",
        publication_controller.update_category,
        methods=["PUT"],
        tags=["Category"]
    )

    # Удаление рубрики
    app.add_api_route(
        prefix + "/publication/category/{category_id}",
        publication_controller.delete_category,
        methods=["DELETE"],
        tags=["Category"]
    )

    # РУБРИКИ ДЛЯ АВТОПОСТИНГА

    # Создание рубрики для автопостинга
    app.add_api_route(
        prefix + "/publication/autoposting-category",
        publication_controller.create_autoposting_category,
        methods=["POST"],
        tags=["AutopostingCategory"]
    )

    # Получение рубрики для автопостинга по ID
    app.add_api_route(
        prefix + "/publication/autoposting-category/{autoposting_category_id}",
        publication_controller.get_autoposting_category_by_id,
        methods=["GET"],
        tags=["AutopostingCategory"]
    )

    # Обновление рубрики для автопостинга
    app.add_api_route(
        prefix + "/publication/autoposting-category/{autoposting_category_id}",
        publication_controller.update_autoposting_category,
        methods=["PUT"],
        tags=["AutopostingCategory"]
    )

    # АВТОПОСТИНГ

    # Создание автопостинга
    app.add_api_route(
        prefix + "/publication/autoposting",
        publication_controller.create_autoposting,
        methods=["POST"],
        tags=["Autoposting"]
    )

    # Получение автопостингов по организации
    app.add_api_route(
        prefix + "/publication/organization/{organization_id}/autopostings",
        publication_controller.get_autoposting_by_organization,
        methods=["GET"],
        tags=["Autoposting"]
    )

    # Обновление автопостинга
    app.add_api_route(
        prefix + "/publication/autoposting/{autoposting_id}",
        publication_controller.update_autoposting,
        methods=["PUT"],
        tags=["Autoposting"]
    )

    # Удаление автопостинга
    app.add_api_route(
        prefix + "/publication/autoposting/{autoposting_id}",
        publication_controller.delete_autoposting,
        methods=["DELETE"],
        tags=["Autoposting"]
    )

    app.add_api_route(
        prefix + "/publication/audio/transcribe",
        publication_controller.transcribe_audio,
        methods=["GET"],
        tags=["Other"]
    )

    # IMAGE EDITING
    app.add_api_route(
        prefix + "/image/edit",
        publication_controller.edit_image,
        methods=["POST"],
        tags=["ImageEditing"]
    )

    app.add_api_route(
        prefix + "/image/combine",
        publication_controller.combine_images,
        methods=["POST"],
        tags=["ImageEditing"]
    )


def include_video_cut_handlers(
        app: FastAPI,
        video_cut_controller: interface.IVideoCutController,
        prefix: str
):
    # НАРЕЗКА ВИДЕО

    # Генерация нарезки видео
    app.add_api_route(
        prefix + "/video-cut/vizard/generate",
        video_cut_controller.generate_vizard_video_cuts,
        methods=["POST"],
        tags=["VideoCut"]
    )

    app.add_api_route(
        prefix + "/video-cut/vizard/create",
        video_cut_controller.create_vizard_video_cuts,
        methods=["POST"],
        tags=["VideoCut"]
    )

    # Изменение нарезки видео
    app.add_api_route(
        prefix + "/video-cut",
        video_cut_controller.change_video_cut,
        methods=["PUT"],
        tags=["VideoCut"]
    )

    app.add_api_route(
        prefix + "/video-cut/{video_cut_id}",
        video_cut_controller.delete_video_cut,
        methods=["DELETE"],
        tags=["VideoCut"]
    )

    # Отправка нарезки на модерацию
    app.add_api_route(
        prefix + "/video-cut/{video_cut_id}/moderation/send",
        video_cut_controller.send_video_cut_to_moderation,
        methods=["POST"],
        tags=["VideoCut"]
    )

    # Получение нарезки по ID
    app.add_api_route(
        prefix + "/video-cut/{video_cut_id}",
        video_cut_controller.get_video_cut_by_id,
        methods=["GET"],
        tags=["VideoCut"]
    )

    # Получение нарезок по организации
    app.add_api_route(
        prefix + "/organization/{organization_id}/video-cuts",
        video_cut_controller.get_video_cuts_by_organization,
        methods=["GET"],
        tags=["VideoCut"],
        response_model=list[model.VideoCut],
    )

    # Модерация нарезки видео
    app.add_api_route(
        prefix + "/video-cut/moderate",
        video_cut_controller.moderate_video_cut,
        methods=["POST"],
        tags=["VideoCut"]
    )

    # Скачивание нарезки видео
    app.add_api_route(
        prefix + "/video-cut/{video_cut_id}/download/file",
        video_cut_controller.download_video_cut,
        methods=["GET"],
        tags=["VideoCut"],
        response_class=StreamingResponse,
    )


def include_social_network_handlers(
        app: FastAPI,
        social_network_controller: interface.ISocialNetworkController,
        prefix: str
):
    # СОЗДАНИЕ СОЦИАЛЬНЫХ СЕТЕЙ

    # Создание YouTube
    app.add_api_route(
        prefix + "/social-network/youtube",
        social_network_controller.create_youtube,
        methods=["POST"],
        tags=["SocialNetwork"]
    )

    # Создание Instagram
    app.add_api_route(
        prefix + "/social-network/instagram",
        social_network_controller.create_instagram,
        methods=["POST"],
        tags=["SocialNetwork"]
    )

    # Создание Telegram
    app.add_api_route(
        prefix + "/social-network/telegram",
        social_network_controller.create_telegram,
        methods=["POST"],
        tags=["SocialNetwork"]
    )

    app.add_api_route(
        prefix + "/social-network/telegram/check-permission/{tg_channel_username}",
        social_network_controller.check_telegram_channel_permission,
        methods=["GET"],
        tags=["SocialNetwork"]
    )

    app.add_api_route(
        prefix + "/social-network/telegram",
        social_network_controller.update_telegram,
        methods=["PUT"],
        tags=["SocialNetwork"]
    )

    app.add_api_route(
        prefix + "/social-network/telegram/{organization_id}",
        social_network_controller.delete_telegram,
        methods=["DELETE"],
        tags=["SocialNetwork"]
    )

    # Создание VKontakt

    # VK OAuth Callback (заглушка для отладки)
    app.add_api_route(
        prefix + "/social-network/vkontakte",
        social_network_controller.vk_oauth_callback,
        methods=["GET"],
        tags=["SocialNetwork"]
    )

    # ПОЛУЧЕНИЕ СОЦИАЛЬНЫХ СЕТЕЙ

    # Получение всех социальных сетей по организации
    app.add_api_route(
        prefix + "/social-network/organization/{organization_id}",
        social_network_controller.get_social_networks_by_organization,
        methods=["GET"],
        tags=["SocialNetwork"]
    )


def include_db_handler(app: FastAPI, db: interface.IDB, prefix: str):
    app.add_api_route(prefix + "/table/create", create_table_handler(db), methods=["GET"])
    app.add_api_route(prefix + "/table/drop", drop_table_handler(db), methods=["GET"])
    app.add_api_route(prefix + "/health", heath_check_handler(), methods=["GET"])


def create_table_handler(db: interface.IDB):
    async def create_table():
        try:
            await db.multi_query(model.create_organization_tables_queries)
        except Exception as err:
            raise err

    return create_table


def heath_check_handler():
    async def heath_check():
        return "ok"

    return heath_check


def drop_table_handler(db: interface.IDB):
    async def drop_table():
        try:
            await db.multi_query(model.drop_queries)
        except Exception as err:
            raise err

    return drop_table
