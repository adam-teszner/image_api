import imghdr

from django import forms
from rest_framework.exceptions import ValidationError


# Checks for image size
def image_size_validator(image, in_admin=False):
    max_size = 2097152
    size_mb = int(max_size * 0.000001)
    msg = f'Max image size is {size_mb}MB'
    err = ValidationError(msg) if in_admin==False else forms.ValidationError(msg)
    if image.size > max_size:
        raise err

# Checks if uploaded image is correct type,
# also if someone just changed the file extension.    
def image_type_validator(image, in_admin=False):
    allowed_types = ['jpg', 'jpeg', 'png']
    img_type = imghdr.what(image)
    msg = f'Allowed image types are: {allowed_types}, your file is {img_type}'
    err = ValidationError(msg) if in_admin==False else forms.ValidationError(msg)
    if img_type not in allowed_types:
        raise err

# Checks if expiring_link input in seconds is between desired range
def expiring_link_value_validator(num, in_admin=False):
    min_val = 300
    max_val = 30000
    if in_admin == True:
        if not num == 0 and not min_val <= num <= max_val:
            raise forms.ValidationError(
                f'Value must be between {min_val} and {max_val}, or 0/blank')
    if not min_val <= num <= max_val:
        raise ValidationError(f'Number must be between {min_val} and {max_val}')
    