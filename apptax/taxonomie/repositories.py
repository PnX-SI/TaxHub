import logging
import os.path
from typing import List

from flask import current_app
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from .filemanager import FILEMANAGER

from . import db
from ..log import logmanager
from ..utils.utilssqlalchemy import dict_merge
from .models import (
    TaxrefBdcStatutCorTextValues,
    TaxrefBdcStatutTaxon,
    TaxrefBdcStatutText,
    TaxrefBdcStatutType,
    TaxrefBdcStatutValues,
    VBdcStatus,
    TMedias,
)
from ref_geo.models import LAreas


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
            try:
                f_media["url"] = os.path.join(current_app.config["S3_PUBLIC_URL"], media.chemin)
            except TypeError:  # file is an URL
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
            filepath = FILEMANAGER.upload_file(file, media.id_media, media.cd_ref, media.titre)
            media.chemin = filepath
            if (old_chemin != "") and (old_chemin != media.chemin):
                FILEMANAGER.remove_file(old_chemin)
        elif not media.chemin and media.url and not is_file:
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


class BdcStatusRepository:
    def get_status(
        self,
        cd_ref: int,
        type_statut: str,
        areas: List[int] = None,
        areas_code: List[str] = None,
        enable=True,
        format=False,
    ):
        """
            Retourne la liste des statuts associés à un taxon
            sous forme hiérarchique

        Args:
            cd_ref (int): cd_ref
            type_statut (str): code du type de statut
            areas (List[int], optional): limite les statuts renvoyés
                aux identifiants de zones géographiques fournies.
            areas_code (List[str], optional): limite les statuts renvoyés
                aux codes de zones géographiques fournies.
            enable (bool, optional): ne retourner que les statuts actifs Defaults to True.
            format (bool, optional): retourne les données formatées. Defaults to False.

        Returns:
            listes des statuts du taxon
        """
        q = (
            db.session.query(TaxrefBdcStatutTaxon)
            .join(TaxrefBdcStatutCorTextValues)
            .join(TaxrefBdcStatutText)
            .filter(TaxrefBdcStatutTaxon.cd_ref == cd_ref)
            .filter(TaxrefBdcStatutText.enable == enable)
        )

        if type_statut:
            q = q.filter(TaxrefBdcStatutText.cd_type_statut == type_statut)

        if areas:
            q = q.filter(TaxrefBdcStatutText.areas.any(LAreas.id_area.in_(areas)))

        if areas_code:
            q = q.filter(TaxrefBdcStatutText.areas.any(LAreas.area_code.in_(areas_code)))

        q = q.options(
            joinedload(TaxrefBdcStatutTaxon.value_text).joinedload(
                TaxrefBdcStatutCorTextValues.value
            )
        ).options(
            joinedload(TaxrefBdcStatutTaxon.value_text)
            .joinedload(TaxrefBdcStatutCorTextValues.text)
            .joinedload(TaxrefBdcStatutText.type_statut)
        )
        data = q.all()

        # Retour des données sous forme formatées ou pas
        if format:
            return self.format_hierarchy_status(data)
        else:
            return data

    def format_hierarchy_status(self, data):
        """
            Formatage des données sous la forme d'un dictionnaire
            type de statut : {
                [text : {
                    [valeurs]
                }]
            }

        Args:
            data ([resultProxy]): Données à formater

        Returns:
            [type]: [description]
        """
        results = {}

        for d in data:
            cd_type_statut = d.value_text.text.type_statut.cd_type_statut
            res = {**d.value_text.text.type_statut.as_dict(), **{"text": {}}}
            id_text = d.value_text.text.id_text
            res["text"][id_text] = {**d.value_text.text.as_dict(), **{"values": {}}}

            res["text"][id_text]["values"][d.value_text.id_value_text] = {
                **d.as_dict(),
                **d.value_text.value.as_dict(),
            }

            if cd_type_statut in results:
                dict_merge(results[cd_type_statut], res)
            else:
                results[cd_type_statut] = res
        return results
