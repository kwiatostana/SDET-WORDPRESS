from typing import Any

import allure
import requests
from requests import Response
from requests.auth import HTTPBasicAuth

from config import Config


class APIClient:
    def __init__(self) -> None:
        """
        Инициализация клиента.
        Создает сессию, чтобы сохранять авторизацию между запросами.
        """
        self.base_url: str = Config.BASE_URL
        self.timeout: int = Config.TIMEOUT
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(Config.API_USER, Config.API_PASSWORD)
        self.session.headers.setdefault("Accept", "application/json")

    def _request(self, method: str, path: str, **kwargs: Any) -> Response:
        """
        Унифицирует вызовы requests.Session и навешивает таймаут по умолчанию.
        """
        kwargs.setdefault("timeout", self.timeout)
        url = f"{self.base_url}{path}"
        return self.session.request(method=method, url=url, **kwargs)

    @allure.step("Отправить POST /wp/v2/posts для создания поста")
    def create_post(self, post_data: dict[str, Any]) -> Response:
        """
        Создает новый пост.
        """
        return self._request("post", "wp/v2/posts", json=post_data)

    @allure.step("Отправить GET /wp/v2/posts/{post_id} для получения поста")
    def get_post(self, post_id: int, params: dict[str, Any] | None = None) -> Response:
        """Получает пост по ID."""
        return self._request("get", f"wp/v2/posts/{post_id}", params=params)

    @allure.step("Отправить GET /wp/v2/posts&include=<ids> для получения списка постов")
    def list_posts(self, params: dict[str, Any] | None = None) -> Response:
        """
        Получает список постов с фильтрацией.
        """
        return self._request("get", "wp/v2/posts", params=params)

    @allure.step("Отправить POST /wp/v2/posts/{post_id} для обновления поста")
    def update_post(self, post_id: int, update_data: dict[str, Any]) -> Response:
        """Обновляет пост."""
        return self._request("post", f"wp/v2/posts/{post_id}", json=update_data)

    @allure.step("Отправить DELETE /wp/v2/posts/{post_id} для удаления поста")
    def delete_post(self, post_id: int, force: bool = True) -> Response:
        """
        Удаляет пост.
        """
        params = {"force": str(force).lower()}
        return self._request("delete", f"wp/v2/posts/{post_id}", params=params)
