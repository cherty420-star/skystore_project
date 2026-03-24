from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product


class Command(BaseCommand):
    help = 'Создание групп модераторов и контент-менеджеров с правами'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('🚀 Создание групп...'))

        # Создаем группу модераторов продуктов
        self.create_moderator_group()

        # Создаем группу контент-менеджеров (доп. задание)
        self.create_content_manager_group()

        self.stdout.write(self.style.SUCCESS('✅ Группы успешно созданы!'))

    def create_moderator_group(self):
        """Создание группы модераторов продуктов"""
        moderator_group, created = Group.objects.get_or_create(name='Модератор продуктов')

        if created:
            self.stdout.write('   Создана группа "Модератор продуктов"')
        else:
            self.stdout.write('   Группа "Модератор продуктов" уже существует')

        # Получаем content type для модели Product
        content_type = ContentType.objects.get_for_model(Product)

        # Получаем нужные разрешения
        permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=['can_unpublish_product', 'can_delete_any_product']
        )

        # Добавляем разрешения группе
        moderator_group.permissions.set(permissions)

        self.stdout.write(f'   Добавлено {permissions.count()} разрешений')

        return moderator_group

    def create_content_manager_group(self):
        """Создание группы контент-менеджеров (для блога)"""
        content_group, created = Group.objects.get_or_create(name='Контент-менеджер')

        if created:
            self.stdout.write('   Создана группа "Контент-менеджер"')
        else:
            self.stdout.write('   Группа "Контент-менеджер" уже существует')

        # Для блога нужны разрешения на работу с BlogPost
        # Так как это доп. задание, пока оставим заглушку
        self.stdout.write('   Разрешения для блога будут настроены позже')

        return content_group