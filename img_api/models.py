from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

# Defines image path based on user_id and current date
def image_path(instance, filename):
    now = datetime.now()
    folder = now.strftime("%Y%m%d%H%M%S%f")
    user_id = instance.created_by.id
    return f'{user_id}/images/{folder}/{filename}'

# Create your models here.
class Tier(models.Model):
    name = models.CharField(max_length=50)
    options = models.JSONField(default=dict, blank=True, null=True)
    original_link = models.BooleanField(default=False)
    bin_img_exp_link = models.IntegerField(blank=True, null=True, default=None)
    list_details = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class CustUser(models.Model):
    account_type = models.ForeignKey(Tier, on_delete=models.SET_NULL,
                                     null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, 
                             blank=True)
    
    def __str__(self):
        return self.user.username

class Image(models.Model):
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey(CustUser, on_delete=models.CASCADE, 
                                   null=True, blank=True)
    image = models.ImageField(upload_to=image_path)
