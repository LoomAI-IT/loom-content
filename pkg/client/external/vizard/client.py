import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging


@dataclass
class VizardConfig:
    """Конфигурация для VizardClient"""
    base_url: str
    api_key: str
    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True


class VizardError(Exception):
    """Базовое исключение для VizardClient"""
    pass


class VizardAuthError(VizardError):
    """Ошибка аутентификации"""
    pass


class VizardAPIError(VizardError):
    """Ошибка API"""

    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class VizardClient:
    """
    Клиент для работы с Vizard API

    Пример использования:
        config = VizardConfig(
            base_url="https://api.vizard.ai",
            api_key="your-api-key"
        )
        client = VizardClient(config)

        # Создать проект
        project = client.create_project("My Project", "Description")

        # Загрузить видео
        video = client.upload_video(project["id"], "/path/to/video.mp4")

        # Получить результаты анализа
        results = client.get_analysis_results(video["id"])
    """

    def __init__(self, config: VizardConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'VizardClient/1.0'
        })
        self.session.verify = config.verify_ssl

        self.logger = logging.getLogger(__name__)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполняет HTTP запрос с обработкой ошибок и повторными попытками"""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        for attempt in range(self.config.max_retries):
            try:
                self.logger.debug(f"Выполняется {method} запрос к {url}, попытка {attempt + 1}")

                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.config.timeout,
                    **kwargs
                )

                if response.status_code == 401:
                    raise VizardAuthError("Неверный API ключ или токен истёк")

                if response.status_code == 429:
                    self.logger.warning("Превышен лимит запросов, повторная попытка...")
                    continue

                response.raise_for_status()

                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"success": True, "data": response.text}

            except requests.exceptions.Timeout:
                if attempt == self.config.max_retries - 1:
                    raise VizardError(f"Превышено время ожидания после {self.config.max_retries} попыток")
                continue

            except requests.exceptions.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise VizardAPIError(
                        f"Ошибка API: {str(e)}",
                        getattr(response, 'status_code', None),
                        getattr(response, 'json', lambda: {})()
                    )
                continue

        raise VizardError("Не удалось выполнить запрос после всех попыток")

    def get_projects(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Получить список проектов"""
        params = {"limit": limit, "offset": offset}
        response = self._make_request("GET", "/projects", params=params)
        return response.get("data", [])

    def create_project(self, name: str, description: str = "") -> Dict[str, Any]:
        """Создать новый проект"""
        data = {
            "name": name,
            "description": description
        }
        response = self._make_request("POST", "/projects", json=data)
        return response.get("data", {})

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Получить информацию о проекте"""
        response = self._make_request("GET", f"/projects/{project_id}")
        return response.get("data", {})

    def update_project(self, project_id: str, name: str = None, description: str = None) -> Dict[str, Any]:
        """Обновить проект"""
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description

        response = self._make_request("PUT", f"/projects/{project_id}", json=data)
        return response.get("data", {})

    def delete_project(self, project_id: str) -> bool:
        """Удалить проект"""
        self._make_request("DELETE", f"/projects/{project_id}")
        return True

    def upload_video(self, project_id: str, video_path: str,
                     metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Загрузить видео в проект"""
        try:
            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                data = {'project_id': project_id}

                if metadata:
                    data.update(metadata)

                # Временно убираем Content-Type для multipart/form-data
                headers = self.session.headers.copy()
                headers.pop('Content-Type', None)

                response = self.session.post(
                    f"{self.config.base_url}/videos/upload",
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=self.config.timeout * 3  # Увеличиваем таймаут для загрузки
                )

                response.raise_for_status()
                return response.json().get("data", {})

        except FileNotFoundError:
            raise VizardError(f"Файл не найден: {video_path}")
        except Exception as e:
            raise VizardError(f"Ошибка загрузки видео: {str(e)}")

    def get_videos(self, project_id: str = None) -> List[Dict[str, Any]]:
        """Получить список видео"""
        params = {}
        if project_id:
            params["project_id"] = project_id

        response = self._make_request("GET", "/videos", params=params)
        return response.get("data", [])

    def get_video(self, video_id: str) -> Dict[str, Any]:
        """Получить информацию о видео"""
        response = self._make_request("GET", f"/videos/{video_id}")
        return response.get("data", {})

    def start_analysis(self, video_id: str, analysis_type: str = "full") -> Dict[str, Any]:
        """Запустить анализ видео"""
        data = {"analysis_type": analysis_type}
        response = self._make_request("POST", f"/videos/{video_id}/analyze", json=data)
        return response.get("data", {})

    def get_analysis_status(self, video_id: str) -> Dict[str, Any]:
        """Получить статус анализа"""
        response = self._make_request("GET", f"/videos/{video_id}/analysis/status")
        return response.get("data", {})

    def get_analysis_results(self, video_id: str) -> Dict[str, Any]:
        """Получить результаты анализа"""
        response = self._make_request("GET", f"/videos/{video_id}/analysis/results")
        return response.get("data", {})

    def export_results(self, video_id: str, format: str = "json") -> Dict[str, Any]:
        """Экспортировать результаты анализа"""
        params = {"format": format}
        response = self._make_request("GET", f"/videos/{video_id}/export", params=params)
        return response.get("data", {})

    def get_user_info(self) -> Dict[str, Any]:
        """Получить информацию о текущем пользователе"""
        response = self._make_request("GET", "/user/profile")
        return response.get("data", {})

    def get_usage_stats(self) -> Dict[str, Any]:
        """Получить статистику использования"""
        response = self._make_request("GET", "/user/usage")
        return response.get("data", {})