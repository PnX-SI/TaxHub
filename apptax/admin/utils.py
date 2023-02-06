from werkzeug.utils import secure_filename

from pypnusershub.db.models import UserApplicationRight

def taxref_media_file_name(obj, file_data):
    """
    Generate file name
    """
    return secure_filename(f"{obj.taxon.cd_ref}_{file_data.filename}")


def get_user_permission(id_app, id_role):
    query = UserApplicationRight.query.filter(
        UserApplicationRight.id_application == id_app
    ).filter(
        UserApplicationRight.id_role == id_role
    )
    return query.scalar()
