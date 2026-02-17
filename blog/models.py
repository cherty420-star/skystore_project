from django.db import models
from django.urls import reverse


class BlogPost(models.Model):
    """Модель блоговой записи"""
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    content = models.TextField(
        verbose_name='Содержимое'
    )
    preview = models.ImageField(
        upload_to='blog/',
        verbose_name='Превью',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано'
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество просмотров'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='URL',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Блоговая запись'
        verbose_name_plural = 'Блоговые записи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Получение абсолютного URL для модели"""
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    def increment_views(self):
        """Увеличение счетчика просмотров"""
        self.views_count += 1
        self.save(update_fields=['views_count'])