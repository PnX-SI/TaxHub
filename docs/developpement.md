# API

## Taxref

-  `/taxref/` : Retourne les données de la table `taxonomie.taxref`
    -   Méthode autorisée : GET
    -   Paramètres autorisés :
        - limit (defaut = 50) : nombre d'éléments à retourner
        - page (defaut = 0) : page à retourner
        - is_ref (default = false) : ne retourne que les noms valides (cd_nom = cd_ref)
        - id_liste : liste d'identifiant des listes
        - cd_nom : liste de cd_nom
        - fields (permet de spécifier les champs renvoyés). Permet aussi de récupérer les données secondaires
        non renvoyées par défaut, en les spécifiant explicitement (`fields=status,rang,medias,attributs,synonymes,listes`)
        - nomColonne : Permet de filtrer
        les données sur un ou plusieurs critères. Le nom du
        paramètre (nom_colonne) doit correspondre à un nom
        de champs de la table taxref au format camel case.
        - ilike-nom_colonne_taxref : Ne renvoie que les données de la
        colonne demandée commençant par le texte fourni
        - orderby (default = cd_nom:ASC) : ordonne les données en fonction de la
        colonne demandée. Par défaut l'ordre de tri est ascendant. Il est possible de spécifier si l'on souhaite un tri descendant. 
        Syntaxe : nom_colonne[:ASC|:DESC].

- `/taxref/{cd_nom}`: Retourne un enregistrement de la table `taxonomie.taxref` avec les synonymes et statuts associés
    - Méthode autorisée : GET

- `/taxref/{cd_nom}/parents`: Retourne les parents de l'enregistrement référencé par le cd_nom. Les parents sont triées du plus lointain au plus proche. Cette entrée s'appuit sur la vue matérialisée `taxonomie.vm_taxreftree`
  - Méthode autorisée : GET
  - Paramètres autorisés :
    - linnaean (defaut = False) : Retourne uniquement les parents linnéens.

- `/taxref/allnamebylist/<int(signed=True):id_liste>` : Retourne les données de la vue matérialisée `vm_taxreflist_for_autocomplete`
    - Paramètres :
        - id_liste : identifiant de la liste (si id_liste est null ou égal à -1 on ne filtre pas sur une liste)
    params GET (facultatifs):
        - code_liste : code de la liste à filtrer, n'est pris en compte que si aucune liste n'est spécifiée
        - search_name : nom recherché. Recherche basée sur la fonction ilike de SQL avec un remplacement des espaces par %
        - regne : filtre sur le règne
        - group2_inpn : filtre sur le groupe 2 INPN
        - limit : nombre de résultats
        - offset : numéro de la page

- `/taxref/bib_habitats` : Retourne la liste des habitats définis dans Taxref
- `/taxref/groupe3_inpn` : Retourne la liste des groupes 3 définis dans Taxref
- `/taxref/regnewithgroupe2` : Retourne une liste hiérarchisée des règnes avec les groupes 2 associés

## Biblistes

- `/biblistes` : retourne le contenu de bib_liste (liste des listes)
- `/biblistes/<regne>` : retourne les listes filtrées par règne
- `/biblistes/<regne>/<group2_inpn>` : retourne les listes filtrées par groupe 2 INPN

## BDC statuts

- `/bdc_statuts/list/<int(signed=True):cd_ref>` : Retourne la liste des statuts associés à un taxon.
- `/bdc_statuts/hierarchy/<int(signed=True):cd_ref>` : Retourne la liste des statuts associés sous forme hiérarchique.
- `/bdc_statuts/status_values/<status_type>` : Retourne les valeurs (code et intitulé) d'un type de statut.
- `/bdc_statuts/status_types` : Retourne les types (code et intitulé) avec leur regroupement.
    - Params :
        -   codes : filtre sur une liste de codes de types de statuts séparés par des virgules.
        -   gatherings : filtre sur une liste de type de regroupement de types de statuts séparés par des virgules.
- `/bdc_statuts/status_symbologies` : Retourne les symbologies associées au statuts au format JSON.  
  Ces symbologies sont définies statiquement, au format suivant :

  ```json
  {
    "symbologies": [
        {
            "types": ["LRM", "LRE", "LRN", "LRR"],
            "values": {
                "EX": {"color": "#000000"},
                "EW": {"color": "#3d1951"},
                "RE": {"color": "#5a1a63"},
                "CR": {"color": "#d3001b"},
                "EN": {"color": "#fbbf00"},
                "VU": {"color": "#ffed00"},
                "NT": {"color": "#fbf2ca"},
                "LC": {"color": "#78b74a"},
                "DD": {"color": "#d3d4d5"},
                "NA": {"color": "#919291"},
                "NE": {"color": "#ffffff"},
            },
        }
    ]
  }
  ```

  > Ces valeurs sont issues de la charte des codes couleurs pour les statuts Liste rouge, définis internationalement par l'Union internationale pour la conservation de la nature (UICN) \
  > <https://uicn.fr/wp-content/uploads/2018/04/guide-pratique-listes-rouges-regionales-especes-menacees.pdf> (page 55)

## Médias

- `/tmedias/thumbnail/<int:id_media>` : Retourne un média redimensionné aux dimensions spécifiées (vignette)
  - Params :
    - id_media : identifiant du média
    - h (defaut = 300) : hauteur souhaitée
    - w (defaut = 400) : largeur souhaitée
    - regenerate : force la régénération du fichier thumbnail
- `/tmedias/types` : Retourne la liste des types de médias
- `/tmedias/types/<int:id>` : Retourne le détail d'un type de média
- `/tmedias/` : Retourne la liste de tous les médias de TaxHub
  - Attention route non paginée et sans filtre, donc peut crasher si il y a beaucoup de médias
- `/tmedias/<int:id>` : Retourne le détail d'un média
- `/tmedias/bycdref/<cd_ref>` : Retourne la liste des médias associés à un taxon
