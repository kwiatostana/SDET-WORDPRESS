import uuid
from collections.abc import Callable
from typing import Any

import allure
import pytest

from src.api_client import APIClient
from src.db_client import DBClient


@pytest.fixture
@allure.title("Готовим API клиента")
def api_client() -> APIClient:
    """
    Фикстура для работы с API.
    Создает экземпляр клиента для каждого теста.
    """
    return APIClient()


@pytest.fixture
@allure.title("Готовим DB клиента")
def db_client() -> DBClient:
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
def cleanup_posts(db_client: DBClient) -> Callable[[int], None]:
    """
    Фикстура для безопасной очистки постов после теста.
    Собирает ID постов для удаления и безопасно удаляет их через БД,
    проверяя существование перед удалением.
    """
    posts_to_cleanup: list[int] = []

    def _register_post(post_id: int) -> None:
        """Регистрирует пост для очистки после теста."""
        posts_to_cleanup.append(post_id)

    yield _register_post

    for post_id in posts_to_cleanup:
        if db_client.post_exists(post_id):
            db_client.delete_post(post_id)


@pytest.fixture
@allure.title("Готовим фабрику постов")
def make_post(
    api_client: APIClient, cleanup_posts: Callable[[int], None]
) -> Callable[[str | None, str, str], dict[str, Any]]:
    """
    Создает пост и автоматически удаляет его после теста.
    """

    def _make_post(
        title: str | None = None, content: str = "Default Content", status: str = "publish"
    ) -> dict[str, Any]:
        if title is None:
            title = f"Auto Test Title {uuid.uuid4()}"

        payload = {"title": title, "content": content, "status": status}
        response = api_client.create_post(payload)
        if response.status_code != 201:
            pytest.fail(f"Не удалось создать пост '{title}': {response.status_code} - {response.text}")
        data = response.json()
        post_id = data["id"]
        cleanup_posts(post_id)
        return data

    return _make_post


@pytest.fixture
@allure.title("Готовим фабрику постов через SQL")
def make_post_via_sql(
    db_client: DBClient, cleanup_posts: Callable[[int], None]
) -> Callable[[str, str, str, int, str], dict[str, Any]]:
    """
    Создает пост напрямую через SQL INSERT и автоматически удаляет его после теста.
    Автоматически подставляет UUID в строки с плейсхолдером {uuid}.
    """

    def _make_post_via_sql(
        post_title: str,
        post_content: str,
        post_status: str = "publish",
        post_author: int = 1,
        uuid_placeholder: str = "{uuid}",
    ) -> dict[str, Any]:
        unique_id = str(uuid.uuid4())

        def apply_uuid(value: str) -> str:
            if isinstance(value, str) and uuid_placeholder in value:
                return value.replace(uuid_placeholder, unique_id)
            return value

        resolved_title = apply_uuid(post_title)
        resolved_content = apply_uuid(post_content)

        post_id = db_client.create_post_via_sql(
            post_title=resolved_title,
            post_content=resolved_content,
            post_status=post_status,
            post_author=post_author,
        )
        cleanup_posts(post_id)

        return {
            "id": post_id,
            "title": {"raw": resolved_title},
            "content": {"raw": resolved_content},
            "status": post_status,
            "uuid": unique_id,
        }

    return _make_post_via_sql
