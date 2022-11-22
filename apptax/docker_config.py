from secrets import token_hex

UPLOAD_FOLDER = "medias"
SQLALCHEMY_TRACK_MODIFICATIONS = False
COOKIE_EXPIRATION = 3600
SECRET_KEY = token_hex(16)
PASS_METHOD = "hash"
