#coding: utf8
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Sequence

from ..utils.genericmodels import serializableModel

from database import db

class BibNoms(serializableModel, db.Model):
    __tablename__ = 'bib_noms'
    __table_args__ = {'schema':'taxonomie'}
    id_nom = db.Column(db.Integer, primary_key=True)
    cd_nom = db.Column(db.Integer, ForeignKey("taxonomie.taxref.cd_nom"), nullable=True)
    cd_ref = db.Column(db.Integer)
    nom_francais = db.Column(db.Unicode)

    taxref = db.relationship("Taxref", lazy='select')
    attributs = db.relationship("CorTaxonAttribut", lazy='select')
    listes = db.relationship("CorNomListe", lazy='select')
    medias = db.relationship("TMedias", lazy='select')


class CorTaxonAttribut(serializableModel, db.Model):
    __tablename__ = 'cor_taxon_attribut'
    __table_args__ = {'schema':'taxonomie'}
    id_attribut = db.Column(db.Integer, ForeignKey("taxonomie.bib_attributs.id_attribut"), nullable=False, primary_key=True)
    cd_ref = db.Column(db.Integer, ForeignKey("taxonomie.bib_noms.cd_ref"), nullable=False, primary_key=True)
    valeur_attribut = db.Column(db.Text, nullable=False)
    bib_nom = db.relationship("BibNoms")
    bib_attribut = db.relationship("BibAttributs")

    def __repr__(self):
        return '<CorTaxonAttribut %r>'% self.valeur_attribut

class BibAttributs(serializableModel, db.Model):
    __tablename__ = 'bib_attributs'
    __table_args__ = {'schema':'taxonomie'}
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
    id_theme = db.Column(db.Integer, ForeignKey("taxonomie.bib_themes.id_theme"), nullable=False, primary_key=False)
    ordre = db.Column(db.Integer)
    theme = db.relationship("BibThemes", lazy='select')

    def __repr__(self):
        return '<BibAttributs %r>'% self.nom_attribut

class BibThemes(serializableModel, db.Model):
    __tablename__ = 'bib_themes'
    __table_args__ = {'schema':'taxonomie'}
    id_theme = db.Column(db.Integer, primary_key=True)
    nom_theme = db.Column(db.Unicode)
    desc_theme = db.Column(db.Unicode)
    ordre = db.Column(db.Integer)
    id_droit = db.Column(db.Integer)
    attributs = db.relationship("BibAttributs", lazy='select')

    def __repr__(self):
        return '<BibThemes %r>'% self.nom_theme

class Taxref(serializableModel, db.Model):
    __tablename__ = 'taxref'
    __table_args__ = {'schema':'taxonomie'}
    cd_nom = db.Column(db.Integer, primary_key=True)
    id_habitat = db.Column(db.Unicode)
    id_habitat = db.Column(db.Integer)
    id_rang = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    phylum = db.Column(db.Unicode)
    classe = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    ordre = db.Column(db.Unicode)
    famille = db.Column(db.Unicode)
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

    def __repr__(self):
        return '<Taxref %r>'% self.nom_complet



class CorNomListe(serializableModel, db.Model):
    __tablename__ = 'cor_nom_liste'
    __table_args__ = {'schema':'taxonomie'}
    id_liste = db.Column(db.Integer, ForeignKey("taxonomie.bib_listes.id_liste"), nullable=False, primary_key=True)
    id_nom = db.Column(db.Integer, ForeignKey("taxonomie.bib_noms.id_nom"), nullable=False, primary_key=True)
    bib_nom = db.relationship("BibNoms")
    bib_liste = db.relationship("BibListes")

    def __repr__(self):
        return '<CorNomListe %r>'% self.id_liste

class BibListes(serializableModel, db.Model):
    __tablename__ = 'bib_listes'
    __table_args__ = {'schema':'taxonomie'}
    id_liste = db.Column(db.Integer, primary_key=True)
    nom_liste = db.Column(db.Unicode)
    desc_liste = db.Column(db.Text)
    picto = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    group2_inpn = db.Column(db.Unicode)

    cnl = db.relationship("CorNomListe", lazy='select')

    def __repr__(self):
        return '<BibListes %r>'% self.nom_liste

class TMedias(serializableModel, db.Model):
    __tablename__ = 't_medias'
    __table_args__ = {'schema':'taxonomie'}
    id_media = db.Column(db.Integer, primary_key=True)
    # cd_ref = db.Column(db.Integer, ForeignKey("taxonomie.bib_noms.cd_nom"), nullable=False)
    cd_ref = db.Column(db.Integer, ForeignKey("taxonomie.bib_noms.cd_ref"), nullable=False, primary_key=False)
    titre = db.Column(db.Unicode)
    url = db.Column(db.Unicode)
    chemin = db.Column(db.Unicode)
    auteur = db.Column(db.Unicode)
    desc_media = db.Column(db.Text)
    #date_media = db.Column(db.DateTime)
    is_public = db.Column(db.BOOLEAN)
    supprime =  db.Column(db.BOOLEAN)
    id_type = db.Column(db.Integer, ForeignKey("taxonomie.bib_types_media.id_type"), nullable=False)
    types = db.relationship("BibTypesMedia", lazy='select')
    def __repr__(self):
        return '<TMedias %r>'% self.titre

class BibTypesMedia(serializableModel, db.Model):
    __tablename__ = 'bib_types_media'
    __table_args__ = {'schema':'taxonomie'}
    id_type = db.Column(db.Integer, primary_key=True)
    nom_type_media = db.Column(db.Unicode)
    desc_type_media = db.Column(db.Text)

    def __repr__(self):
        return '<BibTypesMedia %r>'% self.nom_type_media


class VMTaxrefListForautocomplete(serializableModel, db.Model):
    __tablename__ = 'vm_taxref_list_forautocomplete'
    __table_args__ = {'schema':'taxonomie'}
    cd_nom = db.Column(db.Integer, primary_key=True)
    search_name = db.Column(db.Unicode, primary_key=True)
    nom_valide = db.Column(db.Unicode)
    lb_nom = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    group2_inpn = db.Column(db.Unicode)
    id_liste = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<VMTaxrefListForautocomplete  %r>'% self.search_name
