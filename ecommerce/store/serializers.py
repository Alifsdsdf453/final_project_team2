from rest_framework import serializers
from .models import Category, Product, Customer, Order, OrderItem, CustomUser


# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active']



# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_detail = CategorySerializer(read_only=True, source='category')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'category',
            'category_detail', 'stock_quantity', 'is_available', 'image_url'
        ]
        read_only_fields = ['stock_quantity']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value



# User Serializer (CustomUser)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']



# Customer Registration Serializer
class CustomerRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # ربط مع CustomUser

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'registration_date', 'user']

    def validate_email(self, value):
        if Customer.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        # إنشاء المستخدم أولاً
        user = CustomUser.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data.get('password', 'defaultpassword'),  # يمكن تعديلها
            role=user_data['role']
        )

        # إنشاء Customer وربطه بالمستخدم
        customer = Customer.objects.create(user=user, **validated_data)
        return customer


# Order Item Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'unit_price']



# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.first_name')
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_name', 'order_date', 'total_amount', 'status', 'notes', 'items']
        read_only_fields = ['total_amount', 'order_date', 'status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        total = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            # تحقق من توفر المنتج والكمية
            if not product.is_available or product.stock_quantity < quantity:
                raise serializers.ValidationError(f"Product {product.name} is out of stock or unavailable")

            # إنشاء OrderItem
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price
            )

            # تحديث stock_quantity
            product.stock_quantity -= quantity
            product.save()

            total += product.price * quantity

        # تحديث total_amount
        order.total_amount = total
        order.save()

        return order
