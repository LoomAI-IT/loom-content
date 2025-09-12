import requests
import time


class InstagramReelsPublisher:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"

    def create_media_container(
            self,
            instagram_account_id: str,
            instagram_access_token: str,
            video_url: str,
            caption: str,
            thumb_offset: str = None
    ) -> dict:
        endpoint = f"{self.base_url}/{instagram_account_id}/media"

        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": instagram_access_token
        }

        if thumb_offset:
            payload["thumb_offset"] = thumb_offset

        try:
            response = requests.post(endpoint, data=payload)
            response.raise_for_status()

            result = response.json()
            return result

        except Exception as err:
            raise err

    def check_media_status(self, instagram_access_token: str, creation_id: str) -> dict:
        endpoint = f"{self.base_url}/{creation_id}"
        params = {
            "fields": "status_code",
            "access_token": instagram_access_token
        }

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()


        except Exception as err:
            raise err

    def publish_media(
            self,
            instagram_account_id: str,
            instagram_access_token: str,
            creation_id: str
    ) -> dict:
        endpoint = f"{self.base_url}/{instagram_account_id}/media_publish"

        payload = {
            "creation_id": creation_id,
            "access_token": instagram_access_token
        }

        try:
            response = requests.post(endpoint, data=payload)
            response.raise_for_status()

            return response.json()


        except Exception as err:
            raise err

    def publish_reel(
            self,
            instagram_account_id: str,
            instagram_access_token: str,
            video_url: str,
            caption: str,
            thumb_offset: str = None
    ) -> dict:

        try:
            container_response = self.create_media_container(
                instagram_account_id=instagram_account_id,
                instagram_access_token=instagram_access_token,
                video_url=video_url,
                caption=caption,
                thumb_offset=thumb_offset
            )

            creation_id = container_response.get("id")

            # if not self.wait_for_processing(creation_id):
            #     raise RuntimeError("Ошибка обработки видео")
            #
            # # Шаг 3: Публикация
            # logger.info("Публикация Reels...")
            # publish_response = self.publish_media(creation_id)
            #
            # logger.info("Reels успешно опубликован!")
            # return publish_response

        except Exception as e:
            raise

