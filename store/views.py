from django.db import transaction
from django.conf import settings
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from.models import Product,Cart,CartItem,Order,OrderItem
from.serializers import CartItemSimpleSerializer, ProductSerializer ,CartSerializer,CartSimpleSerializer,CartItemSerializer,OrderCreateSerializer,OrderSerializer,OrderItemSerializer
import stripe


class ProductView(ModelViewSet):
  queryset=Product.objects.all()
  serializer_class=ProductSerializer


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
    http_method_names=['get','patch']
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

        for item in cart.cart_item.all():
            if item.quantity > item.product.stock:
                return Response({"Error":f"Estoque insuficiente para {item.product.name}"},status=status.HTTP_400_BAD_REQUEST)

            OrderItem.objects.bulk_create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.discounted_price,
            )

            item.product.stock -= item.quantity
            item.product.save()

        cart.cart_item.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderItemViewSet(ModelViewSet):
    http_method_names=['get'] 
    serializer_class=OrderItemSerializer

    def get_queryset(self):
      return OrderItem.objects.filter(order_id=self.kwargs['order_pk'])

class CreateCheckoutSession(APIView):
    stripe.api_key = settings.STRIPE_API_KEY

    def post(self, request, cart_pk):
        domain = settings.YOUR_DOMAIN
        try:
            cart_items_qs = CartItem.objects.filter(cart_id=cart_pk)
            serializer = CartItemSerializer(cart_items_qs, many=True, context={"request": request})
            cart_items_data = serializer.data 

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
                            "images": [item["product"]["image"]]
                        }
                    },
                    "quantity": item["quantity"]
                })

                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=line_items,
                    mode='payment',
                    success_url=domain + '?success=true',
                    cancel_url=domain + '?canceled=true',
                )
                checkout_session.url
                return Response({'url':checkout_session.url},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
