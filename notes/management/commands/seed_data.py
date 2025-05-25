from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from notes.models import Category, Note
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Seeds the database with test data'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Створено користувача: {user.username}'))

        Note.objects.all().delete()
        Category.objects.all().delete()

        work = Category.objects.create(title="Робота")
        personal = Category.objects.create(title="Особисте")
        shopping = Category.objects.create(title="Покупки")

        Note.objects.create(
            title="Завдання на день",
            text="Зробити домашнє завдання Django",
            category=work,
            user=user,
            reminder=datetime.now() + timedelta(days=1)
        )

        Note.objects.create(
            title="Купити продукти",
            text="Молоко, хліб, яйця",
            category=shopping,
            user=user
        )

        Note.objects.create(
            title="День народження",
            text="Приготувати подарунок",
            category=personal,
            user=user,
            reminder=datetime.now() + timedelta(days=7)
        )

        self.stdout.write(self.style.SUCCESS('Успішно додано тестові дані'))