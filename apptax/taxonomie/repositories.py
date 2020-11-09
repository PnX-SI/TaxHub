import logging

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
            f_media["url"] = media.s3_url
        return f_media

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
