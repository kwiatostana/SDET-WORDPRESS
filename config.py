import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_URL: str | None = os.getenv("WP_BASE_URL")
    API_USER: str | None = os.getenv("WP_API_USER")
    API_PASSWORD: str | None = os.getenv("WP_API_PASSWORD")

    DB_HOST: str | None = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str | None = os.getenv("DB_USER")
    DB_PASSWORD: str | None = os.getenv("DB_PASSWORD")
    DB_NAME: str | None = os.getenv("DB_NAME")

    TIMEOUT = 10

    @classmethod
    def validate(cls) -> None:
        """Проверяет, что все обязательные переменные окружения заданы."""
        required_vars: dict[str, str | None] = {
            "WP_BASE_URL": cls.BASE_URL,
            "WP_API_USER": cls.API_USER,
            "WP_API_PASSWORD": cls.API_PASSWORD,
            "DB_HOST": cls.DB_HOST,
            "DB_USER": cls.DB_USER,
            "DB_PASSWORD": cls.DB_PASSWORD,
            "DB_NAME": cls.DB_NAME,
        }

        missing_vars: list[str] = [var_name for var_name, var_value in required_vars.items() if not var_value]

        if missing_vars:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")


Config.validate()
