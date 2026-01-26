from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# 1. Custom User Model (لتحقيق نظام الأدوار RBAC)
class CustomUser(AbstractUser):
    ROLES = (
        ('Admin', 'Admin'),
        ('Seller', 'Seller'),
        ('Customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='Customer') # [cite: 67, 71]

# 2. Category Model
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True) # [cite: 8]

    def __str__(self):
        return self.name

# 3. Product Model
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock_quantity = models.PositiveIntegerField() # [cite: 10]
    is_available = models.BooleanField(default=True)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

# 4. Customer Model
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    registration_date = models.DateTimeField(auto_now_add=True) # [cite: 12]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

# 5. Order Model
class Order(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ] # [cite: 58]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    notes = models.TextField(blank=True) # [cite: 14]

    def __str__(self):
        return f"Order {self.id} - {self.customer}"

# 6. OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2) # [cite: 16]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"