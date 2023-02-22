from functools import partial
from urllib.parse import urlparse
from .img_manip import binarize
from datetime import datetime, timedelta
from django.core.signing import Signer
from rest_framework import serializers
from img_api.models import Image, CustUser, Tier
from django.contrib.auth.models import User

from easy_thumbnails.templatetags.thumbnail import thumbnail_url
from easy_thumbnails.files import get_thumbnailer

class TierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tier
        fields = '__all__'

class CustUserSerializer(serializers.ModelSerializer):
    account_type = TierSerializer()

    class Meta:
        model = CustUser
        fields = '__all__'

class ThumbnailSerializer(serializers.ImageField):
    def __init__(self, alias, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.read_only = True
        self.alias = alias

    def to_representation(self, value):
        if not value:
            return None

        url = thumbnail_url(value, self.alias)
        request = self.context.get('request', None)
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class ImageSerializer(serializers.ModelSerializer):


    class Meta:
        model = Image
        fields = '__all__'


class ImgSerializer(serializers.ModelSerializer):
    # image = serializers.SerializerMethodField()
    bin_image = serializers.SerializerMethodField()
    hashed_url = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context')
        options = context.get('options')
        orig_im = options.get('original')
        thumbnails = options.get('thumbnails')
        exp_link = options.get('link_exp')
        super().__init__(*args, **kwargs)
        # self.fields['bin_image'] = serializers.SerializerMethodField()

        if orig_im == 1:
            self.fields['image'] = serializers.SerializerMethodField()

        for field, size in thumbnails.items():
            field_name = f'thumb_{field}'
            method_name = f'get_{field_name}'
            setattr(self, method_name, partial(
                self.get_thumbnail_url, size=size))
            self.fields[field_name] = serializers.SerializerMethodField(
                method_name=method_name)
    

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_bin_image(self, obj):
        request = self.context.get('request')
        img = binarize(obj.image, obj.image.name, 128)
        return request.build_absolute_uri(img)
    
    def get_hashed_url(self, obj):
        image = self.get_bin_image(obj)
        print(image, 'SERIALIZER')
        signer = Signer(sep='&signed=')
        time_stamp = datetime.now() + timedelta(seconds=30)
        expiry_date = time_stamp.strftime("%Y-%m-%d-%H-%M-%S")
        url = image + '/?expires=' + expiry_date
        hashed_url = signer.sign(url)
        return hashed_url



    def get_thumbnail_url(self, obj, size):
        request = self.context.get('request')
        thumbnailer = get_thumbnailer(obj.image)
        thumbnail_options = {
            'size': (size, size),
            'crop': True
        }
        # print(thumbnail_options)
        thumb = thumbnailer.get_thumbnail(thumbnail_options)
        return request.build_absolute_uri(thumb.url)
    

    def create(self, obj):
        pass

    class Meta:
        model = Image
        fields = [
            'id',
            'name',
            'created_by',
            'bin_image',
            'hashed_url'
        ]

class ImgUploadSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    image = serializers.ImageField()


    class Meta:
        model = Image
        fields = [
            'name',
            'image'
        ]