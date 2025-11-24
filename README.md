# WordPress API Automation Tests

Автотесты для проверки REST API WordPress с дополнительной валидацией данных в MySQL. Проект выполнен в рамках внешней стажировки SDET от SimbirSoft.

## Стек
- **Python 3.10+**
- **Pytest** — тестовый фреймворк
- **Requests** — HTTP-клиент
- **mysql-connector-python** — проверки в БД
- **pytest-xdist** — параллельный запуск
- **python-dotenv** — управление конфигурацией

## Структура
- `src/` — клиенты для API и базы данных
- `tests/` — тестовые сценарии и фикстуры
- `config.py` — загрузка переменных окружения

## Быстрый старт
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/kwiatostana/SDET-WORDPRESS
   cd api_tests_d1
   ```
2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   # Linux / macOS
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Создайте `.env` в корне проекта:
   ```env
   WP_BASE_URL=http://localhost:8000/index.php?rest_route=/
   WP_API_USER=<ваш логин>
   WP_API_PASSWORD=<ваш пароль>

   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=<ваши данные>
   DB_PASSWORD=<ваши данные>
   DB_NAME=<ваши данные>
   ```

## Запуск тестов
- Стандартный:
  ```bash
  pytest tests/
  ```
- Параллельный режим (например, 3 воркера):
  ```bash
  pytest -n 3 tests/
  ```

## Отчёт Allure
После запуска тестов c сохранением результатов (`pytest --alluredir=allure-results`) используйте CLI Allure:
- Сгенерировать статический отчёт:
  ```bash
  allure generate allure-results -o allure-report --clean
  ```
- Открыть отчёт в браузере:
  ```bash
  allure open allure-report
  ```