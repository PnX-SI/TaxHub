import re
import os
import logging
from typing import Tuple
import unicodedata
import warnings

from pathlib import Path

from shutil import rmtree
from PIL import Image, ImageOps, UnidentifiedImageError
from io import BytesIO

from werkzeug.utils import secure_filename

from flask import current_app

import urllib.request
from urllib.error import URLError, HTTPError
from apptax.utils.errors import TaxhubError
from apptax.database import generate_user_agent

logger = logging.getLogger()


def remove_dir(dirpath):
    """
    Remove a directory

    Parameters
    ----------
    dirpath : str
        directory path

    Raises
    ------
    Exception
        raised if the path correspond to the root path (/)
    FileNotFoundError
        The directory does not exists
    NotADirectoryError
        The path does not correspond to a directory
    OSError, IOError
        an error occured while removing the directory
    """
    if dirpath == "/":
        raise Exception("rm / is not possible")

    if not os.path.exists(dirpath):
        raise FileNotFoundError("not exists {}".format(dirpath))
    if not os.path.isdir(dirpath):
        raise NotADirectoryError("not isdir {}".format(dirpath))

    try:
        rmtree(dirpath)
    except (OSError, IOError) as e:
        raise e


class LocalFileManagerService:
    """
    Class to media file manipulation functions
    """

    def __init__(self):
        self.dir_file_base = Path(current_app.config["MEDIA_FOLDER"], "taxhub").absolute()
        self.dir_thumb_base = self.dir_file_base / "thumb"

    def _get_media_path_from_db(self, filepath: str) -> str:
        """
        Return the absolute media path

        Parameters
        ----------
        filepath : str
            file path

        Returns
        -------
        str
            media path"""
        return os.path.join(self.dir_file_base, filepath)

    def _get_image_object(self, media) -> Image:
        """
        Return the Image object for a media

        Parameters
        ----------
        media : TMedias
            a media

        Returns
        -------
        PIL.Image
            image of the media
        """
        if media.chemin:
            img = Image.open(self._get_media_path_from_db(media.chemin))
        else:
            img = url_to_image(media.url)

        return img

    def remove_file(self, filepath: str):
        """
        Method to remove a media file

        Parameters
        ----------
        filepath : str
            file path
        """
        try:
            os.remove(self._get_media_path_from_db(filepath))
        except Exception as e:
            warnings.warn(
                f"An error occurred while attempting to remove the media located at: {filepath} : {e}"
            )

    def create_thumb(
        self, media, size: Tuple[int, int], force: bool = False, regenerate: bool = False
    ) -> str:
        """
        Generate a thumbnail of media existing in the database.

        Parameters
        ----------
        media : TMedias
            media
        size : Tuple[int,int]
            desired (width,height) of the thumbnail
        force : bool, optional
            force the regeneration of the thumbnail if it already exists, by default False
        regenerate : bool, optional
            force the regeneration of the thumbnail if it already exists, by default False

        Returns
        -------
        str
            thumbnail path
        """
        try:
            img: Image = self._get_image_object(media)
        except (TaxhubError, UnidentifiedImageError, IOError) as e:
            return None
        id_media = media.id_media
        thumb_file_name = f"{size[0]}x{size[1]}.png"
        thumbpath_full = self.dir_thumb_base / str(id_media) / thumb_file_name

        if regenerate:
            self.remove_file(thumbpath_full)

        # Test if media exists
        if thumbpath_full.exists():
            return thumbpath_full

        # If width only was given in the parameter (height <=> size[1] < 0)
        if size[1] < 0:
            size[1] = (size[0] / img.width) * img.height
        # Same with height
        if size[0] < 0:
            size[0] = (size[1] / img.height) * img.width

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
def url_to_image(url: str) -> Image:
    """
    Download and return a remote image in a `PIL.Image` object

    Parameters
    ----------
    url : str
        image url

    Returns
    -------
    Image
        downloaded image

    Raises
    ------
    TaxhubError
        raised if the image could not be fetched or if the downloaded file does not correspond to an image
    """
    TIMEOUT = 5.0  # secondes
    # Récupération image (échoue si source externe non disponible)
    try:
        request = urllib.request.Request(url)
        request.add_header("user-agent", generate_user_agent())

        with urllib.request.urlopen(request, timeout=TIMEOUT) as r:
            data = r.read()
    except (HTTPError, URLError, Exception) as e:
        logger.warning("url_to_image GET failed url=%s err=%r", url, e)
        raise TaxhubError(f"GET failed for {url}: {e}")

    # Décodage image (échoue vite si non-image)
    try:
        img = Image.open(BytesIO(data))
        img.load()
        return img
    except Exception:
        raise TaxhubError("Media is not an image")


def resize_thumbnail(image: Image, size: Tuple[int, int, bool]) -> Image:
    """

    Resize a generated thumbnail image based on a given size

    Parameters
    ----------
    image : Image
        image
    size : Tuple[int,int,bool]
        width, height and force parameter value

    Returns
    -------
    Image
        resized thumbnail
    """
    (width, height, force) = size

    if force:
        return ImageOps.pad(image, (int(width), int(height)))
    else:
        thumb = image.copy()
        thumb.thumbnail((width, height))
        return thumb
