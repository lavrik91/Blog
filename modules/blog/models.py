from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field

from ..services.utils import unique_slugify, image_compress

User = get_user_model()


class Article(models.Model):
    """
    Модель постов для сайта
    """

    class ArticleManager(models.Manager):
        """
        Кастомный менеджер для модели статей
        """

        def all(self):
            """
            Список статей (SQL запрос с фильтрацией для страницы списка статей)
            """
            return self.get_queryset().select_related('author', 'category').prefetch_related('ratings', 'views').filter(
                status='published')

        def detail(self):
            """
            Детальная статья (SQL запрос с фильтрацией для страницы со статьёй)
            """
            return self.get_queryset().select_related('author', 'category') \
                .prefetch_related('comments', 'comments__author', 'comments__author__profile', 'tags', 'ratings') \
                .filter(status='published')

    STATUS_OPTOINS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )
    title = models.CharField(verbose_name='Заголовок', max_length=255)
    slug = models.SlugField(verbose_name='URL', max_length=255, blank=True, unique=True)
    short_description = CKEditor5Field(verbose_name='Краткое описание', max_length=500, config_name='extends')
    full_description = CKEditor5Field(verbose_name='Полное описание', config_name='extends')
    thumbnail = models.ImageField(
        verbose_name='Превью поста',
        blank=True,
        upload_to='images/thumbnail/%Y/%m/%d',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'webp', 'jpeg', 'gif'])]
    )
    status = models.CharField(verbose_name='Статус поста', choices=STATUS_OPTOINS, default='published', max_length=10)
    time_create = models.DateTimeField(verbose_name='Время добавления', auto_now_add=True)
    time_update = models.DateTimeField(verbose_name='Время обновления', auto_now=True)
    author = models.ForeignKey(verbose_name='Автор', to=User, on_delete=models.SET_DEFAULT, related_name='author_post',
                               default=1)
    updater = models.ForeignKey(verbose_name='Обновил', to=User, on_delete=models.SET_NULL, null=True,
                                related_name='updater_post', blank=True)
    fixed = models.BooleanField(verbose_name='Зафиксировано', default=False)
    category = TreeForeignKey('Category', on_delete=models.PROTECT, related_name='articles', verbose_name='Категория',
                              null=True)
    tags = TaggableManager()

    objects = ArticleManager()

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        db_table = 'app_articles'
        ordering = ['-fixed', '-time_create']
        indexes = [models.Index(fields=['-fixed', '-time_create', 'status'])]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__thumbnail = self.thumbnail if self.pk else None

    def __str__(self):
        """
        Возвращение заголовка поста
        """
        return self.title

    def get_absolute_url(self):
        return reverse('articles_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

        if self.__thumbnail != self.thumbnail and self.thumbnail:
            image_compress(self.thumbnail.path, width=500, height=500)

    def get_sum_rating(self):
        return sum([rating.value for rating in self.ratings.all()])

    def get_view_count(self):
        """
        Возвращает количество просмотров для данной статьи
        """
        return self.views.count()


class Category(MPTTModel):
    """
    Модель категорий с вложенностью
    """

    title = models.CharField(verbose_name='Название категории', max_length=255)
    slug = models.SlugField(verbose_name='URL категории', max_length=255, blank=True)
    description = models.TextField(verbose_name='Описание категории', max_length=300)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name='children',
        verbose_name='Родительская категория'
    )

    class MPTTMeta:
        """
        Сортировка по вложенности
        """
        order_insertion_by = ('title',)

    class Meta:
        """
        Сортировка, название модели в админ панели, таблица в данными
        """
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        db_table = 'app_categories'

    def get_absolute_url(self):
        return reverse('articles_by_category', kwargs={'slug': self.slug})

    def __str__(self):
        """
        Возвращение заголовка статьи
        """
        return self.title


class Comment(MPTTModel):
    """
    Модель древовидных комментариев
    """
    STATUS_OPTIONS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )

    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Статья', related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор статьи',
                               related_name='comments_author')
    content = models.TextField(verbose_name='Текст комментария', max_length=3000)
    time_create = models.DateTimeField(verbose_name='Время добавления', auto_now_add=True)
    time_update = models.DateTimeField(verbose_name='Время обновления', auto_now=True)
    status = models.CharField(verbose_name='Статус поста', choices=STATUS_OPTIONS, default='published', max_length=10)
    parent = TreeForeignKey('self', verbose_name='Родительский комментарий', null=True, blank=True,
                            on_delete=models.CASCADE, related_name='children')

    class MPTTMeta:
        order_insertion_by = ('-time_create',)

    class Meta:
        db_table = 'app_comments'
        indexes = [models.Index(fields=['-time_create', 'time_update', 'status', 'parent'])]
        ordering = ['-time_create']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author}:{self.content}'


class Rating(models.Model):
    """
    Модель рейтинга: Лайк - Дизлайк
    """
    article = models.ForeignKey(to=Article, verbose_name='Статья', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(to=User, verbose_name='Пользователь', on_delete=models.CASCADE, blank=True, null=True)
    value = models.IntegerField(verbose_name='Значение', choices=[(1, 'Нравится'), (-1, 'Не нравится')])
    time_create = models.DateTimeField(verbose_name='Время добавления', auto_now_add=True)
    ip_address = models.GenericIPAddressField(verbose_name='IP Адрес')

    class Meta:
        unique_together = ('article', 'ip_address')
        ordering = ('-time_create',)
        indexes = [models.Index(fields=['-time_create', 'value'])]
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

    def __str__(self):
        return self.article.title


class ViewCount(models.Model):
    """
    Модель просмотров для статей
    """
    article = models.ForeignKey('Article', verbose_name='Статья', on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField(verbose_name='IP адрес')
    viewed_on = models.DateTimeField(verbose_name='Дата просмотра', auto_now_add=True)

    class Meta:
        ordering = ('-viewed_on',)
        indexes = [models.Index(fields=['-viewed_on'])]
        verbose_name = 'Просмотр'
        verbose_name_plural = 'Просмотры'

    def __str__(self):
        return self.article.title
