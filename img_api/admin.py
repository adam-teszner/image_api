from django import forms
from django.contrib import admin

from img_api.models import CustUser, Image, Tier

from .validators import (expiring_link_value_validator, image_size_validator,
                         image_type_validator)


class TierForm(forms.ModelForm):

    def clean_bin_img_exp_link(self):
        '''
        Validates for correct input
        '''
        value = self.cleaned_data.get('bin_img_exp_link')
        if value:
            try:
                expiring_link_value_validator(value, in_admin=True)
            except forms.ValidationError as e:
                self.add_error('bin_img_exp_link', e)
        return value
    
class ImageForm(forms.ModelForm):

    def clean_image(self):
        '''
        Validates for file types and file size in admin
        '''
        img = self.cleaned_data.get('image')
        if img:
            try:
                image_size_validator(img, in_admin=True)
                image_type_validator(img, in_admin=True)
            except forms.ValidationError as e:
                self.add_error('image', e)
        return img

        
# Register your models here.
@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):
    form = TierForm
    fields = [
        'name',
        'options',
        'original_link',
        'bin_img_exp_link',
        'list_details'
    ]

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    form = ImageForm
    fields = [
        'name',
        'image',
        'created_by'
    ]

admin.site.register(CustUser)


