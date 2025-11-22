import uuid

from src.api_client import APIClient
from src.db_client import DBClient


class TestPosts:
    """
    Набор тестов для эндпоинта /wp/v2/posts.
    Включает в себя CRUD операции и проверки валидации.
    """
    def test_create_post(
        self,
        api_client: APIClient,
        db_client: DBClient
    ):
        unique_id = str(uuid.uuid4())
        title = f"Auto Test Title {unique_id}"
        content = "Test content body"
        payload = {
            "title": title,
            "content": content,
            "status": "publish"
        }
        post_id = None

        response = api_client.create_post(payload)
        try:
            assert response.status_code == 201, f"Ожидался 201, пришел {response.status_code}"
            data = response.json()
            post_id = data["id"]

            assert data["title"]["raw"] == title
            assert data["status"] == "publish"
            assert post_id is not None

            db_post = db_client.get_post_by_id(post_id)

            assert db_post is not None, "Пост не найден в базе данных!"
            assert db_post["post_title"] == title
            assert db_post["post_content"] == content
            assert db_post["post_status"] == "publish"
        finally:
            if post_id is not None:
                api_client.delete_post(post_id, force=True)

    def test_create_post_invalid_status(
        self,
        api_client: APIClient,
        db_client: DBClient
    ):
        unique_id = str(uuid.uuid4())
        title = f"Auto Test Title {unique_id}"

        payload = {
            "title": title,
            "content": "Test content",
            "status": "invalid_status_xyz"
        }

        response = api_client.create_post(payload)

        assert response.status_code == 400, f"Ожидался 400, пришел {response.status_code}"

        response_data = response.json()
        assert response_data["code"] == "rest_invalid_param"
        assert "status" in response_data["data"]["params"]

        assert (
            db_client.post_exists_with_title(title) is False
        ), f"Пост с заголовком '{title}' был создан в БД, хотя не должен был!"

    def test_get_post_by_id(
        self,
        api_client: APIClient,
        db_client: DBClient,
        make_post
    ):
        post = make_post()
        post_id = post["id"]
        expected_title = post["title"]["raw"]
        expected_status = post["status"]

        response = api_client.get_post(post_id, params={"context": "edit"})

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == post_id
        assert response_data["title"]["raw"] == expected_title
        assert response_data["status"] == expected_status

        db_post = db_client.get_post_by_id(post_id)
        assert db_post["post_title"] == expected_title
        assert db_post["post_status"] == expected_status

    def test_get_non_existent_post(
        self,
        api_client: APIClient,
        db_client: DBClient
    ):
        non_existent_id = 0
        response = api_client.get_post(non_existent_id)

        assert response.status_code == 404, f"Ожидался 404, пришел {response.status_code}"

        response_data = response.json()
        assert response_data["code"] == "rest_post_invalid_id"

        exists = db_client.post_exists(non_existent_id)
        assert exists is False, f"ID {non_existent_id} внезапно нашелся в БД!"

    def test_list_posts(
        self,
        api_client: APIClient,
        db_client: DBClient,
        make_post):
        first_post = make_post()
        second_post = make_post()

        target_ids = [first_post["id"], second_post["id"]]
        include_param = f"{first_post['id']},{second_post['id']}"

        response = api_client.list_posts(params={"include": include_param})

        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)

        returned_ids = [item["id"] for item in response_data]
        assert first_post["id"] in returned_ids
        assert second_post["id"] in returned_ids

        count = db_client.count_posts_by_ids(target_ids)
        assert count == 2, f"Ожидалось найти 2 записи в БД, найдено {count}"

    def test_update_post(
        self,
        api_client: APIClient,
        db_client: DBClient,
        make_post
    ):
        post = make_post()
        post_id = post["id"]

        new_title = post["title"]["raw"] + " and Updated"
        new_content = "Updated Content"

        response = api_client.update_post(post_id, {
            "title": new_title,
            "content": new_content
        })

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["title"]["raw"] == new_title
        assert response_data["content"]["raw"] == new_content

        db_post = db_client.get_post_by_id(post_id)
        assert db_post["post_title"] == new_title
        assert db_post["post_content"] == new_content

    def test_delete_post(
        self,
        api_client: APIClient,
        db_client: DBClient,
        make_post
    ):
        post = make_post()
        post_id = post["id"]

        response = api_client.delete_post(post_id, force=True)

        assert response.status_code == 200

        response_data = response.json()
        assert response_data["deleted"] is True
        assert response_data["previous"]["id"] == post_id
        assert db_client.post_exists(post_id) is False
