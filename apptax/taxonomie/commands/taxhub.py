import click

import glob
import os
import shutil

from pathlib import Path
from flask import current_app
from flask.cli import with_appcontext

from sqlalchemy import select

from apptax.database import db
from apptax.taxonomie.models import TMedias


import logging

logger = logging.getLogger("taxhub_commands")


@click.group(help="Manager Taxhub app.")
def taxhub():
    pass


@taxhub.command()
@with_appcontext
@click.option("--drop-file", is_flag=True, help="Drop file and thumb dir")
def check_deleted_media(drop_file):
    """
    Suppression des fichiers médias qui ne sont plus référencés en base
    """
    media_dir = Path(current_app.config["MEDIA_FOLDER"], "taxhub").absolute()

    # Traitement des fichiers des médias
    logger.info(f"Process media files {media_dir}")
    for f in glob.glob(f"{media_dir}/*.*"):
        file_name = os.path.basename(f)
        query = select(TMedias).where(TMedias.chemin != None).where(TMedias.chemin == file_name)
        results = db.session.scalars(query).all()
        if not results:
            logger.warning(f"File {file_name} not related to database media")
            if drop_file:
                os.remove(f)
                logger.warning("\t file dropped")
    logger.info("...done")
    # Traitement des thumnails des médias
    logger.info(f"Process thumbnail files {media_dir}/thumb")
    for d in os.listdir(f"{media_dir}/thumb"):
        query = select(TMedias).where(TMedias.id_media == int(d))
        results = db.session.scalars(query).all()
        if not results:
            logger.warning(f"Thumb dir {d} not related to database media")
            if drop_file:
                shutil.rmtree(f"{media_dir}/thumb/{d}")
                logger.warning("\t dir dropped")
    logger.info("...done")


taxhub.add_command(check_deleted_media)
