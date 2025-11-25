import re
from datetime import datetime

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

    def connect(self):
        """Создает соединение с базой данных."""
        if self.connection is None or not self.connection.is_connected():
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                use_pure=True,
            )

    def close(self):
        """Закрывает соединение."""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query, params=None):
        """
        Выполняет SQL-запрос и возвращает результат (для SELECT).
        """
        self.connect()
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def get_post_by_id(self, post_id):
        """
        Специализированный метод для получения поста по ID.
        """
        query = "SELECT ID, post_title, post_content, post_status FROM wp_posts WHERE ID = %s"
        result = self.execute_query(query, (post_id,))
        return result[0] if result else None

    def post_exists(self, post_id):
        """Проверяет, существует ли пост (возвращает True/False)."""
        query = "SELECT count(*) as count FROM wp_posts WHERE ID = %s"
        result = self.execute_query(query, (post_id,))
        return result[0]["count"] > 0

    def post_exists_with_title(self, title):
        """Проверяет, существует ли пост с указанным заголовком."""
        query = "SELECT count(*) as count FROM wp_posts WHERE post_title = %s"
        result = self.execute_query(query, (title,))
        return result[0]["count"] > 0

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

    def delete_post(self, post_id):
        """
        Удаляет пост из базы данных по ID.
        """
        self.connect()
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM wp_posts WHERE ID = %s", (post_id,))
            self.connection.commit()

    def create_post_via_sql(self, post_title, post_content, post_status="publish", post_author=1):
        """
        Создает пост через SQL INSERT и возвращает ID созданного поста.
        """

        self.connect()
        with self.connection.cursor() as cursor:
            now = datetime.now()
            if post_title:
                post_name = re.sub(r"[^\w\s-]", "", post_title.lower())
                post_name = re.sub(r"[-\s]+", "-", post_name).strip("-")
            else:
                post_name = ""

            query = """
                INSERT INTO wp_posts 
                (post_author, post_date, post_date_gmt, post_content, post_title, 
                 post_excerpt, post_status, comment_status, ping_status, post_password, 
                 post_name, to_ping, pinged, post_modified, post_modified_gmt, 
                 post_content_filtered, post_parent, guid, menu_order, post_type, 
                 post_mime_type, comment_count)
                VALUES 
                (%s, %s, %s, %s, %s, '', %s, 'open', 'open', '', %s, '', '', %s, %s, '', 0, '', 0, 'post', '', 0)
            """

            params = (post_author, now, now, post_content, post_title, post_status, post_name, now, now)

            cursor.execute(query, params)
            self.connection.commit()
            return cursor.lastrowid
