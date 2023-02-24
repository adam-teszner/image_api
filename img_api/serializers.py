from functools import partial
from .img_manip import binarize
from datetime import datetime, timedelta
from django.core.signing import Signer
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from img_api.models import Image
from .validators import (image_size_validator, image_type_validator,
                        expiring_link_value_validator)

from easy_thumbnails.templatetags.thumbnail import thumbnail_url
from easy_thumbnails.files import get_thumbnailer


class PrimaryImageSerializer(serializers.ModelSerializer):
    '''
    Serializer for generating model data and dynamically generating
    thumbnails based on Tier settings.
    '''

    image = serializers.ImageField(required=True,
                        write_only=True,
                        validators=[image_size_validator, image_type_validator])
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
        try:
            assert type(size) == int and 0 < size < 2000
        except AssertionError:
            size = 100
        request = self.context.get('request')
        thumbnailer = get_thumbnailer(obj.image)

        # Scaling image in single dimension by using zero as the placeholder in
        # the size. Info at easy-thumbnails>processors>scale_and_crop
        thumbnail_options = {
            'size': (0, size)
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
    expiration_time = serializers.IntegerField(write_only=True, validators=[
        expiring_link_value_validator
    ])
    url = serializers.SerializerMethodField()
    
    
    def get_url(self, obj):
        request = self.context.get('request')
        obj = self.context.get('object')
        image = binarize(obj.image, obj.image.name, 128)
        signer = Signer(sep='&signed=')
        '''
        I decided to go with this approach because I wanted expiration
        link to be generated with default values from User-Tier settings
        on GET request. Additionally, user can define his own expiration
        time and this data gets validated first.
        It can be changed by writing to_representation method, to only
        accept pre validated data, but then there won't be a link on GET request
        '''
        if request.method == 'GET':
            time = self.context.get('bin_img_exp_link')
        elif request.method == 'POST':
            time = int(request.data.get('expiration_time'))
            expiring_link_value_validator(time)
        time_stamp = datetime.now() + timedelta(seconds=int(time))
        expiry_date = time_stamp.strftime("%Y-%m-%d-%H-%M-%S")
        url = image + '/?expires=' + expiry_date
        full_url = request.build_absolute_uri(url)
        hashed_url = signer.sign(full_url)
        return hashed_url


    class Meta:
        model = Image
        fields = ['expiration_time']