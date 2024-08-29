import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from . import db
from ..utils.utilssqlalchemy import dict_merge
from .models import TaxrefBdcStatutCorTextValues, TaxrefBdcStatutTaxon, TaxrefBdcStatutText
from ref_geo.models import LAreas


logger = logging.getLogger()


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
        q = select(TaxrefBdcStatutTaxon)
        q = (
            select(TaxrefBdcStatutTaxon)
            .join(TaxrefBdcStatutCorTextValues)
            .join(TaxrefBdcStatutText)
            .where(TaxrefBdcStatutTaxon.cd_ref == cd_ref)
            .where(TaxrefBdcStatutText.enable == enable)
        )

        if type_statut:
            q = q.where(TaxrefBdcStatutText.cd_type_statut == type_statut)

        if areas:
            q = q.where(TaxrefBdcStatutText.areas.any(LAreas.id_area.in_(areas)))

        if areas_code:
            q = q.where(TaxrefBdcStatutText.areas.any(LAreas.area_code.in_(areas_code)))

        q = q.options(
            joinedload(TaxrefBdcStatutTaxon.value_text).joinedload(
                TaxrefBdcStatutCorTextValues.value
            )
        ).options(
            joinedload(TaxrefBdcStatutTaxon.value_text)
            .joinedload(TaxrefBdcStatutCorTextValues.text)
            .joinedload(TaxrefBdcStatutText.type_statut)
        )
        data = db.session.scalars(q).all()

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
