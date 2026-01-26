from rest_framework.test import APITestCase
from django.urls import reverse
from .models import CustomUser, Category, Product

class ECommerceTests(APITestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(username='admin', role='Admin', password='password')
        self.customer = CustomUser.objects.create_user(username='user', role='Customer', password='password')
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Phone", price=500, category=self.category, stock_quantity=10
        )

    def test_login_jwt(self):
        url = reverse('token_obtain_pair')
        data = {"username": "user", "password": "password"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_admin_create_category(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('category-list')
        data = {"name": "New Category"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_customer_cannot_create_category(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('category-list')
        data = {"name": "Illegal Category"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)

    def test_product_search(self):
        url = reverse('product-list') + "?search=Phone"
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)

    def test_pagination_exists(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertIn('results', response.data)

    def test_admin_stats_access(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('api-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_customer_stats_denied(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('api-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_get_category_products(self):
        url = reverse('category-products', args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
