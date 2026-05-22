import json
from django.db import transaction
from django.conf import settings
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny,IsAuthenticated

from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend 


from.models import Product,Cart,CartItem,Order,OrderItem, WhatsAppStats,Category
from.serializers import CartItemSimpleSerializer, CategorySerializer, ProductSerializer ,CartSerializer,CartSimpleSerializer,CartItemSerializer,OrderCreateSerializer,OrderSerializer,OrderItemSerializer
from django.db.models import Count
import stripe



@api_view(['POST'])
def track_whatsapp_click(request):
    product = request.data.get('product')

    obj, created = WhatsAppStats.objects.get_or_create(
        product_name=product
    )

    obj.clicks += 1
    obj.save()

    return Response({"status": "ok"})


class CategoryListView(ListAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer


#  .\venv\Scripts\Activate.ps1  
# deactivate     

class ProductView(ModelViewSet):
  queryset=Product.objects.all()
  serializer_class=ProductSerializer

  filter_backends = [DjangoFilterBackend, SearchFilter]
  search_fields = ['name']
  filterset_fields = ['category']
#   pagination_class=CustomPagination
  
  
class CartView(ModelViewSet):
  queryset=Cart.objects.all()
  
  def get_serializer_class(self):
    if self.request.method=='POST':
      return CartSimpleSerializer
    else:
      return CartSerializer
  


class CartItemView(ModelViewSet):
  serializer_class=CartItemSerializer
  def get_queryset(self):
    return CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])

  def get_serializer_class(self):

    if self.request.method in ['POST','PATCH']:
      return CartItemSimpleSerializer
    else: 
      return CartItemSerializer
    
  def perform_create(self, serializer):
    cart_id = self.kwargs['cart_pk']
    serializer.save(cart_id=cart_id)

  def create(self, request, *args, **kwargs):
    cart = self.kwargs['cart_pk']
    product = request.data.get("product")
    quantity = request.data.get("quantity", 1)

    # Verifica se o item já existe
    existing_item = CartItem.objects.filter(cart=cart, product=product).first()
    
    if existing_item:
      print(existing_item.quantity)
      existing_item.quantity += int(quantity)
      existing_item.save()
      serializer = self.get_serializer(existing_item)
      return Response(serializer.data, status=status.HTTP_200_OK)
    else:
      return super().create(request, *args, **kwargs)
  
 

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    # http_method_names=['get','patch']
    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        user = request.user
        cart_id = serializer.validated_data["cart_id"]

        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return Response({"error": "Carrinho não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        if not cart.cart_item.exists():
            return Response({"error": "Carrinho vazio"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(customer=user)
        order_itens=[]

        for item in cart.cart_item.all():
            if item.quantity > item.product.stock:
                return Response({"Error":f"Estoque insuficiente para {item.product.name}"},status=status.HTTP_400_BAD_REQUEST)
            order_itens.append(
              OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.discounted_price,
              ))

            OrderItem.objects.bulk_create(order_itens)

            item.product.stock -= item.quantity
            item.product.save()

        # cart.cart_item.all().delete()
        item.delete()
        return Response(
            OrderSerializer(order, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

        # return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)



class OrderItemViewSet(ModelViewSet):
    http_method_names=['get'] 
    serializer_class=OrderItemSerializer

    def get_queryset(self):
      return OrderItem.objects.filter(order_id=self.kwargs['order_pk'])


class SimpleOrderItemViewSet(ModelViewSet):
    http_method_names=['get'] 
    serializer_class=OrderItemSerializer

    
    def get_queryset(self):
      # customer_order=Order.objects.filter(customer=self.request.user).first()
      # return OrderItem.objects.filter(order_id=customer_order.id)
      return OrderItem.objects.all()



class CreateCheckoutSession(APIView):
    stripe.api_key = settings.STRIPE_API_KEY

    def post(self, request, cart_pk):
        domain = settings.YOUR_DOMAIN
        try:
            cart_items_qs = CartItem.objects.filter(cart_id=cart_pk)
            serializer = CartItemSerializer(cart_items_qs, many=True, context={"request": request})
            cart_items_data = serializer.data 
            # print(cart_items_data)
            if not cart_items_qs.exists():
                return Response({"error": "Carrinho vazio ou não encontrado."}, status=400)
        
            line_items = []
            for item in cart_items_data:
                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(item["item_price"] / item["quantity"] * 100),  # preço unitário em centavos
                        "product_data": {
                            "name": item["product"]["name"],
                            "images": [request.build_absolute_uri(item["product"]["image"])]
                            # "images": [item["product"]["image"]]
                        }
                    },
                    "quantity": item["quantity"]
                })

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode='payment',
                client_reference_id=cart_pk,
                metadata={"user_id": str(request.user.id) },

                # success_url='http://localhost:5173/order-success' + '?success=true',
                # cancel_url=domain + '?canceled=true',
                # success_url = domain + '/order-success?success=true',
                # cancel_url = domain + '/cancel?canceled=true',
                # success_url = 'https://httpbin.org/status/200?success=true',
                success_url = 'http://localhost:5173/order-success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url = 'https://httpbin.org/status/200?canceled=true',
            )
            checkout_session.url
            return Response({'url':checkout_session.url},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
class StripeWebhook(APIView):
    # permission_classes=[IsAuthenticated]
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')  # usa .get() para evitar KeyError

        print("Webhook recebido!")
        print("Payload:", payload)
        print("Signature header:", sig_header)

        # try:
        #     event = stripe.Webhook.construct_event(
        #         payload,
        #         sig_header,
        #         settings.STRIPE_WEBHOOK_SECRET
        #     )
        # except ValueError as e:
        #     # Invalid payload
        #     print("Invalid payload:", e)
        #     return Response(status=400)
        # except stripe.error.SignatureVerificationError as e:
        #     # Invalid signature
        #     print("Invalid signature:", e)
        #     return Response(status=400)

        # # Agora sim, dentro do evento válido
        # if event['type'] == 'checkout.session.completed':
        #     session = event['data']['object']
        #     print("Evento checkout.session.completed recebido!")
        #     print("Cart ID:", session.get('client_reference_id'))
        #     print("User ID:", session['metadata'].get('user_id'))

        #     cart_id = session.get('client_reference_id')
        #     user_id = session['metadata'].get('user_id')

        #     if not cart_id:
        #         print("Erro: client_reference_id não encontrado")
        #         return Response(status=200)

        #     with transaction.atomic():
     
        #         order = Order.objects.create(customer=user_id)

        #         cart_items = CartItem.objects.filter(cart_id=cart_id)
        #         for item in cart_items:
        #             if item.quantity > item.product.stock:
        #                 # opcional: cancelar ou tratar erro
        #                 raise ValueError("Estoque insuficiente")

        #             OrderItem.objects.create(
        #                 order=order,
        #                 product=item.product,
        #                 quantity=item.quantity,
        #                 price=item.product.discounted_price,
        #             )
        #             item.product.stock -= item.quantity
        #             item.product.save()

        #         cart_items.delete()

        return Response(status=200,data=payload)


#######################################################################

# class StripeWebhook(APIView):
#     def post(self, request, *args, **kwargs):
#         payload = request.body
#         sig_header = request.META['HTTP_STRIPE_SIGNATURE']

#         print("Webhook recebido!")
#         print("Payload:", request.body)
#         print("Headers:", request.META.get('HTTP_STRIPE_SIGNATURE'))
#         print("Cart ID recebido:", session['client_reference_id'])


#         try:
#             event = stripe.Webhook.construct_event(
#                 payload,
#                 sig_header,
#                 settings.STRIPE_WEBHOOK_SECRET
#             )
#         except stripe.error.SignatureVerificationError:
#             return Response(status=400)

#         # Quando o pagamento for concluído
#         if event['type'] == 'checkout.session.completed':
#             session = event['data']['object']
#             cart_id = session['client_reference_id']
#             user_id = session['metadata']['user_id']

#             with transaction.atomic():
#                 # cria Order e OrderItems baseado no cart_id
#                 order = Order.objects.create(customer=user_id)  # ajuste isso
#                 cart_items = CartItem.objects.filter(cart_id=cart_id)

#                 for item in cart_items:
#                     OrderItem.objects.create(
#                         order=order,
#                         product=item.product,
#                         quantity=item.quantity,
#                         price=item.product.discounted_price,
#                     )
#                     item.product.stock -= item.quantity
#                     item.product.save()

#                 cart_items.delete()

#         return Response(status=200)
