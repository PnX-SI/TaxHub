# coding: utf8

import requests
import os
import unicodedata
import re
# import numpy as np
import math

from shutil import rmtree
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename
from flask import current_app

try:
    from urllib.request import urlopen
except Exception as e:
    from urllib2 import urlopen


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
    r = requests.get(url, stream=True)
    image = Image.open(r.raw)
    return image


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



