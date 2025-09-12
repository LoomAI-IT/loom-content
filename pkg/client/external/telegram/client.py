import requests
import json
import time
from typing import Optional, Dict, List, Union, BinaryIO
from urllib.parse import urlencode
import os
from pathlib import Path


class TelegramClient:
    """
    Клиент для работы с Telegram Bot API для публикации постов в каналы
    """

    def __init__(self, bot_token: str):
        """
        Инициализация Telegram клиента

        Args:
            bot_token: Токен бота, полученный от @BotFather
        """
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}/"

    def _api_call(self, method: str, params: Dict = None, files: Dict = None) -> dict | list:
        """
        Выполнение API запроса к Telegram

        Args:
            method: Метод API
            params: Параметры запроса
            files: Файлы для загрузки

        Returns:
            Ответ от API
        """
        url = f"{self.base_url}{method}"

        if files:
            response = requests.post(url, data=params, files=files)
        else:
            response = requests.post(url, json=params)

        if response.status_code != 200:
            raise Exception(f"HTTP ошибка: {response.status_code} - {response.text}")

        result = response.json()

        if not result['ok']:
            error_code = result.get('error_code', 'Unknown')
            description = result.get('description', 'Unknown error')
            raise Exception(f"Telegram API ошибка {error_code}: {description}")

        return result['result']

    def get_me(self) -> Dict:
        """
        Получение информации о боте

        Returns:
            Информация о боте
        """
        return self._api_call('getMe')

    def get_chat(self, chat_id: Union[str, int]) -> Dict:
        """
        Получение информации о чате/канале

        Args:
            chat_id: ID чата или username канала (@channel_name)

        Returns:
            Информация о чате
        """
        params = {'chat_id': chat_id}
        return self._api_call('getChat', params)

    def get_chat_administrators(self, chat_id: Union[str, int]) -> List[Dict]:
        """
        Получение списка администраторов канала

        Args:
            chat_id: ID канала или username (@channel_name)

        Returns:
            Список администраторов
        """
        params = {'chat_id': chat_id}
        return self._api_call('getChatAdministrators', params)

    def send_message(self,
                     chat_id: Union[str, int],
                     text: str,
                     parse_mode: str = 'HTML',
                     disable_web_page_preview: bool = False,
                     disable_notification: bool = False,
                     reply_markup: Dict = None) -> Dict:
        """
        Отправка текстового сообщения

        Args:
            chat_id: ID канала или username (@channel_name)
            text: Текст сообщения
            parse_mode: Режим парсинга (HTML, Markdown, MarkdownV2)
            disable_web_page_preview: Отключить превью ссылок
            disable_notification: Отправить без уведомления
            reply_markup: Inline клавиатура

        Returns:
            Информация об отправленном сообщении
        """
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview,
            'disable_notification': disable_notification
        }

        if reply_markup:
            params['reply_markup'] = json.dumps(reply_markup)

        return self._api_call('sendMessage', params)

    def send_photo(self,
                   chat_id: Union[str, int],
                   photo: Union[str, BinaryIO],
                   caption: str = "",
                   parse_mode: str = 'HTML',
                   disable_notification: bool = False) -> Dict:
        """
        Отправка фото

        Args:
            chat_id: ID канала или username
            photo: Путь к файлу, file-like объект или file_id
            caption: Подпись к фото
            parse_mode: Режим парсинга
            disable_notification: Отправить без уведомления

        Returns:
            Информация об отправленном сообщении
        """
        params = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': parse_mode,
            'disable_notification': disable_notification
        }

        files = None

        # Если это путь к файлу
        if isinstance(photo, str) and os.path.exists(photo):
            files = {'photo': open(photo, 'rb')}
        # Если это file-like объект
        elif hasattr(photo, 'read'):
            files = {'photo': photo}
        # Если это file_id или URL
        else:
            params['photo'] = photo

        try:
            result = self._api_call('sendPhoto', params, files)
            return result
        finally:
            # Закрываем файл если открывали его
            if files and 'photo' in files:
                files['photo'].close()

    def send_media_group(self,
                         chat_id: Union[str, int],
                         media: List[Dict],
                         disable_notification: bool = False) -> List[Dict]:
        """
        Отправка группы медиа (альбом)

        Args:
            chat_id: ID канала или username
            media: Список медиа объектов
            disable_notification: Отправить без уведомления

        Returns:
            Список отправленных сообщений
        """
        params = {
            'chat_id': chat_id,
            'media': json.dumps(media),
            'disable_notification': disable_notification
        }

        return self._api_call('sendMediaGroup', params)

    def send_document(self,
                      chat_id: Union[str, int],
                      document: Union[str, BinaryIO],
                      caption: str = "",
                      parse_mode: str = 'HTML',
                      disable_notification: bool = False) -> Dict:
        """
        Отправка документа

        Args:
            chat_id: ID канала или username
            document: Путь к файлу, file-like объект или file_id
            caption: Подпись к документу
            parse_mode: Режим парсинга
            disable_notification: Отправить без уведомления

        Returns:
            Информация об отправленном сообщении
        """
        params = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': parse_mode,
            'disable_notification': disable_notification
        }

        files = None

        if isinstance(document, str) and os.path.exists(document):
            files = {'document': open(document, 'rb')}
        elif hasattr(document, 'read'):
            files = {'document': document}
        else:
            params['document'] = document

        try:
            result = self._api_call('sendDocument', params, files)
            return result
        finally:
            if files and 'document' in files:
                files['document'].close()

    def send_video(self,
                   chat_id: Union[str, int],
                   video: Union[str, BinaryIO],
                   caption: str = "",
                   parse_mode: str = 'HTML',
                   width: int = None,
                   height: int = None,
                   duration: int = None,
                   disable_notification: bool = False) -> Dict:
        """
        Отправка видео

        Args:
            chat_id: ID канала или username
            video: Путь к файлу, file-like объект или file_id
            caption: Подпись к видео
            parse_mode: Режим парсинга
            width: Ширина видео
            height: Высота видео
            duration: Длительность в секундах
            disable_notification: Отправить без уведомления

        Returns:
            Информация об отправленном сообщении
        """
        params = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': parse_mode,
            'disable_notification': disable_notification
        }

        if width:
            params['width'] = width
        if height:
            params['height'] = height
        if duration:
            params['duration'] = duration

        files = None

        if isinstance(video, str) and os.path.exists(video):
            files = {'video': open(video, 'rb')}
        elif hasattr(video, 'read'):
            files = {'video': video}
        else:
            params['video'] = video

        try:
            result = self._api_call('sendVideo', params, files)
            return result
        finally:
            if files and 'video' in files:
                files['video'].close()

    def edit_message_text(self,
                          chat_id: Union[str, int],
                          message_id: int,
                          text: str,
                          parse_mode: str = 'HTML',
                          disable_web_page_preview: bool = False,
                          reply_markup: Dict = None) -> Dict:
        """
        Редактирование текста сообщения

        Args:
            chat_id: ID канала
            message_id: ID сообщения
            text: Новый текст
            parse_mode: Режим парсинга
            disable_web_page_preview: Отключить превью ссылок
            reply_markup: Inline клавиатура

        Returns:
            Информация об отредактированном сообщении
        """
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview
        }

        if reply_markup:
            params['reply_markup'] = json.dumps(reply_markup)

        return self._api_call('editMessageText', params)

    def delete_message(self, chat_id: Union[str, int], message_id: int) -> bool:
        """
        Удаление сообщения

        Args:
            chat_id: ID канала
            message_id: ID сообщения

        Returns:
            True если сообщение удалено
        """
        params = {
            'chat_id': chat_id,
            'message_id': message_id
        }

        return self._api_call('deleteMessage', params)

    def pin_chat_message(self,
                         chat_id: Union[str, int],
                         message_id: int,
                         disable_notification: bool = False) -> bool:
        """
        Закрепление сообщения в канале

        Args:
            chat_id: ID канала
            message_id: ID сообщения
            disable_notification: Закрепить без уведомления

        Returns:
            True если сообщение закреплено
        """
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'disable_notification': disable_notification
        }

        return self._api_call('pinChatMessage', params)

    def unpin_chat_message(self,
                           chat_id: Union[str, int],
                           message_id: int = None) -> bool:
        """
        Открепление сообщения

        Args:
            chat_id: ID канала
            message_id: ID сообщения (если не указано, открепляется последнее)

        Returns:
            True если сообщение откреплено
        """
        params = {'chat_id': chat_id}

        if message_id:
            params['message_id'] = message_id

        return self._api_call('unpinChatMessage', params)

    def create_inline_keyboard(self, buttons: List[List[Dict]]) -> Dict:
        """
        Создание inline клавиатуры

        Args:
            buttons: Массив кнопок [
                [{"text": "Кнопка 1", "url": "https://example.com"}],
                [{"text": "Кнопка 2", "callback_data": "button2"}]
            ]

        Returns:
            Объект inline клавиатуры
        """
        return {"inline_keyboard": buttons}

    def format_text(self,
                    text: str,
                    bold: List[str] = None,
                    italic: List[str] = None,
                    code: List[str] = None,
                    links: Dict[str, str] = None) -> str:
        """
        Форматирование текста для HTML parse_mode

        Args:
            text: Исходный текст
            bold: Список слов для выделения жирным
            italic: Список слов для выделения курсивом
            code: Список слов для выделения моноширинным шрифтом
            links: Словарь {текст: ссылка} для создания ссылок

        Returns:
            Отформатированный текст
        """
        formatted_text = text

        if bold:
            for word in bold:
                formatted_text = formatted_text.replace(word, f"<b>{word}</b>")

        if italic:
            for word in italic:
                formatted_text = formatted_text.replace(word, f"<i>{word}</i>")

        if code:
            for word in code:
                formatted_text = formatted_text.replace(word, f"<code>{word}</code>")

        if links:
            for text_link, url in links.items():
                formatted_text = formatted_text.replace(
                    text_link,
                    f'<a href="{url}">{text_link}</a>'
                )

        return formatted_text

    def schedule_message(self,
                         chat_id: Union[str, int],
                         text: str,
                         schedule_time: int,
                         **kwargs) -> Dict:
        """
        Планирование отложенного сообщения (через внешний сервис или собственную реализацию)

        Args:
            chat_id: ID канала
            text: Текст сообщения
            schedule_time: Unix timestamp времени отправки
            **kwargs: Дополнительные параметры для send_message

        Returns:
            Информация о запланированном сообщении
        """
        # Это базовая реализация - в реальном проекте стоит использовать
        # планировщик задач типа Celery, APScheduler или внешний сервис

        current_time = int(time.time())
        delay = schedule_time - current_time

        if delay <= 0:
            # Отправляем сразу если время уже прошло
            return self.send_message(chat_id, text, **kwargs)
        else:
            # В реальном проекте здесь должна быть постановка в очередь
            raise NotImplementedError(
                "Для отложенных сообщений нужно настроить планировщик задач"
            )


# Пример использования
if __name__ == "__main__":
    # Инициализация клиента
    tg_client = TelegramClient("YOUR_BOT_TOKEN")

    # Проверка бота
    try:
        bot_info = tg_client.get_me()
        print(f"Бот активен: @{bot_info['username']}")
    except Exception as e:
        print(f"Ошибка: {e}")

    # Отправка текстового поста
    # tg_client.send_message(
    #     chat_id="@your_channel",
    #     text="<b>Заголовок поста</b>\n\nТекст поста с <i>курсивом</i> и <code>кодом</code>"
    # )

    # Отправка поста с фото
    # tg_client.send_photo(
    #     chat_id="@your_channel",
    #     photo="path/to/image.jpg",
    #     caption="<b>Пост с фотографией</b>\n\nОписание к фото"
    # )

    # Создание поста с кнопками
    # keyboard = tg_client.create_inline_keyboard([
    #     [{"text": "Наш сайт", "url": "https://example.com"}],
    #     [{"text": "Контакты", "url": "https://t.me/support"}]
    # ])
    #
    # tg_client.send_message(
    #     chat_id="@your_channel",
    #     text="Пост с кнопками",
    #     reply_markup=keyboard
    # )