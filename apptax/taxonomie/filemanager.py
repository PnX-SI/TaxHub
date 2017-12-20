# coding: utf8
from werkzeug.utils import secure_filename
from flask import current_app

import os
import unicodedata
import re
import cv2
from shutil import rmtree
try:
    from urllib.request import urlopen
except Exception as e:
    from urllib2 import urlopen

import numpy as np


def remove_dir(dirpath):
    try:
        rmtree(dirpath)
    except Exception as e:
        pass


def remove_file(filepath):
    try:
        print (os.path.join(current_app.config['BASE_DIR'], filepath))
        os.remove(os.path.join(current_app.config['BASE_DIR'], filepath))
    except Exception as e:
        pass


def rename_file(old_chemin, old_title, new_title):
    new_chemin = old_chemin.replace(removeDisallowedFilenameChars(old_title),removeDisallowedFilenameChars(new_title))
    os.rename(os.path.join(current_app.config['BASE_DIR'],old_chemin), os.path.join(current_app.config['BASE_DIR'], new_chemin))
    return new_chemin


def upload_file(file, id_media, cd_ref, titre):
    filename = str(cd_ref) + '_' + str(id_media) + '_' + removeDisallowedFilenameChars(titre) + '.' + file.filename.rsplit('.', 1)[1]
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(os.path.join(current_app.config['BASE_DIR'], filepath))
    return filepath


def removeDisallowedFilenameChars(uncleanString):
    cleanedString = secure_filename(uncleanString)
    cleanedString = unicodedata.normalize('NFKD', uncleanString)
    cleanedString = re.sub('[ ]+', '_', cleanedString)
    cleanedString = re.sub('[^0-9a-zA-Z_-]', '', cleanedString)
    return cleanedString


# METHOD #1: OpenCV, NumPy, and urllib
def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    resp = urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    return image


def resizeAndPad(img, size, pad=True, padColor=0):
    print('resizeAndPad')
    h, w = img.shape[:2]
    new_h = new_w = None
    # aspect ratio of image
    aspect = w/h

    if (size[1] == -1):
        sh, sw = size = (size[0], int(h * aspect))
        new_h = sh
        new_w = np.round(new_h*aspect).astype(int)
        pad = False
    if (size[0] == -1):
        sh, sw = size = (int(w * aspect), size[1])
        new_w = sw
        new_h = np.round(new_w/aspect).astype(int)
        pad = False
    else:
        sh, sw = size

    # compute scaling and pad sizing
    print(pad, size)
    if pad:
        print(pad, aspect, new_h)
        if aspect > 1:
            # horizontal image
            if (new_h is None):
                new_w = sw
                new_h = np.round(new_w/aspect).astype(int)

            pad_vert = abs((sh-new_h)/2)
            pad_top, pad_bot = np.floor(pad_vert).astype(int), np.ceil(pad_vert).astype(int)
            pad_left, pad_right = 0, 0

        elif aspect < 1:
            # vertical image
            if (new_h is None):
                new_h = sh
                new_w = np.round(new_h*aspect).astype(int)

            pad_horz = abs((sw-new_w)/2)
            pad_left, pad_right = np.floor(pad_horz).astype(int), np.ceil(pad_horz).astype(int)
            pad_top, pad_bot = 0, 0
        else:
            # square image
            new_h, new_w = sh, sw
            pad_left, pad_right, pad_top, pad_bot = 0, 0, 0, 0

    # interpolation method
    if h > new_h or w > new_w:
        # shrinking image
        interp = cv2.INTER_AREA
    else:
        # stretching image
        interp = cv2.INTER_CUBIC

    # scale and pad
    scaled_img = cv2.resize(img, (new_w, new_h), interpolation=interp)
    if pad:
        # set pad color
        if len(img.shape) is 3 and not isinstance(padColor, (list, tuple, np.ndarray)):
            # color image but only one color provided
            padColor = [padColor]*3

        scaled_img = cv2.copyMakeBorder(
            scaled_img,
            pad_top, pad_bot, pad_left, pad_right,
            borderType=cv2.BORDER_CONSTANT,
            value=padColor
        )

    return scaled_img
