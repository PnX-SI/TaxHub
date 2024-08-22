import logging
import json

from flask import request, flash

from flask_admin import form
from flask_admin.form import BaseForm
from marshmallow import Schema, ValidationError, fields

log = logging.getLogger(__name__)


def generate_schema_additional_attribut(type_: str = None):
    """
    Generate a schema for additional attributes.

    Parameters
    ----------
    type_ : str, optional
        The type of the additional attributes. Can be "int", "json" or None.
        If None, the default type is "str".

    Returns
    -------
    class
        A schema for additional attributes.

    """
    if type_ == "int":
        type_ = fields.Integer()
    elif type_ == "json":
        type_ = fields.Dict()
    else:
        type_ = fields.String()

    class AdditionalAttributSchema(Schema):
        values = fields.List(type_, required=True)

    return AdditionalAttributSchema


class TAdditionalAttributForm(BaseForm):
    """
    Override BaseForm to include the validation of the values list during the creation/edition of an attribut in TaxHub
    """

    def validate(self, extra_validators=None):
        if self.data["type_widget"] in ("select", "multiselect", "radio"):
            if request.endpoint in ["bibattributs.edit_view", "bibattributs.create_view"]:
                try:
                    data = json.loads(self.data["liste_valeur_attribut"])
                except json.JSONDecodeError as e:
                    log.exception("Liste valeur attribut must be a JSON string")
                    flash("'Valeurs disponibles' doit être au format JSON", "error")
                    return False
                try:
                    type_ = self.data["type_attribut"]
                    generate_schema_additional_attribut(type_)().load(data)
                except ValidationError as e:
                    log.exception(
                        """JSON doesn't match wanted format {"values":["val1","val2",...]} or "values" """
                        """contains a value that does not match te type_attirbut declared"""
                    )
                    flash(
                        """'Valeurs disponibles' doit être format {"values":["val1","val2",...]}"""
                        """ et les valeurs doivent respecter le type déclaré dans 'Type Attribut'""",
                        "error",
                    )
                    return False
        return super().validate(extra_validators)


class ImageUploadFieldWithoutDelete(form.ImageUploadField):
    """
    Extension of the `ImageUploadField` class of Flask-Admin.
    This class is used to upload images without the possibility to delete them.

    The widget used to display the field is a custom class `ImageUploadInputWithoutDelete`
    which is a subclass of `ImageUploadInput`.

    Attributes
    ----------
    widget : ImageUploadInputWithoutDelete
        The widget used to display the field.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        class ImageUploadInputWithoutDelete(form.ImageUploadInput):
            """
            Custom widget to display the ImageUploadFieldWithoutDelete.
            It doesn't allow the deletion of images.
            """

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.data_template = (
                    '<div class="image-thumbnail">'
                    " <img %(image)s>"
                    "</div>"
                    "<br>"
                    "<input %(file)s>"
                )

        self.widget = ImageUploadInputWithoutDelete()
