import allure
import requests
from requests.auth import HTTPBasicAuth

from config import Config


class APIClient:
    def __init__(self):
        """
        Инициализация клиента.
        Создает сессию, чтобы сохранять авторизацию между запросами.
        """
        self.base_url = Config.BASE_URL
        self.timeout = Config.TIMEOUT
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(Config.API_USER, Config.API_PASSWORD)
        self.session.headers.setdefault("Accept", "application/json")

    @allure.step("API реквест: {method} {path}")
    def _request(self, method, path, **kwargs):
        """
        Унифицирует вызовы requests.Session и навешивает таймаут по умолчанию.
        """
        kwargs.setdefault("timeout", self.timeout)
        url = f"{self.base_url}{path}"
        return self.session.request(method=method, url=url, **kwargs)

    @allure.step("Создаем пост")
    def create_post(self, post_data):
        """
        Создает новый пост.
        """
        return self._request("post", "wp/v2/posts", json=post_data)

    @allure.step("Получаем пост {post_id}")
    def get_post(self, post_id, params=None):
        """Получает пост по ID."""
        return self._request("get", f"wp/v2/posts/{post_id}", params=params)

    @allure.step("Получаем список постов")
    def list_posts(self, params=None):
        """
        Получает список постов с фильтрацией.
        """
        return self._request("get", "wp/v2/posts", params=params)

    @allure.step("Обновляем пост {post_id}")
    def update_post(self, post_id, update_data):
        """Обновляет пост."""
        return self._request("post", f"wp/v2/posts/{post_id}", json=update_data)

    @allure.step("Удаляем пост {post_id}")
    def delete_post(self, post_id, force=True):
        """
        Удаляет пост.
        """
        params = {"force": str(force).lower()}
        return self._request("delete", f"wp/v2/posts/{post_id}", params=params)
