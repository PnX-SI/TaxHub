from marshmallow import pre_load, fields
from marshmallow_sqlalchemy.fields import RelatedList
from marshmallow_sqlalchemy import auto_field

from utils_flask_sqla.schema import SmartRelationshipsMixin

from pypnusershub.env import ma

from apptax.taxonomie.models import (
    BibListes,
    TMedias,
    BibTypesMedia,
    Taxref,
    TaxrefTree,
    CorTaxonAttribut,
    BibTaxrefRangs,
    VBdcStatus,
    BibTaxrefHabitats,
    BibTaxrefStatus,
    BibAttributs,
)


class BibTypesMediaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BibTypesMedia
        include_fk = True


class BibAttributsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BibAttributs
        include_fk = True


class TMediasSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TMedias
        include_fk = True

    media_url = fields.String()
    types = fields.Nested(BibTypesMediaSchema())


class BibListesSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BibListes
        include_fk = True

    nb_taxons = fields.Integer()


class CorTaxonAttributSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CorTaxonAttribut
        include_fk = True

    bib_attribut = fields.Nested(BibAttributsSchema, many=False)


class BibTaxrefRangsSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BibTaxrefRangs
        include_fk = True


class BibTaxrefHabitatsSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BibTaxrefHabitats
        include_fk = True


class BibTaxrefStatusSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BibTaxrefStatus
        include_fk = True


class VBdcStatusSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VBdcStatus
        include_fk = True


class TaxrefTreeSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TaxrefTree


class TaxrefSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Taxref
        include_fk = True
        load_instance = True

    medias = fields.Nested(TMediasSchema, many=True)
    attributs = fields.Nested(CorTaxonAttributSchema, many=True)

    rang = fields.Nested(BibTaxrefRangsSchema, many=False)
    status = fields.Nested(VBdcStatusSchema, many=True)
    habitat = fields.Nested(BibTaxrefHabitatsSchema, many=False)
    statut_presence = fields.Nested(BibTaxrefStatusSchema, many=False)
    synonymes = fields.Nested("self", many=True)
    listes = auto_field()
    linnaean_parents = fields.Nested(TaxrefTreeSchema, many=False)
