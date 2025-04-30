from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Store, Product, Order, OrderItem
from django.urls import reverse
from django.db.models import F
from django.contrib import messages
from .models import Profile
from .forms import UpdateProductForm, ManagerRegistrationForm

# List products for a specific store
def product_list(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = Product.objects.filter(store=store)

    return render(request, 'stock/product_list.html', {
        'store': store,
        'products': products
    })
from .forms import AddProductForm
# Add a product to a store
def add_product(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if request.method == 'POST':
        form = AddProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect(reverse('product_list', args=[store.id]))
    else:
        form = AddProductForm()

    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST.get('description', '')
        price = request.POST['price']
        quantity = request.POST['quantity']
        alert_threshold = request.POST['alert_threshold']

        Product.objects.create(
            store=store,
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            alert_threshold=alert_threshold
        )

        messages.success(request, 'Product added successfully!')
        return redirect(reverse('product_list', args=[store.id]))

    return render(request, 'stock/add_product.html', {'store': store, 'form': form})

# Update a product
def update_product(request, product_id):
    # Get product and store using their IDs
    product = get_object_or_404(Product, id=product_id)
    store = product.store

    # Handle the form submission
    if request.method == 'POST':
        form = UpdateProductForm(request.POST, instance=product)
        if form.is_valid():
            updated_product = form.save(commit=False)
            updated_product.store = store
            updated_product.save()

            messages.success(request, 'Product updated successfully!')
            return redirect(reverse('product_list', args=[store.id]))

    else:
        form = UpdateProductForm(instance=product)

    return render(request, 'stock/update_product.html', {'product': product, 'form': form})
# Create an order for a store
from .forms import CreateOrderForm
from django.forms import formset_factory
from .forms import OrderItemForm
def create_order(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = Product.objects.filter(store=store)

    if request.method == 'POST':
        form = OrderItemForm(request.POST, store=store)
        if form.is_valid():
            client_name = form.cleaned_data['client_name']
            client_phone = form.cleaned_data['client_phone']
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']

            if product.quantity < quantity:
                messages.error(request, f'Not enough stock for {product.name}.')
                return redirect(reverse('create_order', args=[store.id]))

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                store=store,
                client_name=client_name,
                client_phone=client_phone,
                total_amount=product.price * quantity
            )

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=product.price
            )

            product.quantity = F('quantity') - quantity
            product.save()

            messages.success(request, 'Order placed successfully!')
            return redirect(reverse('product_list', args=[store.id]))

    else:
        form = OrderItemForm(store=store)

    return render(request, 'stock/create_order.html', {
        'form': form,
        'store': store,
        'products': products
    })
def order_detail(request, order_id):
    # Get the order from the database, or return a 404 if not found
    order = get_object_or_404(Order, id=order_id)

    # Pass the order data to the template
    return render(request, 'stock/order_detail.html', {'order': order})
# Sales report page
def sales_report(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    orders = Order.objects.filter(store=store)
    total_sales = sum(order.total_amount for order in orders)

    return render(request, 'stock/sales_report.html', {
        'store': store,
        'orders': orders,
        'total_sales': total_sales
    })
from django.views.generic import DetailView
class OrderDetailView(DetailView):
    model = Order
    template_name = 'stock/order_detail.html'  # Replace with your template
    context_object_name = 'order'
# Orders list for a specific store
def orders_list(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    orders = Order.objects.filter(store=store)

    return render(request, 'stock/orders_list.html', {
        'store': store,
        'orders': orders
    })

# Stock alert dashboard
def stock_alert_dashboard(request):
    products = Product.objects.filter(quantity__lte=F('alert_threshold'))
    return render(request, 'stock/stock_alert_dashboard.html', {'products': products})

# Store profile page
def store_profile(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    return render(request, 'stock/store_profile.html', {'store': store})

# Admin dashboard (list stores and manage them)
def admin_dashboard(request):
    stores = Store.objects.all()
    return render(request, 'stock/admin_dashboard.html', {'stores': stores})
from django.contrib.auth.models import Group
# Register view
def register_view(request):
    if request.method == 'POST':
        form = ManagerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            store = form.cleaned_data['store']

            # Set user profile role and store
            profile = user.profile
            profile.role = 'MANAGER'
            profile.store = store
            profile.save()

            # Add user to Manager group (create it if missing)
            manager_group, created = Group.objects.get_or_create(name='Manager')
            user.groups.add(manager_group)

            messages.success(request, 'Manager registered successfully!')
            return redirect('login')
    else:
        form = ManagerRegistrationForm()

    return render(request, 'stock/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            user_profile = user.profile
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'stock/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')
def home_view(request):
    if request.user.profile.role == 'ADMIN':
        return redirect('/admin')  # or wherever
    elif request.user.profile.role == 'MANAGER':
        store = request.user.profile.store
        return render(request, 'stock/home.html', {'store': store})
    else:
        messages.error(request, "Access Denied.")
        return redirect('login')

def order_list(request):
    user_profile = Profile.objects.get(user=request.user)
    store = user_profile.store if user_profile.role == 'MANAGER' else None
    orders = Order.objects.filter(store=store) if store else []

    context = {
        'orders': orders,
        'store': store
    }
    return render(request, 'stock/order_list.html', context)

# Password reset view
def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            messages.success(request, 'Password reset email sent.')
            return redirect('login')
    else:
        form = PasswordResetForm()
    return render(request, 'stock/password_reset.html', {'form': form})
