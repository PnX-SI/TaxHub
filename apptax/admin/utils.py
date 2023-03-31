from werkzeug.utils import secure_filename

from pypnusershub.db.models import AppUser, Application
from pypnusershub.utils import get_current_app_id


def taxref_media_file_name(obj, file_data):
    """
    Generate file name
    """
    return secure_filename(f"{obj.taxon.cd_ref}_{file_data.filename}")


def get_user_permission(id_role):
    id_app = (
        Application.query.filter_by(
            code_application="TH",
        )
        .one()
        .id_application
    )

    query = AppUser.query.filter(AppUser.id_application == id_app).filter(
        AppUser.id_role == id_role
    )
    return query.scalar()
