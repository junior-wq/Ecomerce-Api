from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]  # Valida se o desconto está entre 0 e 100
    )
    stock = models.PositiveIntegerField(default=0)

    @property
    def discounted_price(self):
        discount_decimal = Decimal(self.discount) / Decimal(100)
        return self.price - (self.price * discount_decimal)

    def __str__(self):
        return self.name

class ProductImages(models.Model):
    product=models.ForeignKey(Product ,related_name='images', on_delete=models.CASCADE)
    image=models.ImageField(upload_to='product_images/')

    def clean(self):
        if self.product.images.count() >= 5:
            raise ValidationError("Este produto já possui o número máximo de imagens (5).")



class Cart(models.Model):
  created_at=models.DateTimeField(auto_now_add=True)
  id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

  def __str__(self):
    return str(self.id)

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='cart_item')
    
    def clean(self):
        if self.quantity > self.product.stock:
            raise ValidationError("A quantidade solicitada excede o estoque disponível.")
        
    class Meta:
        unique_together = ["product", "cart"]
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    

class User(AbstractUser):
    email=models.EmailField(unique=True)


class Order(models.Model):

    PENDING = 'pending'
    PAID = 'paid'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELED = 'canceled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELED, 'Canceled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at=models.DateField(auto_now_add=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    @property
    def total_price(self):
        return sum([item.total_price for item in self.items.all()])
    
    def __str__(self):
        return f"Order {self.id} - {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)  # preço fixado no momento da compra

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.price * self.quantity