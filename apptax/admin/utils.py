import csv
from werkzeug.utils import secure_filename
from sqlalchemy import select

from pypnusershub.db.models import AppUser, Application
from pypnusershub.utils import get_current_app_id

from apptax.taxonomie.models import BibListes, Taxref
from apptax.database import db


def taxref_media_file_name(obj, file_data):
    """
    Generate file name
    """
    return secure_filename(f"{obj.taxon.cd_ref}_{file_data.filename}")


def get_user_permission(id_role):
    id_app = get_current_app_id()

    query = (
        select(AppUser).where(AppUser.id_application == id_app).where(AppUser.id_role == id_role)
    )

    return db.session.scalar(query)


class PopulateBibListeException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def populate_bib_liste(id_list, delimiter, with_header, file):
    if not ("." in file.filename and file.filename.rsplit(".", 1)[1].lower() == "csv"):
        raise PopulateBibListeException("Format de fichier requis : CSV")

    try:
        fstring = file.read().decode()
        inputcsv = csv.reader(fstring.splitlines(), delimiter=delimiter)
    except Exception:
        raise PopulateBibListeException("Lecture du fichier impossible")

    bibliste = BibListes.query.get(id_list)

    # if header skip first line
    if with_header:
        next(inputcsv, None)

    taxa_set = set()
    for row in inputcsv:
        # Si la ligne est vide
        if not row:
            break
        # Si la valeur du cd_nom est vide
        if not row[0]:
            break

        try:
            cd_nom = int(row[0])
        except (TypeError, ValueError):
            msg = "Invalid cd_nom value: {row[0]}"
            if not row[0].isnumeric():
                msg = """
                    Il semble que votre fichier contienent le nom des colonnes,
                    sélectionner l'option 'with header'
                    ou que la première colonne ne corresponde pas à une liste de cd_nom"""
            raise PopulateBibListeException(msg)

        tax = Taxref.query.get(cd_nom)
        if tax:
            # add in a set to avoid doublon -> integrity error
            taxa_set.add(tax)
    for new_name in taxa_set:
        bibliste.noms.append(new_name)

    db.session.commit()
