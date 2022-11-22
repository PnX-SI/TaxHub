from functools import partial

from flask import has_app_context
from flask_admin.model.filters import BaseFilter

from flask_admin.contrib.sqla.filters import FilterEqual
from flask_admin.babel import lazy_gettext

from sqlalchemy.orm import aliased

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
                (getattr(row, self.column.key), getattr(row, self.column.key))
                for row in Taxref.query.distinct(self.column).order_by(self.column).all()
            ]


class FilterTaxrefAttr(DynamicOptionsMixin, FilterEqual):
    def apply(self, query, value, alias=None):
        return query.join(CorTaxonAttribut).filter(CorTaxonAttribut.id_attribut == value)

    def get_dynamic_options(self, view):
        if has_app_context():
            yield from [
                (attr.id_attribut, attr.label_attribut) for attr in BibAttributs.query.all()
            ]


class FilterBiblist(DynamicOptionsMixin, FilterEqual):
    def apply(self, query, value, alias=None):
        return query.join(Taxref.listes).filter(Taxref.listes.any(id_liste=value))

    def get_dynamic_options(self, view):
        if has_app_context():
            yield from [(list.id_liste, list.nom_liste) for list in BibListes.query.all()]


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
