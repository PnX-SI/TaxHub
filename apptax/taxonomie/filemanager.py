import re
import os
import math
import boto3
import botocore
import logging
import unicodedata

from abc import ABC

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


class FileManagerServiceInterface(ABC):
    """
    Abstract class to media file manipulation functions
    Class who inherite of this class must implement the following abstract methods:
    - remove_file
    - rename_file
    - upload_file
    """

    def __init__(self):
        self.dir_thumb_base = os.path.join(
            current_app.static_folder, current_app.config["UPLOAD_FOLDER"], "thumb"
        )
        self.dir_file_base = os.path.join(
            current_app.static_folder, current_app.config["UPLOAD_FOLDER"]
        )

    def _get_new_chemin(self, old_chemin, old_title, new_title):
        return old_chemin.replace(
            removeDisallowedFilenameChars(old_title),
            removeDisallowedFilenameChars(new_title),
        )

    def _generate_file_name(self, file, id_media, cd_ref, titre):
        return "{cd_ref}_{id_media}_{file_name}.{ext}".format(
            cd_ref=str(cd_ref),
            id_media=str(id_media),
            file_name=removeDisallowedFilenameChars(titre),
            ext=file.filename.rsplit(".", 1)[1],
        )

    def _get_media_path_from_db(self, filepath):
        """Suppression du prefix static contenu en base
        et non nécessaire pour manipuler le fichier

        Args:
            filepath (string): Chemin relatif du fichier
        """
        if filepath.startswith("static/"):
            filepath = filepath[7:]
        return os.path.join(current_app.static_folder, filepath)

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

    def rename_file(self, old_chemin, old_title, new_title):
        new_chemin = self._get_new_chemin(old_chemin, old_title, new_title)
        print(old_chemin, self._get_media_path_from_db(old_chemin))
        os.rename(
            os.path.join(self._get_media_path_from_db(old_chemin)),
            os.path.join(self._get_media_path_from_db(new_chemin)),
        )
        return new_chemin

    def upload_file(self, file, id_media, cd_ref, titre):
        filename = self._generate_file_name(file, id_media, cd_ref, titre)
        filepath = os.path.join(self.dir_file_base, filename)
        file.save(filepath)
        return ("/").join(["static", current_app.config["UPLOAD_FOLDER"], filename])

    def remove_thumb(self, id_media):
        # suppression des thumbnails
        try:

            remove_dir(os.path.join(self.dir_thumb_base, str(id_media)))
        except (FileNotFoundError, IOError, OSError) as e:
            logger.error(e)
            pass

    def create_thumb(self, media, size, regenerate=False):
        id_media = media.id_media
        thumbdir = os.path.join(self.dir_thumb_base, str(id_media))
        thumbpath = os.path.join(thumbdir, "{}x{}.jpg".format(size[0], size[1]))

        if regenerate:
            self.remove_file(thumbpath)

        # Test if media exists
        if os.path.exists(thumbpath):
            return thumbpath

        # Get Image
        img = self._get_image_object(media)

        # Création du thumbnail
        resizeImg = resizeAndPad(img, size)

        # Sauvegarde de l'image
        if not os.path.exists(thumbdir):
            os.makedirs(thumbdir)

        resizeImg.save(thumbpath)
        return thumbpath

    def remove_media_files(self, id_media, filepath):
        # suppression du fichier principal
        # S'il existe

        if filepath:
            self.remove_file(filepath)

        # Suppression des thumbnails
        self.remove_thumb(id_media)


class LocalFileManagerService(FileManagerServiceInterface):
    pass


class S3FileManagerService(FileManagerServiceInterface):
    """
    Class permettant de manipuler des fichiers stockés
        dans un cloud S3 (AWS, OVH, etc..)
    """

    def __init__(self):
        super().__init__()
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=current_app.config["S3_KEY"],
            aws_secret_access_key=current_app.config["S3_SECRET"],
            endpoint_url=current_app.config["S3_ENDPOINT"],
            region_name=current_app.config["S3_REGION_NAME"],
        )

    def _get_image_object(self, media):
        if media.chemin:
            img = url_to_image(os.path.join(current_app.config["S3_PUBLIC_URL"], media.chemin))
        else:
            img = url_to_image(media.url)

        return img

    def remove_file(self, filepath):
        try:
            # TODO prévoir un message d'erreur si echec suppression du bucket ?
            self.s3.delete_object(Bucket=current_app.config["S3_BUCKET_NAME"], Key=filepath)
        except botocore.exceptions.ParamValidationError:  # filepath is None (upload)
            pass

    def rename_file(self, old_chemin, old_title, new_title):
        new_chemin = self._get_new_chemin(old_chemin, old_title, new_title)

        self.s3.copy_object(
            Bucket=current_app.config["S3_BUCKET_NAME"],
            CopySource=os.path.join(current_app.config["S3_BUCKET_NAME"], old_chemin),
            Key=new_chemin,
        )
        self.s3.delete_object(Bucket=current_app.config["S3_BUCKET_NAME"], Key=old_chemin)
        return new_chemin

    def upload_file(self, file, id_media, cd_ref, titre):
        filename = self._generate_file_name(file, id_media, cd_ref, titre)
        self.s3.upload_fileobj(
            file,
            current_app.config["S3_BUCKET_NAME"],
            os.path.join(current_app.config["S3_FOLDER"], filename),
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type,  # sans ça le content type est par défaut binary/octet-stream
            },
        )
        return os.path.join(current_app.config["S3_FOLDER"], filename)


if current_app.config.get("S3_BUCKET_NAME"):  # Use S3 upload
    FILEMANAGER = S3FileManagerService()
else:
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


def add_border(img, border, color=0):
    """
    Ajout d'une bordure à une image
    """
    if isinstance(border, int) or isinstance(border, tuple):
        bimg = ImageOps.expand(img, border=border, fill=color)
    else:
        raise RuntimeError("Border is not an integer or tuple!")

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
        f_h = round(i_h * (n_w / i_w))

        pad_vert = abs((f_h - n_h) / 2)
        pad_top, pad_bot = math.floor(pad_vert), math.ceil(pad_vert)
        pad_left, pad_right = 0, 0
    elif aspect < 1:
        # vertical image
        f_h = n_h
        f_w = round(i_w * (f_h / i_h))
        pad_horz = abs((f_w - n_w) / 2)
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
    aspect = inital_w / inital_h

    if new_size[1] == -1:  # Si largeur non spécifé
        final_h = new_size[0]
        final_w = round(inital_w * (final_h / inital_h))
        pad = False
    elif new_size[0] == -1:  # Si hauteur non spécifé
        final_w = new_size[1]
        final_h = round(inital_h * (final_w / inital_w))
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
        scaled_img = add_border(scaled_img, (pad_left, pad_top, pad_right, pad_bot), color=0)

    return scaled_img
