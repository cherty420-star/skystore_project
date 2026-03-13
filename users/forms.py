from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Форма для регистрации пользователя"""
    email = forms.EmailField(
        required=True,
        label='Электронная почта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.com'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'phone', 'country', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Стилизация дополнительных полей
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '+7 (999) 123-45-67'
        })
        self.fields['country'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Россия'
        })
        self.fields['avatar'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/jpeg,image/png'
        })

        # Делаем поля необязательными
        self.fields['phone'].required = False
        self.fields['country'].required = False
        self.fields['avatar'].required = False

    def clean_email(self):
        """Валидация email"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Устанавливаем username равным email
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """Форма для авторизации пользователя"""
    email = forms.EmailField(
        required=True,
        label='Электронная почта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.com'
        })
    )
    password = forms.CharField(
        required=True,
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class UserProfileForm(UserChangeForm):
    """Форма для редактирования профиля пользователя"""
    password = None  # Убираем поле пароля

    class Meta:
        model = User
        fields = ('email', 'phone', 'country', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'avatar':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'accept': 'image/jpeg,image/png'
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-control'
                })