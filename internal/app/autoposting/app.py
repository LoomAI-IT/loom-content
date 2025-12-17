import asyncio
import traceback
from datetime import datetime

from internal import interface, model


class Autoposting:
    def __init__(
        self,
        tel: interface.ITelemetry,
        publication_service: interface.IPublicationService,
        autoposting_service: interface.IAutopostingService,
    ):
        self.tel = tel
        self.logger = tel.logger()
        self.publication_service = publication_service
        self.autoposting_service = autoposting_service

    async def run(self):
        self.logger.info("Сервис автопостинга запущен")

        while True:
            try:
                self.logger.info("Начата новая итерация автопостинга")

                active_autopostings = await self.autoposting_service.get_active_autopostings()

                if not active_autopostings:
                    self.logger.info("Нет автопостингов для обработки")
                    return

                for autoposting in active_autopostings:
                    await self._process_autoposting(autoposting)

                self.logger.info(f"Итерация завершена, обработано автопостингов: {len(active_autopostings)}")

                await asyncio.sleep(1 * 60)
            except Exception as err:
                await self._handle_critical_error(err)

    async def _process_autoposting(self, autoposting: model.Autoposting):
        try:
            self.logger.info(f"Обработка автопостинга {autoposting.id}, организация {autoposting.organization_id}, каналов {len(autoposting.tg_channels)}")

            suitable_posts = []

            for channel_username in autoposting.tg_channels:
                channel_suitable_posts = await self.autoposting_service.get_suitable_posts(autoposting, channel_username)
                suitable_posts.extend(channel_suitable_posts)
                if len(channel_suitable_posts) == 1:
                    break

            self.logger.info(f"Найдено подходящих постов: {len(suitable_posts)}")

            await self.autoposting_service.create_publication_from_random_suitable_post(autoposting, suitable_posts)
            await self.autoposting_service.update_autoposting(
                autoposting_id=autoposting.id,
                last_active=datetime.now()
            )

        except Exception as autoposting_err:
            self.logger.error(f"Ошибка при обработке автопостинга {autoposting.id}: {autoposting_err}")

    async def _handle_critical_error(self, err: Exception):
        self.logger.error(f"Критическая ошибка в главном цикле: {err}")
        self.logger.error(traceback.format_exc())
        await asyncio.sleep(1 * 60)
