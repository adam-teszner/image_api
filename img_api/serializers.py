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
    # bin_image = serializers.SerializerMethodField()
    hashed_url = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context')
        options = context.get('options')
        orig_im = options.get('original')
        thumbnails = options.get('thumbnails')
        exp_link = options.get('link_exp')
        super().__init__(*args, **kwargs)

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
        # print(image, 'SERIALIZER')
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
        thumb = thumbnailer.get_thumbnail(thumbnail_options)
        return request.build_absolute_uri(thumb.url)
    

    class Meta:
        model = Image
        fields = [
            'id',
            'name',
            'created_by',
            # 'bin_image',
            'hashed_url',
        ]
'''
class ImgUploadSerializer(serializers.ModelSerializer):
    expiration_time = serializers.CharField()
    
    def get_hashed_url(self, obj, time, request):
        request = self.context.get('request')
        image = binarize(obj.image, obj.image.name, 128)
        # print(image, 'SERIALIZER')
        signer = Signer(sep='&signed=')
        time_stamp = datetime.now() + timedelta(seconds=time)
        expiry_date = time_stamp.strftime("%Y-%m-%d-%H-%M-%S")
        url = image + '/?expires=' + expiry_date
        hashed_url = signer.sign(url)
        return request.build_absolute_uri(hashed_url)


    def create(self, validated_data):
        request = self.context.get('request')
        image = validated_data.pop('image')
        created_by = self.context.get('created_by')
        name = validated_data.pop('name')
        expiration_time = validated_data.pop('expiration_time')

        img_obj = Image.objects.create(
            image = image,
            created_by = created_by,
            name = name
        )

        expiration_link = self.get_hashed_url(img_obj, int(expiration_time), request)

        return {
            'id': img_obj.id,
            'name': img_obj.name,
            'created_by': img_obj.created_by,
            'image': img_obj.image,
            'expiration_time': expiration_link
        }
    

    class Meta:
        model = Image
        fields = [
            'id',
            'name',
            'image',
            'expiration_time'
        ]
'''

class ImgUploadSerializer(serializers.ModelSerializer):
    expiration_time = serializers.IntegerField()

    class Meta:
        model = Image
        fields = [
            'id',
            'name',
            'image',
            'expiration_time'
        ]


class PrimaryImageSerializer(serializers.ModelSerializer):
    '''
    Serializer for generating model data and dynamically generating
    thumbnails based on Tier settings.
    '''

    image = serializers.ImageField(write_only=True)
    details = serializers.HyperlinkedIdentityField(
        view_name='api-detail',
        read_only=True,
        lookup_field='pk'
    )

    def __init__(self, *args, **kwargs):
        # Get data from context, passed from view, based on current User Tier
        context = kwargs.get('context')
        thumbnails = context.get('options')
        orig_img_link = context.get('original_link')
        binary_img_link = context.get('bin_img_exp_link')
        super().__init__(*args, **kwargs)


        # Dynamically create thumbnails based on "options" JSONfield in
        # in Tier model.
        try:
            for field, size in thumbnails.items():
                field_name = f'thumb_{field}'
                method_name = f'get_{field_name}'
                setattr(self, method_name, partial(
                    self.get_thumbnail_url, size=size))
                self.fields[field_name] = serializers.SerializerMethodField(
                    method_name=method_name)
        except AttributeError:
            pass

        # Serialize link to the original image
        if orig_img_link == True:
            self.fields['original_image'] = serializers.SerializerMethodField()

        # Save binary image, then serialize expiring link 
        # to the binary version of the image
        if binary_img_link != 0 and binary_img_link != None:
            self.fields['binary_image_link'] = serializers.SerializerMethodField()
            

    def get_original_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_thumbnail_url(self, obj, size):
        request = self.context.get('request')
        thumbnailer = get_thumbnailer(obj.image)
        thumbnail_options = {
            'size': (size, size)
        }
        thumb = thumbnailer.get_thumbnail(thumbnail_options)
        return request.build_absolute_uri(thumb.url)
    
    def get_bin_image(self, obj):
        request = self.context.get('request')
        img = binarize(obj.image, obj.image.name, 128)
        return request.build_absolute_uri(img)
    
    def get_binary_image_link(self, obj):
        seconds = self.context.get('bin_img_exp_link')
        image = self.get_bin_image(obj)
        signer = Signer(sep='&signed=')
        try:
            time_stamp = datetime.now() + timedelta(seconds=seconds)
        except TypeError:
            return None
        expiry_date = time_stamp.strftime("%Y-%m-%d-%H-%M-%S")
        url = image + '/?expires=' + expiry_date
        hashed_url = signer.sign(url)
        return hashed_url
    
    def create(self, validated_data):
        created_by = self.context.get('created_by')
        image = Image.objects.create(**validated_data, created_by=created_by)
        return image
    
    class Meta:
        model = Image
        fields = [
            'id',
            'name',
            'image',
            'details'
        ]

class ExpiringLinkSerializer(serializers.Serializer):
    expiration_time = serializers.IntegerField(write_only=True)
    url = serializers.SerializerMethodField()
    
    
    def get_url(self, obj):
        request = self.context.get('request')
        obj = self.context.get('object')
        image = binarize(obj.image, obj.image.name, 128)
        signer = Signer(sep='&signed=')
        if request.method == 'GET':
            time = self.context.get('bin_img_exp_link')
        elif request.method == 'POST':
            time = request.data.get('expiration_time')
        time_stamp = datetime.now() + timedelta(seconds=int(time))
        expiry_date = time_stamp.strftime("%Y-%m-%d-%H-%M-%S")
        url = image + '/?expires=' + expiry_date
        hashed_url = signer.sign(url)
        return request.build_absolute_uri(hashed_url)
    
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     request = self.context.get('request')
    #     obj = self.context.get('object')
    #     tier_time = self.context.get('bin_img_exp_link')
    #     exp_time = self.validated_data.get('expiration_time')
    #     if exp_time == None:
    #         representation['url'] = self.get_url(obj, tier_time)
    #         return representation
    #     representation['url'] = self.get_url(obj, exp_time)
    #     return representation


    class Meta:
        model = Image
        fields = ['expiration_time']