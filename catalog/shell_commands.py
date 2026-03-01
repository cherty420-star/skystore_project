def run_shell_commands():
    """Примеры команд для выполнения в Django shell"""

    from catalog.models import Category, Product
    from django.utils import timezone

    print("=== СОЗДАНИЕ КАТЕГОРИЙ ===")

    # 1. Создание категорий
    electronics = Category.objects.create(
        name='Электроника',
        description='Техника, гаджеты, компьютеры'
    )

    clothing = Category.objects.create(
        name='Одежда',
        description='Модная одежда и аксессуары'
    )

    # 2. Создание продуктов
    print("\n=== СОЗДАНИЕ ПРОДУКТОВ ===")

    Product.objects.create(
        name='Смартфон iPhone 15',
        description='Новый iPhone с камерой 48 Мп',
        category=electronics,
        price=99999.99
    )

    Product.objects.create(
        name='Джинсы Levis 501',
        description='Классические джинсы',
        category=clothing,
        price=5999.99
    )

    # 3. Получение всех категорий
    print("\n=== ВСЕ КАТЕГОРИИ ===")
    all_categories = Category.objects.all()
    for cat in all_categories:
        print(f"{cat.id}: {cat.name}")

    # 4. Получение всех продуктов
    print("\n=== ВСЕ ПРОДУКТЫ ===")
    all_products = Product.objects.all()
    for prod in all_products:
        print(f"{prod.id}: {prod.name} - {prod.price} руб.")

    # 5. Продукты в определенной категории
    print("\n=== ПРОДУКТЫ В КАТЕГОРИИ 'ЭЛЕКТРОНИКА' ===")
    electronics_products = Product.objects.filter(category__name='Электроника')
    for prod in electronics_products:
        print(f"{prod.name} - {prod.price} руб.")

    # 6. Обновление цены продукта
    print("\n=== ОБНОВЛЕНИЕ ЦЕНЫ ===")
    product = Product.objects.get(name='Смартфон iPhone 15')
    print(f"Старая цена: {product.price}")
    product.price = 89999.99
    product.save()
    print(f"Новая цена: {product.price}")

    # 7. Удаление продукта
    print("\n=== УДАЛЕНИЕ ПРОДУКТА ===")
    deleted_count, _ = Product.objects.filter(name='Джинсы Levis 501').delete()
    print(f"Удалено продуктов: {deleted_count}")

    print("\n=== ИТОГО ===")
    print(f"Категорий: {Category.objects.count()}")
    print(f"Продуктов: {Product.objects.count()}")