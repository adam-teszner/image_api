import tempfile
from datetime import datetime, timedelta

from django.core.signing import Signer
from rest_framework.test import (APIRequestFactory, APITestCase,
                                 override_settings)

from img_api.serializers import ExpiringLinkSerializer, PrimaryImageSerializer

from . import factories



MEDIA_ROOT = tempfile.mkdtemp()

class MyReq(APIRequestFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = kwargs.get('data')
    
@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestPrimaryImageSerializer(APITestCase):
    def setUp(self) -> None:
        self.user = factories.UserModelFactory.create()
        self.tier = factories.TierModelFactory.create()
        self.cust_user = factories.CustUserModelFactory(user=self.user,
                                                        account_type=self.tier)
        self.image = factories.ImageModelFactory(created_by=self.cust_user)
        self.req_factory = APIRequestFactory()
        self.request = self.req_factory.get('/api/')
        self.context = {
            'request': self.request,
            'name': self.tier.name,
            'options': self.tier.options,
            'original_link': self.tier.original_link,
            'bin_img_exp_link': self.tier.bin_img_exp_link
        }

        self.request = APIRequestFactory()
        self.serializer = PrimaryImageSerializer(data=self.image, context=self.context)
        return super().setUp()
    
    def test_serializer_init(self):
        
        context = self.serializer.context
        thumbnails = context.get('options')
        orig_img_link = context.get('original_link')
        binary_img_link = context.get('bin_img_exp_link')

        for k,v in thumbnails.items():
            field = 'thumb_' + k
            self.assertIn(field, self.serializer.fields)
        
        if orig_img_link:
            self.assertIn('original_image', self.serializer.fields)

        if binary_img_link != 0 and binary_img_link != None:
            self.assertIn('binary_image_link', self.serializer.fields)
    
    def test_original_link(self):
        res = self.serializer.get_original_image(self.image)
        expected = r'^http://testserver/media/\d+/images/\d{20}/example\.jpg$'
        self.assertRegex(res, expected)


    def test_binary_image(self):
        res = self.serializer.get_bin_image(self.image)
        expected = r'^http://testserver/media/\d+/images/\d{20}/BINARY_128_example\.jpg$'
        self.assertRegex(res, expected)

    def test_binary_image_link(self):    
        seconds = self.context.get('bin_img_exp_link')
        image = self.serializer.get_bin_image(self.image)
        signer = Signer(sep='&signed=')
        try:
            time_stamp = datetime.now() + timedelta(seconds=seconds)
        except TypeError:
            return None
        expiry_date = time_stamp.strftime("%Y-%m-%d-%H-%M-%S")
        url = image + '/?expires=' + expiry_date
        hashed_url = signer.sign(url)        
        self.assertTrue(signer.unsign(hashed_url))
        expected = r'^http://testserver/media/\d+/images/\d{20}/BINARY_128_example\.jpg/\?expires=' + expiry_date + r'&signed=.+$'
        self.assertRegex(hashed_url, expected)

    def test_get_thumbnail_url(self):
        size = 100
        res = self.serializer.get_thumbnail_url(self.image, size)
        expected = r'^http://testserver/media/\d+/images/\d{20}/example\.jpg\.0x' + str(size) + r'_q85\.jpg$'
        self.assertRegex(res, expected)


    def test_create(self):
        data = {
            'name': 'Adam',
            'image': self.image.image
        }
        context = {'created_by': self.cust_user}
        ser = PrimaryImageSerializer(data=data, context=context)
        ser.is_valid()
        ser.save()
        self.assertIsNotNone(ser.instance.id)
        self.assertTrue(ser.instance.created_by, self.cust_user)

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestExpiringLinkSerializer(APITestCase):
    def setUp(self) -> None:
        self.user = factories.UserModelFactory.create()
        self.tier = factories.TierModelFactory.create()
        self.cust_user = factories.CustUserModelFactory(user=self.user,
                                                        account_type=self.tier)
        self.image = factories.ImageModelFactory(created_by=self.cust_user)
        self.req = APIRequestFactory()
        self.request = self.req.get('/api/')
        self.context = {
            'request': self.request,
            'bin_img_exp_link': self.tier.bin_img_exp_link,
            'object': self.image
        }

        self.serializer = ExpiringLinkSerializer(data=self.image, context=self.context)
        return super().setUp()
    
    def test_get_url_get(self):
        res = self.serializer.get_url(self.image)
        expected = r'^http://testserver/media/\d+/images/\d{20}/BINARY_128_example\.jpg/\?expires=\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}&signed=.+$'
        self.assertRegex(res, expected)

    def test_get_url_post(self):

        ''' 
        request from APIRequestFacotory doesnt have a 'data' attribute...
        not sure if it's correct way to do it
        '''
        data = {'expiration_time': '300'}
        req = MyReq()
        request = req.post('/api/')
        setattr(request, 'data', data)
        context = {
            'request': request,
            'object': self.image
            }
        serializer = ExpiringLinkSerializer(data=request.data, context=context)
        res = serializer.get_url(self.image)
        expected = r'^http://testserver/media/\d+/images/\d{20}/BINARY_128_example\.jpg/\?expires=\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}&signed=.+$'
        self.assertRegex(res, expected)

    

