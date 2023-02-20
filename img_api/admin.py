from django.contrib import admin
from img_api.models import Image, Tier, CustUser

# Register your models here.

admin.site.register(CustUser)
admin.site.register(Image)
admin.site.register(Tier)
