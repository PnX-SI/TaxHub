"""
Description des options de configuration
"""

from marshmallow import Schema, fields, validates_schema, ValidationError, post_load, pre_load
from marshmallow.validate import OneOf, Regexp, Email, Length


class TaxhubAppConf(Schema):
    API_PREFIX = fields.String(
        load_default="",
        validate=Regexp(
            r"(^\/(.+)$)|(^\s*$)",
            error="API_PREFIX must start with a slash.",
        ),
    )
    ID_TYPE_MAIN_PHOTO = fields.Integer(load_default=1)


class TaxhubSchemaConf(TaxhubAppConf):
    SQLALCHEMY_DATABASE_URI = fields.String(
        required=True,
        validate=Regexp(
            r"^(postgres(?:ql)?)((\+psycopg2)?):\/\/(?:([^@\s]+)@)?([^\/\s]+)(?:\/(\w+))?(?:\?(.+))?",
            error="PostgreSQL database URL is invalid. Check for authorized URL here : https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING-URIS",
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = fields.Boolean(load_default=True)
    SESSION_TYPE = fields.String(load_default="filesystem")
    SECRET_KEY = fields.String(required=True, validate=Length(min=20))
    CODE_APPLICATION = fields.String(load_default="TH")
    # le cookie expire toute les 7 jours par défaut
    COOKIE_EXPIRATION = fields.Integer(load_default=3600 * 24 * 7)
    COOKIE_AUTORENEW = fields.Boolean(load_default=True)
    TRAP_ALL_EXCEPTIONS = fields.Boolean(load_default=False)
    APPLICATION_ROOT = fields.String(load_default="/")
    MEDIA_FOLDER = fields.String(load_default="media")
    PASS_METHOD = fields.String(load_default="hash")
    FLASK_ADMIN_SWATCH = fields.String(load_default="cerulean")
    FLASK_ADMIN_FLUID_LAYOUT = fields.Boolean(load_default=True)
