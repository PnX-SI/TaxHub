#!/bin/bash

echo "Arret de l'application..."
sudo -s supervisorctl stop taxhub

. settings.ini

#Création des répertoires systèmes
. create_sys_dir.sh
create_sys_dir

echo "Création du fichier de configuration ..."
if [ ! -f config.py ]; then
  cp config.py.sample config.py
fi

echo "préparation du fichier config.py..."
sed -i "s/SQLALCHEMY_DATABASE_URI = .*$/SQLALCHEMY_DATABASE_URI = \"postgresql:\/\/$user_pg:$user_pg_pass@$db_host:$db_port\/$db_name\"/" config.py


# rendre la commande nvm disponible
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
#installation de node et npm et des librairies JS
cd static/
nvm install 
nvm use
npm ci
cd ..

#Installation du virtual env
echo "Installation du virtual env..."


if [[ $python_path ]]; then
  python3 -m virtualenv -p $python_path $venv_dir
else
  python3 -m virtualenv $venv_dir
fi

source $venv_dir/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

#création d'un fichier de configuration
if [ ! -f static/app/constants.js ]; then
  echo 'Fichier de configuration non existant'
  cp static/app/constants.js.sample static/app/constants.js
fi


#affectation des droits sur le répertoire static/medias
chmod -R 775 static/medias

#Lancement de l'application
DIR=$(readlink -e "${0%/*}")
sudo -s cp taxhub-service.conf /etc/supervisor/conf.d/
sudo -s sed -i "s%APP_PATH%${DIR}%" /etc/supervisor/conf.d/taxhub-service.conf


#création d'un fichier rotation des logs
sudo cp $DIR/log_rotate /etc/logrotate.d/taxhub
sudo -s sed -i "s%APP_PATH%${DIR}%" /etc/logrotate.d/taxhub
sudo logrotate -f /etc/logrotate.conf

sudo -s supervisorctl reread
sudo -s supervisorctl reload
