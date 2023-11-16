from marshmallow import pre_load, fields

from utils_flask_sqla.schema import SmartRelationshipsMixin

from pypnusershub.env import ma

from apptax.taxonomie.models import BibListes, VMRegne, VMGroup2Inpn, TMedias, BibTypesMedia


class BibTypesMediaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BibTypesMedia
        include_fk = True


class TMediasSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TMedias
        include_fk = True

    types = fields.Nested(BibTypesMediaSchema())


class VMRegneSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VMRegne
        include_fk = False


class VMGroup2Inpn(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VMGroup2Inpn
        include_fk = False


class BibListesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BibListes
        include_fk = True

    regne = fields.Pluck(VMRegneSchema, "regne", many=False)
    group2_inpn = fields.Pluck(VMGroup2Inpn, "group2_inpn", many=False)
    nb_taxons = fields.Integer()
