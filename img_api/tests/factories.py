import factory
from PIL import Image
from django.contrib.auth.models import User
from img_api.models import CustUser, Image, Tier


class UserModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user %03d" % n)
    password = factory.Sequence(lambda n: "test12#$ %03d" % n)

class TierModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tier

    name = factory.Sequence(lambda n: "foto %03d" % n)
    options = {
        "small": 200,
        "big": 400
    }
    original_link = True
    bin_img_exp_link = 300
    list_details = False



class CustUserModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustUser

    account_type = factory.SubFactory(TierModelFactory)
    user = factory.SubFactory(UserModelFactory)


class ImageModelFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Image

    image = factory.django.ImageField()
    name = factory.Sequence(lambda n: "Adam %03d" % n)
    created_by = factory.SubFactory(CustUserModelFactory)