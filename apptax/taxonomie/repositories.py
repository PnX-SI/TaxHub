import logging
import os.path
from typing import List

from flask import current_app
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from . import db
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
    def __init__(self, DBSession):
        self.session = DBSession

    def _format_media(self, media, force_path):
        f_media = {**media.as_dict(), **media.types.as_dict()}

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
        print(q)
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
