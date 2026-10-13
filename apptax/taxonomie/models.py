from flask import url_for
from typing import Optional
from datetime import datetime
from sqlalchemy import ForeignKey, select, func, event

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import (
    Mapped,
    backref,
    deferred,
    mapped_column,
    raiseload,
    foreign,
    remote,
    selectinload,
)

from utils_flask_sqla.serializers import serializable
from ref_geo.models import LAreas

from . import db

from utils_flask_sqla.models import qfilter


@serializable
class VMRegne(db.Model):
    __tablename__ = "vm_regne"
    __table_args__ = {"schema": "taxonomie"}
    regne: Mapped[str] = mapped_column(db.Unicode, primary_key=True)

    def __repr__(self):
        return self.regne

    def __str__(self):
        return self.regne


@serializable
class VMGroup2Inpn(db.Model):
    __tablename__ = "vm_group2_inpn"
    __table_args__ = {"schema": "taxonomie"}
    group2_inpn: Mapped[str] = mapped_column(db.Unicode, primary_key=True)

    def __repr__(self):
        return self.group2_inpn

    def __str__(self):
        return self.group2_inpn


@serializable
class CorTaxonAttribut(db.Model):
    __tablename__ = "cor_taxon_attribut"
    __table_args__ = {"schema": "taxonomie"}
    id_attribut: Mapped[int] = mapped_column(
        db.Integer, ForeignKey("taxonomie.bib_attributs.id_attribut"), primary_key=True
    )
    cd_ref: Mapped[int] = mapped_column(
        db.Integer, ForeignKey("taxonomie.taxref.cd_nom"), primary_key=True
    )
    valeur_attribut: Mapped[str]
    bib_attribut = db.relationship("BibAttributs")

    taxon = db.relationship("Taxref", back_populates="attributs")

    def __repr__(self):
        return self.valeur_attribut


@serializable
class BibThemes(db.Model):
    __tablename__ = "bib_themes"
    __table_args__ = {"schema": "taxonomie"}
    id_theme: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    nom_theme: Mapped[Optional[str]]
    desc_theme: Mapped[Optional[str]]
    ordre: Mapped[Optional[int]]
    attributs = db.relationship("BibAttributs", lazy="select", back_populates="theme")

    def __repr__(self):
        return self.nom_theme


@serializable
class BibAttributs(db.Model):
    __tablename__ = "bib_attributs"
    __table_args__ = {"schema": "taxonomie"}
    id_attribut: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    nom_attribut: Mapped[str]
    label_attribut: Mapped[str]
    # TODO : fix in next flask-admin release -> liste_valeur_attribut is set with Unicode and
    # not Text because Text field convert None to empty string
    # https://github.com/pallets-eco/flask-admin/pull/2321
    liste_valeur_attribut: Mapped[Optional[str]]
    obligatoire: Mapped[Optional[bool]] = mapped_column(db.BOOLEAN, server_default=FetchedValue())
    desc_attribut: Mapped[Optional[str]] = mapped_column(db.Text)
    type_attribut: Mapped[Optional[str]]
    type_widget: Mapped[str]
    regne: Mapped[Optional[str]] = mapped_column(
        db.Unicode, ForeignKey(VMRegne.regne), name="regne"
    )
    group2_inpn: Mapped[Optional[str]] = mapped_column(
        db.Unicode, ForeignKey(VMGroup2Inpn.group2_inpn), name="group2_inpn"
    )
    id_theme: Mapped[int] = mapped_column(db.Integer, ForeignKey(BibThemes.id_theme))
    ordre: Mapped[Optional[int]]
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

    cd_nom: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    id_statut: Mapped[Optional[str]]
    id_habitat: Mapped[Optional[int]]
    id_rang: Mapped[Optional[str]]
    regne: Mapped[Optional[str]]
    phylum: Mapped[Optional[str]]
    classe: Mapped[Optional[str]]
    regne: Mapped[Optional[str]]
    ordre: Mapped[Optional[str]]
    famille: Mapped[Optional[str]]
    sous_famille: Mapped[Optional[str]]
    tribu: Mapped[Optional[str]]
    cd_taxsup: Mapped[Optional[int]]
    cd_sup: Mapped[Optional[int]] = mapped_column()
    cd_ref: Mapped[Optional[int]] = mapped_column()
    cd_ba: Mapped[Optional[int]]
    lb_nom: Mapped[Optional[str]]
    lb_auteur: Mapped[Optional[str]]
    nomenclatural_comment: Mapped[Optional[str]]
    nom_complet: Mapped[Optional[str]]
    nom_complet_html: Mapped[Optional[str]]
    nom_vern: Mapped[Optional[str]]
    nom_valide: Mapped[Optional[str]]
    nom_vern_eng: Mapped[Optional[str]]
    group1_inpn: Mapped[Optional[str]]
    group2_inpn: Mapped[Optional[str]]
    group3_inpn: Mapped[Optional[str]]
    url: Mapped[Optional[str]]

    status = db.relationship("VBdcStatus", order_by="VBdcStatus.lb_type_statut")
    synonymes = db.relationship(
        "Taxref",
        primaryjoin=foreign(cd_ref) == remote(cd_ref),
        uselist=True,
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
                    query_option.append(selectinload(getattr(Taxref, f)))
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
    id_liste: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    code_liste: Mapped[Optional[str]]
    nom_liste: Mapped[Optional[str]]
    desc_liste: Mapped[Optional[str]]
    regne: Mapped[Optional[str]] = mapped_column(
        db.Unicode, ForeignKey(VMRegne.regne), name="regne"
    )
    group2_inpn: Mapped[Optional[str]] = mapped_column(
        db.Unicode, ForeignKey(VMGroup2Inpn.group2_inpn), name="group2_inpn"
    )

    noms = db.relationship("Taxref", secondary=cor_nom_liste, back_populates="listes")

    @hybrid_property
    def nb_taxons(self):
        return db.session.scalar(
            select(db.func.count(cor_nom_liste.c.cd_nom)).where(
                cor_nom_liste.c.id_liste == self.id_liste
            )
        )

    @nb_taxons.expression
    def nb_taxons(cls):
        return (
            db.select(db.func.count(cor_nom_liste.c.cd_nom))
            .where(cor_nom_liste.c.id_liste == cls.id_liste)
            .scalar_subquery()
            .label("nb_taxons")
        )

    def __repr__(self):
        return self.nom_liste


@serializable
class BibTypesMedia(db.Model):
    __tablename__ = "bib_types_media"
    __table_args__ = {"schema": "taxonomie"}
    id_type: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    nom_type_media: Mapped[Optional[str]]
    desc_type_media: Mapped[Optional[str]] = mapped_column(db.Text)

    def __repr__(self):
        return self.nom_type_media


@serializable
class TMedias(db.Model):
    __tablename__ = "t_medias"
    __table_args__ = {"schema": "taxonomie"}
    id_media: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    cd_ref: Mapped[int] = mapped_column(db.Integer, ForeignKey(Taxref.cd_nom))
    titre: Mapped[str]
    url: Mapped[Optional[str]]
    chemin: Mapped[Optional[str]]
    auteur: Mapped[Optional[str]]
    desc_media: Mapped[Optional[str]] = mapped_column(db.Text)
    source: Mapped[Optional[str]]
    licence: Mapped[Optional[str]]
    is_public: Mapped[bool] = mapped_column(db.BOOLEAN, default=True)
    id_type: Mapped[int] = mapped_column(db.Integer, ForeignKey(BibTypesMedia.id_type))

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
    gid: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    cd_nom: Mapped[Optional[int]] = mapped_column(db.Integer, ForeignKey(Taxref.cd_nom))
    search_name: Mapped[Optional[str]]
    unaccent_search_name: Mapped[Optional[str]]
    cd_ref: Mapped[Optional[int]]
    nom_valide: Mapped[Optional[str]]
    lb_nom: Mapped[Optional[str]]
    nom_vern: Mapped[Optional[str]]
    regne: Mapped[Optional[str]]
    group2_inpn: Mapped[Optional[str]]
    group3_inpn: Mapped[Optional[str]]

    def __repr__(self):
        return self.search_name


@serializable
class BibTaxrefHabitats(db.Model):
    __tablename__ = "bib_taxref_habitats"
    __table_args__ = {"schema": "taxonomie"}
    id_habitat: Mapped[int] = mapped_column(
        db.Integer, ForeignKey("taxonomie.taxref.id_habitat"), primary_key=True
    )
    nom_habitat: Mapped[Optional[str]]
    desc_habitat: Mapped[Optional[str]]

    def __repr__(self):
        return self.nom_habitat


@serializable
class BibTaxrefRangs(db.Model):
    __tablename__ = "bib_taxref_rangs"
    __table_args__ = {"schema": "taxonomie"}
    id_rang: Mapped[str] = mapped_column(
        db.Unicode, ForeignKey("taxonomie.taxref.id_rang"), primary_key=True
    )
    nom_rang: Mapped[Optional[str]]
    tri_rang: Mapped[Optional[int]]

    def __repr__(self):
        return self.nom_rang


@serializable
class BibTaxrefStatus(db.Model):
    __tablename__ = "bib_taxref_statuts"
    __table_args__ = {"schema": "taxonomie"}
    id_statut: Mapped[int] = mapped_column(
        db.Integer, ForeignKey("taxonomie.taxref.id_statut"), primary_key=True
    )
    nom_statut: Mapped[Optional[str]]

    def __repr__(self):
        return self.nom_statut


@serializable
class VMTaxrefHierarchie(db.Model):
    __tablename__ = "vm_taxref_hierarchie"
    __table_args__ = {"schema": "taxonomie"}
    cd_nom: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    cd_ref: Mapped[Optional[int]]
    regne: Mapped[Optional[str]]
    phylum: Mapped[Optional[str]]
    classe: Mapped[Optional[str]]
    ordre: Mapped[Optional[str]]
    famille: Mapped[Optional[str]]
    lb_nom: Mapped[Optional[str]]
    id_rang: Mapped[Optional[str]]
    nb_tx_fm: Mapped[Optional[int]]
    nb_tx_or: Mapped[Optional[int]]
    nb_tx_cl: Mapped[Optional[int]]
    nb_tx_ph: Mapped[Optional[int]]
    nb_tx_kd: Mapped[Optional[int]]

    def __repr__(self):
        return self.lb_nom


@serializable
class TaxrefBdcStatutType(db.Model):
    __tablename__ = "bdc_statut_type"
    __table_args__ = {"schema": "taxonomie"}
    cd_type_statut: Mapped[str] = mapped_column(db.Unicode, primary_key=True)
    lb_type_statut: Mapped[Optional[str]]
    regroupement_type: Mapped[Optional[str]]
    thematique: Mapped[Optional[str]]
    type_value: Mapped[Optional[str]]

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
    id_text: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    cd_st_text: Mapped[Optional[str]]
    cd_type_statut: Mapped[str] = mapped_column(
        db.Unicode, ForeignKey("taxonomie.bdc_statut_type.cd_type_statut")
    )
    cd_sig: Mapped[Optional[str]]
    cd_doc: Mapped[Optional[str]]
    niveau_admin: Mapped[Optional[str]]
    cd_iso3166_1: Mapped[Optional[str]]
    cd_iso3166_2: Mapped[Optional[str]]
    lb_adm_tr: Mapped[Optional[str]]
    full_citation: Mapped[Optional[str]]
    doc_url: Mapped[Optional[str]]
    enable: Mapped[Optional[bool]]

    type_statut = db.relationship(TaxrefBdcStatutType, lazy="select", back_populates="text")
    cor_text = db.relationship(
        "TaxrefBdcStatutCorTextValues", lazy="select", back_populates="text"
    )

    areas = db.relationship(LAreas, secondary=bdc_statut_cor_text_area)


@serializable
class TaxrefBdcStatutValues(db.Model):
    __tablename__ = "bdc_statut_values"
    __table_args__ = {"schema": "taxonomie"}
    id_value: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    code_statut: Mapped[Optional[str]]
    label_statut: Mapped[Optional[str]]

    @hybrid_property
    def display(self):
        return f"{self.code_statut} - {self.label_statut}"


@serializable
class TaxrefBdcStatutCorTextValues(db.Model):
    __tablename__ = "bdc_statut_cor_text_values"
    __table_args__ = {"schema": "taxonomie"}
    id_value_text: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    id_value: Mapped[str] = mapped_column(
        db.Unicode, ForeignKey("taxonomie.bdc_statut_values.id_value")
    )
    id_text: Mapped[str] = mapped_column(
        db.Unicode, ForeignKey("taxonomie.bdc_statut_text.id_text")
    )

    text = db.relationship(TaxrefBdcStatutText, lazy="select", back_populates="cor_text")
    value = db.relationship(TaxrefBdcStatutValues, lazy="select")

    taxon = db.relationship("TaxrefBdcStatutTaxon", lazy="select", back_populates="value_text")


@serializable
class TaxrefBdcStatutTaxon(db.Model):
    __tablename__ = "bdc_statut_taxons"
    __table_args__ = {"schema": "taxonomie"}
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    id_value_text: Mapped[int] = mapped_column(
        db.Integer, ForeignKey("taxonomie.bdc_statut_cor_text_values.id_value_text")
    )
    cd_nom: Mapped[Optional[int]]
    cd_ref: Mapped[Optional[int]]
    rq_statut: Mapped[Optional[str]]

    value_text = db.relationship(
        TaxrefBdcStatutCorTextValues, lazy="select", back_populates="taxon"
    )


@serializable
class VBdcStatus(db.Model):
    __tablename__ = "v_bdc_status"
    __table_args__ = {"schema": "taxonomie", "info": dict(is_view=True)}
    cd_nom: Mapped[int] = mapped_column(
        db.Integer, ForeignKey("taxonomie.taxref.cd_ref"), primary_key=True
    )
    cd_ref: Mapped[Optional[int]]
    rq_statut: Mapped[Optional[str]]
    code_statut: Mapped[str] = mapped_column(db.Unicode, primary_key=True)
    label_statut: Mapped[Optional[str]]
    cd_type_statut: Mapped[str] = mapped_column(db.Unicode, primary_key=True)
    lb_type_statut: Mapped[Optional[str]]
    regroupement_type: Mapped[Optional[str]]
    thematique: Mapped[Optional[str]]
    cd_st_text: Mapped[str] = mapped_column(db.Unicode, primary_key=True)
    cd_sig: Mapped[Optional[str]]
    cd_doc: Mapped[Optional[str]]
    niveau_admin: Mapped[Optional[str]]
    cd_iso3166_1: Mapped[Optional[str]]
    cd_iso3166_2: Mapped[Optional[str]]
    full_citation: Mapped[str] = mapped_column(db.Unicode, primary_key=True)
    doc_url: Mapped[Optional[str]]
    type_value: Mapped[Optional[str]]


@serializable
class TMetaTaxref(db.Model):
    __tablename__ = "t_meta_taxref"
    __table_args__ = {"schema": "taxonomie"}
    referencial_name: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    version: Mapped[Optional[int]]
    update_date: Mapped[datetime] = mapped_column(db.DateTime, default=db.func.now())


class TaxrefTree(db.Model):
    __tablename__ = "vm_taxref_tree"
    __table_args__ = {"schema": "taxonomie"}
    cd_nom: Mapped[int] = mapped_column(
        db.Integer, ForeignKey("taxonomie.taxref.cd_nom"), primary_key=True
    )
    taxref = db.relationship(Taxref, backref=backref("tree", uselist=False))
    path: Mapped[str]

    def __le__(self, other):
        # self <= other means taxon other is the same or a parent of self
        p1, p2 = self.path.split("."), other.path.split(".")
        return len(p1) >= len(p2) and p1[: len(p2)] == p2


class TaxrefLiens(db.Model):
    __tablename__ = "taxref_liens"
    __table_args__ = {"schema": "taxonomie"}
    ct_name: Mapped[str] = mapped_column(db.Unicode, primary_key=True)
    ct_type: Mapped[Optional[str]]
    ct_authors: Mapped[Optional[str]]
    ct_title: Mapped[Optional[str]]
    ct_url: Mapped[Optional[str]]
    cd_nom: Mapped[int] = mapped_column(
        db.Integer, ForeignKey("taxonomie.taxref.cd_nom"), primary_key=True
    )
    ct_sp_id: Mapped[str] = mapped_column(db.Unicode, primary_key=True)
    url_sp: Mapped[Optional[str]]


# Taxref deffered properties

Taxref.nb_medias = deferred(
    select(func.count(TMedias.id_media)).where(TMedias.cd_ref == Taxref.cd_ref).scalar_subquery()
)


Taxref.nb_attributs = deferred(
    select(func.count(CorTaxonAttribut.id_attribut))
    .where(CorTaxonAttribut.cd_ref == Taxref.cd_ref)
    .correlate_except(CorTaxonAttribut)
    .scalar_subquery()
)


@event.listens_for(TMedias, "after_update")
def after_update_t_media(mapper, connection, target):
    # Regénération des thumnails des médias quand modification du média
    from apptax.taxonomie.filemanager import LocalFileManagerService

    LocalFileManagerService().create_thumb(target, (300, 400), regenerate=True)
