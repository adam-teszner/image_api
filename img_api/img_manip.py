from PIL import Image
from django.conf import settings

def binarize(image: object, image_name: str, threshold: int) -> str:
    '''
    Binarizes images using pillow, 
    arg image = obj.image,
    arg image_name = obj.image.name, 
    arg threshold - int between 0-255 

    method from:
    https://stackoverflow.com/questions/68957686/pillow-how-to-binarize-an-image-with-threshold
    '''

    if threshold < 0 or threshold > 255:
        raise ValueError('Threshold value must be between 0-255')

    file_name: str = image_name.rsplit('/', 1)[1]
    new_file_name: str = '/' + 'BINARY_' + str(threshold) + '_' + file_name
    new_image_name: str = image_name.rsplit('/', 1)[0] + new_file_name
    url_path: str = str(settings.MEDIA_URL) + new_image_name
    save_path: str = str(settings.MEDIA_ROOT) + '/' + new_image_name

    i: object = Image.open(image)
    gray: object = i.convert("L")
    binary: object = gray.point(lambda x: 255 if x > threshold else 0, "1")
    binary.save(save_path)
    return url_path