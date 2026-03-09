import csv
from time import perf_counter

from werkzeug.utils import secure_filename
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from pypnusershub.db.models import AppUser, Application
from pypnusershub.utils import get_current_app_id

from apptax.taxonomie.models import BibListes, Taxref, cor_nom_liste
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


def _chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def _parse_input_cd_noms(file, delimiter, with_header):
    try:

        fstring = file.read().decode()
        inputcsv = csv.reader(fstring.splitlines(), delimiter=delimiter)

        # if header skip first line
        if with_header:
            next(inputcsv, None)

        rows_read = 0
        input_cd_noms = []
        for row in inputcsv:
            # Si la ligne est vide
            if not row:
                break

            first_value = row[0].strip() if row[0] else ""
            # Si la valeur du cd_nom est vide
            if not first_value:
                break

            rows_read += 1

            try:
                input_cd_noms.append(int(first_value))
            except (TypeError, ValueError):
                msg = f"Invalid cd_nom value: {first_value}"
                if not first_value.isnumeric():
                    msg = """
                    Il semble que votre fichier contienent le nom des colonnes,
                    sélectionner l'option 'with header'
                    ou que la première colonne ne corresponde pas à une liste de cd_nom"""
                raise PopulateBibListeException(msg)
    except PopulateBibListeException:
        raise
    except Exception as exc:
        raise PopulateBibListeException(f"Lecture du fichier impossible ({exc})")

    return rows_read, input_cd_noms


def _populate_bib_liste_batch(id_list, input_cd_noms):
    valid_cd_noms = set()
    unique_input_cd_noms = sorted(set(input_cd_noms))
    for batch in _chunked(unique_input_cd_noms, 5000):
        query = select(Taxref.cd_nom).where(Taxref.cd_nom.in_(batch))
        valid_cd_noms.update(db.session.execute(query).scalars().all())

    inserted_count = 0
    sorted_valid_cd_noms = sorted(valid_cd_noms)
    for batch in _chunked(sorted_valid_cd_noms, 5000):
        values = [{"id_liste": id_list, "cd_nom": cd_nom} for cd_nom in batch]
        insert_stmt = (
            pg_insert(cor_nom_liste)
            .values(values)
            .on_conflict_do_nothing(
                index_elements=[cor_nom_liste.c.id_liste, cor_nom_liste.c.cd_nom]
            )
            .returning(cor_nom_liste.c.cd_nom)
        )
        inserted_count += len(db.session.execute(insert_stmt).scalars().all())

    db.session.commit()

    return {
        "unique_cd_nom_count": len(unique_input_cd_noms),
        "valid_cd_nom_count": len(sorted_valid_cd_noms),
        "not_found_count": len(unique_input_cd_noms) - len(sorted_valid_cd_noms),
        "already_in_list_count": len(sorted_valid_cd_noms) - inserted_count,
        "inserted_count": inserted_count,
    }


def populate_bib_liste(id_list, delimiter, with_header, file):
    if not ("." in file.filename and file.filename.rsplit(".", 1)[1].lower() == "csv"):
        raise PopulateBibListeException("Format de fichier requis : CSV")

    started_at = perf_counter()

    if isinstance(id_list, (tuple, list)):
        id_list = id_list[0] if id_list else None

    try:
        id_list = int(id_list)
    except (TypeError, ValueError):
        raise PopulateBibListeException("Identifiant de liste invalide")

    if not db.session.get(BibListes, id_list):
        raise PopulateBibListeException("Liste introuvable")

    rows_read, input_cd_noms = _parse_input_cd_noms(file, delimiter, with_header)
    result = _populate_bib_liste_batch(id_list, input_cd_noms)

    result["rows_read"] = rows_read
    result["duration_ms"] = (perf_counter() - started_at) * 1000

    return result
