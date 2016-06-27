#coding: utf8

'''
mappings applications et utilisateurs
'''

import hashlib
from server import db

class User(db.Model):

    __tablename__ = 't_roles'
    __table_args__ = {'schema':'utilisateurs'}
    groupe = db.Column(db.Boolean)
    id_role = db.Column(db.Integer, primary_key=True)
    identifiant = db.Column(db.Unicode)
    nom_role = db.Column(db.Unicode)
    prenom_role = db.Column(db.Unicode)
    desc_role = db.Column(db.Unicode)
    _password = db.Column('pass', db.Unicode)
    email = db.Column(db.Unicode)
    id_organisme = db.Column(db.Integer)
    organisme = db.Column(db.Unicode)
    id_unite = db.Column(db.Integer)
    remarques = db.Column(db.Unicode)
    pn = db.Column(db.Boolean)
    session_appli = db.Column(db.Unicode)
    date_insert = db.Column(db.DateTime)
    date_update = db.Column(db.DateTime)

    # applications_droits = db.relationship('AppUser', lazy='joined')

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pwd):
        self._password = hashlib.sha256(pwd.encode('utf8')).hexdigest()

    def check_password(self, pwd):
        print(pwd)
        return self._password == hashlib.sha256(pwd.encode('utf8')).hexdigest()

    def to_json(self):
        out = {
            'id': self.id_role,
            'login': self.identifiant,
            'email': self.email,
            'applications': []
        }
        for app_data in self.applications_droits:
            app = {
                    'id': app_data.application_id,
                    'nom': app_data.application.nom_application,
                    'niveau': app_data.id_droit_max
                    }
            out['applications'].append(app)
        return out

class Application(db.Model):
    '''
    Représente une application ou un module
    '''
    __tablename__ = 't_applications'
    __table_args__ = {'schema':'utilisateurs'}
    id_application = db.Column(db.Integer, primary_key=True)
    nom_application = db.Column(db.Unicode)
    desc_application = db.Column(db.Unicode)

class AppUser(db.Model):
    '''
    Relations entre applications et utilisateurs
    '''
    __tablename__ = 'v_userslist_forall_applications'
    __table_args__ = {'schema':'utilisateurs'}
    id_role = db.Column(db.Integer,
            db.ForeignKey('utilisateurs.t_roles.id_role'), primary_key=True)
    id_application = db.Column(db.Integer,
            db.ForeignKey('utilisateurs.application.id_application'), primary_key=True)
    identifiant = db.Column(db.Unicode)
    _password = db.Column('pass', db.Unicode)
    id_droit_max = db.Column(db.Integer, primary_key=True)
    # user = db.relationship('User', backref='relations', lazy='joined')
    # application = db.relationship('Application', backref='relations', lazy='joined')

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pwd):
        self._password = hashlib.md5(pwd.encode('utf8')).hexdigest()

    def check_password(self, pwd):
        print(pwd)
        return self._password == hashlib.md5(pwd.encode('utf8')).hexdigest()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name != 'pass' }
