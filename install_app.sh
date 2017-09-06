#!/bin/bash


echo "Arret de l'application..."
sudo supervisorctl stop taxhub

. settings.ini

echo "Création du fichier de configuration ..."
if [ ! -f config.py ]; then
  cp config.py.sample config.py
fi

echo "préparation du fichier config.py..."
sed -i "s/SQLALCHEMY_DATABASE_URI = .*$/SQLALCHEMY_DATABASE_URI = \"postgresql:\/\/$user_pg:$user_pg_pass@$db_host:$db_port\/$db_name\"/" config.py

nano config.py

#installation des librairies
cd static/
npm install
cd ..

#Installation du virtual env
echo "Installation du virtual env..."
virtualenv venv

if [[ $python_path ]]; then
  virtualenv -p $python_path venv
fi

source venv/bin/activate
pip install -r requirements.txt
deactivate

#création d'un fichier de configuration
if [ ! -f static/app/constants.js ]; then
  echo 'Fichier de configuration non existant'
  cp static/app/constants.js.sample static/app/constants.js
fi

nano static/app/constants.js

#affectation des droits sur le répertoire static/medias
chmod -R 775 static/medias

#Lancement de l'application
sudo cp taxhub-service.conf /etc/supervisor/conf.d/taxhub-service.conf
sudo supervisorctl reread
sudo supervisorctl reload
