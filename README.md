# GNSS Telemetry Analysis Service

FastAPI-сервис для анализа GNSS данных тягача с LLM-классификацией пользовательских запросов.

---

##  Поддерживаемые типы запросов

| Action | Описание |
|--------|----------|
| `max_speed` | Максимальная скорость |
| `pos_type_19` | Проблемы GPS (статус 19) |
| `hour_16_19` | Данные в интервале 16–19 |
| `strong_negative_acceleration` | Резкое торможение |
| `geo_bounds` | Нахождение в координатах трассы М11 |
| `unknown` | Запрос не относится к телеметрии |

---

##  Как запустить проект 

### 1. Клонировать репозиторий

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### 2. Создать файл окружения `.env`

В корне проекта создайте файл `.env`:

```bash
touch .env
```

Добавьте в него ваш API-ключ:

```env
OPENROUTER_API_KEY=your_api_key_here
```

### 3. Собрать и запустить контейнер

В корне проекта выполните команду:

```bash
docker compose up --build
```

**Docker автоматически:**
* Соберёт образ
* Установит все зависимости
* Запустит FastAPI-приложение

После успешного запуска сервис будет доступен в браузере по адресу:
* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
