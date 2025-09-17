from fastapi import FastAPI
from starlette.responses import StreamingResponse

from internal import model, interface
from internal.controller.http.handler.publication.model import *


def NewHTTP(
        db: interface.IDB,
        publication_controller: interface.IPublicationController,
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

    return app


def include_middleware(
        app: FastAPI,
        http_middleware: interface.IHttpMiddleware,
):
    http_middleware.authorization_middleware04(app)
    http_middleware.logger_middleware03(app)
    http_middleware.metrics_middleware02(app)
    http_middleware.trace_middleware01(app)


def include_publication_handlers(
        app: FastAPI,
        publication_controller: interface.IPublicationController,
        prefix: str
):
    # ПУБЛИКАЦИИ

    # Генерация публикации
    app.add_api_route(
        prefix + "/generate",
        publication_controller.generate_publication,
        methods=["POST"],
        tags=["Publication"],
        response_model=model.Publication,
    )

    # Регенерация изображения публикации
    app.add_api_route(
        prefix + "/{publication_id}/image/regenerate",
        publication_controller.regenerate_publication_image,
        methods=["POST"],
        tags=["Publication"],
        response_model=PublicationResponse,
    )

    # Регенерация текста публикации
    app.add_api_route(
        prefix + "/{publication_id}/text/regenerate",
        publication_controller.regenerate_publication_text,
        methods=["POST"],
        tags=["Publication"],
        response_model=DataResponse,
    )

    # Изменение публикации
    app.add_api_route(
        prefix + "/{publication_id}",
        publication_controller.change_publication,
        methods=["PUT"],
        tags=["Publication"],
        response_model=SuccessResponse,
    )

    # Удаление изображения публикации
    app.add_api_route(
        prefix + "/{publication_id}/image",
        publication_controller.delete_publication_image,
        methods=["DELETE"],
        tags=["Publication"],
        response_model=SuccessResponse,
    )

    # Отправка публикации на модерацию
    app.add_api_route(
        prefix + "/{publication_id}/moderation/send",
        publication_controller.send_publication_to_moderation,
        methods=["POST"],
        tags=["Publication"],
        response_model=SuccessResponse,
    )

    # Модерация публикации
    app.add_api_route(
        prefix + "/moderate",
        publication_controller.moderate_publication,
        methods=["POST"],
        tags=["Publication"],
        response_model=SuccessResponse,
    )

    # Получение публикации по ID
    app.add_api_route(
        prefix + "/{publication_id}",
        publication_controller.get_publication_by_id,
        methods=["GET"],
        tags=["Publication"],
        response_model=DataResponse,
    )

    # Получение публикаций по организации
    app.add_api_route(
        prefix + "/organization/{organization_id}/publications",
        publication_controller.get_publications_by_organization,
        methods=["GET"],
        tags=["Publication"],
        response_model=list[model.Publication],
    )

    # Скачивание изображения публикации
    app.add_api_route(
        prefix + "/{publication_id}/image/download",
        publication_controller.download_publication_image,
        methods=["GET"],
        tags=["Publication"],
        response_class=StreamingResponse,
    )

    # РУБРИКИ

    # Создание рубрики
    app.add_api_route(
        prefix + "/category",
        publication_controller.create_category,
        methods=["POST"],
        tags=["Category"],
        response_model=CategoryResponse,
    )

    # Получение рубрики по ID
    app.add_api_route(
        prefix + "/category/{category_id}",
        publication_controller.get_category_by_id,
        methods=["GET"],
        tags=["Category"],
        response_model=DataResponse,
    )

    # Получение рубрик по организации
    app.add_api_route(
        prefix + "/organization/{organization_id}/categories",
        publication_controller.get_categories_by_organization,
        methods=["GET"],
        tags=["Category"],
        response_model=list[model.Category],
    )

    # Обновление рубрики
    app.add_api_route(
        prefix + "/category/{category_id}",
        publication_controller.update_category,
        methods=["PUT"],
        tags=["Category"],
        response_model=SuccessResponse,
    )

    # Удаление рубрики
    app.add_api_route(
        prefix + "/category/{category_id}",
        publication_controller.delete_category,
        methods=["DELETE"],
        tags=["Category"],
        response_model=SuccessResponse,
    )

    # АВТОПОСТИНГ

    # Создание автопостинга
    app.add_api_route(
        prefix + "/autoposting",
        publication_controller.create_autoposting,
        methods=["POST"],
        tags=["Autoposting"],
        response_model=AutopostingResponse,
    )

    # Получение автопостингов по организации
    app.add_api_route(
        prefix + "/organization/{organization_id}/autopostings",
        publication_controller.get_autoposting_by_organization,
        methods=["GET"],
        tags=["Autoposting"],
        response_model=ListDataResponse,
    )

    # Обновление автопостинга
    app.add_api_route(
        prefix + "/autoposting/{autoposting_id}",
        publication_controller.update_autoposting,
        methods=["PUT"],
        tags=["Autoposting"],
        response_model=SuccessResponse,
    )

    # Удаление автопостинга
    app.add_api_route(
        prefix + "/autoposting/{autoposting_id}",
        publication_controller.delete_autoposting,
        methods=["DELETE"],
        tags=["Autoposting"],
        response_model=SuccessResponse,
    )

    # НАРЕЗКА ВИДЕО

    # Генерация нарезки видео
    app.add_api_route(
        prefix + "/video-cut/generate",
        publication_controller.generate_video_cut,
        methods=["POST"],
        tags=["VideoCut"],
        response_model=VideoCutResponse,
    )

    # Изменение нарезки видео
    app.add_api_route(
        prefix + "/video-cut/{video_cut_id}",
        publication_controller.change_video_cut,
        methods=["PUT"],
        tags=["VideoCut"],
        response_model=SuccessResponse,
    )

    # Отправка нарезки на модерацию
    app.add_api_route(
        prefix + "/video-cut/{video_cut_id}/moderation/send",
        publication_controller.send_video_cut_to_moderation,
        methods=["POST"],
        tags=["VideoCut"],
        response_model=SuccessResponse,
    )

    # Получение нарезки по ID
    app.add_api_route(
        prefix + "/video-cut/{video_cut_id}",
        publication_controller.get_video_cut_by_id,
        methods=["GET"],
        tags=["VideoCut"],
        response_model=DataResponse,
    )

    # Получение нарезок по организации
    app.add_api_route(
        prefix + "/organization/{organization_id}/video-cuts",
        publication_controller.get_video_cuts_by_organization,
        methods=["GET"],
        tags=["VideoCut"],
        response_model=list[model.VideoCut],
    )

    # Модерация нарезки видео
    app.add_api_route(
        prefix + "/video-cut/moderate",
        publication_controller.moderate_video_cut,
        methods=["POST"],
        tags=["VideoCut"],
        response_model=SuccessResponse,
    )

    # Скачивание нарезки видео
    app.add_api_route(
        prefix + "/video-cut/{video_cut_id}/download",
        publication_controller.download_video_cut,
        methods=["GET"],
        tags=["VideoCut"],
        response_class=StreamingResponse,
    )


def include_db_handler(app: FastAPI, db: interface.IDB, prefix: str):
    app.add_api_route(prefix + "/table/create", create_table_handler(db), methods=["GET"])
    app.add_api_route(prefix + "/table/drop", drop_table_handler(db), methods=["GET"])


def create_table_handler(db: interface.IDB):
    async def create_table():
        try:
            await db.multi_query(model.create_organization_tables_queries)
        except Exception as err:
            raise err

    return create_table


def drop_table_handler(db: interface.IDB):
    async def drop_table():
        try:
            await db.multi_query(model.drop_organization_tables_queries)
        except Exception as err:
            raise err

    return drop_table