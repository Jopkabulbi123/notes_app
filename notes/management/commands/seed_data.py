from django.core.management.base import BaseCommand
from notes.models import Category, Note
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Seeds the database with test data'

    def handle(self, *args, **options):
        Note.objects.all().delete()
        Category.objects.all().delete()

        work = Category.objects.create(title="Робота")
        personal = Category.objects.create(title="Особисте")
        shopping = Category.objects.create(title="Покупки")

        Note.objects.create(
            title="Завдання на день",
            text="Зробити домашнє завдання Django",
            category=work,
            reminder=datetime.now() + timedelta(days=1))

        Note.objects.create(
            title="Купити продукти",
            text="Молоко, хліб, яйця",
            category=shopping)

        Note.objects.create(
            title="День народження",
            text="Приготувати подарунок",
            category=personal,
            reminder=datetime.now() + timedelta(days=7))

        self.stdout.write(self.style.SUCCESS('Успішно додано тестові дані'))