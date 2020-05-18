MANUEL UTILISATEUR
==================

Par @DonovanMaillard

Généralités : gérer la taxonomie avec TaxHub
--------------------------------------------

L'application TaxHub permet de gérer les informations liées à la taxonomie dans votre instance de GeoNature : espèces saisissables sur le module Occtax de GeoNature, informations diverses sur les espèces, enrichissement des fiches espèces de GeoNature-Atlas, regroupement des taxons en listes personnalisées etc. 

3 onglets principaux structurent l'application : 

- TAXREF : Dans cet onglet, tout utilisateur connecté ou non peut explorer le référentiel taxonomique. Un utilisateur disposant des droits suffisants pourra également ajouter un taxon à son instance depuis cet onglet.

- TAXONS : Cet onglet permet d'explorer l'ensemble des taxons disponibles dans votre propre instance de GeoNature et de consulter leurs informations (attributs, médias, listes etc)

- LISTES : Cet onglet recense les listes disponibles et permet d'en créer des nouvelles, de les peupler, les modifier et les exporter. 


Exploration du Taxref
---------------------

Dans l'onglet Taxref, vous pouvez explorer le référentiel national complet. Vous pouvez ainsi requêter selon différents champs, afficher ou masquer les colonnes qui vous intéressent et filtrer les résultats sur ces différentes colonnes, ou encore consulter les fiches espèces sur le site de l'INPN. Pour ces fonctions, il n'est pas nécessaire d'être connecté. 

.. image :: http://geonature.fr/docs/img/taxhub/2018-10-exploration_taxref.gif

Cet onglet ne comporte donc aucune information propre à votre instance, et ne fait que lire le référentiel taxonomique national tel qu'il est diffusé par le Muséum National d'Histoire Naturelle. 


Ajouter une espèce à la liste de ses taxons
-------------------------------------------

Les outils GeoNature s'appuient sur le référentiel taxonomique national TAXREF. Cependant pour davantage d'efficacité, les outils n'intègrent pas d'office tout le référentiel, mais comportent seulement un "extrait" géré par l'administrateur de l'instance (extrait visible dans l'onglet "Taxons"). Cela permet également à l'administrateur de GeoNature d'ajouter des informations qu'il souhaite attribuer à chacun des taxons.

Pour ajouter une espèce à la liste des taxons disponibles dans votre instance, vous devez vous connecter avec les droits nécessaires et rechercher l'entité que vous souhaitez dans l'onglet Taxref. Vous devez ensuite l'ajouter à vos taxons (bouton +). 

Vous serez alors invité à renseigner ses informations qui sont propre à votre contexte : attributs, listes auxquelles appartient l'espèce, médias. Ces informations sont consultables et modifiables par la suite.

.. image :: http://geonature.fr/docs/img/taxhub/2018-10-ajout_taxon.gif

Le taxon ainsi ajouté sera désormais visible, avec les informations que vous lui avez attribuées, dans l'onlet "taxons" de votre taxhub. 


Mettre à jour les informations d'un taxon
-----------------------------------------

L'une des raisons qui a poussé à utiliser les "taxons" et ne pas s'appuyer directement sur le Taxref est de pouvoir "surcoucher" le référentiel national avec des informations taxonomiques propres aux contextes des différents utilisateurs, et propres à leurs besoins respectifs. 

Ainsi, les taxons peuvent se voir attribuer un certain nombre d'informations, nommées "attributs", et être classés dans des listes personnalisées, sans lien obligatoire avec la taxonomie.  

Afin d'attribuer des informations à un taxon, celui-ci doit être ajouté à la liste des "taxons" de votre instance, comme expliqué précédemment. Vous pourrez alors l'éditer (bouton "crayon" depuis l'onglet Taxons ou directement depuis l'onglet Taxref), et renseigner les différents attributs qui concernent l'espèce. 

De la même manière, vous pourrez intégrer ce taxon à des "listes" personnalisées. Un taxon peut appartenir à plusieurs listes. 
Enfin, vous pourrez associer un ou plusieurs médias à un taxon. Ces médias peuvent être des images, des vidéos, des enregistrements sonores, des fichiers pdf etc.

.. image :: http://pole-invertebres.fr/wp-content/uploads/GIF_Taxhub/Edition_taxon.gif


Créer et gérer des listes personnalisées
----------------------------------------

TaxHub permet d'organiser les taxons au sein de listes personnalisées. Ces listes peuvent répondre à tous types de besoins : espèces invasives, espèces ciblées par un programme d'étude, espèces saisissables dans un module, espèces jugées douteuses dans la base de données de votre organisme etc. Seules les taxons ajoutés à votre instance (donc disponibles dans l'onglet "taxons") peuvent être ajoutées à des listes.

Pour consulter les listes existantes, vous devez aller dans l'onglet "listes". Vous y verrez et pourrez explorer les listes disponibles (bouton "oeil"), ainsi que les exporter au format csv. 

Avec les droits nécessaires, vous pourrez éditer les informations relatives à vos listes. Vous pourrez également associer à la liste en question de nouvelles entités parmi les taxons de votre instance (bouton "peupler"). 

Enfin, vous pouvez créer de nouvelles listes en renseignant les informations relatives à celles-ci (id, nom, description, éventuellement règne ou Groupe2 INPN associé, ainsi qu'un éventuel pictogramme). Dans ce cas, seules des espèces du règne ou du groupe pourront peupler la liste en question. Ces restrictions évitent, par exemple, de peupler une liste 'insectes pollinisateurs' avec des taxons qui autres que des insectes.

.. image :: http://pole-invertebres.fr/wp-content/uploads/GIF_Taxhub/Gestion_listes.gif

Une fois la liste créée, vous pourrez la peupler ou l'exporter comme vu précédemment.


Créer et gérer des thèmes et attributs personnalisés
----------------------------------------------------

Afin de mieux répondre à vos besoins et attacher les informations dont vous avez besoin à vos taxons, il est possible de créer de nouveaux attributs et de les organiser en "thèmes". Ces attributs peuvent être organisés en plusieurs thèmes, qu'il est possible d'ordonner.  

Par défaut, 4 attributs dans un thème unique (atlas) existent. 

.. image :: http://pole-invertebres.fr/wp-content/uploads/GIF_Taxhub/Screenshot_attributs.png

Dans notre exemple, un thème est déjà ajouté avec un attribut pour les listes rouges. Un nouveau sera créé pour intégrer une notion d'actions :

.. image :: http://pole-invertebres.fr/wp-content/uploads/GIF_Taxhub/Ajout_attribut_1.gif

Afin d'ajouter et ordonner des thèmes, il faut créer une nouvelle entrée dans la table ``bib_themes`` du schéma ``taxonomie``. En créant cette entité, un rang peut être donné au nouveau thème afin de les ordonner dans l'interface.

De la même manière, pour créer un attribut, il faut créer une nouvelle entrée dans la table ``bib_attributs``, également dans le schéma ``taxonomie``. Il est alors possible de définir ses modalités possibles (type et valeurs), de l'ordonner et de lui attribuer un thème. Comme pour les listes, les attributs peuvent ou non être limités à un règne ou à un groupe 2 INPN. 

.. image :: http://pole-invertebres.fr/wp-content/uploads/GIF_Taxhub/Ajout_attribut_2.gif

Votre application TaxHub est désormais dotée de nouveaux attributs !

.. image :: http://pole-invertebres.fr/wp-content/uploads/GIF_Taxhub/Ajout_attribut_3.png


Gérer le contenu de GeoNature-atlas
-----------------------------------

Les informations "statiques" diffusées sur les fiches espèces sont les suivantes : 

- Les photos (une photo principale, et des photos)
- Les autres médias : enregistrements sonores, fichiers pdf, vidéos etc
- Les champs description, commentaires, les milieux et la chorologie.

L'ensemble de ces informations sont rattachées à un taxon sous forme de médias et d'attributs. Les informations des fiches espèces sont donc enrichies en éditant les attributs du thème "atlas", et les médias d'un taxon (voir partie : mettre à jour les informations d'un taxon).
