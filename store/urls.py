# from rest_framework.routers import DefaultRouter
from.views import CreateCheckoutSession, ProductView,CartView,CartItemView,OrderViewSet,OrderItemViewSet
from django.urls import path,include
from rest_framework_nested import routers

router=routers.DefaultRouter()
router.register('products',ProductView)
router.register('carts',CartView)
router.register('orders', OrderViewSet, basename='orders')

cart_router = routers.NestedDefaultRouter(router, r'carts', lookup='cart')
cart_router.register(r'items', CartItemView, basename='cart-items')

order_router=routers.NestedDefaultRouter(router, r'orders', lookup='order')
order_router.register(r'items', OrderItemViewSet, basename='order-items')

urlpatterns = (
    router.urls +
    cart_router.urls +
    order_router.urls +
    [
      path('checkout/<uuid:cart_pk>/',
      CreateCheckoutSession.as_view(), name='checkout')
    ]
)




