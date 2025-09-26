from aiogram import Bot
from aiogram.types import (
    Message, BufferedInputFile,
)

from internal import interface


class TelegramClient(interface.ITelegramClient):
    def __init__(
            self,
            bot_token: str,
    ):
        self.bot = Bot(token=bot_token)

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
                parse_mode=parse_mode,
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
                parse_mode=parse_mode,
            )

            return message

        except Exception as e:
            raise