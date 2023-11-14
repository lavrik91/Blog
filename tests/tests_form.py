from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from modules.blog.forms import ArticleUpdateForm, ArticleCreateForm, CommentCreateForm
from modules.blog.models import Article, Comment, Category
from modules.system.forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm, UserLoginFrom, FeedbackCreateForm, \
    UserSetNewPasswordForm, UserForgotPasswordForm, UserPasswordChangeForm


class SystemFormsTestCase(TestCase):
    """
    Тесты форм для приложения System
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')

    def test_user_update_form(self):
        form_data = {
            'username': 'new_username',
            'email': 'new_email@example.com',
            'first_name': 'New',
            'last_name': 'User',
        }
        form = UserUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_profile_update_form(self):
        form_data = {
            'slug': 'new-slug',
            'birth_date': '2000-01-01',
            'bio': 'New bio',
        }
        form = ProfileUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())

    # Тест работает только при отключенном подтверждении действия по почте
    def test_user_register_form(self):
        form_data = {
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password1': 'new1password',
            'password2': 'new1password',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_login_form(self):
        recaptcha_response = 'test_recaptcha_response'

        form_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'recaptcha': recaptcha_response,
        }
        form = UserLoginFrom(data=form_data)

        # Теперь, ожидаем, что форма не является допустимой
        self.assertFalse(form.is_valid())

        # Проверяем, что в форме есть ошибка reCAPTCHA
        self.assertIn('recaptcha', form.errors)

    def test_user_password_change_form(self):
        form_data = {
            'old_password': 'testpassword',
            'new_password1': 'newtestpassword',
            'new_password2': 'newtestpassword',
        }
        form = UserPasswordChangeForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    # Тест работает только при отключенном подтверждении действия по почте
    def test_user_forgot_password_form(self):
        form_data = {
            'email': 'testuser@example.com',
        }
        form = UserForgotPasswordForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_set_new_password_form(self):
        form_data = {
            'new_password1': 'newtestpassword',
            'new_password2': 'newtestpassword',
        }
        form = UserSetNewPasswordForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_feedback_create_form(self):
        form_data = {
            'subject': 'Test Subject',
            'email': 'testuser@example.com',
            'context': 'Test Context',
        }
        form = FeedbackCreateForm(data=form_data)
        self.assertTrue(form.is_valid())


class BlogFormsTestCase(TestCase):
    """
    Тесты форм для приложения Blog
    """

    def setUp(self):
        # Создаем пользователя для тестов
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Создаем категорию для тестов
        self.category = Category.objects.create(title='Test Category', slug='test-category')

        image_path = r'D:\DjangoPROD\DjangoRepit\blog_test\media\images\thumbnail\test\test.jpg'
        self.image = SimpleUploadedFile('test_image.jpg', content=open(image_path, 'rb').read(),
                                        content_type='image/jpeg')

    def test_article_create_form(self):
        form_data = {
            'title': 'Test Article',
            'slug': 'test-article',
            'category': self.category,
            'short_description': 'Short description for testing',
            'full_description': 'Full description for testing',
            'thumbnail': self.image,
            'status': 'published',
        }
        form = ArticleCreateForm(data=form_data, files={'thumbnail': self.image})
        self.assertTrue(form.is_valid())

    def test_article_update_form(self):
        article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            category=self.category,
            short_description='Short description for testing',
            full_description='Full description for testing',
            thumbnail=self.image,
            status='published',
            author=self.user,
        )

        form_data = {
            'title': 'Updated Test Article',
            'slug': 'updated-test-article',
            'category': self.category.id,  # Используйте ID созданной категории
            'short_description': 'Updated short description for testing',
            'full_description': 'Updated full description for testing',
            'thumbnail': self.image,
            'status': 'draft',
            'updater': self.user.id,
            'fixed': True,
        }

        form = ArticleUpdateForm(instance=article, data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_create_form(self):
        article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            category=self.category,
            short_description='Short description for testing',
            full_description='Full description for testing',
            thumbnail=self.image,
            status='published',
            author=self.user,
        )

        form_data = {
            'content': 'Test comment content',
            'parent': None,
        }

        form = CommentCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
