# coding: utf8
"""
Fonctions utilitaires
"""
import collections
from flask import jsonify, Response, current_app
import json
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, create_engine, MetaData
from werkzeug.datastructures import Headers


from . import db


class GenericTable:
    def __init__(self, tableName, schemaName):
        engine = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
        meta = MetaData(bind=engine)
        meta.reflect(schema=schemaName, views=True)
        self.tableDef = meta.tables[tableName]
        self.columns = [column.name for column in self.tableDef.columns]

    def serialize(self, data):
        return serializeQuery(data, self.columns)


def serializeQuery(data, columnDef):
    rows = [
        {c["name"]: getattr(row, c["name"]) for c in columnDef if getattr(row, c["name"]) != None}
        for row in data
    ]
    return rows


def serializeQueryOneResult(row, columnDef):
    row = {
        c["name"]: getattr(row, c["name"]) for c in columnDef if getattr(row, c["name"]) != None
    }
    return row


def _normalize(obj, columns):
    """
    Retourne un dictionnaire dont les clés sont le tableau de colonnes
    fourni (`columns`) et les valeurs sont issues de l'objet `obj` fourni.
    """
    out = {}
    for col in columns:
        if isinstance(col.type, db.Date):
            out[col.name] = str(getattr(obj, col.name))
        else:
            out[col.name] = getattr(obj, col.name)
    return out


def normalize(obj, *parents):
    """
    Prend un objet mappé SQLAlchemy et le transforme en dictionnaire pour
    être sérialisé en JSON.
    Le second paramêtre `parents` permet de compléter la normalisation
    avec les données des tables liées par une relation d'héritage.
    """
    try:
        return obj.to_json()
    except AttributeError:
        out = _normalize(obj, obj.__table__.columns)
        for p in parents:
            out.update(_normalize(obj, p().__table__.columns))
        return out


def json_resp(fn):
    """
    Décorateur transformant le résultat renvoyé par une vue
    en objet JSON
    """

    @wraps(fn)
    def _json_resp(*args, **kwargs):
        res = fn(*args, **kwargs)
        if isinstance(res, tuple):
            res, status = res
        else:
            status = 200
        return Response(json.dumps(res), status=status, mimetype="application/json")

    return _json_resp


def csv_resp(fn):
    """
    Décorateur transformant le résultat renvoyé en un fichier csv
    """

    @wraps(fn)
    def _csv_resp(*args, **kwargs):
        res = fn(*args, **kwargs)
        filename, data, columns, separator = res
        outdata = [separator.join(columns)]

        headers = Headers()
        headers.add("Content-Type", "text/plain")
        headers.add("Content-Disposition", "attachment", filename="export_%s.csv" % filename)

        for o in data:
            outdata.append(
                separator.join('"%s"' % (o.get(i), "")[o.get(i) == None] for i in columns)
            )

        out = "\r\n".join(outdata)
        return Response(out, headers=headers)

    return _csv_resp


def dict_merge(dct, merge_dct):
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.Mapping):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
