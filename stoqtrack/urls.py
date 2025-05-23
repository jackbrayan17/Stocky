from django.contrib import admin
from django.urls import path, include
from core import views
# from .views import OrderDetailView, orders_list
app_name = 'stoqtrack'
urlpatterns = [
    # Authentication Routes
      path('store/', include('core.urls')), 
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('suggestion/', views.suggestion_view, name='suggestion'),
    # Admin Route
    path('admin/', admin.site.urls),
    path('orders/<int:order_id>/download/', views.download_order_pdf, name='download_order_pdf'),
    path('orders/<int:order_id>/deliver/', views.mark_order_delivered, name='mark_order_delivered'),

    path('notifications/', views.notifications_view, name='notifications'),
  path('notifications/<int:order_id>/', views.notifications_view, name='notifications_with_order'),
# Product Management Routes
    path('store/<int:store_id>/products/', views.product_list, name='product_list'),
    path('store/<int:store_id>/add-product/', views.add_product, name='add_product'),
    path('product/<int:product_id>/update/', views.update_product, name='update_product'),
    path('home/', views.home_view, name='home'),
    # Order Routes
    path('dashboard/suggestions/', views.suggestion_list, name='suggestion_list'),
    path('store/<int:store_id>/create-order/', views.create_order, name='create_order'),
    # path('orders-list/', views.orders_list, name='orders_list'),
     path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    # Additional Pages
  path('suspend-manager/<int:store_id>/', views.suspend_manager, name='suspend_manager'),
    path('store/<int:store_id>/sales-report/', views.sales_report, name='sales_report'),
    path('store/<int:store_id>/orders-list/', views.orders_list, name='orders_list'),
    path('stock-alert-dashboard/', views.stock_alert_dashboard, name='stock_alert_dashboard'),
    path('store/<int:store_id>/profile/', views.store_profile, name='store_profile'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
]
