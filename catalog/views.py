from django.shortcuts import render
from .forms import ContactForm


def home(request):
    """Контроллер для домашней страницы"""
    return render(request, 'catalog/home.html')


def contacts(request):
    """Контроллер для страницы контактов с улучшенной обработкой формы"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Обработка валидных данных
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            message = form.cleaned_data['message']

            # Здесь можно добавить логику:
            # 1. Сохранение в базу данных
            # 2. Отправку email
            # 3. Интеграцию с CRM

            return render(request, 'catalog/contacts.html', {
                'form': ContactForm(),  # Очищенная форма
                'success_message': f'Спасибо, {name}! Ваше сообщение отправлено. Мы свяжемся с вами по телефону {phone}.'
            })
    else:
        form = ContactForm()

    return render(request, 'catalog/contacts.html', {'form': form})