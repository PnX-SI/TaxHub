# Stockage des médias avec S3

Les médias associés aux taxons sont stockés par défaut sur le serveur
où TaxHub est installé (paramètre `MEDIA_FOLDER`).

Mais il est aussi possible d'externaliser le stockage des médias sur un serveur S3 en le
\"montant\" dans le système de fichiers, en utilisant notamment le paquet
[s3fs](https://manpages.debian.org/stretch/s3fs/s3fs.1).

#### Droits d'accès avec s3fs

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

#### Procédure de montage s3fs

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

De nombreuses autres options peuvent vous servir en fonction de vos besoins :
mise en place d'un système de cache, redirection des logs...
N'hésitez pas à aller faire un tour sur la doc officielle (lien ci-dessus)
pour voir ce qui pourrait vous être utile.

#### Vérification de s3fs

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
Vous pouvez tester le volume en copiant un fichier du serveur vers le S3,
puis du S3 vers le serveur.

La commande `ls -h ` `doit alors vous afficher les droits suivants :
* `drwxr-x---` pour le dossier `<LOCAL_FOLDER>` où est monté le S3
* `-rw-r-----` pour les fichiers qui y sont contenus

Soit :
* Accès en lecture et écriture (`rw(x)`) pour le propriétaire `geonatureadmin` (donc TaxHub)
* Accès en lecture seule (`r-(x)`) pour le groupe `www-data` (donc apache)
* Aucun accès (`---`) pour tout autre utilisateur

Ce qui correspond à ce qu'on souhaite. =)
