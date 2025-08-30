import time
from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.TextField()
    message = models.TextField()

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=10)  # S, M, L, XL

    def __str__(self):
        return self.name



class Product(models.Model):
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    # Main image
    image_main = models.ImageField(upload_to='products/')

    # Optional thumbnails
    image_thumb1 = models.ImageField(upload_to='products/', blank=True, null=True)
    image_thumb2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image_thumb3 = models.ImageField(upload_to='products/', blank=True, null=True)

    stock = models.PositiveIntegerField(default=0)
    sizes = models.ManyToManyField(Size, blank=True)

    # Sale related fields
    is_on_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_display_price(self):
        if self.is_on_sale and self.sale_price:
            return self.sale_price
        return self.price


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    size = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(max_length=500)

    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return self.user.username  # now it shows user's name
    



from django.db import models
from django.contrib.auth.models import User
from myApp.models import Product  # assuming Product model exists



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')


    def __str__(self):
        return f"Order #{self.id} by {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    size = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    def total_price(self):
        return self.price * self.quantity
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
