# coding: utf8
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Sequence
from sqlalchemy.ext.hybrid import hybrid_property

from ..utils.genericmodels import serializableModel

from . import db

import os.path

class BibNoms(serializableModel, db.Model):
    __tablename__ = "bib_noms"
    __table_args__ = {"schema": "taxonomie"}
    id_nom = db.Column(db.Integer, primary_key=True)
    cd_nom = db.Column(db.Integer, ForeignKey("taxonomie.taxref.cd_nom"), nullable=True)
    cd_ref = db.Column(db.Integer)
    nom_francais = db.Column(db.Unicode)
    comments = db.Column(db.Unicode)

    taxref = db.relationship("Taxref", lazy="select")
    attributs = db.relationship("CorTaxonAttribut", lazy="select")
    listes = db.relationship("CorNomListe", lazy="select")
    medias = db.relationship("TMedias", lazy="select")


class CorTaxonAttribut(serializableModel, db.Model):
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


class BibAttributs(serializableModel, db.Model):
    __tablename__ = "bib_attributs"
    __table_args__ = {"schema": "taxonomie"}
    id_attribut = db.Column(db.Integer, primary_key=True)
    nom_attribut = db.Column(db.Unicode)
    label_attribut = db.Column(db.Unicode)
    liste_valeur_attribut = db.Column(db.Text)
    obligatoire = db.Column(db.BOOLEAN)
    desc_attribut = db.Column(db.Text)
    type_attribut = db.Column(db.Unicode)
    type_widget = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    group2_inpn = db.Column(db.Unicode)
    id_theme = db.Column(
        db.Integer,
        ForeignKey("taxonomie.bib_themes.id_theme"),
        nullable=False,
        primary_key=False,
    )
    ordre = db.Column(db.Integer)
    theme = db.relationship("BibThemes", lazy="select")

    def __repr__(self):
        return "<BibAttributs %r>" % self.nom_attribut


class BibThemes(serializableModel, db.Model):
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


class Taxref(serializableModel, db.Model):
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

    def __repr__(self):
        return "<Taxref %r>" % self.nom_complet


class CorNomListe(serializableModel, db.Model):
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


class BibListes(serializableModel, db.Model):
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

    def __repr__(self):
        return "<BibListes %r>" % self.nom_liste


class TMedias(serializableModel, db.Model):
    __tablename__ = "t_medias"
    __table_args__ = {"schema": "taxonomie"}
    id_media = db.Column(db.Integer, primary_key=True)
    cd_ref = db.Column(
        db.Integer,
        ForeignKey("taxonomie.bib_noms.cd_nom"),
        nullable=False,
        primary_key=False,
    )
    titre = db.Column(db.Unicode)
    url = db.Column(db.Unicode)
    chemin = db.Column(db.Unicode)
    auteur = db.Column(db.Unicode)
    desc_media = db.Column(db.Text)
    is_public = db.Column(db.BOOLEAN)
    supprime = db.Column(db.BOOLEAN)
    id_type = db.Column(
        db.Integer, ForeignKey("taxonomie.bib_types_media.id_type"), nullable=False
    )
    types = db.relationship("BibTypesMedia", lazy="select")

    def __repr__(self):
        return "<TMedias %r>" % self.titre


class BibTypesMedia(serializableModel, db.Model):
    __tablename__ = "bib_types_media"
    __table_args__ = {"schema": "taxonomie"}
    id_type = db.Column(db.Integer, primary_key=True)
    nom_type_media = db.Column(db.Unicode)
    desc_type_media = db.Column(db.Text)

    def __repr__(self):
        return "<BibTypesMedia %r>" % self.nom_type_media


class VMTaxrefListForautocomplete(serializableModel, db.Model):
    __tablename__ = "vm_taxref_list_forautocomplete"
    __table_args__ = {"schema": "taxonomie"}
    cd_nom = db.Column(db.Integer, primary_key=True)
    search_name = db.Column(db.Unicode, primary_key=True)
    cd_ref = db.Column(db.Integer)
    nom_valide = db.Column(db.Unicode)
    lb_nom = db.Column(db.Unicode)
    nom_vern = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    group2_inpn = db.Column(db.Unicode)

    def __repr__(self):
        return "<VMTaxrefListForautocomplete  %r>" % self.search_name


class BibTaxrefHabitats(serializableModel, db.Model):
    __tablename__ = "bib_taxref_habitats"
    __table_args__ = {"schema": "taxonomie"}
    id_habitat = db.Column(db.Integer, primary_key=True)
    nom_habitat = db.Column(db.Unicode)
    desc_habitat = db.Column(db.Text)

    def __repr__(self):
        return "<BibTaxrefHabitats %r>" % self.nom_habitat


class BibTaxrefRangs(serializableModel, db.Model):
    __tablename__ = "bib_taxref_rangs"
    __table_args__ = {"schema": "taxonomie"}
    id_rang = db.Column(db.Integer, primary_key=True)
    nom_rang = db.Column(db.Unicode)
    tri_rang = db.Column(db.Integer)

    def __repr__(self):
        return "<BibTaxrefRangs %r>" % self.nom_rang


class BibTaxrefStatus(serializableModel, db.Model):
    __tablename__ = "bib_taxref_statuts"
    __table_args__ = {"schema": "taxonomie"}
    id_statut = db.Column(db.Integer, primary_key=True)
    nom_statut = db.Column(db.Unicode)

    def __repr__(self):
        return "<BibTaxrefStatus %r>" % self.nom_statut


class TaxrefProtectionArticles(serializableModel, db.Model):
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


class VMTaxrefHierarchie(serializableModel, db.Model):
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


class VTaxrefHierarchieBibtaxons(serializableModel, db.Model):
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


class BibTaxrefLR(serializableModel, db.Model):
    __tablename__ = "bib_taxref_categories_lr"
    __table_args__ = {"schema": "taxonomie"}
    id_categorie_france = db.Column(db.Unicode, primary_key=True)
    categorie_lr = db.Column(db.Unicode)
    nom_categorie_lr = db.Column(db.Unicode)
    desc_categorie_lr = db.Column(db.Unicode)
