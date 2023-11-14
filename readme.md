# Запуск Radise через Docker:
1. Запуск приложения Docker:
2. В pyCharm открыть проект:
3. Создание сервера если не создавался
```shell
docker pull redis:latest
```

```shell
docker run --name redis-server -p 6379:6379 -d redis:latest
```
Запуск и сотановка сервера Redis
```shell
docker start redis-server
docker stop redis-server
```

# Запуск Celery в Django для работы почты
1. Запускаем redis
2. Запускаем проект Django
```shell
py manage.py runserver
```
3. Открываем второй терминал и запускаем Celery
```shell
celery --app=blog_test worker --loglevel=info --pool=solo 

```
# Запуск Celery в Django для запуска отложенных процесов(резервная копия БД)
Открываем доп терминал и запускаем Celery Beat
```shell
celery -A blog_test beat -l info
```
Завершить процесс Ctrl+C дважды