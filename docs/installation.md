# INSTALLATION

Cette documentation décrit l'installation indépendante (standalone) de TaxHub. 
Si vous utilisez GeoNature, TaxHub y est intégré et il n'est alors pas nécessaire d'installer 
TaxHub indépendamment.

## Prérequis

Pour installer TaxHub, il vous faut un serveur avec Debian 11 ou 12.
L'utilisation de TaxHub avec une autre distribution est théoriquement
possible, mais n'est pas officiellement supporté.

## Création d'un utilisateur

Vous devez disposer d'un utilisateur Linux pour faire tourner TaxHub
(nommé `synthese` dans notre exemple). L'utilisateur doit appartenir aux
groupes `sudo` et `www-data`. Le répertoire de cet utilisateur
`synthese` doit être dans `/home/synthese`. Si vous souhaitez utiliser
un autre utilisateur Linux, vous devrez adapter les lignes de commande
proposées dans cette documentation.

```sh
adduser --home /home/synthese synthese
adduser synthese sudo
adduser synthese www-data
```

>**_NOTE:_** 
> Pour la suite de l'installation, veuillez utiliser l'utilisateur
> Linux créé précedemment (`synthese` dans l'exemple), et non
> l'utilisateur `root`.

## Installation des dépendances requises

Installez les dépendances suivantes :

```sh
sudo apt install -y apache2 python3-pip python3-venv libpq-dev libgdal-dev sudo unzip
sudo apt install -y postgresql postgresql-postgis
```

## Configuration de PostgreSQL

Créer un utilisateur PostgreSQL :

```sh
sudo -u postgres createuser geonatadmin --pwpromt
```

## Récupération du code source de TaxHub

Récupérer le zip de l'application sur le [Github du projet](https://github.com/PnX-SI/TaxHub/releases) 
(X.Y.Z à remplacer par le numéro de version
souhaité), dézippez le dans
le répertoire `/home/synthese` :

```sh
cd /home/synthese
wget https://github.com/PnX-SI/TaxHub/archive/X.Y.Z.zip
unzip X.Y.Z.zip
mv TaxHub-X.Y.Z taxhub
rm X.Y.Z.zip
cd taxhub
```

## Configuration de l'installation

Créer et mettre à jour le fichier `settings.ini` :

```sh
cp settings.ini.sample settings.ini
nano settings.ini
```

ATTENTION : Les valeurs renseignées dans ce fichier sont utilisées par
le script d'installation de la base de données `install_db.sh` et par
le script `install_app.sh`.

Renseignez les informations nécessaires à la connexion à la base de
données PostgreSQL. Il est possible de laisser la plupart des valeurs
proposées par défaut, mais lisez au moins le fichier de bout en bout
pour savoir ce qu'il est possible de changer.

La valeur la plus importante à mettre à jour est `user_pg_pass=monpassachanger` 
(`monpassachanger` doit être remplacé par celui choisi lors de l'étape
de configuration de PostgreSQL).

### Stockage des médias

Les médias associés aux taxons peuvent être stockés sur le serveur
(paramètre `MEDIA_FOLDER`).

Il est possible d'utiliser le service de stockage S3 AWS en le
\"montant\" dans le système de fichier en utilisant notamment le paquet
[s3fs](https://manpages.debian.org/stretch/s3fs/s3fs.1).

#### Droits d'accès

> ⚠️ s3fs crée un "pont" entre le serveur où est installé TaxHub
et le serveur S3 où sont stockés vos médias. Il faut se montrer
particulièrement vigilant sur les droits d'accès aux fichiers, afin d'éviter
qu'un attaquant puisse accéder à votre S3 si votre serveur applicatif est compromis.

Pour que les médias soient accessibles et manipulables par l'application
(lecture, ajout, suppression...), il faut que l'utilisateur propriétaire
de l'application  ait accès aux fichiers en lecture et en écriture.

Pour que les images puissent être servies par apache via l'URL de l'API
(`<domaine>/api/media/...`), il faut que l'application apache,
identifiée comme l'utilisateur `www-data`, ait accès aux fichiers en lecture.

Toute autre permission est superflue et devrait donc être retirée.

Dans la proposition de procédure qui suit, on identifie le propriétaire
du volume comme l'utilisateur propriétaire de TaxHub (ici `geonatureadmin`),
et le groupe propriétaire comme l'utilisateur `www-data`.
On donne ensuite les permissions adaptées au propriétaire et au groupe,
puis on retire toute les permissions des autres utilisateurs.


#### Procédure de montage

> *Toutes les actions ci-dessous doivent être réalisées 
en étant connecté avec l'utilisateur propriétaire de TaxHub.*

s3fs utilise un "token" d'authentification pour se connecter au S3.
Vous pouvez en créer un par exemple avec [openstack](https://openmetal.io/docs/manuals/openstack-admin/access-swift-s3-api) :

```sh
source openrc.sh 

openstack ec2 credentials create
```

Notez les identifiants obtenus dans le fichier `/etc/passwd-s3fs`
(ou `~/.passwd-s3fs`, au choix) et attribuez des permissions
en lecture seule au propriétaire :

```sh
sudo vi /etc/passwd-s3fs

sudo chmod 600 /etc/passwd-s3fs
```

Montez le volume S3 :

```sh
s3fs <BUCKET_NAME> <LOCAL_FOLDER> \
  -o url="<BUCKET_URL>",endpoint=<ENDPOINT>,use_path_request_style \
  -o passwd_file=/etc/passwd-s3fs \
  -o gid=<GID>,allow_other,mp_umask=0027
```

Avec : 
* `<BUCKET_NAME>` : le nom du bucket où sont stockées les médias TaxHub sur le S3
* `<LOCAL_FOLDER>` : le dossier local où vous souhaitez monter votre volume S3,
  en l'occurrence, le dossier indiqué par le paramètre `MEDIA_FOLDER`
  dans la configuration de l'application.
* `<BUCKET_URL>` et `<ENDPOINT>` : informations de connexion à votre S3.
* `gid=<GID>`pour que les fichiers soient vus par le serveur comme appartenant
  au groupe www-data (on obtient `<GID>` l'id de ce goupe
  avec `getent group www-data` ou `grep www-data /etc/passwd`)
* `allow_other` pour que le volume soit accessible
  par les autres (par défaut il ne l'est que pour le propriétaire)
* `mp_umask=0027` pour restreindre l'accès en lecture seule pour le groupe
  (ici www-data) et pas d'accès du tout pour les autres

#### Vérification

> ⚠️ s3fs permet d'accéder au contenu du S3 via le système de gestion fichier
du serveur. Il n'est pas fait pour naviguer sur le S3 comme sur
n'importe quel autre volume. Chaque opération de manipulation de contenu,
y compris lister les fichiers, implique des appels à l'API swift
qui peuvent être coûteux. Il vaut mieux éviter d'ouvrir le volume
dans un explorateur de fichier graphique, et privilégier la ligne de commande.
Ciblez toujours un fichier précis plutôt que de lister le contenu des dossiers,
y compris avec l'autocomplétion !

Une fois monté dans le dossier de votre choix, les fichiers doivent apparaître dans votre
système de fichier comme s'ils étaient stockés en local sur votre serveur.
Vous pouvez tester le volume en copiant un fichier du serveur vers le s3,
puis du s3 vers le serveur.

La commande `ls -h ` `doit alors vous afficher les droits suivants :
* `drwxr-x---` pour le dossier `<LOCAL_FOLDER>` où est monté le S3
* `-rw-r-----` pour les fichiers qui y sont contenus

Soit :
* Accès en lecture et écriture (`rw(x)`) pour le propriétaire geonatureadmin (donc TaxHub)
* Accès en lecture seule (`r-(x)`) pour le groupe www-data (donc apache)
* Aucun accès (`---`) pour tout autre utilisateur

Ce qui correspond à ce qu'on souhaite =)


## Installation de l'application

Lancez le fichier d'installation et de configuration de l'application

```sh
./install_app.sh
```

## Création de la base de données

Lancer le fichier d'installation et de préparation de la base de
données :

```sh
cd ~/taxhub
./install_db.sh
```

Le script va ouvrir une nouvelle fois le fichier de configuration
`settings.ini` avec nano, pour vous donner une opportunité de revoir une
dernière fois ses paramètres. Vous pouvez sauvegarder le fichier tel
quel pour continuer (ctrl + x).

## Configuration de l'application

- La configuration de l'application est réalisée dans le fichier `config/taxhub_config.toml` (créé automatiquement lors de l'installation de TaxHub)
- La liste de tous paramètres et de leurs valeurs par défaut est disponible dans `config/taxhub_config.toml.default`
- Si vous modifiez le fichier de configuration de TaxHub (`config/taxhub_config.toml`), vous devez redémarrer l'application avec la commande `sudo systemctl restart taxhub`

## Arrêter/Lancer l'application

- Pour arrêter TaxHub
  ```sh
  sudo systemctl stop taxhub
  ```
- Pour démarrer TaxHub
  ```
  sudo supervisorctl start taxhub
  ```

## Configuration Apache

Voici une des manières de configurer Apache. Elle se base sur le fait
que la configuration `/etc/apache2/sites-available/000-default.conf`
existe par défaut et va automatiquement charger notre nouvelle entrée.

Le script d'installation de TaxHub crée automatiquement le ficher
`/etc/apache2/conf-available/taxhub.conf` (à partir du fichier `taxhub_apache.conf`) et l'active
(`a2enconf taxhub`). Ce fichier vous permet d'accéder à TaxHub via l'URL
<http://ADRESSE_DU_SERVEUR/taxhub/>.

## Mise à jour de l'application

Les différentes versions de TaxHub sont disponibles sur le Github du
projet (<https://github.com/PnX-SI/TaxHub/releases>)

- Lire attentivement les notes de chaque version si il y a des
  spécificités (<https://github.com/PnX-SI/TaxHub/releases>). Suivre
  ces instructions avant de continuer la mise à jour.

- Télécharger et extraire la version souhaitée dans un répertoire
  séparé (où `X.Y.Z` est à remplacer par le numéro de la version que
  vous installez) :
  ```sh
  cd
  wget https://github.com/PnX-SI/TaxHub/archive/X.Y.Z.zip
  unzip X.Y.Z.zip
  mv taxhub taxhub_old
  mv TaxHub-X.Y.Z/ taxhub
  rm X.Y.Z.zip
  ```

- Récupérer les anciens fichiers de configuration :
  ```sh
  cp taxhub_old/settings.ini taxhub/settings.ini
  cp taxhub_old/config/taxhub_config.toml taxhub_old/config/taxhub_config.toml 
  ```

- Récupérer les médias uploadés dans la précédente version de TaxHub (avant la version 2.0) :
  ```sh
  cp -aR taxhub_old/static/medias/ taxhub/static/
  ```

- Récupérer les médias uploadés dans la précédente version de TaxHub (après la version 2.0) :
  ```sh
  cp -aR taxhub_old/media taxhub
  ```
- Lancer l'installation de l'application et de ses dépendances :
  ```sh
  cd taxhub
  ./install_app.sh
  ```

- Mettre à jour le schéma de base de données en activant l'environnement virtuel :
  ```sh
  cd taxhub
  source venv/bin/activate
  flask db autoupgrade
  deactivate
  ```

- Une fois que l'installation est terminée et fonctionnelle, vous
  pouvez supprimer la version précédente de TaxHub (répertoire
  `taxhub_old`).

## Développement

Pour lancer l'application en mode debug :

```sh
cd ~/taxhub
source venv/bin/activate
flask run
```

TaxHub est alors accessible à l'adresse : `http://localhost:5000` (sans
`/taxhub`).
