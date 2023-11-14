import os
from celery import Celery

# Установите переменную окружения DJANGO_SETTINGS_MODULE в ваш файл settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_test.settings')

# Создайте экземпляр Celery
app = Celery('blog_test')

# Загрузите конфигурацию из настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Загрузите задачи из всех зарегистрированных Django-приложений
app.autodiscover_tasks()
