from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Store, Product, Order, OrderItem
from django.urls import reverse
from django.db.models import F
from django.contrib import messages
from .models import Profile, Notification
from .forms import SuggestionForm, UpdateProductForm, ManagerRegistrationForm
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from django.db.models.functions import TruncDay, TruncMonth, TruncYear

from django.http import HttpResponse
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter

def download_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    template = get_template('stock/order_receipt.html')
    html = template.render({'order': order})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Order_{order.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    create_notification(
                    request.user, 
                    f'New Order for "{order.client_name}" printed successfully.', 
                    'SUCCESS'
                )
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response



from django.contrib.auth.decorators import login_required
@login_required
def mark_order_delivered(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.status = 'Delivered'
    order.save()
    messages.success(request, f'Order {order.id} marked as Delivered.')
    return redirect('orders_list', store_id=order.store.id)


def create_notification(user, message, notif_type='INFO'):
    Notification.objects.create(
        user=user,
        message=message,
        notif_type=notif_type
    )


def notifications_view(request, order_id=None):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_notifications_count = notifications.filter(is_read=False).count()
    notifications.filter(is_read=False).update(is_read=True)
    order = None
    store = None
    if order_id:
        order = get_object_or_404(Order, id=order_id)
        store = order.store
    return render(request, 'stock/notifications.html', {'notifications': notifications, 'order': order, 'store': store, 'unread_notifications_count': unread_notifications_count})


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
            if request.user.is_authenticated:
                create_notification(
                    request.user, 
                    f'Product "{product.name}" added successfully to {store.store_namename}.', 
                    'SUCCESS'
                )
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
            if request.user.is_authenticated:
                create_notification(
                    request.user, 
                    f'Product "{updated_product.name}" was updated in {store.store_name}.', 
                    'INFO'
                )
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
                if product.quantity <= product.alert_threshold:
                    for manager in Profile.objects.filter(store=store, role='MANAGER'):
                        create_notification(
                            manager.user,
                            f'Product "{product.name}" stock is low: {product.quantity} remaining.',
                            'WARNING'
                        )
        # Update order total
        order.total_amount = order_total
        order.save()
        for manager in Profile.objects.filter(store=store, role='MANAGER'):
            create_notification(
                manager.user,
                f'New order created for {client_name} at {store.store_name}.',
                'INFO'
            )
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

def suspend_manager(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    store.is_active = False
    store.save()
    # Notify the manager about the suspension
    for manager in Profile.objects.filter(store=store, role='MANAGER'):
        create_notification(
            manager.user,
            f'Store {store.store_name} has been suspended.',
            'WARNING'
        )
    # Notify the admin about the suspension
    create_notification(
        request.user,
        f'Store {store.store_name} has been suspended.',
        'WARNING'
    )
    messages.success(request, f"Manager for store {store.store_name} has been suspended.")
    return redirect('admin_dashboard') 

# Admin dashboard (list stores and manage them)
from django.db.models import Count, Sum
from django.utils.timezone import now, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncWeek

@login_required
def admin_dashboard(request):
    current_time = now()
    day_ago = current_time - timedelta(hours=24)

    total_stores = Store.objects.count()
    new_stores_last_24h = Store.objects.filter(created_at__gte=day_ago).count()

    total_orders = Order.objects.count()
    new_orders_last_24h = Order.objects.filter(created_at__gte=day_ago).count()

    category_orders = (
        OrderItem.objects.values('product__category__name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    print(category_orders)

    managers = Profile.objects.filter(role='MANAGER')
    print(managers)
    weekly_orders = (
        Order.objects.annotate(week=TruncWeek('created_at'))
        .values('week')
        .annotate(total=Count('id'))
        .order_by('week')
    )
    print(weekly_orders)

    top_stores = (
        Order.objects.values('store__store_name')
        .annotate(order_count=Count('id'))
        .order_by('-order_count')[:10]
    )
    print(top_stores)

    top_products = (
        OrderItem.objects.values(
            'product__name',
            'product__category__name',
            'product__store__store_name'
        )
        .annotate(total_ordered=Sum('quantity'))
        .order_by('-total_ordered')[:10]
    )
    print(top_products)
    # Get the top 10 products sold in the last 30 days  
    top_products_last_30_days = (
        OrderItem.objects.filter(order__created_at__gte=day_ago)
        .values('product__name', 'product__category__name', 'product__store__store_name')
        .annotate(total_ordered=Sum('quantity'))
        .order_by('-total_ordered')[:10]
    )
    print(top_products_last_30_days)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_notifications_count = notifications.filter(is_read=False).count()
    context = {
        'total_stores': total_stores,
        'new_stores_last_24h': new_stores_last_24h,
        'total_orders': total_orders,
        'new_orders_last_24h': new_orders_last_24h,
        'category_orders': category_orders,
        'managers': managers,
        'weekly_orders': weekly_orders,
        'top_stores': top_stores,
        'top_products': top_products,
    }

    return render(request, 'stock/admin_dashboard.html', context)



from django.contrib.auth.models import Group
# Register view
from django.utils.timezone import now, timedelta

def register_view(request):
    if request.method == 'POST':
        form = ManagerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            store = form.cleaned_data['store']

            profile = user.profile
            profile.role = 'MANAGER'
            profile.store = store
            profile.subscription_start = now()
            profile.subscription_end = now() + timedelta(days=30)
            profile.save()

            manager_group, created = Group.objects.get_or_create(name='Manager')
            user.groups.add(manager_group)

            messages.success(request, 'Manager registered successfully! Free Trial activated 🎉')
            return redirect('login')
    else:
        form = ManagerRegistrationForm()

    return render(request, 'stock/register.html', {'form': form})


from django.utils.timezone import now
from django.contrib.auth import logout

from django.utils.timezone import now

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            profile = user.profile

            # Check if user has a subscription_end date
            if profile.subscription_end:
                if profile.subscription_end < now():
                    # Subscription expired, deactivate account
                    user.is_active = False
                    user.save()
                    messages.error(request, 'Your free trial has ended. Please renew your subscription to access your account.')
                    return redirect('login')
            else:
                # If no subscription_end date, give them 1 month from now (on first login or registration)
                profile.subscription_start = now()
                profile.subscription_end = now() + timedelta(days=30)
                profile.save()

            # Log them in
            login(request, user)

            # Track session data
            profile.last_login_time = now()
            profile.login_count = (profile.login_count or 0) + 1
            profile.save()
            if user.is_superuser:
                return redirect('admin-dashboard')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'stock/login.html', {'form': form})


# Logout view
def logout_view(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        profile.is_logged_in = False
        profile.save()

    logout(request)
    return redirect('login')


from django.db.models import Sum, Count, Q
from django.utils.timezone import now
from django.db.models.functions import TruncMonth

from django.utils.timezone import now, timedelta
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncMonth
from django.db.models.functions import Coalesce
def home_view(request):
    if request.user.profile.role == 'ADMIN':
        return redirect('/admin')
    elif request.user.profile.role == 'MANAGER':
        store = request.user.profile.store

        # Top 10 most sold products
        top_products = (
            Product.objects.filter(store=store).annotate(total_sold=Coalesce(Sum('order_item__quantity'), 0)).order_by('-total_sold')[:10].values('name', 'total_sold')
        )
        
        # for product in top_products:
            # print(f"{product['name']}: {product['total_sold']}")
        # Stock status counts
        in_stock_count = Product.objects.filter(store=store, quantity__gt=F('alert_threshold')).count()
        low_stock_count = Product.objects.filter(store=store, quantity__lte=F('alert_threshold')).count()

        # Total revenue
        total_revenue = Order.objects.filter(store=store).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Total orders
        total_orders = Order.objects.filter(store=store).count()
        total_products = Product.objects.filter(store=store).count()
        # Orders in the last 24h
        now_time = now()
        last_24h_orders = Order.objects.filter(
            store=store,
            created_at__gte=now_time - timedelta(hours=24)
        ).count()

        # Orders in the previous 24h (24h-48h ago)
        previous_24h_orders = Order.objects.filter(
            store=store,
            created_at__gte=now_time - timedelta(hours=48),
            created_at__lt=now_time - timedelta(hours=24)
        ).count()

        # Difference calculation
        orders_diff = last_24h_orders - previous_24h_orders
       # Products in the last 24h
        last_24h_products = Product.objects.filter(
            store=store,
            created_at__gte=now_time - timedelta(hours=24)
        ).count()

        # Products in the previous 24h
        previous_24h_products = Product.objects.filter(
            store=store,
            created_at__gte=now_time - timedelta(hours=48),
            created_at__lt=now_time - timedelta(hours=24)
        ).count()

        # Difference and trend
        products_diff = last_24h_products - previous_24h_products
        products_increase = products_diff >= 0


        # Revenue in the last 24h
        last_24h_revenue = Order.objects.filter(
            store=store,
            created_at__gte=now_time - timedelta(hours=24)
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Revenue in the previous 24h
        previous_24h_revenue = Order.objects.filter(
            store=store,
            created_at__gte=now_time - timedelta(hours=48),
            created_at__lt=now_time - timedelta(hours=24)
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Difference and trend
        revenue_diff = last_24h_revenue - previous_24h_revenue
        revenue_increase = revenue_diff >= 0

        is_increase = orders_diff >= 0

        # Orders evolution over last 12 months
        orders_per_month = (
            Order.objects.filter(store=store, created_at__year=now_time.year)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Count('id'))
            .order_by('month')
        )

        subscription_end = request.user.profile.subscription_end

        return render(request, 'stock/home.html', {
            'store': store,
            'top_products': top_products,
            'total_products': total_products,
            'in_stock_count': in_stock_count,
            'low_stock_count': low_stock_count,
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'orders_per_month': orders_per_month,
            'subscription_end': subscription_end,
            'last_24h_orders': last_24h_orders,
            'orders_diff': abs(orders_diff),
            'is_increase': is_increase,
            'products_diff': abs(products_diff),
            'products_increase': products_increase,
            'revenue_diff': abs(revenue_diff),
            'revenue_increase': revenue_increase,
        })
    else:
        messages.error(request, "Access Denied.")
        return redirect('login')

from .models import Suggestion

def suggestion_list(request):
    suggestions = Suggestion.objects.order_by('-date_submitted')
    return render(request, 'stock/suggestions_list.html', {'suggestions': suggestions})


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
