from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ProductViewSet, OrderViewSet, 
    StatisticsView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    path('statistics/', StatisticsView.as_view(), name='api-statistics'),
    
    path('categories/<int:pk>/products/', CategoryViewSet.as_view({'get': 'products'}), name='category-products'),
]