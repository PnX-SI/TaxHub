# flaskmodule-UserHub-auth

Module flask permettant de gérer l'authentification suivant le modèle UserHub.

Prévu pour être utilisé comme un submodule git


## Routes : 

* login : 
  * parametres : login, password, id_application
  * return : token
  

## Fonction de décoration : 
* check_auth 
  * parametres : level = niveau de droit
  * utilise le token passé en cookie de la requête

## Exemple d'usage

```
  #Import de la librairie
  fnauth = importlib.import_module("apptax.flaskmodule-UserHub-auth.routes")
  
  #Ajout d'un test d'authentification avec niveau de droit
  @adresses.route('/', methods=['POST', 'PUT'])
  @fnauth.check_auth(4)
  def insertUpdate_bibtaxons(id_taxon=None):
    ...
```
