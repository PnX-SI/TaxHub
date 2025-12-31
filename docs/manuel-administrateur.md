# MANUEL ADMINISTRATEUR

## Commandes

-   `flask taxref info` : Indique le nombre de taxons et de status
    contenus dans la base de données
-   `flask taxref link-bdc-statut-to-areas` : Permet d'associer les
    statuts aux départements contenus dans le Ref_geo
-   `flask taxref enable-bdc-statut-text -d <MON_DEP_1> -d <MON_DEP_2> --clean`
    : Permet d'activer les statuts par départements. Il est possible de
    spécifier plusieurs départements (par `code_area`).
-   `flask taxref delete` : Supprimer toutes les données Taxref.
-   `flask taxref delete-bdc`: Supprimer la base de connaissance des statuts.
-   `flask taxref import-bdc-v18` : Importer la base de connaissance des statuts (existe également pour les versions antérieures).
-   `flask taxref import-v18`: Importer Taxref et la base de connaissance des statuts (existe également pour les versions antérieures)
    - `--skip-bdc-statuts`: Ne pas importer la base de connaissance des statuts
    - `--taxref-region` : Pour prendre en compte la région Taxref (colonne "fr", "gf", "mar", "gua"... de Taxref) pour remplir la colonne `taxonomie.taxref.id_statut` ("fr" par défaut)
-   `flask taxref import-inpn-media list_cd_ref.csv` : Import des photos depuis l'API de l'INPN.
    Pour spécifier les taxons à traiter, la commande prend comme paramètre
    un fichier CSV contenant une liste de cd_nom.

> [!WARNING]
> L'api de l'inpn n'est plus disponible. Cette commande est temporairement inutilisable


-   `flask taxref import-wikidata-media list_cd_ref.csv` : Import des médias depuis l'API de wikidata.
    Pour spécifier les taxons à traiter la commande prend comme paramètre
    un fichier CSV contenant une liste de cd_nom

-   `flask taxref import-gbif-media list_cd_ref.csv` : Import des médias depuis l'API de gbif.
    Pour spécifier les taxons à traiter la commande prend comme paramètre
    un fichier CSV contenant une liste de cd_nom


|option              |commande       |Type|Défaut|Obligatoire|Description                                                                                         |
|--------------------|---------------|----|------|-----------|----------------------------------------------------------------------------------------------------|
|file                |inpn, gbif, wikidata|Path|      |Oui        |Chemin vers le fichier CSV contenant une colonne avec les cd_ref ou cd_nom.|
|--wd-media-prop     |wikidata       |str |P18   |           |Code de la propriété Wikidata a  utiliser : - P18 : image - P51 : son                               |
|--media-type-id     |gbif, wikidata |int |2     |           |Code du type de média dans TaxHub : - 2 : image - 5 : audio                                         |
|--nb-max            |gbif           |int |3     |           |Nombre maximal de média importé (sur 20 images récupérés)                                           |

Pour générer une liste de cd_nom, vous pouvez vous appuyer sur vos données d'observations. Par exemple, si vous utilisez GeoNature, vous pouvez générer une liste des cd_nom disposant d'au moins une observation avec la requête `SELECT DISTINCT cd_nom FROM gn_synthese.synthese`.

Si vous utilisez TaxHub intégré à GeoNature, `flask` est à remplacer par `geonature` dans toutes les commandes indiquées dans la documentation et à lancer depuis le "venv" de GeoNature.

## Mise à jour de Taxref

Un ensemble de commandes permettent de réaliser un changement de version
de Taxref.

La documentation détaillée est accessible ici :
<https://taxhub.readthedocs.io/fr/latest/update-taxref-version.html>

## Mise à jour de la BDC statuts

Les nouvelles versions de la base de connaissance des statuts sont fournies et mises à jour en même temps que chaque mise à jour de Taxref. Mais en cas de version intermédiaire de la BDC statuts, il est possible de la mettre à jour en procédant de la façon suivante :

```sh
# Suppression des données de la BDC statuts
flask taxref delete-bdc
# Import de la nouvelle version
flask taxref import-bdc-v18
# Optionnel : activation/désactivation des textes en fonction du contexte géographique
flask taxref enable-bdc-statut-text -d <MON_DEP_1> -d <MON_DEP_2> --clean
```

## Gestion des permissions

**Attention** :

Si vous avez installé TaxHub via GeoNature, les permissions ne sont pas
gérées de la même manière et sont uniquement pilotées par le module de
gestion des permissions de GeoNature (voir la documentation de GeoNature
à ce sujet).

Si vous avez installé TaxHub indépendamment (standalone),
la gestion des permissions de l'application TaxHub se fait via les
"profils" UsersHub :

-   Profils 2 : peut ajouter / modifier des médias et attributs sur les
    taxons. Peut ajouter / enlever des taxons dans des listes
-   Profil 6 = peut en plus administrer toutes les tables : création /
    modification / suppression de listes, d'attributs, et de thèmes

## Fonctions SQL

La base de données comprend plusieurs fonctions permettant d'utiliser
plus aisément le référentiel Taxref.

### Arbre taxonomique

-   `find_cdref(cd_nom int) --> int` : cd_ref d'un taxon
-   `find_cdref_sp(cd_nom int) --> int` : cd_nom de l'espèce de
    référence s'il s'agit d'une espèce ou d'un taxon
    infra-spécifique. Retourne `NULL` s'il s'agit d'un taxon
    supra-spécifique.
-   `find_all_taxons_children(cd_nom int) --> int[]` : Les cd_nom des
    taxons inférieurs au taxon en entrée.
-   `find_all_taxons_children(cd_nom int[]) --> table` : Les cd_nom des
    taxons inférieurs aux taxons en entrée.
-   `find_all_taxons_parents(cd_nom int) --> int[]` : Les cd_nom des
    taxons supérieurs au taxon en entrée, du plus bas vers le plus haut
    (domaine).
-   `find_all_taxons_parents_t(cd_nom int) --> table` : Les cd_nom des
    taxons supérieurs au taxon en entrée, du plus bas vers le plus haut
    (domaine). Sous forme de table avec le rang indiqué.
-   `find_lowest_common_ancestor(cd_nom1 int, cd_nom2 int) --> int` :
    cd_ref de l'ancêtre commun le plus récent à deux taxons.
-   `find_regne(cd_nom int) --> text` : Libellé du règne du taxon.
-   `check_is_cd_ref(mycdnom integer) --> boolean` : True si l'argument
    donné est un cd_ref existant
-   `match_binomial_taxref(mytaxonname character varying)` : Cd_nom ou
    Cd_ref correspondant au nom latin donné en argument (si un seul cd
    possible, sinon NULL)
