import logging
import os.path

from flask import current_app
from sqlalchemy.exc import IntegrityError
from .models import TMedias
from .filemanager import FILEMANAGER

logger = logging.getLogger()


class MediaRepository:
    s3_storage = False

    def __init__(self, DBSession, s3_bucket_name):
        self.session = DBSession
        if s3_bucket_name:
            self.s3_storage = True

    def _format_media(self, media, force_path):
        f_media = {**media.as_dict(), **media.types.as_dict()}
        if self.s3_storage:
            if not force_path:
                f_media["chemin"] = None
            try :
                f_media["url"] = os.path.join(current_app.config['S3_PUBLIC_URL'], media.chemin)
            except TypeError: #file is an URL
                f_media["url"] = media.url
        return f_media

    def _populate_data_media(self, media, data):
        # TODO Change add default value in DB
        if "supprime" not in data:
            data["supprime"] = False
        else:
            data["supprime"] = bool(data["supprime"])

        if "is_public" in data:
            data["is_public"] = bool(data["is_public"])
        
        if data.get("chemin", False):
            data["url"] = None
        
        for k in data:
            if hasattr(TMedias, k) and not data[k] == "null":
                setattr(media, k, data[k])
        return media

    def get_media_filter_by(self, filters):
        q = self.session.query(TMedias)
        if filters:
            q = q.filter_by(**filters)
        return q.all()

    def get_and_format_media_filter_by(self, filters, force_path=False):
        results = self.get_media_filter_by(filters)
        medias = []
        for media in results:
            medias.append(self._format_media(media, force_path))
        return medias

    def get_one_media(self, id):
        return self.session.query(TMedias).get(id)

    def get_and_format_one_media(self, id, force_path=False):
        media = self.get_one_media(id)
        if media:
            return self._format_media(media, force_path)
        else:
            return None

    def import_media(self, data, upload_file, id_media=None):
        # case update
        if id_media:
            # Todo add test id media doesn't exists
            media = self.get_one_media(id_media)
            old_media = self.update_media_file(media)
            action = "UPDATE"
        else:
            media = TMedias()
            action = "INSERT"
            old_media = None

        # update data media
        media = self._populate_data_media(media, data)
        self.session.add(media)
        self._process_comit()

        # Process file
        media = self.process_media_file(upload_file, media, bool(data["isFile"]), old_media)
        self.session.add(media)
        self._process_comit()

        return (media, action)

    def process_media_file(self, file, media, is_file, old_media_data):
        if file and is_file:
            # Cas 1 : upload media
            media.url = None
            old_chemin = media.chemin
            filepath = FILEMANAGER.upload_file(
                file, media.id_media, media.cd_ref, media.titre
            )
            media.chemin = filepath
            if (old_chemin != "") and (old_chemin != media.chemin):
                FILEMANAGER.remove_file(old_chemin)
        elif (not media.chemin and media.url and not is_file):
            # Cas 2 : URL
            if media.chemin:
                FILEMANAGER.remove_file(media.chemin)
                media.chemin = None
        elif old_media_data["titre"] != media.titre:
            # Cas 3 : Changement du titre du média
            filepath = FILEMANAGER.rename_file(media.chemin, old_media_data["titre"], media.titre)
            media.chemin = filepath

        return media

    def update_media_file(self, media):
        # Keep old data
        old_media = media.as_dict()
        # Remove thumb
        FILEMANAGER.remove_thumb(media.id_media)

        return old_media

    def persist(self, entity):
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete(self, id):
        media = self.get_one_media(id)
        chemin = None
        if media.chemin != "":
            chemin = media.chemin

        # Suppression de l'entrée en base
        try:
            self.session.delete(media)
            self.session.commit()
        except Exception as e:
            raise (e)

        # Suppression des fichiers
        FILEMANAGER.remove_media_files(id, chemin)

        return media

    def _process_comit(self, rollback=True):
        try:
            self.session.commit()
        except IntegrityError as e:
            logger.error(e)
            if rollback:
                self.session.rollback()
            raise e
        except Exception as e:
            logger.error(e)
            if rollback:
                self.session.rollback()
            raise e
