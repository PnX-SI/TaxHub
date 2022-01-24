#!/bin/bash


#Création des répertoires systèmes


cp config.py.docker apptax/config.py

echo "préparation du fichier config.py..."
sed -i "s/SQLALCHEMY_DATABASE_URI = .*$/SQLALCHEMY_DATABASE_URI = \"postgresql:\/\/$user_pg:$user_pg_pass@$db_host:$db_port\/$db_name\"/" apptax/config.py

echo "SECRET_KEY='${SECRET_KEY}'" >> apptax/config.py

# rendre la commande nvm disponible
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

#création d'un fichier de configuration
if [ ! -f static/app/constants.js ]; then
  echo 'Fichier de configuration non existant'
  cp static/app/constants.js.sample static/app/constants.js
fi


#affectation des droits sur le répertoire static/medias
chmod -R 775 static/medias

#Lancement de l'application
export PYTHONPATH=$BASE_DIR:$PYTHONPATH
export FLASK_APP=server
exec gunicorn "apptax.app:create_app()" --pid="${app_name}.pid" -w "${gun_num_workers}"  -b "${gun_host}:${gun_port}"  -n "${app_name}"

