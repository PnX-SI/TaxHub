=============
DEVELOPPEMENT
=============

Cette rubrique est destinée aux développeurs qui souhaiteraient...


Routes Symfony
--------------

Pour avoir toutes les routes à jour, il suffit dans symfony de lancer la commande
::

    php app/console router:debug

Aujourd'hui les différentes routes générées par symfony sont

Taxref
======

* /taxref/[?[limit=nb]&[page=nb]&[is_ref=boolean]&[is_inbibtaxons=boolean]&[nomColonne=ValeurFiltre]*&[ilike=debutChaine]]
    * Retourne les données de la table taxonomie.taxref ainsi que le id_taxon pour les taxons présents dans bib_taxons
    * Méthode autorisée : GET
    * Paramètres autorisés : 
        * limit (defaut = 50) : nombre d'élément à retourner
        * page (defaut = 0) : page à retourner
        * is_ref (default = false): ne retourne que les nom valides (cd_nom = cd_ref) 
        * bibtaxonsonly (default = false): ne retourne que les taxons présents dans bib_taxref (cd_nom = cd_ref)
        * [nomColonne=ValeurFiltre]* = Permet de filtrer les données sur un ou plusieurs critères. Le nom du paramètre (nom_colonne) doit correspondre a un nom de champs de la table taxref au format camel case.
        * [ilike=debutChaine] = Ne revoie les données de la colonne lbNom qui commence par debutChaine
        
* /taxref/{id}
    * Retourne un enregistrement de la table taxonomie.taxref
    * Méthode autorisée : GET
    * Paramètre: l'id de l'enregistrement correspond au cd_nom du taxref
    
* /taxref/distinct/{field}[?[nomColonne=ValeurFiltre]*&[ilike=debutChaine]]
    * Retourne un distinct de la table taxonomie.taxref sur un champ spécifié
    * Méthode autorisée : GET
    * Paramètre obligatoire : le champ du distinct (n'importe quel champ de la table taxref)
    * Paramètres facultatifs : 
        * [nomColonne=ValeurFiltre]* = Permet de filtrer les données sur un ou plusieurs critères. Le nom du paramètre (nom_colonne) doit correspondre a un nom de champs de la table taxref au format camel case.
        * [ilike=debutChaine] = Ne revoie les données de la colonne recherchée qui commence par debutChaine
    * Exemples
        - /taxref/distinct/phylum : retourne tous les phylum de la table
        - /taxref/distinct/famille?regne=Plantae&ordre=Rosales : retourne les familles du regne Plantae et de l'ordre Rosales

* /taxref/bibtaxons/[?[limit=nb]&[page=nb]&[is_ref=boolean]&[nomColonne=ValeurFiltre]*&[ilike=debutChaine]]
    * Retourne toutes les données de la table taxonomie.taxref uniquement pour les taxons présents dans bib_taxons
    * Méthode autorisée : GET
    * Paramètres autorisés : 
        * limit (defaut = 50) : nombre d 'élément à retourner
        * page (defaut = 0) : page à retourner
        * is_ref (default = false): ne retourne que les nom valides (cd_nom = cd_ref)
        * [nomColonne=ValeurFiltre]* = Permet de filtrer les données sur un ou plusieurs critères. Le nom du paramètre (nom_colonne) doit correspondre a un nom de champs de la table taxref au format camel case.
        * [ilike=debutChaine] = Ne revoie les données de la colonne lbNom qui commence par debutChaine
              
* /taxref/hierarchie/{rang}[?[limit=nb]&[nomColonne=ValeurFiltre]*&[ilike=debutChaine]]
    * Selection des niveaux hiérarchiques de taxref avec le nombre de taxons associés aux différents rangs
    * Méthode autorisée : GET
    * Paramètre obligatoire : le nom du rang désiré
    * Paramètres facultatifs : 
        * limit (defaut = 10) : nombre d'élément à retourner
        * [nomColonne=ValeurFiltre]* = Permet de filtrer les données sur un ou plusieurs critères. Le nom du paramètre (nom_colonne) doit correspondre a un nom de champs de la table taxref au format camel case.
        * [ilike=debutChaine] = Ne revoie les taxons du rang recherché qui commence par debutChaine
    * Exemples
        - /hierarchie/FM?ordre=Chiroptera&limit=1000&regne=Animalia&ilike=m : retourne la liste des familles des chiroptères qui commencent par un m
        
* /taxref/hierarchiebibtaxons/{rang}[?[limit=nb]&[nomColonne=ValeurFiltre]*&[ilike=debutChaine]]
    * Selection des niveaux hiérarchiques de taxref pour les taxons présents dans bib_taxons avec le nombre de taxons associés aux différents rangs
    * Méthode autorisée : GET
    * Paramètre obligatoire : le nom du rang désiré
    * Paramètres facultatifs : 
        * limit (defaut = 10) : nombre d'élément à retourner
        * [nomColonne=ValeurFiltre]* = Permet de filtrer les données sur un ou plusieurs critères. Le nom du paramètre (nom_colonne) doit correspondre a un nom de champs de la table taxref au format camel case.
        * [ilike=debutChaine] = Ne revoie les taxons du rang recherché qui commence par debutChaine
    * Exemples
        - /hierarchie/FM?ordre=Chiroptera&limit=1000&regne=Animalia&ilike=m : retourne la liste des familles des chiroptères qui commencent par un m

Bibtaxons
=========

* /bibtaxons/[?[limit=nb]&[page=nb]&[nomColonne=ValeurFiltre]&[ilikefr=debutChaine]&[ilikelatin=debutChaine]]
    * Retourne les données de la table taxonomie.bib_taxons
    * Méthode autorisée : GET
    * Paramètres autorisés :
        * limit (defaut = 50) : nombre d'élément à retourner
        * page (defaut = 0) : page à retourner
        * [nomColonne=ValeurFiltre]* = Permet de filtrer les données sur un ou plusieurs critères. Le nom du paramètre (nom_colonne) doit correspondre a un nom de champs de la table bib_taxons ou de la table taxref au format camel case.
        * [ilikelfr=debutChaine] = Ne revoie les données de la colonne nomFrancais qui commence par debutChaine
        * [ilikelatin=debutChaine] = Ne revoie les données de la colonne nomLatin qui commence par debutChaine
    
* /bibtaxons/taxonomie
    * Retourne cd_nom, cd_taxsup, lb_nom et id_rang pour les familles, ordre, classe, phylum et regne des enregistrements de la table taxonomie.bibtaxons
    * Méthode autorisée : GET
    
* /bibtaxons/{id}
    * Retourne un enregistrement de la table taxonomie.bib_taxons
    * Méthode autorisée : GET
    * Paramètre: l'id de l'enregistrement
    
* /bibtaxons/{id} 
    * Création ou mise à jour d'un enregistrement dans la table taxonomie.bib_taxons
    * Méthode autorisée : POST|PUT
    * Paramètre: l'id de l'enregistrement (si update) ou rien (si create)
    
* /bibtaxons/{id} 
    * SUppression d'un enregistrement dans la table taxonomie.bib_taxons
    * Méthode autorisée : DELETE
    * Paramètre: l'id de l'enregistrement à supprimer
    
Biblistes
=========
* /biblistes/[{id}]
    * Selection des données relatives à la ou aux listes avec les taxons associés
    * Méthode autorisée : GET
    * Paramètres facultatifs : 
        * id : identifiant de la liste
        
* /biblistes/simpleliste
    * Selection des données contenues uniquement dans la table biblistes
    * Méthode autorisée : GET
    
* /biblistes/taxonliste/{id}
    * Selection des taxons associés à la liste demandée
    * Méthode autorisée : GET
    * Paramètre obligatoire : 
        * id : identifiant de la liste

Bibattributs
==========
* /bibattributs/
    * Retourne toutes les données de la table taxonomie.bib_attributs
    * Méthode autorisée : GET
    
* /bibattributs/{id}
    * Retourne un enregistrement de la table taxonomie.bib_attributs
    * Méthode autorisée : GET
    * Paramètre:
        id : id de l'enregistrement
    
* /taxonsattribut/{id}/{value}
    * Retourne tous les taxons ayant l'attribut passé en paramètre ainsi que le nom et la valeur de l'attribut.
    * il est possible de filtrer sur la valeur de l'attribut.
    * Méthode autorisée : GET
    * Paramètre: 
        id  : id de l'attribut, obligatoire
        value : valeur de l'attribut, facultatif

* /taxonsattribut/{regne}/{group2inpn}
    * Retourne les attributs correspondant au(x) filtre(s) taxonomique(s) passé(s) en paramètre. 
    * En base, si un attribut n'a pas de regne renseigné, c'est qu'il conserne tous les règnes. L'attribut est toujours retourné quelques soient les paramètres transmis.
    * En base, si un attribut n'a pas de group2inpn renseigné mais un regne renseigné, c'est qu'il conserne tous les group2inpn ; il est donc retrourné. Soit uniquement pour le regne transmis en paramètre soit pour tous les règnes si aucun regne valide n'est transmis.
    * En base, si un attribut n'a pas de regne mais group2inpn renseigné, c'est une erreur (un group2inpn correspond forcement à un regne). L'attribut est donc toujours retourné quelque soit les paramètres transmis.
    * Méthode autorisée : GET
    * Paramètre: 
        regne : facultatif
        group2inpn : facultatif. Ne peut être utilisé si ``regne`` n'est pas fourni.


Bla bla bla
-----------

The most minimal components required to run an instance are :

* PostGIS 2 server
* GDAL, GEOS, libproj
* gettext
* libfreetype
* libxml2, libxslt
* Usual Python dev stuff

A voir : `the list of minimal packages on Debian/Ubuntu <https://github.com/makinacorpus/Geotrek/blob/211cd/install.sh#L136-L148>`_.

.. note::

    En lancant ``env_dev`` et ``update`` is recommended after a pull of new source code,
    but is not mandatory : ``make serve`` is enough most of the time.
