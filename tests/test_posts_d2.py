import allure

from src.api_client import APIClient


@allure.epic("WordPress Posts API pt.2")
@allure.feature("Чтение постов подготовленных через SQL")
class TestPostsD2:
    """
    Набор тестов, где тестовые данные подготавливаются напрямую в БД.
    """

    @allure.title("Получаем стандартный пост, созданный через прямой SQL-запрос")
    def test_get_post_created_via_sql(
        self,
        api_client: APIClient,
        make_post_via_sql,
    ):
        with allure.step("Создать пост напрямую через SQL INSERT"):
            post = make_post_via_sql(
                post_title="DB Auto Title [{uuid}]",
                post_content="DB Auto Content Body",
                post_status="publish",
                post_author=1,
            )
            post_id = post["id"]

        response = api_client.get_post(post_id, params={"context": "edit"})

        with allure.step("Проверить что GET /wp/v2/posts/{id} вернул корректные данные"):
            assert response.status_code == 200, f"Ожидался код ответа 200 OK, получен {response.status_code}"
            response_data = response.json()
            expected_title = post["title"]["raw"]
            expected_content = post["content"]["raw"]
            expected_status = post["status"]
            assert response_data["id"] == post_id, (
                f"ID поста не совпадает. Ожидалось: {post_id}, получено: {response_data['id']}"
            )
            assert response_data["title"]["raw"] == expected_title, (
                f"Поле title.raw не совпадает. Ожидалось: '{expected_title}', получено: '{response_data['title']['raw']}'"
            )
            assert response_data["content"]["raw"] == expected_content, (
                f"Поле content.raw не совпадает. Ожидалось: '{expected_content}', получено: '{response_data['content']['raw']}'"
            )
            assert response_data["status"] == expected_status, (
                f"Поле status не совпадает. Ожидалось: '{expected_status}', получено: '{response_data['status']}'"
            )

    @allure.title("Проверяем кодировку")
    def test_get_post_with_russian_text(
        self,
        api_client: APIClient,
        make_post_via_sql,
    ):
        with allure.step("Создать пост с русским текстом напрямую через SQL INSERT"):
            post = make_post_via_sql(
                post_title="Тестовый Заголовок на Русском [{uuid}]",
                post_content="Содержание статьи с буквами: ё, й, щ, ъ.",
                post_status="publish",
            )
            post_id = post["id"]

        response = api_client.get_post(post_id, params={"context": "edit"})
        with allure.step("Проверить что GET /wp/v2/posts/{id} возвращает корректный код ответа"):
            assert response.status_code == 200, f"Ожидался код ответа 200 OK, получен {response.status_code}"
        response_data = response.json()

        with allure.step("Проверить что GET /wp/v2/posts/{id} вернул корректные данные с русским текстом"):
            expected_title = post["title"]["raw"]
            expected_content = post["content"]["raw"]
            assert response_data["id"] == post_id, (
                f"ID поста не совпадает. Ожидалось: {post_id}, получено: {response_data['id']}"
            )
            assert response_data["title"]["raw"] == expected_title, (
                f"Поле title.raw строго не равно ожидаемому. Ожидалось: '{expected_title}', получено: '{response_data['title']['raw']}'"
            )
            assert response_data["content"]["raw"] == expected_content, (
                f"Поле content.raw строго не равно ожидаемому. Ожидалось: '{expected_content}', получено: '{response_data['content']['raw']}'"
            )

    @allure.title("Получаем пост с пустым заголовком")
    def test_get_post_with_empty_title(
        self,
        api_client: APIClient,
        make_post_via_sql,
    ):
        with allure.step("Создать пост с пустым заголовком напрямую через SQL INSERT"):
            post = make_post_via_sql(
                post_title="",
                post_content="Content with empty title [{uuid}]",
                post_status="publish",
            )
            post_id = post["id"]

        response = api_client.get_post(post_id, params={"context": "edit"})
        with allure.step("Проверить что GET /wp/v2/posts/{id} возвращает корректный код ответа"):
            assert response.status_code == 200, f"Ожидался код ответа 200 OK, получен {response.status_code}"

        response_data = response.json()

        with allure.step("Проверить что GET /wp/v2/posts/{id} вернул корректные данные с пустым заголовком"):
            expected_title = post["title"]["raw"]
            expected_content = post["content"]["raw"]
            assert response_data["id"] == post_id, (
                f"ID поста не совпадает. Ожидалось: {post_id}, получено: {response_data['id']}"
            )
            assert response_data["title"]["raw"] == expected_title, (
                f"Поле title.raw должно быть пустой строкой. Ожидалось: '{expected_title}', получено: '{response_data['title']['raw']}'"
            )
            assert response_data["content"]["raw"] == expected_content, (
                f"Поле content.raw не соответствует введенному контенту. Ожидалось: '{expected_content}', получено: '{response_data['content']['raw']}'"
            )
