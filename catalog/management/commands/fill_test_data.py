from django.core.management.base import BaseCommand
from catalog.models import Category, Product


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными (удаляет старые перед добавлением)'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Начало заполнения базы тестовыми данными...')

        # 1. Удаляем старые данные (ОБЯЗАТЕЛЬНО для задания!)
        self.stdout.write('🗑️  Удаление старых данных...')
        deleted_products, _ = Product.objects.all().delete()
        deleted_categories, _ = Category.objects.all().delete()
        self.stdout.write(f'   Удалено продуктов: {deleted_products}')
        self.stdout.write(f'   Удалено категорий: {deleted_categories}')

        # 2. Создаем категории
        self.stdout.write('📂 Создание категорий...')
        categories_data = [
            {'name': 'Электроника', 'description': 'Техника, гаджеты, компьютеры'},
            {'name': 'Одежда', 'description': 'Модная одежда и аксессуары'},
            {'name': 'Книги', 'description': 'Художественная и учебная литература'},
            {'name': 'Спорт', 'description': 'Спортивные товары и инвентарь'},
            {'name': 'Мебель', 'description': 'Домашняя и офисная мебель'},
        ]

        categories = []
        for cat_data in categories_data:
            category = Category.objects.create(**cat_data)
            categories.append(category)
            self.stdout.write(f'   ✅ Создана категория: {category.name}')

        # 3. Создаем продукты
        self.stdout.write('🛍️  Создание продуктов...')
        products_data = [
            {'name': 'Смартфон iPhone 15 Pro', 'price': 99999.99, 'category': categories[0],
             'description': 'Флагманский смартфон Apple с процессором A17 Pro'},
            {'name': 'Ноутбук Dell XPS 13', 'price': 129999.00, 'category': categories[0],
             'description': 'Ультрабук с безрамочным дисплеем 13.4"'},
            {'name': 'Наушники Sony WH-1000XM5', 'price': 29999.99, 'category': categories[0],
             'description': 'Беспроводные наушники с шумоподавлением'},
            {'name': 'Футболка Nike Sportswear', 'price': 2499.99, 'category': categories[1],
             'description': 'Хлопковая футболка с логотипом Nike'},
            {'name': 'Джинсы Levis 501', 'price': 5999.99, 'category': categories[1],
             'description': 'Классические джинсы прямого кроя'},
            {'name': 'Курта The North Face', 'price': 14999.99, 'category': categories[1],
             'description': 'Теплая зимняя куртка'},
            {'name': 'Книга "Гарри Поттер и философский камень"', 'price': 899.99, 'category': categories[2],
             'description': 'Первая книга культовой серии'},
            {'name': "Python. К вершинам мастерства", 'price': 1899.99, 'category': categories[2],
             'description': 'Продвинутое руководство по Python'},
            {'name': 'Футбольный мяч Adidas', 'price': 2999.99, 'category': categories[3],
             'description': 'Официальный мяч для профессиональных матчей'},
            {'name': 'Гантели наборные 20 кг', 'price': 3999.99, 'category': categories[3],
             'description': 'Набор гантелей для домашних тренировок'},
            {'name': 'Диван угловой "Модерн"', 'price': 45999.99, 'category': categories[4],
             'description': 'Угловой диван с ортопедическим матрасом'},
            {'name': 'Стол компьютерный', 'price': 12999.99, 'category': categories[4],
             'description': 'Эргономичный стол для работы за компьютером'},
        ]

        for prod_data in products_data:
            product = Product.objects.create(**prod_data)
            self.stdout.write(f'   ✅ Создан продукт: {product.name} - {product.price} руб.')

        # 4. Итоги
        total_categories = Category.objects.count()
        total_products = Product.objects.count()

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('✅ БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!'))
        self.stdout.write(f'📊 ИТОГО:')
        self.stdout.write(f'   Категорий: {total_categories}')
        self.stdout.write(f'   Продуктов: {total_products}')
        self.stdout.write('=' * 50)