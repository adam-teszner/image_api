import json
import tempfile
from datetime import datetime

from django.contrib.auth.models import User
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient, APITestCase, override_settings

from img_api.views import ImageView, ImgApiViewSet

from . import factories



MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestApiViewSet(APITestCase):
    def setUp(self) -> None:

        self.client = APIClient()
        self.view = ImgApiViewSet.as_view(actions=
            {
            'get': 'list',
            'get': 'retrieve',
            'post': 'create',
            'get': 'generate_expiring_url',
            'post': 'generate_expiring_url'
            }
        )
        self.user = factories.UserModelFactory.create()
        self.tier = factories.TierModelFactory.create()
        self.cust_user = factories.CustUserModelFactory(user=self.user,
                                                        account_type=self.tier)
        self.image = factories.ImageModelFactory(created_by=self.cust_user)

        return super().setUp()
    
    def test_list(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        self.client.force_login(self.user)
        response = self.client.get(f'/api/{self.image.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        
        data = {
            'name': 'Adam',
            'image': self.image.image
        }
        self.client.force_login(self.user)
        response = self.client.post('/api/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_not_image(self):
        data = {
            'name': 'Adam',
            'image': 'not a file'
        }
        self.client.force_login(self.user)
        response = self.client.post('/api/', data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_generate_expiring_url_get(self):
        self.client.force_login(self.user)
        response = self.client.get(f'/api/{self.image.id}/generate_expiring_url/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_generate_expiring_url_post(self):
        self.client.force_login(self.user)
        response = self.client.post(
            f'/api/{self.image.id}/generate_expiring_url/',
            data={'expiration_time': '300'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_generate_expiring_url_post_invalid_time(self):
        self.client.force_login(self.user)
        response = self.client.post(
            f'/api/{self.image.id}/generate_expiring_url/',
            data={'expiration_time': '10'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestImageView(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.view = ImageView.as_view()
        self.user = factories.UserModelFactory.create()
        self.user_one = User.objects.create_user(
            username = 'Lauren',
            password = 'sercretpass'
        )

        self.tier = factories.TierModelFactory.create()
        self.cust_user = factories.CustUserModelFactory(user=self.user_one,
                                                        account_type=self.tier)
        self.image = factories.ImageModelFactory(created_by=self.cust_user)

        # Log the user to get the link
        cred = {
            'username': 'Lauren',
            'password': 'sercretpass'
        }
        self.client.login(**cred)

        # Get the content from response, convert bytes to json/dict
        content = self.client.get(f'/api/{self.image.id}/')
        self.b = content.content
        self.d = json.loads(self.b)

        # Extract needed data
        self.binary_link = self.d.get('binary_image_link')
        self.original_image = self.d.get('original_image')


        return super().setUp()
    
    def test_get(self):

        # Test if logged user can get original image
        response = self.client.get(self.original_image+'/')        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Logout the user for tests
        self.client.logout()
        
        # Try to open image (using link)
        response = self.client.get(self.binary_link)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try to open image (signed-link, but modified)
        mod_bin_link = self.binary_link + 'x'
        response = self.client.get(mod_bin_link)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Try to open different image
        response = self.client.get(self.original_image+'/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Test unathenticated user can see bin image after link has expired
    # https://github.com/spulec/freezegun
    @freeze_time(datetime.now(), tz_offset=24)
    def test_get_expired_link(self):
        self.client.logout()
        response = self.client.get(self.binary_link)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)