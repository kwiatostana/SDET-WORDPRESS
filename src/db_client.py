import allure
import mysql.connector

from config import Config


class DBClient:
    def __init__(self):
        """Инициализация подключения с использованием настроек из Config."""
        self.host = Config.DB_HOST
        self.port = Config.DB_PORT
        self.user = Config.DB_USER
        self.password = Config.DB_PASSWORD
        self.database = Config.DB_NAME
        self.connection = None

    @allure.step("Подключаемся к БД")
    def connect(self):
        """Создает соединение с базой данных."""
        if self.connection is None or not self.connection.is_connected():
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                use_pure=True
            )

    @allure.step("Закрываем соединение с БД")
    def close(self):
        """Закрывает соединение."""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    @allure.step("Выполняем SQL запрос")
    def execute_query(self, query, params=None):
        """
        Выполняет SQL-запрос и возвращает результат (для SELECT).
        """
        self.connect()
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @allure.step("Получаем пост из БД по ID {post_id}")
    def get_post_by_id(self, post_id):
        """
        Специализированный метод для получения поста по ID.
        """
        query = "SELECT ID, post_title, post_content, post_status FROM wp_posts WHERE ID = %s"
        result = self.execute_query(query, (post_id,))
        return result[0] if result else None

    @allure.step("Проверяем наличие поста {post_id} в БД")
    def post_exists(self, post_id):
        """Проверяет, существует ли пост (возвращает True/False)."""
        query = "SELECT count(*) as count FROM wp_posts WHERE ID = %s"
        result = self.execute_query(query, (post_id,))
        return result[0]["count"] > 0

    @allure.step("Проверяем пост по заголовку {title}")
    def post_exists_with_title(self, title):
        """Проверяет, существует ли пост с указанным заголовком."""
        query = "SELECT count(*) as count FROM wp_posts WHERE post_title = %s"
        result = self.execute_query(query, (title,))
        return result[0]["count"] > 0

    @allure.step("Считаем посты по списку ID")
    def count_posts_by_ids(self, id_list):
        """
        Считает количество постов, ID которых входят в переданный список.
        """
        if not id_list:
            return 0

        placeholders = ", ".join(["%s"] * len(id_list))
        query = f"SELECT count(*) as count FROM wp_posts WHERE ID IN ({placeholders})"

        result = self.execute_query(query, tuple(id_list))
        return result[0]["count"]

    @allure.step("Удаляем пост из БД {post_id}")
    def delete_post(self, post_id):
        """
        Удаляет пост из базы данных по ID.
        """
        self.connect()
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM wp_posts WHERE ID = %s", (post_id,))
            self.connection.commit()
