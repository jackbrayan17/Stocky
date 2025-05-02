from django.contrib import admin
from .models import Store, Product, Order, OrderItem, Profile, Location
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import StoreAdminForm

# Inline profile editing in the admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Store Admin
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    form = StoreAdminForm
    list_display = ('store_name', 'manager_name', 'store_number', 'town', 'country', 'store_code', 'is_active')
    search_fields = ('store_name', 'manager_name', 'store_code')
    list_filter = ('town', 'country', 'is_active')
    ordering = ('store_name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'price', 'quantity', 'alert_threshold', 'created_at')
    search_fields = ('name', 'store__store_name')
    list_filter = ('store',)
    ordering = ('-created_at',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'client_name', 'client_phone', 'total_amount', 'created_at')
    search_fields = ('client_name', 'store__store_name')
    list_filter = ('store', 'created_at')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_at_purchase')
    search_fields = ('product__name', 'order__id')
    ordering = ('-order',)

admin.site.register(Location)
