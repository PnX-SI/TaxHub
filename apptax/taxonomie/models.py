#coding: utf8
from server import db

from sqlalchemy import ForeignKey, Sequence

class BibTaxons(db.Model):
    __tablename__ = 'bib_taxons'
    __table_args__ = {'schema':'taxonomie'}
    id_taxon = db.Column(db.Integer, primary_key=True)
    cd_nom = db.Column(db.Integer, ForeignKey("taxonomie.taxref.cd_nom"), nullable=False)
    nom_latin = db.Column(db.Unicode)
    nom_francais = db.Column(db.Unicode)
    auteur = db.Column(db.Unicode)
    taxref = db.relationship("Taxref", lazy='select')
    attributs = db.relationship("CorTaxonAttribut", lazy='select')
    listes = db.relationship("CorTaxonListe", lazy='select')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<BibTaxons %r>'% self.nom_latin

class CorTaxonAttribut(db.Model):
    __tablename__ = 'cor_taxon_attribut'
    __table_args__ = {'schema':'taxonomie'}
    id_attribut = db.Column(db.Integer, ForeignKey("taxonomie.bib_attributs.id_attribut"), nullable=False, primary_key=True)
    id_taxon = db.Column(db.Integer, ForeignKey("taxonomie.bib_taxons.id_taxon"), nullable=False, primary_key=True)
    valeur_attribut = db.Column(db.Unicode, nullable=False)
    bib_taxon = db.relationship("BibTaxons")
    bib_attribut = db.relationship("BibAttributs")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<CorTaxonAttribut %r>'% self.valeur_attribut

class BibAttributs(db.Model):
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

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<BibAttributs %r>'% self.nom_attribut

class Taxref(db.Model):
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
    nom_valide = db.Column(db.Unicode)
    nom_valide = db.Column(db.Unicode)
    nom_vern_eng = db.Column(db.Unicode)
    group1_inpn = db.Column(db.Unicode)
    group2_inpn = db.Column(db.Unicode)

    def __repr__(self):
        return '<Taxref %r>'% self.nom_complet

class CorTaxonListe(db.Model):
    __tablename__ = 'cor_taxon_liste'
    __table_args__ = {'schema':'taxonomie'}
    id_liste = db.Column(db.Integer, ForeignKey("taxonomie.bib_listes.id_liste"), nullable=False, primary_key=True)
    id_taxon = db.Column(db.Integer, ForeignKey("taxonomie.bib_taxons.id_taxon"), nullable=False, primary_key=True)
    bib_taxon = db.relationship("BibTaxons")
    bib_liste = db.relationship("BibListes")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<CorTaxonListe %r>'% self.id_liste

class BibListes(db.Model):
    __tablename__ = 'bib_listes'
    __table_args__ = {'schema':'taxonomie'}
    id_liste = db.Column(db.Integer, primary_key=True)
    nom_liste = db.Column(db.Unicode)
    desc_liste = db.Column(db.Text)
    picto = db.Column(db.Unicode)
    regne = db.Column(db.Unicode)
    group2_inpn = db.Column(db.Unicode)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<BibListes %r>'% self.nom_attribut
