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

    @staticmethod
    def get_status(
        cd_ref: int,
        type_statut: str,
        areas: List[int] = None,
        areas_code: List[str] = None,
        enable=True,
        format=False,
    ):
        """
        Retourne la liste des statuts associés à un taxon sous forme hiérarchique.

        Parameters
        ----------
        cd_ref : int
            cd_ref
        type_statut : str
            code du type de statut
        areas : List[int], optional
            Limite les statuts renvoyés aux identifiants de zones géographiques fournies.
        areas_code : List[str], optional
            Limite les statuts renvoyés aux codes de zones géographiques fournies.
        enable : bool, optional
            Ne retourner que les statuts actifs (default is True)
        format : bool, optional
            Retourne les données formatées (default is False)

        Returns
        -------
        listes des statuts du taxon
        """
        query = (
            select(TaxrefBdcStatutTaxon)
            .join(TaxrefBdcStatutCorTextValues)
            .join(TaxrefBdcStatutText)
            .where(TaxrefBdcStatutTaxon.cd_ref == cd_ref, TaxrefBdcStatutText.enable == enable)
        )

        if type_statut:
            query = query.where(TaxrefBdcStatutText.cd_type_statut == type_statut)

        if areas:
            query = query.where(TaxrefBdcStatutText.areas.any(LAreas.id_area.in_(areas)))

        if areas_code:
            query = query.where(TaxrefBdcStatutText.areas.any(LAreas.area_code.in_(areas_code)))

        query = query.options(
            joinedload(TaxrefBdcStatutTaxon.value_text).joinedload(
                TaxrefBdcStatutCorTextValues.value
            )
        ).options(
            joinedload(TaxrefBdcStatutTaxon.value_text)
            .joinedload(TaxrefBdcStatutCorTextValues.text)
            .joinedload(TaxrefBdcStatutText.type_statut)
        )
        data = db.session.scalars(query).all()

        # Retour des données sous forme formatées ou pas
        if format:
            return BdcStatusRepository.format_hierarchy_status(data)
        else:
            return data

    @staticmethod
    def format_hierarchy_status(data):
        """
        Formatage des données sous la forme d'un dictionnaire

        Parameters
        ----------
        data : resultProxy
            Données à formater

        Returns
        -------
        dict
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
