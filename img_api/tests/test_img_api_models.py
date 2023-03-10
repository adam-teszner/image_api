import tempfile

from django.test import TestCase, override_settings

from img_api.models import CustUser, Image

from . import factories




# Creates a temp directory, outside of projects MEDIA_ROOT folder
# https://dirtycoder.net/2016/02/09/testing-a-model-that-have-an-imagefield/
MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestModels(TestCase):


    def setUp(self):        
        self.user = factories.UserModelFactory.create()
        self.tier = factories.TierModelFactory.create()
        self.cust_user = factories.CustUserModelFactory(user=self.user,
                                                        account_type=self.tier)
        self.image = factories.ImageModelFactory(created_by=self.cust_user)
        self.objects = [
            self.user,
            self.tier,
            self.cust_user,
            self.image
        ]


    def test_models_create(self):
        for o in self.objects:
            self.assertIsNotNone(o.id)
        self.assertEqual(self.cust_user.user, self.user)
        self.assertEqual(self.cust_user.account_type, self.tier)
        
        

    # Testing on_delete.CASCADE and on_delete.SET_NULL
    def test_models_delete(self):
        self.tier.delete()
        self.cust_user.refresh_from_db()
        self.assertEqual(self.cust_user.account_type, None)
        self.user.delete()
        with self.assertRaises(CustUser.DoesNotExist):
            self.cust_user.refresh_from_db()
        self.assertRaises(Image.DoesNotExist)        
        
            
    # Testing image upload and if user.id is in file path
    def test_image_upload(self):
        img = factories.ImageModelFactory.create()
        user_id = str(img.image)
        id_path = int(user_id[0])
        self.assertIsNotNone(img.image)
        self.assertEqual(id_path, img.created_by.id)
