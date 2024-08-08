# MANUEL UTILISATEUR

## Généralités : gérer la taxonomie avec TaxHub

L'application TaxHub permet de gérer les informations liées à la
taxonomie dans votre instance de GeoNature : espèces saisissables sur le
module Occtax de GeoNature, informations diverses sur les espèces,
enrichissement des fiches espèces de GeoNature-atlas, regroupement des
taxons en listes personnalisées etc.

3 onglets principaux structurent l'application :

-   **TAXREF** : Dans cet onglet, tout utilisateur connecté ou non peut
    explorer le référentiel taxonomique. Un utilisateur disposant des
    permissions suffisantss pourra également ajouter des attributs ou médias à un taxon. 
-   **LISTES** : Cet onglet recense les listes disponibles et permet d'en
    créer des nouvelles, de les peupler, les modifier et les exporter.
-   **ATTRIBUTS** : Cet onglet recense les attributs disponibles et permet d'en
    créer de nouveaux.

## Exploration du Taxref

Dans l'onglet Taxref, vous pouvez explorer le référentiel national
complet. Vous pouvez ainsi requêter selon différents champs et filtrer les résultats sur
ces différentes colonnes, ou encore consulter les fiches espèces sur le
site de l'INPN. Pour ces fonctions, il n'est pas nécessaire d'être
connecté.

![image](images/explore_taxref.gif)

Cet onglet permet d'explorer le référentiel taxonomique national et de consultrer pour chaque taxon les attributs et médias de votre instance.

![image](images/detail_taxon.gif)


## Mettre à jour les informations d'un taxon

Ainsi, les taxons peuvent se voir attribuer un certain nombre
d'informations, nommées "attributs", et être classés dans des listes
personnalisées.

Afin d'attribuer des informations à un taxon, il faut l'éditer (bouton "crayon" 
depuis l'onglet Taxref), et renseigner
les différents attributs qui concernent l'espèce.

De la même manière, vous pourrez intégrer ce taxon à des "listes"
personnalisées. Un taxon peut appartenir à plusieurs listes. Enfin, vous
pourrez associer un ou plusieurs médias à un taxon. Ces médias peuvent
être des images, des vidéos, des enregistrements sonores, des fichiers
PDF etc.


## Créer et gérer des listes personnalisées

TaxHub permet d'organiser les taxons au sein de listes personnalisées.
Ces listes peuvent répondre à tous types de besoins : espèces invasives,
espèces ciblées par un programme d'étude, espèces saisissables dans un
module, espèces jugées douteuses dans la base de données de votre
organisme etc.

Pour consulter les listes existantes, vous devez aller dans l'onglet
"listes". Vous y verrez et pourrez explorer les listes disponibles
(bouton "oeil"), ainsi que les exporter au format csv.

Avec les droits nécessaires, vous pourrez éditer les informations
relatives à vos listes. Vous pourrez également associer à la liste en
question de nouvelles entités parmi les taxons de votre instance depuis un fichier CSV de cd_nom (bouton
"peupler").

Enfin, vous pouvez créer de nouvelles listes en renseignant les
informations relatives à celles-ci (nom, description, éventuellement
règne ou Groupe 2 INPN associé). Dans
ce cas, seules des taxons du règne ou du groupe pourront peupler la
liste en question. Ces restrictions évitent, par exemple, de peupler une
liste 'insectes pollinisateurs' avec des taxons qui autres que des
insectes.

Une fois la liste créée, vous pourrez la peupler ou l'exporter comme vu
précédemment.

![image](images/create_use_lists.gif)

## Créer et gérer des thèmes et attributs personnalisés

Afin de mieux répondre à vos besoins et attacher les informations dont
vous avez besoin à vos taxons, il est possible de créer de nouveaux
attributs et de les organiser en "thèmes". Ces attributs peuvent être
organisés en plusieurs thèmes, qu'il est possible d'ordonner.

Par défaut, 4 attributs dans un thème unique (atlas) existent.

Dans notre exemple, un thème est déjà ajouté avec un attribut pour les
listes rouges. Un nouveau sera créé pour intégrer une notion d'actions
:

Afin d'ajouter et ordonner des thèmes, il faut créer une nouvelle
entrée dans l'onglet "Thème". En créant cette
entité, un ordre peut être donné au nouveau thème afin de les ordonner
dans l'interface.

![image](images/create_theme.gif)

De la même manière, pour créer un attribut, il faut créer une nouvelle
entrée dans l'onglet "Attribut"`. Il est alors possible de définir ses modalités possibles
(type et valeurs), de l'ordonner et de lui attribuer un thème. Comme
pour les listes, les attributs peuvent ou non être limités à un règne ou
à un groupe 2 INPN.

Votre application TaxHub est désormais dotée de nouveaux attributs !

![image](images/create_attribut.gif)


## Gérer le contenu de GeoNature-atlas

Les informations "statiques" diffusées sur les fiches espèces sont les
suivantes :

-   Les photos (une photo principale, et des photos)
-   Les autres médias : enregistrements sonores, fichiers pdf, vidéos
    etc
-   Les champs description, commentaires, les milieux et la chorologie.

L'ensemble de ces informations sont rattachées à un taxon sous forme de
médias et d'attributs. Les informations des fiches espèces sont donc
enrichies en éditant les attributs du thème "atlas", et les médias
d'un taxon (voir partie : mettre à jour les informations d'un taxon).
