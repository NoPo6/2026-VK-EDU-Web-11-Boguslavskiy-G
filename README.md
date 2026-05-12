# Проект: Модели данных и наполнение базы

## Как запустить

1. Склонировать репозиторий.
2. Заменить .env.example на .env со своими данными, например:
    DB_NAME=django_db
    DB_USER=german
    DB_PASSWORD=qwerty
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY=django-insecure-fixme-12345
    DEBUG=True
4. В терминале выполнить: `docker-compose up --build`
5. Дождаться запуска контейнеров, затем:  
   `docker-compose exec web python manage.py migrate`
6. Для заполнения тестовыми данными:  
   `docker-compose exec web python manage.py fill_db 10000`
7. Открыть в браузере `http://localhost:8000`
8. Для закрытия проекта: `docker-compose down -v`

Для несуществующих объектов возвращается 404. При пустой базе выводятся сообщения "Пока нет ни одного вопроса" и т.п. Пагинация (20 записей) на всех списках.

## Что реализовано

- **Модели**: Question, Answer, Tag, Profile, QuestionLike, AnswerLike, QuestionTag. Связи, уникальные ограничения для лайков (unique_together/UniqueConstraint).
- **ModelManager** для Question с методами get_new, get_best, get_by_tag, question_detailes; **AnswerManager** для Answer с методом with_likes. Использованы select_related, prefetch_related, аннотации для подсчёта лайков и ответов.
- **Django admin**: зарегистрированы все модели, локализованы (русский язык). Inline для профиля внутри пользователя и для ответов внутри вопроса.
- **Команда fill_db [ratio]**: генерирует пользователей, теги, вопросы, ответы, лайки с помощью Faker и bulk_create. Объём при ratio=10000: >10k пользователей, >100k вопросов, >1M ответов, >10k тегов, >2M лайков.
- **Views** используют методы менеджера. Пагинация вынесена в отдельную функцию.
- **Debug-toolbar** подключается только при DEBUG=True.
- **СУБД**: PostgreSQL (контейнер в docker-compose). Настроены healthcheck, volume для данных.
- **Переменные окружения**: .env.example (коммитится), .env.local и .env.docker (в .gitignore). settings.py читает переменные через os.getenv.
- **Пока что есть проблема с долгой загрузкой всех вопросов.**
