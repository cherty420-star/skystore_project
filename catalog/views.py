from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.conf import settings
from .models import Product, Category, ContactMessage
from .forms import ContactForm, ProductForm
from .services import get_products_by_category, get_all_categories_with_counts, clear_category_cache


class HomeListView(ListView):
    """Контроллер для главной страницы"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        # Показываем только опубликованные товары
        return Product.objects.filter(
            is_published=True
        ).select_related('category', 'owner').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.filter(is_published=True).count()
        context['total_categories'] = Category.objects.count()
        context['categories'] = get_all_categories_with_counts()  # Используем сервисную функцию
        return context


@method_decorator(cache_page(300), name='dispatch')  # Кешируем на 5 минут
class ProductDetailView(DetailView):
    """Контроллер для страницы товара (с кешированием)"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.select_related('category', 'owner')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Проверяем, опубликован ли товар
        user = self.request.user
        if not obj.is_published:
            if not (user.is_authenticated and
                    (user == obj.owner or
                     user.has_perm('catalog.can_unpublish_product'))):
                raise PermissionDenied("Этот товар не опубликован и доступен только владельцу и модераторам")
        return obj


class CategoryProductsView(ListView):
    """Контроллер для отображения продуктов в категории"""
    template_name = 'catalog/category_products.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """Получаем продукты из категории с использованием сервисной функции"""
        self.category_id = self.kwargs.get('category_id')
        self.category = get_object_or_404(Category, id=self.category_id)

        # Используем сервисную функцию с кешированием
        return get_products_by_category(self.category_id, use_cache=settings.CACHE_ENABLED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = get_all_categories_with_counts()
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Контроллер для создания продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        # Очищаем кеш категорий при создании нового продукта
        if self.object.category:
            clear_category_cache(self.object.category.id)
        messages.success(self.request, '✅ Товар успешно создан!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, '❌ Исправьте ошибки в форме')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление нового товара'
        return context


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Контроллер для редактирования продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return user == product.owner or user.has_perm('catalog.can_unpublish_product')

    def handle_no_permission(self):
        messages.error(self.request, '❌ У вас нет прав для редактирования этого товара')
        return redirect('catalog:product_detail', pk=self.get_object().pk)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        # Очищаем кеш категории при обновлении продукта
        if self.object.category:
            clear_category_cache(self.object.category.id)
        messages.success(self.request, '✅ Товар успешно обновлен!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, '❌ Исправьте ошибки в форме')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование: {self.object.name}'
        return context


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Контроллер для удаления продукта"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return user == product.owner or user.has_perm('catalog.can_delete_any_product')

    def handle_no_permission(self):
        messages.error(self.request, '❌ У вас нет прав для удаления этого товара')
        return redirect('catalog:product_detail', pk=self.get_object().pk)

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        category_id = product.category.id if product.category else None
        response = super().delete(request, *args, **kwargs)

        # Очищаем кеш категории при удалении продукта
        if category_id:
            clear_category_cache(category_id)

        messages.success(request, '✅ Товар успешно удален!')
        return response


class ProductUnpublishView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Контроллер для отмены публикации продукта"""
    model = Product
    permission_required = 'catalog.can_unpublish_product'
    template_name = 'catalog/product_unpublish.html'
    fields = []

    def handle_no_permission(self):
        messages.error(self.request, '❌ У вас нет прав для отмены публикации товара')
        return redirect('catalog:product_detail', pk=self.get_object().pk)

    def form_valid(self, form):
        self.object.is_published = False
        self.object.save()

        # Очищаем кеш категории
        if self.object.category:
            clear_category_cache(self.object.category.id)

        messages.success(self.request, f'✅ Публикация товара "{self.object.name}" отменена')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('catalog:home')


class ContactsView(TemplateView):
    """Контроллер для страницы контактов"""
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_messages'] = ContactMessage.objects.filter(
            is_processed=False
        ).order_by('-created_at')[:10]
        context['total_messages'] = ContactMessage.objects.count()
        context['unprocessed_messages'] = ContactMessage.objects.filter(
            is_processed=False
        ).count()
        context['urgent_messages'] = ContactMessage.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=1),
            is_processed=False
        ).count()
        context['form'] = ContactForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data.get('email', ''),
                message=form.cleaned_data['message'],
                is_processed=False
            )
            messages.success(request, f'✅ Спасибо, {contact_message.name}! Ваше сообщение отправлено.')
            return redirect('catalog:contacts')

        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)