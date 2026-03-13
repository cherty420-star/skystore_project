from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from .models import Product, Category, ContactMessage  # ContactMessage должен быть здесь
from .forms import ContactForm, ProductForm


class HomeListView(ListView):
    """Контроллер для главной страницы (общедоступный)"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'

    def get_queryset(self):
        # Показываем только опубликованные товары на главной
        return Product.objects.filter(is_published=True).select_related('category').order_by('-created_at')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.filter(is_published=True).count()
        context['total_categories'] = Category.objects.count()
        return context


class ProductDetailView(DetailView):
    """Контроллер для страницы товара (общедоступный)"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.select_related('category')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Проверяем, опубликован ли товар или пользователь - владелец/модератор
        user = self.request.user
        if not obj.is_published:
            if not (user.is_authenticated and
                    (user == obj.owner or
                     user.has_perm('catalog.can_unpublish_product'))):
                raise PermissionDenied("Этот товар не опубликован и доступен только владельцу и модераторам")
        return obj


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Контроллер для создания продукта (только для авторизованных)"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

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


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Контроллер для редактирования продукта (только для владельца или модератора)"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def test_func(self):
        """Проверка прав на редактирование"""
        product = self.get_object()
        user = self.request.user

        # Редактировать может владелец или модератор (с правом на отмену публикации)
        return user == product.owner or user.has_perm('catalog.can_unpublish_product')

    def handle_no_permission(self):
        """Обработка отсутствия прав"""
        messages.error(self.request, '❌ У вас нет прав для редактирования этого товара')
        return redirect('catalog:product_detail', pk=self.get_object().pk)

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

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


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Контроллер для удаления продукта (владелец или модератор)"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')

    def test_func(self):
        """Проверка прав на удаление"""
        product = self.get_object()
        user = self.request.user

        # Удалять может владелец или модератор (с правом на удаление любого продукта)
        return user == product.owner or user.has_perm('catalog.can_delete_any_product')

    def handle_no_permission(self):
        """Обработка отсутствия прав"""
        messages.error(self.request, '❌ У вас нет прав для удаления этого товара')
        return redirect('catalog:product_detail', pk=self.get_object().pk)

    def delete(self, request, *args, **kwargs):
        messages.success(request, '✅ Товар успешно удален!')
        return super().delete(request, *args, **kwargs)


class ProductUnpublishView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Контроллер для отмены публикации продукта (только для модераторов)"""
    model = Product
    permission_required = 'catalog.can_unpublish_product'
    template_name = 'catalog/product_unpublish.html'
    fields = []  # Не обновляем никакие поля, просто меняем статус
    success_url = reverse_lazy('catalog:home')

    def handle_no_permission(self):
        messages.error(self.request, '❌ У вас нет прав для отмены публикации товара')
        return redirect('catalog:product_detail', pk=self.get_object().pk)

    def form_valid(self, form):
        """Отменяем публикацию продукта"""
        self.object.is_published = False
        self.object.save()
        messages.success(self.request, f'✅ Публикация товара "{self.object.name}" отменена')
        return super().form_valid(form)


class ContactsView(TemplateView):
    """Контроллер для страницы контактов (общедоступный)"""
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