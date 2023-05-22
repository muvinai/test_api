import os
import requests
import shutil
import boto3
import base64
import random
import string
from typing import Optional
from botocore.exceptions import NoCredentialsError

import PIL
from PIL import Image

from config.constants import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET
from utils.logger import logger


def get_size_format(b, factor=1024, suffix='B'):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if b < factor:
            return f'{b:.2f}{unit}{suffix}'
        b /= factor
    return f'{b:.2f}Y{suffix}'


def compress_img(image_name, folder=None, suffix='compressed', new_size_ratio=1.0, quality=90,
                 width=None, height=None, to_jpg=True):
    try:
        # load the image to memory
        img = Image.open(image_name)
    except PIL.UnidentifiedImageError:
        return
    # print the original image shape
    print('[*] Image shape:', img.size)
    # get the original image size in bytes
    image_size = os.path.getsize(image_name)
    # print the size before compression/resizing
    print('[*] Size before compression:', get_size_format(image_size))
    if width:
        current_width = img.size[0]
        new_size_ratio = width / current_width if width < current_width else 1

    if new_size_ratio < 1.0:
        # if resizing ratio is below 1.0, then multiply width & height with this ratio to reduce image size
        img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), Image.ANTIALIAS)
        # print new image shape
        print('[+] New Image shape:', img.size)
    elif width and height:
        # if width and height are set, resize with them instead
        img = img.resize((width, height), Image.ANTIALIAS)
        # print new image shape
        print('[+] New Image shape:', img.size)

    # split the filename and extension
    filename, ext = os.path.splitext(image_name)
    # make new filename appending _compressed to the original file name
    if suffix:
        filename = f'{filename}_{suffix}'
    if to_jpg:
        # change the extension to JPEG
        new_filename = f'{filename}.jpg'
    else:
        # retain the same extension of the original image
        new_filename = f'{filename}{ext}'
    if folder:
        new_filename = os.path.join(folder, new_filename.split('/')[-1])
    try:
        # save the image with the corresponding quality and optimize set to True
        img.save(new_filename, quality=quality, optimize=True)
    except OSError:
        # convert the image to RGB mode first
        img = img.convert('RGB')
        # save the image with the corresponding quality and optimize set to True
        img.save(new_filename, quality=quality, optimize=True)
    print('[+] New file saved:', new_filename)
    # get the new image size in bytes
    new_image_size = os.path.getsize(new_filename)
    # print the new size in a good format
    print('[+] Size after compression:', get_size_format(new_image_size))
    # calculate the saving bytes
    saving_diff = new_image_size - image_size
    # print the saving percentage
    print(f'[+] Image size change: {saving_diff / image_size * 100:.2f}% of the original image size.')
    return new_filename


def create_thumbnail(filepath):
    return compress_img(filepath, suffix='thumbnail', width=480)


def download_image(image_url, filename, folder=None, replace_ext=True):
    # Open the url image, set stream to True, this will return the stream content.
    try:
        r = requests.get(image_url, stream=True)
    except requests.exceptions.MissingSchema:
        logger.info('Could not download image')
        return

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        extension = image_url.split('.')[-1] if '.' in image_url else ''
        if len(extension) > 4:
            extension = 'jpg'
        if not folder:
            folder = '/tmp'
        if replace_ext:
            filepath = os.path.join(folder, f'{filename}.{extension}')
        else:
            filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        print('Image successfully Downloaded: ', filepath)
        return filepath

    print('Image Could not be retrieved')


def upload_to_s3(local_file: str, resource: str, filename: str) -> Optional[str]:
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    try:
        s3.upload_file(local_file, AWS_S3_BUCKET, os.path.join(resource, filename))
        print('Upload Successful')
        return os.path.join(f'https://{AWS_S3_BUCKET}.s3.us-east-2.amazonaws.com', resource, filename)
    except FileNotFoundError:
        print('The file was not found')
        return None
    except NoCredentialsError:
        print('Credentials not available')
        return None


def encode_image(filepath):
    with open(filepath, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string


def random_string(size=20):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(size))


def create_image_obj(picture: dict, resource: str) -> dict:
    image_url = picture['original']
    if not image_url:
        return picture

    filename = random_string()
    img_filepath = download_image(image_url, filename)
    if not img_filepath:
        return picture
    ext = img_filepath.split('.')[-1]
    if len(ext) < 5:
        filename = f'{filename}.{ext}'

    if not f'{AWS_S3_BUCKET}.s3' in image_url:
        original_image_url = upload_to_s3(img_filepath, f'originals/{resource}/', filename)
    else:
        filename = image_url.split('/')[-1]
        original_image_url = image_url
    thumbnail_image_url = f'https://{AWS_S3_BUCKET}.s3.us-east-2.amazonaws.com/thumbnails/{resource}/{filename}'
    r = requests.get(thumbnail_image_url)
    if r.status_code >= 400:
        thumbnail_filepath = create_thumbnail(img_filepath)
        if thumbnail_filepath:
            thumbnail_image_url = upload_to_s3(thumbnail_filepath, f'thumbnails/{resource}/', filename)

    picture['original'] = original_image_url
    picture['thumbnail'] = thumbnail_image_url

    return picture
