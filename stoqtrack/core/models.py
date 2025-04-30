from django.db import models
import string, random
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Function to generate a unique alphanumeric 7-character store code
def generate_store_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

# Store model
class Store(models.Model):
    store_name = models.CharField(max_length=255)
    manager_name = models.CharField(max_length=255)
    store_number = models.CharField(max_length=50)
    manager_phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Cameroon')
    town = models.CharField(max_length=100)
    quarter = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    store_code = models.CharField(max_length=7, unique=True, default=generate_store_code)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.store_name} ({self.store_code})"

# Product model
class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    alert_threshold = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.store.store_name}"

# Order model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=255)
    client_phone = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def items(self):
        return OrderItem.objects.filter(order=self)

    def calculate_total(self):
        total = sum(item.product.price * item.quantity for item in self.items.all())
        self.total_amount = total
        self.save()
    def __str__(self):
        return f"Order {self.id} - {self.store.store_name}"

# Order Item model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Profile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MANAGER')
    store = models.OneToOneField('Store', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# Auto-create Profile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()