from functools import partial

from flask import has_app_context
from flask_admin.model.filters import BaseFilter

from flask_admin.contrib.sqla.filters import FilterEqual
from flask_admin.babel import lazy_gettext

from sqlalchemy import select
from sqlalchemy.orm import aliased

from apptax.database import db

from apptax.taxonomie.models import (
    Taxref,
    BibAttributs,
    CorTaxonAttribut,
    BibListes,
    TMedias,
)


# https://github.com/flask-admin/flask-admin/issues/1807
# https://stackoverflow.com/questions/54638047/correct-way-to-register-flask-admin-views-with-application-factory
class ReloadingIterator:
    def __init__(self, iterator_factory):
        self.iterator_factory = iterator_factory

    def __iter__(self):
        return self.iterator_factory()


class DynamicOptionsMixin:
    def get_dynamic_options(self, view):
        raise NotImplementedError

    def get_options(self, view):
        return ReloadingIterator(partial(self.get_dynamic_options, view))


class TaxrefDistinctFilter(DynamicOptionsMixin, FilterEqual):
    def get_dynamic_options(self, view):
        if has_app_context():
            yield from [
                (row[0], row[0])
                for row in db.session.execute(
                    select(self.column).distinct().order_by(self.column)
                ).all()
            ]


class FilterTaxrefAttr(DynamicOptionsMixin, BaseFilter):
    def apply(self, query, value, alias=None):
        return query.join(Taxref.attributs).filter(CorTaxonAttribut.id_attribut == value)

    def operation(self):
        return lazy_gettext("equals")

    def get_dynamic_options(self, view):
        if has_app_context():
            yield from db.session.execute(
                select(BibAttributs.id_attribut, BibAttributs.label_attribut)
            ).all()


class FilterBiblist(DynamicOptionsMixin, BaseFilter):
    def apply(self, query, value, alias=None):
        return query.filter(Taxref.listes.any(id_liste=value))

    def operation(self):
        return lazy_gettext("equals")

    def get_dynamic_options(self, view):
        if has_app_context():
            yield from db.session.execute(select(BibListes.id_liste, BibListes.nom_liste)).all()


class FilterIsValidName(BaseFilter):
    def apply(self, query, value, alias=None):
        if int(value) == 1:
            return query.filter(Taxref.cd_nom == Taxref.cd_ref)
        else:
            return query.filter(Taxref.cd_nom != Taxref.cd_ref)

    def operation(self):
        return lazy_gettext("equal")


class FilterMedia(BaseFilter):
    def apply(self, query, value, alias=None):
        TaxonValid = aliased(Taxref)
        query = query.join(TaxonValid, Taxref.cd_ref == TaxonValid.cd_ref)
        medias_filter = TaxonValid.medias.any()
        if int(value) == 1:
            return query.filter(medias_filter)
        else:
            return query.filter(~medias_filter)

    def operation(self):
        return lazy_gettext("equal")


class FilterAttributes(BaseFilter):
    def apply(self, query, value, alias=None):
        TaxonValid = aliased(Taxref)
        query = query.join(TaxonValid, Taxref.cd_ref == TaxonValid.cd_ref)
        attr_filter = TaxonValid.attributs.any()
        if int(value) == 1:
            return query.filter(attr_filter)
        else:
            return query.filter(~attr_filter)

    def operation(self):
        return lazy_gettext("equal")
