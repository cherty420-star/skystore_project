from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category

# Список запрещенных слов (в нижнем регистре)
FORBIDDEN_WORDS = [
    'казино',
    'криптовалюта',
    'крипта',
    'биржа',
    'дешево',
    'бесплатно',
    'обман',
    'полиция',
    'радар'
]


class ContactForm(forms.Form):
    """Форма обратной связи"""
    name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя'
        })
    )

    phone = forms.CharField(
        max_length=20,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (900) 123-45-67'
        })
    )

    email = forms.EmailField(
        required=False,
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        })
    )

    message = forms.CharField(
        label='Сообщение',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Опишите ваш вопрос или проблему...',
            'rows': 5
        })
    )


class ProductForm(forms.ModelForm):
    """Форма для создания и редактирования продуктов"""

    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'category', 'price', 'is_published']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Получаем пользователя из kwargs
        super().__init__(*args, **kwargs)

        # Стилизация всех полей
        for field_name, field in self.fields.items():
            if field_name == 'is_published':
                field.widget.attrs['class'] = 'form-check-input'
                field.label = 'Опубликовать товар'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

            # Добавляем placeholder для текстовых полей
            if field_name == 'name':
                field.widget.attrs['placeholder'] = 'Введите название товара'
            elif field_name == 'description':
                field.widget.attrs['placeholder'] = 'Введите описание товара'
                field.widget.attrs['rows'] = 5
            elif field_name == 'price':
                field.widget.attrs['placeholder'] = '0.00'
                field.widget.attrs['step'] = '0.01'
                field.widget.attrs['min'] = '0'
            elif field_name == 'image':
                field.widget.attrs['accept'] = 'image/jpeg,image/png'

        # Добавляем подписи к полям
        self.fields['name'].label = 'Название товара'
        self.fields['description'].label = 'Описание'
        self.fields['image'].label = 'Изображение'
        self.fields['category'].label = 'Категория'
        self.fields['price'].label = 'Цена (₽)'
        self.fields['category'].empty_label = 'Выберите категорию'

    def validate_forbidden_words(self, value, field_name):
        """Общая валидация на запрещенные слова"""
        if value:
            # Приводим к нижнему регистру для проверки
            value_lower = value.lower()

            # Проверяем каждое запрещенное слово
            for word in FORBIDDEN_WORDS:
                if word in value_lower:
                    raise ValidationError(
                        f'Поле "{field_name}" содержит запрещенное слово: "{word}". '
                        f'Пожалуйста, уберите его из текста.'
                    )
        return value

    def clean_name(self):
        """Валидация поля name на запрещенные слова"""
        name = self.cleaned_data.get('name')
        return self.validate_forbidden_words(name, 'Название')

    def clean_description(self):
        """Валидация поля description на запрещенные слова"""
        description = self.cleaned_data.get('description')
        return self.validate_forbidden_words(description, 'Описание')

    def clean_price(self):
        """Валидация цены (не может быть отрицательной)"""
        price = self.cleaned_data.get('price')

        if price is None:
            raise ValidationError('Цена обязательна для заполнения')

        if price < 0:
            raise ValidationError('Цена не может быть отрицательной')

        if price == 0:
            raise ValidationError('Цена должна быть больше 0')

        return price

    def clean_image(self):
        """Валидация изображения"""
        image = self.cleaned_data.get('image')

        if image:
            # Проверка размера файла (макс 5 МБ)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Размер файла не должен превышать 5 МБ')

            # Проверка формата файла
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise ValidationError('Поддерживаются только форматы JPEG и PNG')

        return image

    def save(self, commit=True):
        """Сохраняем продукт с привязкой к владельцу"""
        instance = super().save(commit=False)

        # Если создается новый продукт и есть пользователь
        if not instance.pk and self.user and not self.user.is_anonymous:
            instance.owner = self.user

        if commit:
            instance.save()
            self.save_m2m()

        return instance