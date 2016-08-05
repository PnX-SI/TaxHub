#coding: utf8
from flask import jsonify, json, Blueprint
from flask import request, Response

from server import db

from ..utils.utilssqlalchemy import json_resp
from .models import BibTypesMedia
from sqlalchemy import select, or_

adresses = Blueprint('bib_types_media', __name__)

@adresses.route('/', methods=['GET'])
@adresses.route('/<int:id>', methods=['GET'])
@json_resp
def get_bibtypesmedia(id = None):
    if id:
        data = db.session.query(BibTypesMedia).filter_by(id_type=id).first()
        return data.as_dict()
    else :
        data = db.session.query(BibTypesMedia).all()
        return [type.as_dict() for type in data]