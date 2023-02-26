from django.urls import include, path, reverse, resolve
from rest_framework.test import APITestCase, URLPatternsTestCase
from img_api.urls import urlpatterns, router


class TestUrlsViewset(APITestCase, URLPatternsTestCase):
    
    urlpatterns = [
        path('', include(router.urls))
    ]

    def test_list(self): 
        name = 'api-list'
        url = reverse(name)
        res_url = resolve(url).view_name
        self.assertEqual(res_url, name)

    def test_retrieve(self):
        name = 'api-detail'
        url = reverse(name, args=[1])
        res_url = resolve(url).view_name
        self.assertEqual(res_url, name)

    def test_action(self):
        name = 'api-generate-expiring-url'
        url = reverse(name, args=[1])
        res_url = resolve(url).view_name
        self.assertEqual(res_url, name)

class TestImageView(APITestCase):
    def setUp(self) -> None:
        self.name = 'image_view'
        return super().setUp()
    def test_image_view(self):
        file = 'example.jpg'
        url = reverse(self.name, kwargs={'pk': 1, 'filename': file})
        res_url = resolve(url).view_name
        self.assertEqual(res_url, self.name)
