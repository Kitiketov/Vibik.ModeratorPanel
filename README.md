# Vibik Moderator Panel

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Aiogram](https://img.shields.io/badge/Aiogram-Telegram%20Bot-blue)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)

Панель для модерации пользовательских фотографий в проекте Vibik.

## Оглавление

- [О проекте](#о-проекте)
- [Связь с Vibik](#связь-с-vibik)
- [Возможности](#возможности)
- [Как это работает](#как-это-работает)
- [Установка и запуск](#установка-и-запуск)
- [Переменные окружения](#переменные-окружения)
- [API](#api)
- [Команды бота](#команды-бота)
- [Tech Stack](#tech-stack)
- [CI/CD](#cicd)
- [Автор](#автор)

## О проекте

Vibik Moderator Panel — отдельный сервис для модерации пользовательских фотографий через Telegram-бота и FastAPI.

Это часть экосистемы **Vibik**: сервис отвечает за модерацию контента и работает в связке с основным backend проекта.

Сервис помогает модераторам быстро получать новые задачи, просматривать фотографии, одобрять или отклонять их прямо из Telegram, а также смотреть сводку по пользовательским метрикам.

## Связь с Vibik

Этот репозиторий содержит отдельный сервис модерации для проекта **Vibik**.

Связанные репозитории:

- **Основной проект Vibik** — <https://github.com/Kitiketov/Vibik>
- **Ветка разработки Vibik** — <https://github.com/Kitiketov/Vibik/tree/dev>
- **Этот сервис** — <https://github.com/Kitiketov/Vibik.ModeratorPanel>

Если кратко, основной репозиторий отвечает за продуктовую логику и backend приложения, а `Vibik.ModeratorPanel` закрывает задачи модерации, уведомлений и просмотра метрик через Telegram.

## Возможности

- уведомления модераторов о новых задачах;
- получение следующей фотографии на модерацию;
- одобрение и отклонение фото через Telegram-интерфейс;
- проверка прав модератора;
- получение и визуализация метрик за последние недели;
- запуск API и Telegram-бота в одном сервисе.

## Как это работает

Внутри проекта одновременно работают две части:

- **FastAPI API** — принимает запросы на уведомление модераторов;
- **Telegram-бот** — показывает задачи на модерацию и обрабатывает действия модераторов.

Сервис общается с основным backend Vibik через HTTP-клиент и использует внешние ручки для:

- получения следующей задачи на модерацию;
- approve/reject действий;
- проверки доступа модератора;
- получения продуктовых метрик.

## Установка и запуск

### Локально

```bash
git clone https://github.com/Kitiketov/Vibik.ModeratorPanel.git
cd Vibik.ModeratorPanel
pip install -r requirements.txt
python main.py
```

### Через Docker

```bash
docker build -t vibik-moderator-panel .
docker run --env-file .env -p 8090:8090 vibik-moderator-panel
```

## Переменные окружения

Пример `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
BOT_SECRET=your_secret
API_BASE_HOST=https://your-production-api
API_BASE_LOCAL=http://localhost:8080
API_ENV=prod
NOTIFY_HOST=0.0.0.0
NOTIFY_PORT=8090
NOTIFY_PATH=/api/moderation/notify
```

Основные переменные:

- `BOT_TOKEN` — токен Telegram-бота;
- `BOT_SECRET` — токен для авторизации в основном backend;
- `API_BASE_HOST` — адрес production API;
- `API_BASE_LOCAL` — адрес локального API;
- `API_ENV` — режим (`prod` или `local`);
- `NOTIFY_HOST` / `NOTIFY_PORT` — параметры запуска FastAPI;
- `NOTIFY_PATH` — путь для уведомлений.

## API

### POST `/api/moderation/notify`

Отправляет уведомление выбранным модераторам о новой задаче.

Пример тела запроса:

```json
{
  "moderator_ids": [123456789, 987654321]
}
```

Пример ответа:

```json
{
  "sent": 2,
  "failed": []
}
```

## Команды бота

- `/start` — старт бота;
- `/next_photo` — взять следующую задачу на модерацию;
- `/metrics` — посмотреть метрики за последнюю неделю с графиком.

Также в боте доступны кнопки для одобрения и отклонения фотографий.

## Tech Stack

- **Python 3.11+**
- **FastAPI**
- **Aiogram 3**
- **Uvicorn**
- **Aiohttp**
- **Pydantic / pydantic-settings**
- **Matplotlib**
- **Docker**
- **GitHub Actions**

## CI/CD

В репозитории настроен workflow, который:

- проверяет проект на `push` и `pull_request` в `main`;
- валидирует исходники через `compileall`;
- собирает Docker image;
- пушит image в `ghcr.io`;
- деплоит контейнер на сервер по SSH.

## Автор

- **Илья Котов** — backend, Telegram moderation bot, FastAPI API, интеграция с основным backend, метрики.
