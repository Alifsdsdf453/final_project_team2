from rest_framework import serializers
from django.db import transaction
from .models import Category, Product, Customer, Order, OrderItem, CustomUser

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active']

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(read_only=True, source='category')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'category',
            'category_detail', 'stock_quantity', 'is_available', 'image_url'
        ]

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role', 'first_name', 'last_name']

# Customer Registration Serializer
class CustomerRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ['user', 'phone', 'address']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        with transaction.atomic():
            user = CustomUser.objects.create_user(**user_data)
            customer = Customer.objects.create(user=user, **validated_data)
        return customer

# Order Item Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price']
        read_only_fields = ['unit_price']

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer_name = serializers.ReadOnlyField(source='customer.user.username')

    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_name', 'order_date', 'total_amount', 'status', 'notes', 'items']
        read_only_fields = ['total_amount', 'status', 'order_date']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            total = 0
            
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']

                if not product.is_available or product.stock_quantity < quantity:
                    raise serializers.ValidationError(f"المنتج {product.name} غير متوفر حالياً أو الكمية المطلوبة غير متاحة.")

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price
                )

                product.stock_quantity -= quantity
                product.save()

                total += product.price * quantity

            order.total_amount = total
            order.save()
            
        return order