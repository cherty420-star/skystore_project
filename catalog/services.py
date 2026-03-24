from django.core.cache import cache
from django.conf import settings
from django.db import models  # Добавляем импорт models
from .models import Product, Category


def get_products_by_category(category_id, use_cache=True):
    """
    Возвращает список всех продуктов в указанной категории
    с использованием кеширования
    """
    cache_key = f'products_by_category_{category_id}'

    # Проверяем кеш
    if use_cache and settings.CACHE_ENABLED:
        products = cache.get(cache_key)
        if products is not None:
            print(f"📦 Кеш HIT для категории {category_id}")
            return products

    # Получаем продукты из базы
    try:
        category = Category.objects.get(id=category_id)
        products = Product.objects.filter(
            category=category,
            is_published=True
        ).select_related('category', 'owner').order_by('-created_at')

        # Сохраняем в кеш (на 10 минут)
        if use_cache and settings.CACHE_ENABLED:
            cache.set(cache_key, products, 600)  # 10 минут
            print(f"💾 Кеш SET для категории {category_id}")

        return products
    except Category.DoesNotExist:
        return None


def get_all_categories_with_counts(use_cache=True):
    """
    Возвращает список всех категорий с количеством продуктов в каждой
    """
    cache_key = 'all_categories_with_counts'

    # Проверяем кеш
    if use_cache and settings.CACHE_ENABLED:
        categories = cache.get(cache_key)
        if categories is not None:
            print("📦 Кеш HIT для категорий")
            return categories

    # Получаем из базы
    from django.db.models import Count
    categories = Category.objects.annotate(
        products_count=Count('products', filter=models.Q(products__is_published=True))
    ).order_by('name')

    # Сохраняем в кеш
    if use_cache and settings.CACHE_ENABLED:
        cache.set(cache_key, categories, 600)
        print("💾 Кеш SET для категорий")

    return categories


def clear_category_cache(category_id):
    """Очищает кеш для конкретной категории"""
    cache_key = f'products_by_category_{category_id}'
    cache.delete(cache_key)
    cache.delete('all_categories_with_counts')
    print(f"🗑️ Кеш очищен для категории {category_id}")