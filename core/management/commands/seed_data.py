from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Store, Product, Order, OrderItem, Category
from faker import Faker
import random
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify

fake = Faker()

# Cameroon-like data for stores and managers
stores_and_managers = [
    ('Meka Supermarket', 'Brayan', 'Yaounde', 'Bastos'),
    ('Akwa Electronics', 'Aissatou', 'Douala', 'Akwa'),
    ('Diana Fashion', 'Stephane', 'Yaounde', 'Mvog-Ada'),
    ('JB Store', 'Diane', 'Douala', 'Logbaba'),
    ('Supermarket Express', 'Yannick', 'Yaounde', 'Nlongkak')
]

categories = ['Beverages', 'Electronics', 'Clothing', 'Home Appliances', 'Mobile Phones']

# Realistic product names for each category
products_by_category = {
    'Electronics': ['Phone', 'Laptop', 'Headphones', 'TV', 'Smartwatch'],
    'Groceries': ['Rice', 'Oil', 'Sugar', 'Flour', 'Salt'],
    'Fashion': ['T-shirt', 'Jeans', 'Sneakers', 'Dress', 'Cap'],
    'Books': ['Novel', 'Comics', 'Bible', 'Dictionary', 'Cookbook'],
    'Home Appliances': ['Fridge', 'Microwave', 'Fan', 'Blender', 'Iron'],
    'Health & Beauty': ['Shampoo', 'Perfume', 'Lotion', 'Toothpaste', 'Deodorant'],
    'Toys': ['Action Figure', 'Puzzle', 'Doll', 'Remote Car', 'Board Game'],
    'Sports': ['Football', 'Basketball', 'Tennis Racket', 'Jersey', 'Running Shoes'],
    'Automotive': ['Car Battery', 'Engine Oil', 'Seat Cover', 'Air Freshener', 'Car Jack'],
    'Music Instruments': ['Guitar', 'Drums', 'Piano', 'Violin', 'Microphone'],
    'Stationery': ['Notebook', 'Pen', 'Pencil', 'Eraser', 'Marker'],
    'Garden & Outdoors': ['Hose Pipe', 'Shovel', 'Flower Pot', 'Lawn Mower', 'Fertilizer'],
    'Pet Supplies': ['Dog Food', 'Cat Toy', 'Bird Cage', 'Fish Tank', 'Leash'],
    'Gaming': ['PS5 Console', 'Xbox Controller', 'Gaming Chair', 'VR Headset', 'Gaming Mouse'],
    'Jewelry': ['Gold Chain', 'Earrings', 'Bracelet', 'Watch', 'Ring']
}

camer_names = [
    'Brayan Eyoum', 'Aline Mbarga', 'Emile Abena', 'Sandrine Ekani', 'Marc Tchounga',
    'Vanessa Mballa', 'Boris Essomba', 'Claire Ngo', 'Serge Talla', 'Kelly Nguimfack',
    'Patricia Ndongo', 'Junior Abega', 'Lionel Nkoulou', 'Diane Fotso', 'Axel Djoumessi'
]

quarters_yaounde = ['Bastos', 'Nlongkak', 'Mvog-Ada', 'Essos']
quarters_douala = ['Bonamoussadi', 'Akwa', 'Deido', 'Logbaba']

def random_camer_number():
    return '+23769' + ''.join([str(random.randint(0, 9)) for _ in range(7)])

class Command(BaseCommand):
    help = "Seed the database with fake store, product, order data, and manager logins."

    def handle(self, *args, **kwargs):
        # Create Categories if they don't exist
        if Category.objects.count() == 0:
            for category in categories:
                Category.objects.create(name=category)
        else:
            categories = Category.objects.all()

        # Optional: reset existing data
        Store.objects.all().delete()
        Product.objects.all().delete()
        Order.objects.all().delete()
        OrderItem.objects.all().delete()

        # Delete previous manager users for a clean reset
        User.objects.filter(is_staff=True).delete()

        stores = []
        for i, (store_name, manager_name, town, quarter) in enumerate(stores_and_managers):
            # Create manager User
            username = slugify(store_name)[:25] + str(random.randint(10, 99))
            user = User.objects.create_user(
                username=username,
                password='brayan8003',
                first_name=manager_name,
                last_name=fake.last_name(),
                email=fake.email(),
                is_staff=True  # So you can distinguish them as managers/admin in Django admin
            )

            # Create store
            store = Store.objects.create(
                store_name=store_name,
                manager_name=manager_name,
                store_number=random_camer_number(),
                manager_phone=random_camer_number(),
                town=town,
                quarter=quarter,
                latitude=fake.latitude(),
                longitude=fake.longitude(),
            )
            stores.append(store)

            # Assign products to the store (real-world categories)
            for category_name in categories:
                category_name_str = category_name.name
                if category_name_str in products_by_category:
                    for product_name in products_by_category[category_name_str]:
                        category = Category.objects.get(name=category_name_str)
                        Product.objects.create(
                            store=store,
                            name=product_name,
                            description=fake.sentence(),
                            price=round(random.uniform(1000, 50000), 2),
                            quantity=random.randint(5, 100),
                            category=category
                        )
                else:
                    # Optional: log skipped categories for awareness
                    print(f"⚠️ No products listed for category: {category_name_str}")


        # Simulating orders from February 1st to now
        start_date = timezone.datetime(2025, 2, 1, tzinfo=timezone.get_current_timezone())
        for store in stores:
            for _ in range(random.randint(20, 30)):  # Each store gets 20-30 orders
                order_date = start_date + timedelta(days=random.randint(0, (timezone.now() - start_date).days))
                order = Order.objects.create(
                    store=store,
                    client_name=random.choice(camer_names),
                    client_phone=random_camer_number(),
                    status=random.choice(['Pending', 'Delivered']),
                    created_at=order_date
                )

                products = store.products.all()
                total = 0
                for _ in range(random.randint(1, 4)):  # Each order can have 1 to 4 items
                    product = random.choice(products)
                    quantity = random.randint(1, 3)
                    price_at_purchase = product.price
                    total += price_at_purchase * quantity

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price_at_purchase=price_at_purchase
                    )
                order.total_amount = total
                order.save()

        self.stdout.write(self.style.SUCCESS("✅ Camer market data and manager logins seeded successfully! Password: 'brayan8003' for all managers."))

