import re
import os
import logging
import unicodedata

from pathlib import Path

from shutil import rmtree
from PIL import Image, ImageOps

from werkzeug.utils import secure_filename

from flask import current_app

import urllib.request


logger = logging.getLogger()


def remove_dir(dirpath):
    """
    Fonction de suppression d'un répertoire
    """
    if dirpath == "/":
        raise Exception("rm / is not possible")

    if not os.path.exists(dirpath):
        raise FileNotFoundError("not exists {}".format(dirpath))
    if not os.path.isdir(dirpath):
        raise FileNotFoundError("not isdir {}".format(dirpath))

    try:
        rmtree(dirpath)
    except (OSError, IOError) as e:
        raise e


def removeDisallowedFilenameChars(uncleanString):
    cleanedString = secure_filename(uncleanString)
    cleanedString = unicodedata.normalize("NFKD", uncleanString)
    cleanedString = re.sub("[ ]+", "_", cleanedString)
    cleanedString = re.sub("[^0-9a-zA-Z_-]", "", cleanedString)
    return cleanedString


class LocalFileManagerService:
    """
    Class to media file manipulation functions
    """

    def __init__(self):
        self.dir_thumb_base = Path(current_app.config["MEDIA_FOLDER"], "thumb")
        self.dir_file_base = Path(current_app.config["MEDIA_FOLDER"])
        self.relative_thumb_base = "thumb"

    def _get_media_path_from_db(self, filepath):
        """Suppression du prefix static contenu en base
        et non nécessaire pour manipuler le fichier

        Args:
            filepath (string): Chemin relatif du fichier
        """
        # UNUSED?
        # if filepath.startswith("static/"):
        #     filepath = filepath[7:]
        return os.path.join(Path(current_app.config["MEDIA_FOLDER"]), filepath)

    def _get_image_object(self, media):
        if media.chemin:
            img = Image.open(self._get_media_path_from_db(media.chemin))
        else:
            img = url_to_image(media.url)

        return img

    def remove_file(self, filepath):
        try:
            os.remove(self._get_media_path_from_db(filepath))
        except Exception:
            pass

    def create_thumb(self, media, size, force=False, regenerate=False):
        id_media = media.id_media
        thumb_rel_path = f"{self.relative_thumb_base}/{str(id_media)}/"
        thumbpath = Path(self.dir_file_base.absolute(), thumb_rel_path)
        thumb_file_name = f"{size[0]}x{size[1]}.png"
        thumbpath_full = thumbpath / thumb_file_name

        if regenerate:
            self.remove_file(os.path.join(self.dir_file_base, thumbpath, thumb_file_name))

        # Test if media exists
        if os.path.exists(thumbpath_full):
            return thumbpath_full

        # Get Image
        img = self._get_image_object(media)
        # Création du thumbnail
        resizeImg = resize_thumbnail(img, (size[0], size[1], force))
        # Sauvegarde de l'image
        if not os.path.exists(thumbpath):
            os.makedirs(thumbpath)

        resizeImg.save(thumbpath_full)
        return thumb_rel_path + thumb_file_name


FILEMANAGER = LocalFileManagerService()


# METHOD #2: PIL
def url_to_image(url):
    """
    Récupération d'une image à partir d'une url
    """
    local_filename, headers = urllib.request.urlretrieve(url)
    try:
        img = Image.open(local_filename)
        urllib.request.urlcleanup()
    except IOError:
        raise Exception("Media is not an image")
    return img


def resize_thumbnail(image, size):
    (width, height, force) = size

    if image.size[0] > width or image.size[1] > height:
        if force:
            return ImageOps.fit(image, (width, height), Image.ANTIALIAS)
        else:
            thumb = image.copy()
            thumb.thumbnail((width, height), Image.ANTIALIAS)
            return thumb

    return image
