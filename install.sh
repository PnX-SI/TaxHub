#!/bin/bash

. settings.ini

echo "Créer le fichier de configuration ..."
cp app/config/parameters.yml.sample app/config/parameters.yml

echo "préparation du fichier app/config/parameters.yml..."
sed -i "s/database_host: .*$/database_host: $db_host/" app/config/parameters.yml
sed -i "s/database_port: .*$/database_port: $db_port/" app/config/parameters.yml
sed -i "s/database_name: .*$/database_name: $db_name/" app/config/parameters.yml
sed -i "s/database_user: .*$/database_user: $user_pg/" app/config/parameters.yml
sed -i "s/database_password: .*$/database_password: $user_pg_pass/" app/config/parameters.yml

# Installation des dépendances
echo "lancer composer install"
composer install

# Donner les droits nécessaires pour le bon fonctionnement de l'application 
echo "Configuration des droits des répertoires de l'application..."
chmod -R 777 app/logs app/cache
php app/console cache:clear --env=prod
chmod -R 777 app/logs app/cache

