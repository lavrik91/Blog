from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect


class AuthorRequiredMixin(AccessMixin):
    """
    Mixin: кастомный миксин ограничивающий действия только для авторов статьи
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Если пользователь является автором статьи или администратором, разрешаем доступ
        if request.user == self.get_object().author or request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.info(request, 'Изменение и удаление статьи доступно только автору')
            return redirect('home')


class UserIsNotAuthenticatedMixin(UserPassesTestMixin):
    """
    Миксин для запрета регистрации авторизованных юзеров
    """

    def test_func(self):
        if self.request.user.is_authenticated:
            messages.info(self.request, 'Вы уже авторизованы. Вы не можете посетить эту страницу.')
            raise PermissionDenied
        return True

    def handle_no_permission(self):
        return redirect('home')