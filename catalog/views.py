from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from .models import Product, Category, ContactMessage
from .forms import ContactForm, ProductForm


class HomeListView(ListView):
    """Контроллер для главной страницы"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'

    def get_queryset(self):
        """Получаем последние 5 продуктов"""
        return Product.objects.select_related('category').order_by('-created_at')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем статистику
        context['total_products'] = Product.objects.count()
        context['total_categories'] = Category.objects.count()

        # Выводим в консоль (для отладки)
        print("\n" + "=" * 60)
        print("ПОСЛЕДНИЕ 5 СОЗДАННЫХ ПРОДУКТОВ:")
        print("=" * 60)
        for product in context['products']:
            category_name = product.category.name if product.category else 'Без категории'
            print(f"- {product.name} - {product.price} руб. ({category_name})")
        print("=" * 60)

        return context


class ProductDetailView(DetailView):
    """Контроллер для страницы товара"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        """Оптимизируем запрос с select_related"""
        return Product.objects.select_related('category')


class ProductCreateView(CreateView):
    """Контроллер для создания продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        messages.success(self.request, '✅ Товар успешно создан!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '❌ Исправьте ошибки в форме')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление нового товара'
        return context


class ProductUpdateView(UpdateView):
    """Контроллер для редактирования продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def get_success_url(self):
        messages.success(self.request, '✅ Товар успешно обновлен!')
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def form_invalid(self, form):
        messages.error(self.request, '❌ Исправьте ошибки в форме')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование: {self.object.name}'
        return context


class ProductDeleteView(DeleteView):
    """Контроллер для удаления продукта"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')

    def delete(self, request, *args, **kwargs):
        messages.success(request, '✅ Товар успешно удален!')
        return super().delete(request, *args, **kwargs)


class ContactsView(TemplateView):
    """Контроллер для страницы контактов"""
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем необработанные сообщения
        context['contact_messages'] = ContactMessage.objects.filter(
            is_processed=False
        ).order_by('-created_at')[:10]

        # Статистика
        context['total_messages'] = ContactMessage.objects.count()
        context['unprocessed_messages'] = ContactMessage.objects.filter(
            is_processed=False
        ).count()
        context['urgent_messages'] = ContactMessage.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=1),
            is_processed=False
        ).count()

        # Форма
        context['form'] = ContactForm()

        return context

    def post(self, request, *args, **kwargs):
        """Обработка POST запроса"""
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

            messages.success(request, f'✅ Спасибо, {contact_message.name}! Ваше сообщение отправлено.')
            return redirect('catalog:contacts')

        # Если форма невалидна, возвращаем страницу с ошибками
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)