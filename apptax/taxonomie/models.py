from flask import url_for
from sqlalchemy import ForeignKey, select, func, event

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import backref, deferred, raiseload, joinedload, foreign, remote

from utils_flask_sqla.serializers import serializable
from ref_geo.models import LAreas

from . import db

from utils_flask_sqla.models import qfilter


@serializable
class VMRegne(db.Model):
    __tablename__ = "vm_regne"
    __table_args__ = {"schema": "taxonomie"}
    regne = db.Column(db.Unicode, primary_key=True)

    def __repr__(self):
        return self.regne

    def __str__(self):
        return self.regne


@serializable
class VMGroup2Inpn(db.Model):
    __tablename__ = "vm_group2_inpn"
    __table_args__ = {"schema": "taxonomie"}
    group2_inpn = db.Column(db.Unicode, primary_key=True)

    def __repr__(self):
        return self.group2_inpn

    def __str__(self):
        return self.group2_inpn


@serializable
class CorTaxonAttribut(db.Model):
    __tablename__ = "cor_taxon_attribut"
    __table_args__ = {"schema": "taxonomie"}
    id_attribut = db.Column(
        db.Integer,
        ForeignKey("taxonomie.bib_attributs.id_attribut"),
        nullable=False,
        primary_key=True,
    )
    cd_ref = db.Column(
        db.Integer,
        ForeignKey("taxonomie.taxref.cd_nom"),
        nullable=False,
        primary_key=True,
    )
    valeur_attribut = db.Column(db.Text, nullable=False)
    bib_attribut = db.relationship("BibAttributs")

    taxon = db.relationship("Taxref", back_populates="attributs")

    def __repr__(self):
        return self.valeur_attribut


@serializable
class BibThemes(db.Model):
    __tablename__ = "bib_themes"
    __table_args__ = {"schema": "taxonomie"}
    id_theme = db.Column(db.Integer, primary_key=True)
    nom_theme = db.Column(db.Unicode)
    desc_theme = db.Column(db.Unicode)
    ordre = db.Column(db.Integer)
    attributs = db.relationship("BibAttributs", lazy="select", back_populates="theme")

    def __repr__(self):
        return self.nom_theme


@serializable
class BibAttributs(db.Model):
    __tablename__ = "bib_attributs"
    __table_args__ = {"schema": "taxonomie"}
    id_attribut = db.Column(db.Integer, primary_key=True)
    nom_attribut = db.Column(db.Unicode, nullable=False)
    label_attribut = db.Column(db.Unicode, nullable=False)
    # TODO : fix in next flask-admin release -> liste_valeur_attribut is set with Unicode and
    # not Text because Text field convert None to empty string
    # https://github.com/pallets-eco/flask-admin/pull/2321
    liste_valeur_attribut = db.Column(db.Unicode, nullable=True)
    obligatoire = db.Column(db.BOOLEAN, nullable=True, server_default=FetchedValue())
    desc_attribut = db.Column(db.Text)
    type_attribut = db.Column(db.Unicode)
    type_widget = db.Column(db.Unicode, nullable=False)
    regne = db.Column(
        db.Unicode,
        ForeignKey(VMRegne.regne),
        name="regne",
        nullable=True,
        primary_key=False,
    )
    group2_inpn = db.Column(
        db.Unicode,
        ForeignKey(VMGroup2Inpn.group2_inpn),
        name="group2_inpn",
        nullable=True,
        primary_key=False,
    )
    id_theme = db.Column(
        db.Integer,
        ForeignKey(BibThemes.id_theme),
        nullable=False,
        primary_key=False,
    )
    ordre = db.Column(db.Integer)
    theme = db.relationship(BibThemes)

    def __repr__(self):
        return self.nom_attribut


cor_nom_liste = db.Table(
    "cor_nom_liste",
    db.Column(
        "id_liste",
        db.Integer,
        ForeignKey("taxonomie.bib_listes.id_liste"),
        nullable=False,
        primary_key=True,
    ),
    db.Column(
        "cd_nom",
        db.Integer,
        ForeignKey("taxonomie.taxref.cd_nom"),
        nullable=False,
        primary_key=True,
    ),
    schema="taxonomie",
)


@serializable(exclude=["nom_vern_or_lb_nom"])
class Taxref(db.Model):
    __tablename__ = "taxref"
    __table_args__ = {"schema": "taxonomie"}

    cd_nom = db.Column(db.Integer, primary_key=True)
    id_statut = db.Column(db.Unicode)
    id_habitat = db.Column(db.Integer)
    id_rang = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    phylum = db.Column(db.Unicode)
    classe = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    ordre = db.Column(db.Unicode)
    famille = db.Column(db.Unicode)
    sous_famille = db.Column(db.Unicode)
    tribu = db.Column(db.Unicode)
    cd_taxsup = db.Column(db.Integer)
    cd_sup = db.Column(db.Integer)
    cd_ref = db.Column(db.Integer)
    cd_ba = db.Column(db.Integer)
    lb_nom = db.Column(db.Unicode)
    lb_auteur = db.Column(db.Unicode)
    nomenclatural_comment = db.Column(db.Unicode)
    nom_complet = db.Column(db.Unicode)
    nom_complet_html = db.Column(db.Unicode)
    nom_vern = db.Column(db.Unicode)
    nom_valide = db.Column(db.Unicode)
    nom_vern_eng = db.Column(db.Unicode)
    group1_inpn = db.Column(db.Unicode)
    group2_inpn = db.Column(db.Unicode)
    group3_inpn = db.Column(db.Unicode)
    url = db.Column(db.Unicode)

    status = db.relationship("VBdcStatus", order_by="VBdcStatus.lb_type_statut")
    synonymes = db.relationship(
        "Taxref",
        foreign_keys=[cd_ref],
        primaryjoin="Taxref.cd_ref == Taxref.cd_ref",
        uselist=True,
        post_update=True,
    )
    parent = db.relationship("Taxref", primaryjoin=foreign(cd_sup) == remote(cd_ref))
    attributs = db.relationship("CorTaxonAttribut", back_populates="taxon")
    listes = db.relationship("BibListes", secondary=cor_nom_liste, back_populates="noms")
    medias = db.relationship("apptax.taxonomie.models.TMedias", back_populates="taxon")

    rang = db.relationship("BibTaxrefRangs", uselist=False)
    habitat = db.relationship("BibTaxrefHabitats", uselist=False)
    statut_presence = db.relationship("BibTaxrefStatus", uselist=False)

    @hybrid_property
    def nom_vern_or_lb_nom(self):
        return self.nom_vern if self.nom_vern else self.lb_nom

    @nom_vern_or_lb_nom.expression
    def nom_vern_or_lb_nom(cls):
        return db.func.coalesce(cls.nom_vern, cls.lb_nom)

    def __repr__(self):
        return self.nom_complet

    @qfilter(query=True)
    def joined_load(cls, fields=None, *, query, **kwargs):

        query_option = [raiseload("*")]
        if fields:
            for f in fields:
                if f in Taxref.__mapper__.relationships:
                    query_option.append(joinedload(getattr(Taxref, f)))
        query = query.options(*tuple(query_option))

        return query

    @qfilter(query=True)
    def where_id_liste(cls, id_liste, *, query):
        return query.filter(Taxref.listes.any(BibListes.id_liste.in_(tuple(id_liste))))

    @qfilter(query=True)
    def where_params(cls, filters=None, *, query):

        for filter in filters:
            # Test empty values
            if not filters[filter]:
                continue

            if hasattr(Taxref, filter) and isinstance(filters[filter], list):
                col = getattr(Taxref, filter)
                query = query.filter(col.in_(tuple(filters[filter])))
            elif hasattr(Taxref, filter) and filters[filter] != "":
                col = getattr(Taxref, filter)
                query = query.filter(col == filters[filter])
            elif filter == "is_ref" and filters[filter] == "true":
                query = query.filter(Taxref.cd_nom == Taxref.cd_ref)
            elif filter == "ilike":
                query = query.filter(Taxref.lb_nom.ilike(filters[filter] + "%"))
            elif filter.split("-")[0] == "ilike":
                value = filters[filter]
                column = str(filter.split("-")[1])
                col = getattr(Taxref, column)
                query = query.filter(col.ilike(value + "%"))
        return query

    def __le__(self, other):
        return self.tree <= other.tree


@serializable
class BibListes(db.Model):
    __tablename__ = "bib_listes"
    __table_args__ = {"schema": "taxonomie"}
    id_liste = db.Column(db.Integer, primary_key=True)
    code_liste = db.Column(db.Unicode)
    nom_liste = db.Column(db.Unicode)
    desc_liste = db.Column(db.Text)
    regne = db.Column(
        db.Unicode,
        ForeignKey(VMRegne.regne),
        name="regne",
        nullable=True,
        primary_key=False,
    )
    group2_inpn = db.Column(
        db.Unicode,
        ForeignKey(VMGroup2Inpn.group2_inpn),
        name="group2_inpn",
        nullable=True,
        primary_key=False,
    )

    noms = db.relationship("Taxref", secondary=cor_nom_liste, back_populates="listes")

    @hybrid_property
    def nb_taxons(self):
        return db.session.scalar(
            select([db.func.count(cor_nom_liste.c.cd_nom)]).where(
                cor_nom_liste.c.id_liste == self.id_liste
            )
        )

    @nb_taxons.expression
    def nb_taxons(cls):
        return (
            db.select([db.func.count(cor_nom_liste.c.cd_nom)])
            .where(cor_nom_liste.c.id_liste == cls.id_liste)
            .label("nb_taxons")
        )

    def __repr__(self):
        return self.nom_liste


@serializable
class BibTypesMedia(db.Model):
    __tablename__ = "bib_types_media"
    __table_args__ = {"schema": "taxonomie"}
    id_type = db.Column(db.Integer, primary_key=True)
    nom_type_media = db.Column(db.Unicode)
    desc_type_media = db.Column(db.Text)

    def __repr__(self):
        return self.nom_type_media


@serializable
class TMedias(db.Model):
    __tablename__ = "t_medias"
    __table_args__ = {"schema": "taxonomie"}
    id_media = db.Column(db.Integer, primary_key=True)
    cd_ref = db.Column(
        db.Integer,
        ForeignKey(Taxref.cd_nom),
        nullable=False,
        primary_key=False,
    )
    titre = db.Column(db.Unicode, nullable=False)
    url = db.Column(db.Unicode)
    chemin = db.Column(db.Unicode)
    auteur = db.Column(db.Unicode)
    desc_media = db.Column(db.Text)
    source = db.Column(db.Unicode)
    licence = db.Column(db.Unicode)
    is_public = db.Column(db.BOOLEAN, nullable=False, default=True)
    id_type = db.Column(
        db.Integer,
        ForeignKey(BibTypesMedia.id_type),
        nullable=False,
    )

    types = db.relationship(BibTypesMedia)

    taxon = db.relationship(Taxref, back_populates="medias")

    @hybrid_property
    def media_url(self):
        if self.url:
            return self.url
        elif self.chemin:
            return url_for("media_taxhub", filename=self.chemin, _external=True)

    def __repr__(self):
        return self.titre


@serializable
class VMTaxrefListForautocomplete(db.Model):
    __tablename__ = "vm_taxref_list_forautocomplete"
    __table_args__ = {"schema": "taxonomie"}
    gid = db.Column(db.Integer, primary_key=True)
    cd_nom = db.Column(db.Integer, ForeignKey(Taxref.cd_nom))
    search_name = db.Column(db.Unicode)
    unaccent_search_name = db.Column(db.Unicode)
    cd_ref = db.Column(db.Integer)
    nom_valide = db.Column(db.Unicode)
    lb_nom = db.Column(db.Unicode)
    nom_vern = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    group2_inpn = db.Column(db.Unicode)
    group3_inpn = db.Column(db.Unicode)

    def __repr__(self):
        return self.search_name


@serializable
class BibTaxrefHabitats(db.Model):
    __tablename__ = "bib_taxref_habitats"
    __table_args__ = {"schema": "taxonomie"}
    id_habitat = db.Column(db.Integer, ForeignKey("taxonomie.taxref.id_habitat"), primary_key=True)
    nom_habitat = db.Column(db.Unicode)
    desc_habitat = db.Column(db.Text)

    def __repr__(self):
        return self.nom_habitat


@serializable
class BibTaxrefRangs(db.Model):
    __tablename__ = "bib_taxref_rangs"
    __table_args__ = {"schema": "taxonomie"}
    id_rang = db.Column(db.Unicode, ForeignKey("taxonomie.taxref.id_rang"), primary_key=True)
    nom_rang = db.Column(db.Unicode)
    tri_rang = db.Column(db.Integer)

    def __repr__(self):
        return self.nom_rang


@serializable
class BibTaxrefStatus(db.Model):
    __tablename__ = "bib_taxref_statuts"
    __table_args__ = {"schema": "taxonomie"}
    id_statut = db.Column(db.Integer, ForeignKey("taxonomie.taxref.id_statut"), primary_key=True)
    nom_statut = db.Column(db.Unicode)

    def __repr__(self):
        return self.nom_statut


@serializable
class VMTaxrefHierarchie(db.Model):
    __tablename__ = "vm_taxref_hierarchie"
    __table_args__ = {"schema": "taxonomie"}
    cd_nom = db.Column(db.Integer, primary_key=True)
    cd_ref = db.Column(db.Integer)
    regne = db.Column(db.Unicode)
    phylum = db.Column(db.Unicode)
    classe = db.Column(db.Unicode)
    ordre = db.Column(db.Unicode)
    famille = db.Column(db.Unicode)
    lb_nom = db.Column(db.Unicode)
    id_rang = db.Column(db.Unicode)
    nb_tx_fm = db.Column(db.Integer)
    nb_tx_or = db.Column(db.Integer)
    nb_tx_cl = db.Column(db.Integer)
    nb_tx_ph = db.Column(db.Integer)
    nb_tx_kd = db.Column(db.Integer)

    def __repr__(self):
        return self.lb_nom


@serializable
class TaxrefBdcStatutType(db.Model):
    __tablename__ = "bdc_statut_type"
    __table_args__ = {"schema": "taxonomie"}
    cd_type_statut = db.Column(db.Unicode, primary_key=True)
    lb_type_statut = db.Column(db.Unicode)
    regroupement_type = db.Column(db.Unicode)
    thematique = db.Column(db.Unicode)
    type_value = db.Column(db.Unicode)

    text = db.relationship("TaxrefBdcStatutText", lazy="select", back_populates="type_statut")

    @hybrid_property
    def display(self):
        return f"{self.lb_type_statut} - {self.cd_type_statut}"


bdc_statut_cor_text_area = db.Table(
    "bdc_statut_cor_text_area",
    db.Column(
        "id_text", db.Integer, ForeignKey("taxonomie.bdc_statut_text.id_text"), primary_key=True
    ),
    db.Column("id_area", db.Integer, ForeignKey(LAreas.id_area), primary_key=True),
    schema="taxonomie",
)


@serializable
class TaxrefBdcStatutText(db.Model):
    __tablename__ = "bdc_statut_text"
    __table_args__ = {"schema": "taxonomie"}
    id_text = db.Column(db.Integer, primary_key=True)
    cd_st_text = db.Column(db.Unicode)
    cd_type_statut = db.Column(
        db.Unicode, ForeignKey("taxonomie.bdc_statut_type.cd_type_statut"), nullable=False
    )
    cd_sig = db.Column(db.Unicode)
    cd_doc = db.Column(db.Unicode)
    niveau_admin = db.Column(db.Unicode)
    cd_iso3166_1 = db.Column(db.Unicode)
    cd_iso3166_2 = db.Column(db.Unicode)
    lb_adm_tr = db.Column(db.Unicode)
    full_citation = db.Column(db.Unicode)
    doc_url = db.Column(db.Unicode)
    enable = db.Column(db.Boolean)

    type_statut = db.relationship(TaxrefBdcStatutType, lazy="select", back_populates="text")
    cor_text = db.relationship(
        "TaxrefBdcStatutCorTextValues", lazy="select", back_populates="text"
    )

    areas = db.relationship(LAreas, secondary=bdc_statut_cor_text_area)


@serializable
class TaxrefBdcStatutValues(db.Model):
    __tablename__ = "bdc_statut_values"
    __table_args__ = {"schema": "taxonomie"}
    id_value = db.Column(db.Integer, primary_key=True)
    code_statut = db.Column(db.Unicode)
    label_statut = db.Column(db.Unicode)

    @hybrid_property
    def display(self):
        return f"{self.code_statut} - {self.label_statut}"


@serializable
class TaxrefBdcStatutCorTextValues(db.Model):
    __tablename__ = "bdc_statut_cor_text_values"
    __table_args__ = {"schema": "taxonomie"}
    id_value_text = db.Column(db.Integer, primary_key=True)
    id_value = db.Column(
        db.Unicode, ForeignKey("taxonomie.bdc_statut_values.id_value"), nullable=False
    )
    id_text = db.Column(
        db.Unicode, ForeignKey("taxonomie.bdc_statut_text.id_text"), nullable=False
    )

    text = db.relationship(TaxrefBdcStatutText, lazy="select", back_populates="cor_text")
    value = db.relationship(TaxrefBdcStatutValues, lazy="select")

    taxon = db.relationship("TaxrefBdcStatutTaxon", lazy="select", back_populates="value_text")


@serializable
class TaxrefBdcStatutTaxon(db.Model):
    __tablename__ = "bdc_statut_taxons"
    __table_args__ = {"schema": "taxonomie"}
    id = db.Column(db.Integer, primary_key=True)
    id_value_text = db.Column(
        db.Integer,
        ForeignKey("taxonomie.bdc_statut_cor_text_values.id_value_text"),
        nullable=False,
    )
    cd_nom = db.Column(db.Integer)
    cd_ref = db.Column(db.Integer)
    rq_statut = db.Column(db.Unicode)

    value_text = db.relationship(
        TaxrefBdcStatutCorTextValues, lazy="select", back_populates="taxon"
    )


@serializable
class VBdcStatus(db.Model):
    __tablename__ = "v_bdc_status"
    __table_args__ = {"schema": "taxonomie", "info": dict(is_view=True)}
    cd_nom = db.Column(db.Integer, ForeignKey("taxonomie.taxref.cd_ref"), primary_key=True)
    cd_ref = db.Column(db.Integer)
    rq_statut = db.Column(db.Unicode)
    code_statut = db.Column(db.Unicode, primary_key=True)
    label_statut = db.Column(db.Unicode)
    cd_type_statut = db.Column(db.Unicode, primary_key=True)
    lb_type_statut = db.Column(db.Unicode)
    regroupement_type = db.Column(db.Unicode)
    thematique = db.Column(db.Unicode)
    cd_st_text = db.Column(db.Unicode, primary_key=True)
    cd_sig = db.Column(db.Unicode)
    cd_doc = db.Column(db.Unicode)
    niveau_admin = db.Column(db.Unicode)
    cd_iso3166_1 = db.Column(db.Unicode)
    cd_iso3166_2 = db.Column(db.Unicode)
    full_citation = db.Column(db.Unicode, primary_key=True)
    doc_url = db.Column(db.Unicode)
    type_value = db.Column(db.Unicode)


@serializable
class TMetaTaxref(db.Model):
    __tablename__ = "t_meta_taxref"
    __table_args__ = {"schema": "taxonomie"}
    referencial_name = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    update_date = db.Column(db.DateTime, default=db.func.now(), nullable=False)


class TaxrefTree(db.Model):
    __tablename__ = "vm_taxref_tree"
    __table_args__ = {"schema": "taxonomie"}
    cd_nom = db.Column(db.Integer, ForeignKey("taxonomie.taxref.cd_nom"), primary_key=True)
    taxref = db.relationship(Taxref, backref=backref("tree", uselist=False))
    path = db.Column(db.String, nullable=False)

    def __le__(self, other):
        # self <= other means taxon other is the same or a parent of self
        p1, p2 = self.path.split("."), other.path.split(".")
        return len(p1) >= len(p2) and p1[: len(p2)] == p2


class TaxrefLiens(db.Model):
    __tablename__ = "taxref_liens"
    __table_args__ = {"schema": "taxonomie"}
    ct_name = db.Column(db.Unicode, primary_key=True)
    ct_type = db.Column(db.Unicode)
    ct_authors = db.Column(db.Unicode)
    ct_title = db.Column(db.Unicode)
    ct_url = db.Column(db.Unicode)
    cd_nom = db.Column(db.Integer, ForeignKey("taxonomie.taxref.cd_nom"), primary_key=True)
    ct_sp_id = db.Column(db.Unicode, primary_key=True)
    url_sp = db.Column(db.Unicode)


# Taxref deffered properties

Taxref.nb_medias = deferred(
    select([func.count(TMedias.id_media)]).where(TMedias.cd_ref == Taxref.cd_ref).scalar_subquery()
)

Taxref.nb_attributs = deferred(
    select([func.count(CorTaxonAttribut.id_attribut)])
    .where(CorTaxonAttribut.cd_ref == Taxref.cd_ref)
    .correlate_except(CorTaxonAttribut)
    .scalar_subquery()
)


@event.listens_for(TMedias, "after_update")
def after_update_t_media(mapper, connection, target):
    # Regénération des thumnails des médias quand modification du média
    from apptax.taxonomie.filemanager import FILEMANAGER

    FILEMANAGER.create_thumb(target, (300, 400), regenerate=True)
