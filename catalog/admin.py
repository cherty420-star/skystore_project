from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    search_fields = ('name', 'description')
    ordering = ('id',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    list_editable = ('price',)
    ordering = ('-created_at',)

    # Опционально: форматирование цены
    def price_rub(self, obj):
        return f"{obj.price} руб."

    price_rub.short_description = 'Цена'