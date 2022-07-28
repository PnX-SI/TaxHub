from csv import DictReader
from io import TextIOWrapper

from alembic import op
import sqlalchemy as sa


def get_csv_field_names(f, encoding, delimiter):
    if encoding == "WIN1252":  # postgresql encoding
        encoding = "cp1252"  # python encoding
    t = TextIOWrapper(f, encoding=encoding)
    reader = DictReader(t, delimiter=delimiter)
    field_names = reader.fieldnames
    t.detach()  # avoid f to be closed on t garbage collection
    f.seek(0)
    return field_names


"""
Insert CSV file into specified table.
If source columns are specified, CSV file in copied in a temporary table,
then data restricted to specified source columns are copied in final table.
"""


def copy_from_csv(
    f,
    table,
    dest_cols="",
    source_cols=None,
    schema="taxonomie",
    header=True,
    encoding=None,
    delimiter=None,
):
    tmp_table = False
    if dest_cols:
        dest_cols = " (" + ", ".join(dest_cols) + ")"
    if source_cols:
        final_table = table
        final_table_cols = dest_cols
        table = f"import_{table}"
        dest_cols = ""
        field_names = get_csv_field_names(f, encoding=encoding, delimiter=delimiter)
        op.create_table(
            table, *[sa.Column(c, sa.String) for c in map(str.lower, field_names)], schema=schema
        )

    options = ["FORMAT CSV"]
    if header:
        options.append("HEADER")
    if encoding:
        options.append(f"ENCODING '{encoding}'")
    if delimiter:
        options.append(f"DELIMITER E'{delimiter}'")
    options = ", ".join(options)
    cursor = op.get_bind().connection.cursor()
    cursor.copy_expert(
        f"""
        COPY {schema}.{table}{dest_cols}
        FROM STDIN WITH ({options})
    """,
        f,
    )

    if source_cols:
        source_cols = ", ".join(source_cols)
        op.execute(
            f"""
        INSERT INTO {schema}.{final_table}{final_table_cols}
          SELECT {source_cols}
            FROM {schema}.{table};
        """
        )
        op.drop_table(table, schema=schema)
