from aiogram import Bot
from aiogram.types import (
    Message, BufferedInputFile,
)
from sulguk import SULGUK_PARSE_MODE, AiogramSulgukMiddleware

from internal import interface


class TelegramClient(interface.ITelegramClient):
    def __init__(
            self,
            bot_token: str,
    ):
        self.bot = Bot(token=bot_token)
        self.bot.session.middleware(AiogramSulgukMiddleware())

    async def send_text_message(
            self,
            channel_id: str | int,
            text: str,
            parse_mode: str = None,
    ) -> Message:
        try:
            message = await self.bot.send_message(
                chat_id="@"+channel_id,
                text=text,
                parse_mode=SULGUK_PARSE_MODE,
            )

            return message

        except Exception as e:
            raise

    async def send_photo(
            self,
            channel_id: str | int,
            photo: bytes,
            caption: str = None,
            parse_mode: str = None,
    ) -> Message:
        try:
            photo_input = BufferedInputFile(photo, "file")

            message = await self.bot.send_photo(
                chat_id="@"+channel_id,
                photo=photo_input,
                caption=caption,
                parse_mode=SULGUK_PARSE_MODE,
            )

            return message

        except Exception as e:
            raise