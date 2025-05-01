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
from .forms import SuggestionForm, UpdateProductForm, ManagerRegistrationForm
from django.db.models import Q

def suggestion_view(request):
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your suggestion 🙏🏽✨')
            return redirect('home')
    else:
        form = SuggestionForm()
    return render(request, 'stock/suggestions.html', {'form': form})

def product_list(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    search_query = request.GET.get('q', '')  # récupère la valeur du champ search

    if search_query:
        products = Product.objects.filter(
            Q(store=store) & 
            (Q(name__icontains=search_query) | Q(price__icontains=search_query))
        )
    else:
        products = Product.objects.filter(store=store)

    return render(request, 'stock/product_list.html', {
        'store': store,
        'products': products,
        'search_query': search_query
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
from django.urls import reverse

def create_order(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = Product.objects.filter(store=store)
    form = CreateOrderForm(store, request.POST or None)

    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        client_phone = request.POST.get('client_phone')

        order = Order.objects.create(
            client_name=client_name,
            client_phone=client_phone,
            store=store
        )

        product_ids = request.POST.getlist('product')
        quantities = request.POST.getlist('quantity')

        order_total = 0

        for product_id, quantity in zip(product_ids, quantities):
            quantity = int(quantity)
            if quantity > 0:
                product = Product.objects.filter(id=product_id, store=store).first()
                if not product:
                    continue
                if product.quantity < quantity:
                    continue
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=product.price
                )
                product.quantity -= quantity
                product.save()

                # Add to total
                order_total += product.price * quantity

        # Update order total
        order.total_amount = order_total
        order.save()

        return redirect(reverse('core:orders_list', args=[store.id]))

    context = {
        'form': form,
        'products': products,
        'store': store, 
        'store_id': store_id,
    }
    return render(request, 'stock/create_order.html', context)



def order_detail(request, order_id):
    # Get the order from the database, or return a 404 if not found
    order = get_object_or_404(Order, id=order_id)
    store = order.store
    # Pass the order data to the template
    return render(request, 'stock/order_detail.html', {'order': order,'store':store})
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
from django.db.models import Sum, Count, Q
from django.utils.timezone import now
from django.db.models.functions import TruncMonth

def home_view(request):
    if request.user.profile.role == 'ADMIN':
        return redirect('/admin')
    elif request.user.profile.role == 'MANAGER':
        store = request.user.profile.store

        # Top 10 most sold products
        top_products = (
            Product.objects.filter(store=store)
            .annotate(total_sold=Sum('orderitem__quantity'))
            .order_by('-total_sold')[:10]
        )

        # Stock status counts
        in_stock_count = Product.objects.filter(store=store, quantity__gt=F('alert_threshold')).count()
        low_stock_count = Product.objects.filter(store=store, quantity__lte=F('alert_threshold')).count()

        # Total revenue
        total_revenue = Order.objects.filter(store=store).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Total orders
        total_orders = Order.objects.filter(store=store).count()
        total_products = Product.objects.count()
        # Orders evolution over last 12 months
        orders_per_month = (
            Order.objects.filter(store=store, created_at__year=now().year)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Count('id'))
            .order_by('month')
        )

        return render(request, 'stock/home.html', {
            'store': store,
            'top_products': top_products,
            'total_products': total_products,
            'in_stock_count': in_stock_count,
            'low_stock_count': low_stock_count,
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'orders_per_month': orders_per_month
        })
    else:
        messages.error(request, "Access Denied.")
        return redirect('login')



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
