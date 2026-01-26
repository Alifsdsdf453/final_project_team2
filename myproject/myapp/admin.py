from django.contrib import admin
from .models import CustomUser, Category, Product, Customer, Order, OrderItem

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'total_amount', 'status')
    list_filter = ('status', 'order_date')
    inlines = [OrderItemInline] 

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity', 'category', 'is_available')
    list_editable = ('stock_quantity', 'is_available') 
    search_fields = ('name',)

admin.site.register(Category)
admin.site.register(Customer)
