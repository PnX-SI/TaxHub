#!/bin/bash

. settings.ini

echo "Création du fichier de configuration ..."
cp config.py.sample config.py

echo "préparation du fichier config.py..."
#monuser:monpassachanger@localhost/taxhubdb
sed -i "s/SQLALCHEMY_DATABASE_URI = .*$/SQLALCHEMY_DATABASE_URI = \"$user_pg:$user_pg_pass@$db_host:$db_port\/$db_name\"/" config.py


#Installation du virtual env
echo "Installation du virtual env..."
virtualenv venv
virtualenv -p /usr/bin/python3.4 venv
source venv/bin/activate
pip install -r requirements.txt 
deactivate
