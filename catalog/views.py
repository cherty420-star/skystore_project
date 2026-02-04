from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from .models import Product, Category, ContactMessage
from django.utils import timezone


def home(request):
    """Контроллер для домашней страницы"""
    # Получаем последние 5 продуктов
    latest_products = Product.objects.select_related('category').order_by('-created_at')[:5]

    # Выводим в консоль (для дополнительного задания)
    print("\n" + "=" * 60)
    print("ПОСЛЕДНИЕ 5 СОЗДАННЫХ ПРОДУКТОВ:")
    print("=" * 60)

    if latest_products.exists():
        for idx, product in enumerate(latest_products, 1):
            category_name = product.category.name if product.category else 'Без категории'
            print(f"{idx}. {product.name} - {product.price} руб. ({category_name})")
    else:
        print("Товаров пока нет в базе данных")

    print(f"Всего показано товаров: {len(latest_products)}")
    print("=" * 60)

    # Получаем статистику
    total_products = Product.objects.count()
    total_categories = Category.objects.count()

    context = {
        'latest_products': latest_products,
        'total_products': total_products,
        'total_categories': total_categories,
    }

    return render(request, 'catalog/home.html', context)


def contacts(request):
    """Контроллер для страницы контактов"""
    # Получаем контактные сообщения из базы данных
    contact_messages = ContactMessage.objects.filter(is_processed=False).order_by('-created_at')[:10]

    # Статистика
    total_messages = ContactMessage.objects.count()
    unprocessed_messages = ContactMessage.objects.filter(is_processed=False).count()
    urgent_messages = ContactMessage.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=1),
        is_processed=False
    ).count()

    # Инициализируем форму
    form = ContactForm()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Сохраняем в базу данных
            contact_message = ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data.get('email', ''),
                message=form.cleaned_data['message'],
                is_processed=False
            )

            # Выводим информацию в консоль
            print(f"\n✅ Новое сообщение сохранено в БД: {contact_message.name}")

            messages.success(request, f'Спасибо, {contact_message.name}! Ваше сообщение отправлено.')
            return redirect('contacts')

    context = {
        'form': form,
        'contact_messages': contact_messages,
        'total_messages': total_messages,
        'unprocessed_messages': unprocessed_messages,
        'urgent_messages': urgent_messages,
    }

    return render(request, 'catalog/contacts.html', context)


# Дополнительные функции для других маршрутов (если нужно)
def about(request):
    return render(request, 'catalog/about.html', {'title': 'О нас'})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'catalog/product_list.html', {'products': products})