#coding: utf8
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class serializableModel(db.Model):
    __abstract__ = True

    def as_dict(self, recursif=False):
        if recursif :
            return self.as_dict_withrelationships()
        else :
            return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_dict_withrelationships(self):
        obj = self.as_dict()
        for key in self.__mapper__.relationships.keys() :
            if self.__mapper__.relationships[key].uselist :
                obj[key] = [ item.as_dict() for item in getattr(self, key)]
            else :
                obj[key] = getattr(self, key).as_dict()
        return obj
