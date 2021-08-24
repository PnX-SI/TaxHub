import os
from flask_sqlalchemy import SQLAlchemy

os.environ['FLASK_SQLALCHEMY_DB'] = 'apptax.database.db'
db = SQLAlchemy()
