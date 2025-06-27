from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/products', views.ProductViewSet, basename='product')
router.register(r'api/carts', views.CartViewSet, basename='cart')
router.register(r'api/orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('author/', views.author, name='author'),
    path('spec/', views.spec_list, name='spec_list'),
    path('spec/<int:id>/', views.spec_detail, name='spec_detail'),
    path('404/', views.error_404, name='error_404'),
    path('catalog/', views.product_list, name='product_list'),
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout, name='checkout'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]