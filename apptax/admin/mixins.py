from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.form.fields import Select2Field
from sqlalchemy import select

from apptax.database import db
from apptax.taxonomie.models import VMRegne, VMGroup2Inpn

from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.form.fields import Select2Field
from sqlalchemy import select

from apptax.database import db
from apptax.taxonomie.models import VMRegne, VMGroup2Inpn


class RegneAndGroupFormMixin:
    form_overrides = {"regne": QuerySelectField, "group2_inpn": QuerySelectField}

    form_args = {
        "regne": {
            "query_factory": lambda: db.session.scalars(
                select(VMRegne).where(VMRegne.regne.isnot(None))
            ).all(),
            "allow_blank": True,
        },
        "group2_inpn": {
            "query_factory": lambda: db.session.scalars(
                select(VMGroup2Inpn).where(VMGroup2Inpn.group2_inpn.isnot(None))
            ),
            "allow_blank": True,
        },
    }

    def on_model_change(self, form, model, is_created):
        """
        Force None on empty string regne
        and put transform orm object in str
        """
        # HACK otherwise QuerySelectField insert the VRegne object ..
        # Select2Fields with choices does not work because choices list
        # is load when app is loaded (its a probleme for migrations)
        if model.regne:
            model.regne = model.regne.regne
        if model.regne == "":
            model.regne = None

        if model.group2_inpn:
            model.group2_inpn = model.group2_inpn.group2_inpn
        if model.group2_inpn == "":
            model.group2_inpn = None
