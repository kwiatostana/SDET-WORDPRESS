import uuid

import allure

from src.api_client import APIClient
from src.db_client import DBClient


@allure.epic("WordPress Posts API")
@allure.feature("CRUD операции с постами")
class TestPosts:
    """
    Набор тестов для эндпоинта /wp/v2/posts.
    Включает в себя CRUD операции и проверки валидации.
    """
    @allure.title("Создаем пост через API и проверяем в БД")
    def test_create_post(
        self,
        api_client: APIClient,
        db_client: DBClient,
        cleanup_posts
    ):
        unique_id = str(uuid.uuid4())
        title = f"Auto Test Title {unique_id}"
        content = "Test content body"
        payload = {
            "title": title,
            "content": content,
            "status": "publish"
        }

        with allure.step("Создаем пост через API"):
            response = api_client.create_post(payload)
            assert response.status_code == 201, f"Ожидался 201, пришел {response.status_code}"
            data = response.json()
            post_id = data["id"]
            cleanup_posts(post_id)

        with allure.step("Проверяем ответ API"):
            assert data["title"]["raw"] == title, f"Заголовок поста не совпадает. Ожидалось: '{title}', получено: '{data['title']['raw']}'"
            assert data["status"] == "publish", f"Статус поста не совпадает. Ожидалось: 'publish', получено: '{data['status']}'"
            assert post_id is not None, "ID поста не должен быть None"

        with allure.step("Проверяем запись в БД"):
            db_post = db_client.get_post_by_id(post_id)
            assert db_post is not None, "Пост не найден в базе данных!"
            assert db_post["post_title"] == title, f"Заголовок поста в БД не совпадает. Ожидалось: '{title}', получено: '{db_post['post_title']}'"
            assert db_post["post_content"] == content, f"Содержимое поста в БД не совпадает. Ожидалось: '{content}', получено: '{db_post['post_content']}'"
            assert db_post["post_status"] == "publish", f"Статус поста в БД не совпадает. Ожидалось: 'publish', получено: '{db_post['post_status']}'"

    @allure.title("Создаем пост с невалидным статусом")
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

        with allure.step("Вызываем API со статусом 400"):
            response = api_client.create_post(payload)
            assert response.status_code == 400, f"Ожидался 400, пришел {response.status_code}"

        with allure.step("Проверяем тело ответа"):
            response_data = response.json()
            assert response_data["code"] == "rest_invalid_param", f"Код ошибки не совпадает. Ожидалось: 'rest_invalid_param', получено: '{response_data['code']}'"
            assert "status" in response_data["data"]["params"], "Параметр 'status' отсутствует в списке невалидных параметров"

        with allure.step("Убеждаемся, что пост не создали в БД"):
            assert (
                db_client.post_exists_with_title(title) is False
            ), f"Пост с заголовком '{title}' был создан в БД, хотя не должен был!"

    @allure.title("Получаем пост по ID")
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

        with allure.step("Запрашиваем пост через API"):
            response = api_client.get_post(post_id, params={"context": "edit"})
            assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
            response_data = response.json()
            assert response_data["id"] == post_id, f"ID поста не совпадает. Ожидалось: {post_id}, получено: {response_data['id']}"
            assert response_data["title"]["raw"] == expected_title, f"Заголовок поста не совпадает. Ожидалось: '{expected_title}', получено: '{response_data['title']['raw']}'"
            assert response_data["status"] == expected_status, f"Статус поста не совпадает. Ожидалось: '{expected_status}', получено: '{response_data['status']}'"

        with allure.step("Проверяем с БД"):
            db_post = db_client.get_post_by_id(post_id)
            assert db_post["post_title"] == expected_title, f"Заголовок поста в БД не совпадает. Ожидалось: '{expected_title}', получено: '{db_post['post_title']}'"
            assert db_post["post_status"] == expected_status, f"Статус поста в БД не совпадает. Ожидалось: '{expected_status}', получено: '{db_post['post_status']}'"

    @allure.title("Получаем несуществующий пост")
    def test_get_non_existent_post(
        self,
        api_client: APIClient,
        db_client: DBClient
    ):
        non_existent_id = 0

        with allure.step("Вызываем API для несуществующего поста"):
            response = api_client.get_post(non_existent_id)
            assert response.status_code == 404, f"Ожидался 404, пришел {response.status_code}"

        with allure.step("Проверяем ответ сервера"):
            response_data = response.json()
            assert response_data["code"] == "rest_post_invalid_id", f"Код ошибки не совпадает. Ожидалось: 'rest_post_invalid_id', получено: '{response_data['code']}'"

        with allure.step("Убеждаемся, что записи нет в БД"):
            exists = db_client.post_exists(non_existent_id)
            assert exists is False, f"ID {non_existent_id} внезапно нашелся в БД!"

    @allure.title("Получаем список постов по include")
    def test_list_posts(
        self,
        api_client: APIClient,
        db_client: DBClient,
        make_post):
        with allure.step("Готовим два поста"):
            first_post = make_post()
            second_post = make_post()
            target_ids = [first_post["id"], second_post["id"]]
            include_param = f"{first_post['id']},{second_post['id']}"

        with allure.step("Запрашиваем список по include"):
            response = api_client.list_posts(params={"include": include_param})
            assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
            response_data = response.json()
            assert isinstance(response_data, list), f"Ответ должен быть списком, получен тип: {type(response_data)}"

        with allure.step("Проверяем, что вернулись нужные ID"):
            returned_ids = [item["id"] for item in response_data]
            assert first_post["id"] in returned_ids, f"ID первого поста ({first_post['id']}) отсутствует в списке возвращенных постов"
            assert second_post["id"] in returned_ids, f"ID второго поста ({second_post['id']}) отсутствует в списке возвращенных постов"

        with allure.step("Сверяем количество записей в БД"):
            count = db_client.count_posts_by_ids(target_ids)
            assert count == 2, f"Ожидалось найти 2 записи в БД, найдено {count}"

    @allure.title("Обновляем существующий пост")
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
        payload = {"title": new_title, "content": new_content}

        with allure.step("Отправляем запрос на обновление"):
            response = api_client.update_post(post_id, payload)
            assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
            response_data = response.json()
            assert response_data["title"]["raw"] == new_title, f"Заголовок поста не обновлен. Ожидалось: '{new_title}', получено: '{response_data['title']['raw']}'"
            assert response_data["content"]["raw"] == new_content, f"Содержимое поста не обновлено. Ожидалось: '{new_content}', получено: '{response_data['content']['raw']}'"

        with allure.step("Проверяем, что изменения попали в БД"):
            db_post = db_client.get_post_by_id(post_id)
            assert db_post["post_title"] == new_title, f"Заголовок поста в БД не обновлен. Ожидалось: '{new_title}', получено: '{db_post['post_title']}'"
            assert db_post["post_content"] == new_content, f"Содержимое поста в БД не обновлено. Ожидалось: '{new_content}', получено: '{db_post['post_content']}'"

    @allure.title("Удаляем существующий пост")
    def test_delete_post(
        self,
        api_client: APIClient,
        db_client: DBClient,
        make_post
    ):
        post = make_post()
        post_id = post["id"]

        with allure.step("Удаляем пост через API"):
            response = api_client.delete_post(post_id, force=True)
            assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
            response_data = response.json()
            assert response_data["deleted"] is True, f"Флаг удаления не установлен. Ожидалось: True, получено: {response_data['deleted']}"
            assert response_data["previous"]["id"] == post_id, f"ID удаленного поста не совпадает. Ожидалось: {post_id}, получено: {response_data['previous']['id']}"

        with allure.step("Проверяем, что записи нет в БД"):
            assert db_client.post_exists(post_id) is False, f"Пост с ID {post_id} все еще существует в БД после удаления"
