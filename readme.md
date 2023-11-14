# Для запуска сайта необходимо 
1. Клонировать проект
    ```shell
    git clone https://github.com/lavrik91/Blog.git
    ```
2. Заполнить создать фаил _.env.dev_ в _blog_test/docker/env_ и заполнить по примеру файла [.env.example](docker%2Fenv%2F.env.example)

3. Запустим билд проекта в терминале следующей командой:
    ```shell
    docker compose -f docker-compose.dev.yml build
    ```
4. После создания образа с контейнерами билд необходимо запустить, делается это следующей командой:
    ```shell
    docker compose -f docker-compose.dev.yml up
    ```
5. Создание учетной записи администратора из консоли
    ```shell
    docker exec -it django sh
    python manage.py createsuperuser
    ```
6. Чтобы комментарии заработали необходимо создать 1 комментарий в админке и удалить его



