import uuid

import allure
import pytest

from src.api_client import APIClient
from src.db_client import DBClient


@pytest.fixture
@allure.title("Готовим API клиента")
def api_client():
    """
    Фикстура для работы с API.
    Создает экземпляр клиента для каждого теста.
    """
    return APIClient()

@pytest.fixture
@allure.title("Готовим DB клиента")
def db_client():
    """
    Фикстура для работы с БД.
    Создает клиента и передает его в тест.
    После теста закрывает соединение.
    """
    client = DBClient()
    yield client
    client.close()

@pytest.fixture
@allure.title("Настраиваем пост-очистку")
def cleanup_posts(db_client: DBClient):
    """
    Фикстура для безопасной очистки постов после теста.
    Собирает ID постов для удаления и безопасно удаляет их через БД,
    проверяя существование перед удалением.
    """
    posts_to_cleanup = []

    def _register_post(post_id):
        """Регистрирует пост для очистки после теста."""
        posts_to_cleanup.append(post_id)

    yield _register_post

    for post_id in posts_to_cleanup:
        if db_client.post_exists(post_id):
            db_client.delete_post(post_id)

@pytest.fixture
@allure.title("Готовим фабрику постов")
def make_post(api_client: APIClient, cleanup_posts):
    """
    Создает пост и автоматически удаляет его после теста.
    """
    def _make_post(title=None, content="Default Content", status="publish"):
        if title is None:
            title = f"Auto Test Title {uuid.uuid4()}"

        payload = {
            "title": title,
            "content": content,
            "status": status
        }
        response = api_client.create_post(payload)
        if response.status_code != 201:
            pytest.fail(
                f"Не удалось создать пост '{title}': {response.status_code} - {response.text}"
            )
        data = response.json()
        post_id = data["id"]
        cleanup_posts(post_id)
        return data

    return _make_post
