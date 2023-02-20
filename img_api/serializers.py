from functools import partialmethod, partial
from django.conf import settings
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
    # image = ThumbnailSerializer(alias='image')
    # avatar = ThumbnailSerializer(alias='avatar', source='image')
    # created_by = CustUserSerializer()


    # def to_representation(self, instance):
    #     repr = super().to_representation(instance)
    #     return repr

    class Meta:
        model = Image
        fields = '__all__'
    
'''
class ImSer(serializers.ModelSerializer):
    # image = serializers.ImageField()
    image = serializers.SerializerMethodField()
    # thumb = serializers.SerializerMethodField()


    def __init__(self, *args, **kwargs):
        context = kwargs.get('context')
        tier_name = context.get('name')
        thumbnails = context['options']['thumbnails']
        print(thumbnails)
        # print(tier_name)
        # print(kwargs)        
        super().__init__(*args, **kwargs)

        for field, size in thumbnails.items():
            field_name = f'thumb_{field}'
            print(field_name)
            print(size)
            method_name = f'get_{field_name}'
            field = partialmethod(self.get_thumbnail_url, size=size)
            # print(field)
            self.fields[field_name] = serializers.SerializerMethodField(
                method_name=field
            )
            print(method_name)
            

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    # def get_thumb(self, obj):
    #     request = self.context.get('request')
    #     thumbnailer = get_thumbnailer(obj.image)
    #     thumbnail_options = {
    #         'size': (100, 100), 'crop': True
    #     }
    #     thumb = thumbnailer.get_thumbnail(thumbnail_options)
    #     return request.build_absolute_uri(thumb.url)

    def get_thumbnail_url(self, obj, size):
        request = self.context.get('request')
        thumbnailer = get_thumbnailer(obj.image)
        options = {
            'size': (size, size),
            'crop': True
        }
        thumb = thumbnailer.get_thumbnail(thumbnail_options)
        return request.build_absolute_uri(thumb.url)
    

    class Meta:
        model = Image
        fields = '__all__'


'''

class ImSer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context')
        thumbnails = context['options']['thumbnails']
        super().__init__(*args, **kwargs)

        for field, size in thumbnails.items():
            field_name = f'thumb_{field}'
            method_name = f'get_{field_name}'
            setattr(self, method_name, partial(self.get_thumbnail_url, size=size))
            self.fields[field_name] = serializers.SerializerMethodField(method_name=method_name)

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_thumbnail_url(self, obj, size):
        request = self.context.get('request')
        thumbnailer = get_thumbnailer(obj.image)
        thumbnail_options = {
            'size': (size, size),
            'crop': True
        }
        print(thumbnail_options)
        thumb = thumbnailer.get_thumbnail(thumbnail_options)
        return request.build_absolute_uri(thumb.url)

    class Meta:
        model = Image
        fields = '__all__'
