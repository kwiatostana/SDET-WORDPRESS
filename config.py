import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_URL = os.getenv("WP_BASE_URL")
    API_USER = os.getenv("WP_API_USER")
    API_PASSWORD = os.getenv("WP_API_PASSWORD")

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    TIMEOUT = 10
