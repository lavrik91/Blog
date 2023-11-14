from django.core import mail
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from modules.blog.models import Article, Category, Comment, Rating, ViewCount
from modules.blog.forms import ArticleCreateForm, ArticleUpdateForm, CommentCreateForm


class BlogViewTestCase(TestCase):
    """
    Тесты views для приложения Blog
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Создаем категорию
        self.category = Category.objects.create(title='Test Category', slug='test-category',
                                                description='Category for testing')

        image_path = r'D:\DjangoPROD\DjangoRepit\blog_test\media\images\thumbnail\test\test.jpg'
        self.image = SimpleUploadedFile('test_image.jpg', content=open(image_path, 'rb').read(),
                                        content_type='image/jpeg')

    def test_article_creation(self):
        self.client.force_login(self.user)

        # Создаем статью
        response = self.client.post(reverse('articles_create'), {
            'title': 'Test Article',
            'short_description': 'Test short_description',
            'full_description': 'Test full_description',
            'thumbnail': self.image,
            'category': self.category.id,
            'status': 'published',
        })

        self.assertEqual(response.status_code, 302)
        article_exists = Article.objects.filter(title='Test Article').exists()

        # Проверяем, что статья была успешно создана
        self.assertTrue(article_exists)

        # Проверяем статью
        article = Article.objects.get(title='Test Article')
        self.assertEqual(article.category, self.category)

    def test_article_list_view(self):
        Article.objects.create(
            title='Test Article 1',
            short_description='Short description 1',
            full_description='Full description 1',
            author=self.user,
            thumbnail=self.image,
            category=self.category,
        )

        Article.objects.create(
            title='Test Article 2',
            short_description='Short description 2',
            full_description='Full description 2',
            author=self.user,
            thumbnail=self.image,
            category=self.category,
        )
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], 'Главная страница')
        self.assertEqual(len(response.context['articles']), 2)

    def test_article_detail_view(self):
        # Создаем статью
        article = Article.objects.create(
            title='Test Article',
            short_description='Test short_description',
            full_description='Test full_description',
            author=self.user,
            thumbnail=self.image,
            category=self.category,
            status='published',
        )
        response = self.client.get(reverse('articles_detail', args=[article.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], article.title)
        self.assertEqual(response.context['form'].__name__, CommentCreateForm.__name__)
        self.assertQuerysetEqual(response.context['similar_articles'], Article.objects.none())

    def test_article_deletion(self):
        # Создаем статью, которую попытаемся удалить
        article = Article.objects.create(
            title='Test Article',
            short_description='Test short_description',
            full_description='Test full_description',
            author=self.user,
            thumbnail=self.image,
            category=self.category,
            status='published',
        )

        # Авторизуемся
        self.client.force_login(self.user)

        # Отправляем запрос на удаление
        response = self.client.post(reverse('articles_delete', args=[article.slug]))

        # Проверяем, что статья удалена
        self.assertEqual(response.status_code, 302)  # 302 - редирект, так как мы указали success_url
        self.assertFalse(Article.objects.filter(pk=article.pk).exists())


class SystemViewsTestCase(TestCase):
    """
    Тесты views для приложения System
    """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')
        self.profile = self.user.profile

    def test_profile_detail_view(self):
        response = self.client.get(reverse('profile_detail', args=[self.profile.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile.user.username)
        self.assertContains(response, 'Страница пользователя')

    def test_profile_update_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Редактирование профиля')

    def test_profile_following_create_view(self):
        self.client.force_login(self.user)
        other_user = User.objects.create_user(username='otheruser', password='otherpassword')
        other_profile = other_user.profile

        response = self.client.post(reverse('follow', args=[other_profile.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.profile.following.count(), 1)

        response = self.client.post(reverse('follow', args=[other_profile.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.profile.following.count(), 0)

    def test_user_logout_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout


    # Тест не работает из за подтверждения почты
    # def test_user_register_view(self):
    #     response = self.client.get(reverse('register'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, 'Регистрация на сайте')
    #
    #     response = self.client.post(reverse('register'), {
    #         'username': 'newuser',
    #         'email': 'newuser@example.com',
    #         'password1': 'newpassword',
    #         'password2': 'newpassword',
    #     })
    #     self.assertEqual(response.status_code, 302)  # Redirect after successful registration
    #
    #     new_user = User.objects.get(username='newuser')
    #     self.assertFalse(new_user.is_active)
    #
    #     # Check that the activation email was sent
    #     self.assertEqual(len(mail.outbox), 1)
    #     activation_email = mail.outbox[0]
    #     self.assertIn(new_user.email, activation_email.to)
    #     self.assertEqual(activation_email.subject, 'Активация учетной записи')
    #
    # #Работает только при отключенной рекапчи
    # def test_user_login_view(self):
    #     response = self.client.get(reverse('login'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, 'Авторизация на сайте')
    #
    #     response = self.client.post(reverse('login'), {
    #         'username': 'testuser',
    #         'password': 'testpassword',
    #     })
    #     self.assertEqual(response.status_code, 302)  # Redirect after successful login
    #
    # # Тест не работает из за подтверждения почты
    # def test_user_password_change_view(self):
    #     self.client.force_login(self.user)
    #     response = self.client.get(reverse('password_change'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, 'Изменение пароля на сайте')
    #
    #     response = self.client.post(reverse('password_change'), {
    #         'old_password': 'testpassword',
    #         'new_password1': 'newtestpassword',
    #         'new_password2': 'newtestpassword',
    #     })
    #     self.assertEqual(response.status_code, 302)  # Redirect after successful password change
    #
    # # Не работает без Celery and redis
    # def test_feedback_create_view(self):
    #     response = self.client.get(reverse('feedback'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, 'Контактная форма')
    #
    #     response = self.client.post(reverse('feedback'), {
    #         'subject': 'Test Subject',
    #         'email': 'testuser@example.com',
    #         'context': 'Test Context',
    #     })
    #     self.assertEqual(response.status_code, 302)  # Redirect after successful feedback creation


