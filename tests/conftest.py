import uuid

import pytest

from src.api_client import APIClient
from src.db_client import DBClient


@pytest.fixture
def api_client():
    """
    Фикстура для работы с API.
    Создает экземпляр клиента для каждого теста.
    """
    return APIClient()

@pytest.fixture
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
def make_post(api_client: APIClient):
    """
    Создает пост и автоматически удаляет его после теста.
    """
    created_posts_ids = []

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
        created_posts_ids.append(post_id)
        return data

    yield _make_post

    for post_id in created_posts_ids:
        api_client.delete_post(post_id, force=True)
