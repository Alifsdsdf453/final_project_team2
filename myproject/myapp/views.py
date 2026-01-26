from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Order, Customer
from .serializers import *
from rest_framework.views import APIView
from permission import IsAdminUser, IsSellerUser, IsCustomerUser
from rest_framework import permissions

# 1. Categories ViewSet
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()] # الأدمن فقط يدير التصنيفات 
        return [permissions.AllowAny()]

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        products = category.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

# 2. Products ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'price'] 
    search_fields = ['name', 'description'] 

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSellerUser()] 
        return [permissions.AllowAny()]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsCustomerUser()] 
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Customer':
            return Order.objects.filter(customer__user=user) 
        return Order.objects.all() 

    @action(detail=True, methods=['put'], url_path='status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        if request.user.role in ['Admin', 'Seller']:
            order.status = request.data.get('status')
            order.save()
            return Response({'status': 'order status updated'})
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)


class StatisticsView(APIView):
    permission_classes = [IsAdminUser] 

    def get(self, request):
        stats = {
            'total_customers': Customer.objects.count(),
            'total_orders': Order.objects.count(),
            'total_products': Product.objects.count(),
            'top_5_products': Product.objects.order_by('-orderitem__quantity')[:5].values('name') # اختيار أعلى 5 منتجات طلباً [cite: 63]
        }
        return Response(stats)
