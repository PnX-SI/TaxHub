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
from urllib.error import HTTPError
from apptax.utils.errors import TaxhubError

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
        self.dir_file_base = Path(current_app.config["MEDIA_FOLDER"], "taxhub").absolute()
        self.dir_thumb_base = self.dir_file_base / "thumb"

    def _get_media_path_from_db(self, filepath):
        """Suppression du prefix static contenu en base
        et non nécessaire pour manipuler le fichier

        Args:
            filepath (string): Chemin relatif du fichier
        """
        # UNUSED?
        # if filepath.startswith("static/"):
        #     filepath = filepath[7:]
        return os.path.join(self.dir_file_base, filepath)

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
        thumb_file_name = f"{size[0]}x{size[1]}.png"
        thumbpath_full = self.dir_thumb_base / str(id_media) / thumb_file_name

        if regenerate:
            self.remove_file(thumbpath_full)

        # Test if media exists
        if thumbpath_full.exists():
            return thumbpath_full

        # Get Image
        try:
            img: Image = self._get_image_object(media)
        except TaxhubError as e:
            return None

        # If width only was given in the parameter (height <=> size[1] < 0)
        if size[1] < 0:
            size[1] = img.width / size[0] * img.height
        # Same with height
        if size[0] < 0:
            size[0] = img.height / size[1] * img.width

        # Création du thumbnail
        resizeImg = resize_thumbnail(img, (size[0], size[1], force))
        # Sauvegarde de l'image
        thumb_taxon_dir = self.dir_thumb_base / str(id_media)
        if not thumb_taxon_dir.exists():
            os.makedirs(thumb_taxon_dir)

        resizeImg.save(thumbpath_full)
        return thumbpath_full


FILEMANAGER = LocalFileManagerService()


# METHOD #2: PIL
def url_to_image(url):
    """
    Récupération d'une image à partir d'une url
    """
    try:
        local_filename, headers = urllib.request.urlretrieve(url)
    except HTTPError as e:
        raise TaxhubError(e.reason)
    try:
        img = Image.open(local_filename)
        urllib.request.urlcleanup()
        return img
    except IOError:
        raise TaxhubError("Media is not an image")


def resize_thumbnail(image, size):
    (width, height, force) = size

    if image.size[0] > width or image.size[1] > height:
        if force:
            return ImageOps.fit(image, (width, height))
        else:
            thumb = image.copy()
            thumb.thumbnail((width, height))
            return thumb

    return image
