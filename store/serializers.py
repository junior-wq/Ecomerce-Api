from decimal import Decimal
from rest_framework import serializers 
from.models import Product,Cart,CartItem,Order,OrderItem
from django.conf import settings

class ProductSerializer(serializers.ModelSerializer):
  images = serializers.SerializerMethodField()
  class Meta:
    model=Product
    fields=['id','images','description','price','discount','discounted_price','name','stock']

  def get_images(self, product):
    return [self.context['request']\
            .build_absolute_uri(image.image.url)\
                for image in product.images.all()]
 

class CartItemProductSerializer(serializers.ModelSerializer):
  image=serializers.SerializerMethodField()
  class Meta:
    model=Product
    fields=['id','image','name','stock']
  
  def get_image(self,product):
    return self.context['request']\
      .build_absolute_uri(product.images.all()[0].image.url)
  
class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer()
    item_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_price']

    def get_item_price(self, obj):
        return obj.quantity * obj.product.discounted_price

class CartItemSimpleSerializer(serializers.ModelSerializer):
    
  def validate(self, attrs):
    product = attrs['product']
    quantity = attrs['quantity']

    if quantity > product.stock:
        raise serializers.ValidationError({
            'quantity': "A quantidade solicitada excede o estoque disponível."
        })
    return attrs

  class Meta:
    model = CartItem
    fields = ['id', 'product', 'quantity']
    

class CartSerializer(serializers.ModelSerializer):
  total_price=serializers.SerializerMethodField()
  total_items=serializers.SerializerMethodField()
  cart_item=CartItemSerializer(many=True) 

  class Meta:
    model=Cart
    fields=['id','cart_item','total_price','total_items']

  def get_total_price(self,cart:Cart):
    total = sum(item.quantity*item.product.discounted_price \
                for item in cart.cart_item.all())
    return total
  
  def get_total_items(self, cart: Cart):
      return sum(item.quantity for item in cart.cart_item.all())
  
  def save(self, **kwargs):
     return super().save(**kwargs)

class CartSimpleSerializer(serializers.ModelSerializer):
  class Meta:
    model=Cart
    fields=['id']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "customer", "status", "created_at", "items"]

class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
