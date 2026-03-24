from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import BlogPost


class BlogListView(ListView):
    """Список блоговых записей"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        """Выводим только опубликованные статьи"""
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')


class BlogDetailView(DetailView):
    """Детальная страница блоговой записи"""
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        """Увеличиваем счетчик просмотров при просмотре статьи"""
        obj = super().get_object(queryset)
        obj.increment_views()

        # Дополнительное задание: отправка письма при 100 просмотрах
        if obj.views_count == 100:
            # Здесь можно добавить отправку email
            print(f"🎉 Статья '{obj.title}' достигла 100 просмотров!")

        return obj


class BlogCreateView(CreateView):
    """Создание новой блоговой записи"""
    model = BlogPost
    template_name = 'blog/blog_form.html'
    fields = ['title', 'content', 'preview', 'is_published']
    success_url = reverse_lazy('blog:blog_list')

    def form_valid(self, form):
        messages.success(self.request, 'Статья успешно создана!')
        return super().form_valid(form)


class BlogUpdateView(UpdateView):
    """Редактирование блоговой записи"""
    model = BlogPost
    template_name = 'blog/blog_form.html'
    fields = ['title', 'content', 'preview', 'is_published']

    def get_success_url(self):
        """После успешного редактирования перенаправляем на страницу статьи"""
        messages.success(self.request, 'Статья успешно обновлена!')
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})


class BlogDeleteView(DeleteView):
    """Удаление блоговой записи"""
    model = BlogPost
    template_name = 'blog/blog_confirm_delete.html'
    success_url = reverse_lazy('blog:blog_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Статья успешно удалена!')
        return super().delete(request, *args, **kwargs)