#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
echo $DIR
cd $DIR

echo "run composer install"
composer install

echo "Configuration des droits des répertoires de l'application..."
chmod -R 777 app/logs app/cache
php app/console cache:clear --env=prod
chmod -R 777 app/logs app/cache

