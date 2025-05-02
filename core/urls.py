from django.contrib import admin
from django.urls import path
from . import views



app_name = 'core'
urlpatterns = [
    # Authentication Routes
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_view, name='password_reset'),

    # Admin Route
    path('admin/', admin.site.urls),

    # Product Management Routes
    path('store/<int:store_id>/products/', views.product_list, name='product_list'),
    path('store/<int:store_id>/add-product/', views.add_product, name='add_product'),
    path('product/<int:product_id>/update/', views.update_product, name='update_product'),
    path('suggestion/', views.suggestion_view, name='suggestion'),
    path('notifications/', views.notifications_view, name='notifications'),
    # Order Routes
    path('store/<int:store_id>/create-order/', views.create_order, name='create_order'),
    # path('order/<int:order_id>/', views.order_detail, name='order_detail'),
     path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    # Additional Pages
    path('store/<int:store_id>/sales-report/', views.sales_report, name='sales_report'),
    # path('orders-list/<int:store_id>/', views.orders_list, name='orders_list'),
    path('store/<int:store_id>/orders-list/', views.orders_list, name='orders_list'),
    path('stock-alert-dashboard/', views.stock_alert_dashboard, name='stock_alert_dashboard'),
    path('store/<int:store_id>/profile/', views.store_profile, name='store_profile'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
