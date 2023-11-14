from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
import tempfile

from modules.blog.models import Article, Category, Comment, Rating, ViewCount
from modules.system.models import Profile, Feedback

User = get_user_model()


class BlogModelTest(TestCase):
    """
    Тестирование моделей приложения Blog
    """

    def setUp(self):
        # Создаем пользователя для тестов
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Создаем категорию для тестов
        self.category = Category.objects.create(title='TestCategory', description='Test Description',
                                                slug='test-category')

        # Создаем статью для тестов
        self.article = Article.objects.create(
            title='Test Article',
            short_description='Short description',
            full_description='Full description',
            status='published',
            author=self.user,
            category=self.category
        )
        # Слздаем комментарий для тестов
        self.comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='Test Comment'
        )

    def tearDown(self):
        self.user.delete()
        self.article.delete()
        self.category.delete()

    def test_article_get_absolute_url(self):
        # Тест для метода get_absolute_url
        expected_url = f'/articles/{self.article.slug}/'
        self.assertEqual(self.article.get_absolute_url(), expected_url)

    def test_article_save_method(self):
        # Тест для метода save
        self.assertEqual(self.article.slug, 'test-article')  # Проверяем, что slug установлен корректно

    def test_article_str_method(self):
        # Тест для метода __str__
        expected_str = 'Test Article'
        self.assertEqual(str(self.article), expected_str)

    # Category model
    def test_category_get_absolute_url(self):
        expected_url = f'/category/{self.category.slug}/'
        self.assertEqual(self.category.get_absolute_url(), expected_url)

    def test_category_str_method(self):
        expected_str = 'TestCategory'
        self.assertEqual(str(self.category), expected_str)

    # Comment model
    def test_comment_str_method(self):
        expected_str = 'testuser:Test Comment'
        self.assertEqual(str(self.comment), expected_str)

    def test_get_sum_rating(self):
        # Тест для метода get_sum_rating
        Rating.objects.create(article=self.article, user=self.user, value=1, ip_address='127.0.0.1')
        Rating.objects.create(article=self.article, user=self.user, value=-1, ip_address='127.0.0.2')
        self.assertEqual(self.article.get_sum_rating(), 0)

    def test_get_view_count(self):
        # Тест для метода get_view_count
        ViewCount.objects.create(article=self.article, ip_address='127.0.0.1')
        ViewCount.objects.create(article=self.article, ip_address='127.0.0.2')
        self.assertEqual(self.article.get_view_count(), 2)


class SystemModelTest(TestCase):
    """
    Тестирование моделей приложения System
    """

    def setUp(self):
        # Создаем пользователя для тестов
        self.user = User.objects.create(username='testuser', password='testpassword')
        self.profile = Profile.objects.get(user=self.user)

    def tearDown(self):
        self.user.delete()

    def test_profile_creation(self):
        self.assertTrue(isinstance(self.profile, Profile))
        self.assertEqual(self.profile.__str__(), self.user.username)
        self.assertEqual(self.profile.get_absolute_url(), reverse('profile_detail', kwargs={'slug': self.profile.slug}))

    def test_profile_slug_creation(self):
        self.assertEqual(self.profile.slug, 'testuser')

    def test_profile_online_status(self):
        # Перед проверкой убедится что сервер Redis включен
        # Проверяем, что изначально пользователь не онлайн
        self.assertFalse(self.profile.is_online())

        # Сохраняем время последней активности в кеш
        cache.set(f'last-seen-{self.user.id}', timezone.now())

        # Проверяем, что теперь пользователь онлайн
        self.assertTrue(self.profile.is_online())

        # Проверяем, что если время последней активности старше 300 секунд, пользователь не онлайн
        cache.set(f'last-seen-{self.user.id}', timezone.now() - timezone.timedelta(seconds=301))
        self.assertFalse(self.profile.is_online())

    def test_profile_avatar_url(self):
        # Проверяем, что если у пользователя есть аватар, используется его URL
        with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_file:
            avatar = SimpleUploadedFile('test_avatar.jpg', temp_file.read(), content_type='image/jpg')
            self.profile.avatar = avatar
            self.profile.save()

        expected_url = f'/media/{self.profile.avatar.name}'
        self.assertEqual(self.profile.get_avatar, expected_url)

        # Проверяем, что если у пользователя нет аватара, используется URL с ui-avatars.com
        self.profile.avatar = None
        self.profile.save()
        expected_url = f'https://ui-avatars.com/api/?size=190&background=random&name={self.profile.slug}'
        self.assertEqual(self.profile.get_avatar, expected_url)

