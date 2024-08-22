from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.form.fields import Select2Field
from sqlalchemy import select

from apptax.database import db
from apptax.taxonomie.models import VMRegne, VMGroup2Inpn

from wtforms.fields import SelectField
from sqlalchemy import select

from apptax.database import db
from apptax.taxonomie.models import VMRegne, VMGroup2Inpn


class RegneAndGroupFormMixin:
    form_overrides = {"regne": SelectField, "group2_inpn": SelectField}

    def overwrite_form(self, form):
        """
        Surcharge du formulaire :
            Liste des règnes et groupe2_inpn
        """
        regne = db.session.scalars(select(VMRegne.regne).where(VMRegne.regne.isnot(None))).all()
        regne_choices = [(m, m) for m in regne]
        group2_inpn = db.session.scalars(
            select(VMGroup2Inpn.group2_inpn).where(VMGroup2Inpn.group2_inpn.isnot(None))
        ).all()
        group2_inpn_choices = [(m, m) for m in group2_inpn]

        form.regne.choices = [("", "---")] + regne_choices
        form.group2_inpn.choices = [("", "---")] + group2_inpn_choices

        return form

    def create_form(self, obj=None):
        """
        Surcharge du formulaire :
            Liste des règnes et groupe2_inpn
        """
        form = super().create_form(obj)
        form = self.overwrite_form(form)
        return form

    def edit_form(self, obj=None):
        """
        Surcharge du formulaire :
            Liste des règnes et groupe2_inpn
        """
        form = super().edit_form(obj)
        form = self.overwrite_form(form)
        return form

    def validate_form(self, form):
        if form.group2_inpn.data == "":
            form.group2_inpn.data = None
        if form.regne.data == "":
            form.regne.data = None
        return super().validate_form(form)
