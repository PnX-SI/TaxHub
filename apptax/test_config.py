SQLALCHEMY_DATABASE_URI = "postgresql://geonatadmin:geonatpasswd@127.0.0.1:5432/geonature2db"
ID_APP = 2

APPLICATION_ROOT = '/taxhub'


SESSION_TYPE = 'filesystem'
SECRET_KEY = 'a7e0a755dd3f2c382bac5b5cea6c9329802aeedf39e3f10d0462ffb52c3f5e99'
COOKIE_EXPIRATION = 3600
COOKIE_AUTORENEW = True

# File
UPLOAD_FOLDER = 'medias'

#S3
S3_BUCKET_NAME = ''
S3_KEY = ''
S3_SECRET = ''
S3_ENDPOINT = 'https://s3.gra.cloud.ovh.net/' #URL pour l'api S3 (ex : https://s3.gra.cloud.ovh.net/ )
S3_PUBLIC_URL = '' #URL publique qui permet au client d'accéder aux médias (stocker dans la BDD) (ex : media.mon_instance_geonature.fr)
S3_FOLDER = 'taxons/' # dossier ou sont stocker les media de cette applicarion (ex : taxons ou taxhub)
S3_REGION_NAME = '' #région (ex : gra )

# Authentification crypting method (hash or md5)
PASS_METHOD='hash'
