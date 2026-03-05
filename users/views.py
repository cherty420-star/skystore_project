from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User


class UserRegistrationView(CreateView):
    """Регистрация пользователя"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """Отправка приветственного письма после успешной регистрации"""
        response = super().form_valid(form)

        # Отправляем приветственное письмо
        subject = 'Добро пожаловать в Skystore!'
        message = f'''
        Здравствуйте, {self.object.email}!

        Благодарим вас за регистрацию в нашем магазине Skystore.
        Теперь вы можете просматривать товары, оставлять отзывы и делать покупки.

        С уважением,
        Команда Skystore
        '''
        from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@skystore.ru'
        to_email = self.object.email

        try:
            send_mail(subject, message, from_email, [to_email])
            messages.success(self.request, 'Регистрация прошла успешно! Проверьте вашу почту.')
        except Exception as e:
            messages.warning(self.request, 'Регистрация прошла успешно, но не удалось отправить письмо.')

        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Исправьте ошибки в форме')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context


class UserLoginView(LoginView):
    """Авторизация пользователя"""
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход в систему'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Вы успешно вошли в систему!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Неверный email или пароль')
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    """Выход из системы"""

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Вы вышли из системы')
        return super().dispatch(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Исправьте ошибки в форме')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мой профиль'
        return context