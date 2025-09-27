from aiogram import Bot
from aiogram.types import BufferedInputFile
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
    ) -> str:
        try:
            message = await self.bot.send_message(
                chat_id="@"+channel_id,
                text=text,
                parse_mode=SULGUK_PARSE_MODE,
            )
            post_link = self._create_post_link(str(channel_id), message.message_id)
            return post_link

        except Exception as e:
            raise

    async def send_photo(
            self,
            channel_id: str | int,
            photo: bytes,
            caption: str = None,
            parse_mode: str = None,
    ) -> str:
        try:
            photo_input = BufferedInputFile(photo, "file")

            message = await self.bot.send_photo(
                chat_id="@"+channel_id,
                photo=photo_input,
                caption=caption,
                parse_mode=SULGUK_PARSE_MODE,
            )
            post_link = self._create_post_link(str(channel_id), message.message_id)
            return post_link

        except Exception as e:
            raise

    async def check_permission(
            self,
            channel_id: str | int,
    ) -> bool:
        try:
            chat = await self.bot.get_chat(chat_id="@" + channel_id)
            print(f"{chat=}")

            bot_member = await self.bot.get_chat_member(
                chat_id="@" + channel_id,
                user_id=self.bot.id
            )
            print(f"{bot_member=}")

            allowed_statuses = ["administrator", "creator"]

            if bot_member.status in allowed_statuses:
                return True
            elif bot_member.status == "member":

                if chat.type in ["channel", "supergroup"]:
                    return False
                else:
                    return True
            else:
                return False

        except Exception as e:
            return False

    def _create_post_link(self, channel_username: str, message_id: int) -> str:
        clean_username = channel_username.lstrip('@')
        return f"https://t.me/{clean_username}/{message_id}"