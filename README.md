## Delivery Service API

API для расчёта стоимости доставки и управления посылками.

### Основные возможности

- Приём запросов на создание посылки через REST API
- Асинхронный расчёт стоимости доставки с учётом курса USD (ЦБР API)
- Кэширование курса USD в Redis
- Фоновая обработка задач Celery
- Хранение данных в MySQL через SQLAlchemy и Alembic
- Централизованное логирование с единым конфигом

### Технологии

- Python
- FastAPI
- Uvicorn
- Celery + RabbitMQ
- Redis
- SQLAlchemy + MySQL
- Alembic


### Быстрый старт

1. Клонируйте репозиторий и перейдите в директорию проекта:

   ```bash
   git clone https://github.com/DmitriiSvarovskii/fastapi-delivery-service.git
   cd fastapi-delivery-service
   ```

2. Создайте файл `.env` на основе примера из `.env.example` и заполните необходимые переменные


3. Запустите Docker Compose:

   ```bash
   docker-compose up -d --build
   ```

4. **После первого запуска** выполните миграции и инициализацию данных (типы посылок):

   ```bash
   # Выполнить миграции
   docker-compose exec fastapi alembic upgrade head

   # Выполнить initial_data_db
   docker-compose exec fastapi sh -c 'export PYTHONPATH=/app && python -m src.utils.initial_data_db'
   ```

5. Откройте документацию API:

   ```
   http://localhost:8080/docs
   ```


