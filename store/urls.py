# from rest_framework.routers import DefaultRouter
from.views import CategoryListView, CreateCheckoutSession, ProductView,CartView,CartItemView,OrderViewSet,OrderItemViewSet,SimpleOrderItemViewSet, StripeWebhook, track_whatsapp_click
from django.urls import path,include
from rest_framework_nested import routers

router=routers.DefaultRouter()
router.register('products',ProductView)
router.register('carts',CartView)
router.register('orders', OrderViewSet, basename='orders')
router.register('order_items', SimpleOrderItemViewSet, basename='order_items')

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
          CreateCheckoutSession.as_view(), name='checkout'),
      path('stripe/webhook/', 
           StripeWebhook.as_view(), name='stripe-webhook'),
    
      path('report/whatsapp/', track_whatsapp_click),
      path('product-categories/', CategoryListView.as_view(),name='category'),
      

    ]
)


#LOGICA PARA DEIXAR REVIEWS
# IF ORDER EXISTS AND NOT REVIEWS AND PLACED_ORDER_DATE < 4 DIAS

# RETUNR TRUE 
# ELSE RETUR FALSE



