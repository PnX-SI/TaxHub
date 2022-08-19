import os.path

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Sequence
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import FetchedValue

from utils_flask_sqla.serializers import serializable
from ref_geo.models import LAreas

from . import db


@serializable
class BibNoms(db.Model):
    __tablename__ = "bib_noms"
    __table_args__ = {"schema": "taxonomie"}
    id_nom = db.Column(db.Integer, primary_key=True)
    cd_nom = db.Column(db.Integer, ForeignKey("taxonomie.taxref.cd_nom"), nullable=True)
    cd_ref = db.Column(db.Integer)
    nom_francais = db.Column(db.Unicode)
    comments = db.Column(db.Unicode)

    taxref = db.relationship("Taxref")
    attributs = db.relationship("CorTaxonAttribut")
    listes = db.relationship("CorNomListe")
    # medias relationship defined through backref


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
        ForeignKey("taxonomie.bib_noms.cd_ref"),
        nullable=False,
        primary_key=True,
    )
    valeur_attribut = db.Column(db.Text, nullable=False)
    bib_nom = db.relationship("BibNoms")
    bib_attribut = db.relationship("BibAttributs")

    def __repr__(self):
        return "<CorTaxonAttribut %r>" % self.valeur_attribut


@serializable
class BibThemes(db.Model):
    __tablename__ = "bib_themes"
    __table_args__ = {"schema": "taxonomie"}
    id_theme = db.Column(db.Integer, primary_key=True)
    nom_theme = db.Column(db.Unicode)
    desc_theme = db.Column(db.Unicode)
    ordre = db.Column(db.Integer)
    id_droit = db.Column(db.Integer)
    attributs = db.relationship("BibAttributs", lazy="select")

    def __repr__(self):
        return "<BibThemes %r>" % self.nom_theme


@serializable
class BibAttributs(db.Model):
    __tablename__ = "bib_attributs"
    __table_args__ = {"schema": "taxonomie"}
    id_attribut = db.Column(db.Integer, primary_key=True)
    nom_attribut = db.Column(db.Unicode, nullable=True)
    label_attribut = db.Column(db.Unicode, nullable=True)
    liste_valeur_attribut = db.Column(db.Text, nullable=True)
    obligatoire = db.Column(db.BOOLEAN, nullable=True, server_default=FetchedValue())
    desc_attribut = db.Column(db.Text)
    type_attribut = db.Column(db.Unicode)
    type_widget = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    group2_inpn = db.Column(db.Unicode)
    id_theme = db.Column(
        db.Integer,
        ForeignKey(BibThemes.id_theme),
        nullable=False,
        primary_key=False,
    )
    ordre = db.Column(db.Integer)
    theme = db.relationship(BibThemes)

    def __repr__(self):
        return "<BibAttributs %r>" % self.nom_attribut


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
    lb_nom = db.Column(db.Unicode)
    lb_auteur = db.Column(db.Unicode)
    nom_complet = db.Column(db.Unicode)
    nom_complet_html = db.Column(db.Unicode)
    nom_vern = db.Column(db.Unicode)
    nom_valide = db.Column(db.Unicode)
    nom_vern_eng = db.Column(db.Unicode)
    group1_inpn = db.Column(db.Unicode)
    group2_inpn = db.Column(db.Unicode)
    url = db.Column(db.Unicode)

    @hybrid_property
    def nom_vern_or_lb_nom(self):
        return self.nom_vern if self.nom_vern else self.lb_nom

    @nom_vern_or_lb_nom.expression
    def nom_vern_or_lb_nom(cls):
        return db.func.coalesce(cls.nom_vern, cls.lb_nom)

    def __repr__(self):
        return "<Taxref %r>" % self.nom_complet


@serializable
class CorNomListe(db.Model):
    __tablename__ = "cor_nom_liste"
    __table_args__ = {"schema": "taxonomie"}
    id_liste = db.Column(
        db.Integer,
        ForeignKey("taxonomie.bib_listes.id_liste"),
        nullable=False,
        primary_key=True,
    )
    id_nom = db.Column(
        db.Integer,
        ForeignKey("taxonomie.bib_noms.id_nom"),
        nullable=False,
        primary_key=True,
    )
    bib_nom = db.relationship("BibNoms")
    bib_liste = db.relationship("BibListes")

    def __repr__(self):
        return "<CorNomListe %r>" % self.id_liste


@serializable
class BibListes(db.Model):
    __tablename__ = "bib_listes"
    __table_args__ = {"schema": "taxonomie"}
    id_liste = db.Column(db.Integer, primary_key=True)
    code_liste = db.Column(db.Unicode)
    nom_liste = db.Column(db.Unicode)
    desc_liste = db.Column(db.Text)
    picto = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    group2_inpn = db.Column(db.Unicode)

    cnl = db.relationship("CorNomListe", lazy="select")
    noms = db.relationship("BibNoms", secondary=CorNomListe.__table__)

    def __repr__(self):
        return "<BibListes %r>" % self.nom_liste


@serializable
class BibTypesMedia(db.Model):
    __tablename__ = "bib_types_media"
    __table_args__ = {"schema": "taxonomie"}
    id_type = db.Column(db.Integer, primary_key=True)
    nom_type_media = db.Column(db.Unicode)
    desc_type_media = db.Column(db.Text)

    def __repr__(self):
        return "<BibTypesMedia %r>" % self.nom_type_media


@serializable
class TMedias(db.Model):
    __tablename__ = "t_medias"
    __table_args__ = {"schema": "taxonomie"}
    id_media = db.Column(db.Integer, primary_key=True)
    cd_ref = db.Column(
        db.Integer,
        ForeignKey(BibNoms.cd_nom),
        nullable=False,
        primary_key=False,
    )
    titre = db.Column(db.Unicode)
    url = db.Column(db.Unicode)
    chemin = db.Column(db.Unicode)
    auteur = db.Column(db.Unicode)
    desc_media = db.Column(db.Text)
    source = db.Column(db.Unicode)
    licence = db.Column(db.Unicode)
    is_public = db.Column(db.BOOLEAN)
    supprime = db.Column(db.BOOLEAN)
    id_type = db.Column(
        db.Integer,
        ForeignKey(BibTypesMedia.id_type),
        nullable=False,
    )

    types = db.relationship(BibTypesMedia)
    bib_nom = db.relationship(BibNoms, backref="medias")

    def __repr__(self):
        return "<TMedias %r>" % self.titre


@serializable
class VMTaxrefListForautocomplete(db.Model):
    __tablename__ = "vm_taxref_list_forautocomplete"
    __table_args__ = {"schema": "taxonomie"}
    gid = db.Column(db.Integer, primary_key=True)
    cd_nom = db.Column(db.Integer)
    search_name = db.Column(db.Unicode)
    cd_ref = db.Column(db.Integer)
    nom_valide = db.Column(db.Unicode)
    lb_nom = db.Column(db.Unicode)
    nom_vern = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    group2_inpn = db.Column(db.Unicode)

    def __repr__(self):
        return "<VMTaxrefListForautocomplete  %r>" % self.search_name


@serializable
class BibTaxrefHabitats(db.Model):
    __tablename__ = "bib_taxref_habitats"
    __table_args__ = {"schema": "taxonomie"}
    id_habitat = db.Column(db.Integer, primary_key=True)
    nom_habitat = db.Column(db.Unicode)
    desc_habitat = db.Column(db.Text)

    def __repr__(self):
        return "<BibTaxrefHabitats %r>" % self.nom_habitat


@serializable
class BibTaxrefRangs(db.Model):
    __tablename__ = "bib_taxref_rangs"
    __table_args__ = {"schema": "taxonomie"}
    id_rang = db.Column(db.Integer, primary_key=True)
    nom_rang = db.Column(db.Unicode)
    tri_rang = db.Column(db.Integer)

    def __repr__(self):
        return "<BibTaxrefRangs %r>" % self.nom_rang


@serializable
class BibTaxrefStatus(db.Model):
    __tablename__ = "bib_taxref_statuts"
    __table_args__ = {"schema": "taxonomie"}
    id_statut = db.Column(db.Integer, primary_key=True)
    nom_statut = db.Column(db.Unicode)

    def __repr__(self):
        return "<BibTaxrefStatus %r>" % self.nom_statut


@serializable
class TaxrefProtectionArticles(db.Model):
    __tablename__ = "taxref_protection_articles"
    __table_args__ = {"schema": "taxonomie"}
    cd_protection = db.Column(db.Unicode, primary_key=True)
    article = db.Column(db.Unicode)
    intitule = db.Column(db.Unicode)
    arrete = db.Column(db.Unicode)
    cd_arrete = db.Column(db.Integer)
    url_inpn = db.Column(db.Unicode)
    cd_doc = db.Column(db.Integer)
    url = db.Column(db.Unicode)
    date_arrete = db.Column(db.Integer)
    type_protection = db.Column(db.Unicode)
    concerne_mon_territoire = db.Column(db.Boolean)

    def __repr__(self):
        return "<TaxrefProtectionArticles %r>" % self.article


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
        return "<VMTaxrefHierarchie %r>" % self.lb_nom


@serializable
class VTaxrefHierarchieBibtaxons(db.Model):
    __tablename__ = "v_taxref_hierarchie_bibtaxons"
    __table_args__ = {"schema": "taxonomie"}
    cd_nom = db.Column(db.Integer, primary_key=True)
    cd_ref = db.Column(db.Integer)
    regne = db.Column(db.Unicode)
    phylum = db.Column(db.Unicode)
    classe = db.Column(db.Unicode)
    ordre = db.Column(db.Unicode)
    lb_nom = db.Column(db.Unicode)
    id_rang = db.Column(db.Unicode)
    nb_tx_fm = db.Column(db.Integer)
    nb_tx_or = db.Column(db.Integer)
    nb_tx_cl = db.Column(db.Integer)
    nb_tx_ph = db.Column(db.Integer)
    nb_tx_kd = db.Column(db.Integer)

    def __repr__(self):
        return "<VMTaxrefHierarchie %r>" % self.lb_nom


@serializable
class BibTaxrefLR(db.Model):
    __tablename__ = "bib_taxref_categories_lr"
    __table_args__ = {"schema": "taxonomie"}
    id_categorie_france = db.Column(db.Unicode, primary_key=True)
    categorie_lr = db.Column(db.Unicode)
    nom_categorie_lr = db.Column(db.Unicode)
    desc_categorie_lr = db.Column(db.Unicode)


@serializable
class TaxrefBdcStatutType(db.Model):
    __tablename__ = "bdc_statut_type"
    __table_args__ = {"schema": "taxonomie"}
    cd_type_statut = db.Column(db.Unicode, primary_key=True)
    lb_type_statut = db.Column(db.Unicode)
    regroupement_type = db.Column(db.Unicode)
    thematique = db.Column(db.Unicode)
    type_value = db.Column(db.Unicode)

    text = db.relationship("TaxrefBdcStatutText", lazy="select")

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

    type_statut = db.relationship("TaxrefBdcStatutType", lazy="select")
    cor_text = db.relationship("TaxrefBdcStatutCorTextValues", lazy="select")

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

    text = db.relationship("TaxrefBdcStatutText", lazy="select")
    value = db.relationship("TaxrefBdcStatutValues", lazy="select")

    taxon = db.relationship("TaxrefBdcStatutTaxon", lazy="select")


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

    value_text = db.relationship("TaxrefBdcStatutCorTextValues", lazy="select")


@serializable
class VBdcStatus(db.Model):
    __tablename__ = "v_bdc_status"
    __table_args__ = {"schema": "taxonomie", "info": dict(is_view=True)}
    cd_nom = db.Column(db.Integer, primary_key=True)
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
