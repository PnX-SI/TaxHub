#!/bin/bash

. settings.ini

echo "Création du fichier de configuration ..."
cp config.py.sample config.py

echo "préparation du fichier config.py..."
#monuser:monpassachanger@localhost/taxhubdb
sed -i "s/SQLALCHEMY_DATABASE_URI = .*$/SQLALCHEMY_DATABASE_URI = \"postgresql:\/\/$user_pg:$user_pg_pass@$db_host:$db_port\/$db_name\"/" config.py

#installation des librairies
cd static/
bower install bower.json
cd ..

#Installation du virtual env
echo "Installation du virtual env..."
virtualenv venv
virtualenv -p $python_path venv #TODO adapater le chemin à la version de python du server
source venv/bin/activate
pip install -r requirements.txt
deactivate

#création d'un fichier de configuration
cp static/app/constants.js.sample static/app/constants.js

