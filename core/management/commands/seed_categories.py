from django.core.management.base import BaseCommand
from core.models import Category

class Command(BaseCommand):
    help = 'Seed database with default product categories'

    def handle(self, *args, **kwargs):
        categories = [
            'Electronics',
            'Groceries',
            'Fashion',
            'Books',
            'Home Appliances',
            'Health & Beauty',
            'Toys',
            'Sports',
            'Automotive',
            'Music Instruments',
            'Stationery',
            'Garden & Outdoors',
            'Pet Supplies',
            'Gaming',
            'Jewelry'
        ]

        for cat in categories:
            Category.objects.get_or_create(name=cat)

        self.stdout.write(self.style.SUCCESS('✅ Categories seeded successfully.'))
