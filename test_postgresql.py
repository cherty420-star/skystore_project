import os
import django
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Проверка подключения
from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL подключен успешно!")
        print(f"   Версия PostgreSQL: {version[0]}")

        # Проверка таблиц
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        print(f"   Таблиц в базе: {len(tables)}")

except Exception as e:
    print(f"❌ Ошибка подключения к PostgreSQL: {e}")