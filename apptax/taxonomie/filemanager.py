# coding: utf8

import requests
import os
import unicodedata
import re
# import numpy as np
import math
import boto3

from shutil import rmtree
from PIL import Image, ImageOps
import io

from werkzeug.utils import secure_filename
from flask import current_app

try:
    from urllib.request import urlopen
except Exception:
    from urllib2 import urlopen

if current_app.config['S3_BUCKET_NAME'] : #Use S3 upload
    s3 = boto3.client('s3',
          aws_access_key_id=current_app.config['S3_KEY'],
          aws_secret_access_key=current_app.config['S3_SECRET'],
          endpoint_url=current_app.config['S3_ENDPOINT'],
          region_name=current_app.config['S3_REGION_NAME'])

def remove_dir(dirpath):
    if(dirpath == '/'):
        raise Exception('rm / is not possible')

    if (not os.path.exists(dirpath)):
        raise FileNotFoundError('not exists {}'.format(dirpath))
    if (not os.path.isdir(dirpath)):
        raise FileNotFoundError('not isdir {}'.format(dirpath))

    try:
        rmtree(dirpath)
    except (OSError, IOError) as e:
        raise e


def remove_file(filepath):
    try :
        if current_app.config['S3_BUCKET_NAME'] and filepath.startswith(current_app.config['S3_PUBLIC_URL'] ): #Use S3
            container_path=filepath.replace(current_app.config['S3_PUBLIC_URL'],'' )
            s3.delete_object(Bucket=current_app.config['S3_BUCKET_NAME'], Key=container_path) #TODO prévoir un message d'erreur si echec suppression du bucket ?
    except AttributeError: #filepath is None (upload)
        pass
    try:
        os.remove(os.path.join(current_app.config['BASE_DIR'], filepath))
    except Exception as e:
        pass


def rename_file(old_chemin, old_title, new_title):
    new_chemin = old_chemin.replace(
        removeDisallowedFilenameChars(old_title),
        removeDisallowedFilenameChars(new_title)
    )
    os.rename(
        os.path.join(current_app.config['BASE_DIR'], old_chemin),
        os.path.join(current_app.config['BASE_DIR'], new_chemin)
    )
    return new_chemin


def upload_file(file, id_media, cd_ref, titre):
    filename = "{cd_ref}_{id_media}_{file_name}.{ext}".format(
        cd_ref=str(cd_ref),
        id_media=str(id_media),
        file_name=removeDisallowedFilenameChars(titre),
        ext=file.filename.rsplit('.', 1)[1]
    )

    if current_app.config['S3_BUCKET_NAME'] : #Use S3 upload
        s3.upload_fileobj(file, 
             current_app.config['S3_BUCKET_NAME'],
             os.path.join( current_app.config['S3_FOLDER'], filename ),
             ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type #sans ça le content type est par défaut binary/octet-stream
             } )
        return os.path.join(current_app.config['S3_PUBLIC_URL'],current_app.config['S3_FOLDER'], filename)

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(os.path.join(current_app.config['BASE_DIR'], filepath))
    return filepath


def removeDisallowedFilenameChars(uncleanString):
    cleanedString = secure_filename(uncleanString)
    cleanedString = unicodedata.normalize('NFKD', uncleanString)
    cleanedString = re.sub('[ ]+', '_', cleanedString)
    cleanedString = re.sub('[^0-9a-zA-Z_-]', '', cleanedString)
    return cleanedString

# METHOD #2: PIL
def url_to_image(url):
    """
        Récupération d'une image à partir d'une url
    """
    r = requests.get(url, stream=True)
    try:
        img = Image.open(io.BytesIO(r.content))
    except IOError:
        raise Exception("Media is not an image")
    return img


def add_border(img, border, color=0):
    '''
        Ajout d'une bordure à une image
    '''
    if isinstance(border, int) or isinstance(border, tuple):
        bimg = ImageOps.expand(img, border=border, fill=color)
    else:
        raise RuntimeError('Border is not an integer or tuple!')

    return bimg


def calculate_border(initial_size, new_size, aspect):
    """
        Calcul de la taille de l'image et de ces bordures
    """
    i_h, i_w = initial_size
    n_h, n_w = new_size
    if aspect > 1:
        # horizontal image
        f_w = n_w
        f_h = round(i_h*(n_w/i_w))

        pad_vert = abs((f_h-n_h)/2)
        pad_top, pad_bot = math.floor(pad_vert), math.ceil(pad_vert)
        pad_left, pad_right = 0, 0
    elif aspect < 1:
        # vertical image
        f_h = n_h
        f_w = round(i_w*(f_h/i_h))
        pad_horz = abs((f_w-n_w)/2)
        pad_left, pad_right = math.floor(pad_horz), math.ceil(pad_horz)
        pad_top, pad_bot = 0, 0
    else:
        # square image
        f_h, f_w = new_size
        pad_left, pad_right, pad_top, pad_bot = 0, 0, 0, 0

    return ((f_h, f_w), (pad_left, pad_right, pad_top, pad_bot))


def resizeAndPad(img, new_size, pad=True, padColor=0):

    inital_w, inital_h = img.size
    final_h = final_w = None
    pad_left, pad_top, pad_right, pad_bot = (0, 0, 0, 0)

    # aspect ratio of image
    aspect = inital_w/inital_h

    if (new_size[1] == -1):  # Si largeur non spécifé
        final_h = new_size[0]
        final_w = round(inital_w*(final_h/inital_h))
        pad = False
    elif (new_size[0] == -1):  # Si hauteur non spécifé
        final_w = new_size[1]
        final_h = round(inital_h*(final_w/inital_w))
        pad = False
    else:
        final_h, final_w = new_size

    if pad:
        final, border = calculate_border((inital_h, inital_w), new_size, aspect)
        final_h, final_w = final
        pad_left, pad_right, pad_top, pad_bot = border

    # scale and pad
    scaled_img = img.resize((final_w, final_h))

    if pad:
        scaled_img = add_border(
            scaled_img,
            (pad_left, pad_top, pad_right, pad_bot),
            color=0
        )

    return scaled_img
