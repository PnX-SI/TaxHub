app.controller('bibListeCreateCtrl',[ '$scope','$filter', '$http','$uibModal','$route','$routeParams','NgTableParams','toaster', 'backendCfg','loginSrv',
  function($scope,$filter, $http,$uibModal,$route, $routeParams,NgTableParams,toaster,backendCfg,loginSrv) {
    var self = this;
    self.route='listes';
    self.showSpinner = true;
    self.formCreate = {
        "id_liste" : "",
        "nom_liste" : "",
        "des_liste" : "",
        "picto" : "nopicto.gif",
        "regne" : "",
        "group2_inpn" : "Autres"
    };
    
    //----------------------Gestion des droits---------------//
    if (loginSrv.getCurrentUser()) {
        self.userRightLevel = loginSrv.getCurrentUser().id_droit_max;
        // gestion de l'onglet actif ; 0 par default
        if (self.userRightLevel==backendCfg.user_low_privilege) {
        self.activeForm = 2;
        }
    }
    self.userRights = loginSrv.getCurrentUserRights();


//----------------------- Get list of id_liste-------------------------------------------
    $http.get(backendCfg.api_url+"biblistes/id_liste").then(function(response) {
        self.create_id_liste = response.data;
    });
//----------------------- Get list of nom_liste-------------------------------------------
    $http.get(backendCfg.api_url+"biblistes/nom_liste").then(function(response) {
        self.create_nom_liste = response.data;
    });
//-----------------------Get list of regne-----------------------------------------------
    $http.get(backendCfg.api_url+"biblistes/taxref/regne").then(function(response) {
        self.create_regne = response.data;
    });
 //-----------------------Get list of group2_inpn-----------------------------------------
    $http.get(backendCfg.api_url+"biblistes/taxref/group2_inpn").then(function(response) {
        self.create_group2_inpn = response.data;
    });
//-----------------------Get list of picto  in database biblistes -------------------------
    $http.get(backendCfg.api_url+"biblistes/picto_biblistes").then(function(response) {
        self.create_picto_db = response.data;
    });
//-----------------------Get list of picto in dossier ./static/images/pictos --------------
    $http.get(backendCfg.api_url+"biblistes/picto_projet").then(function(response) {
        self.create_picto_projet = response.data;
        //----- stop spinner ------
        self.showSpinner = false;
    });


    var toasterMsg = {
        'saveSuccess':{"title":"Taxon enregistré", "msg": "Le taxon a été enregistré avec succès"},
        'submitError_nom_liste':{"title":"Nom de la liste existe déjà"},
        'submitError_id_liste':{"title":"Id de la liste existe déjà"},
        'submitInfo_nothing_change':{"title":"L'Information de la liste ne change pas"},
        'saveError':{"title":"Erreur d'enregistrement"},
    }

    self.submit = function() {
        var flow = true;

        //-- traiter id_liste, si il existe déjà, ne faire pas submit
        for(i = 0; i < self.create_id_liste.length; i++)
            if(self.create_id_liste[i] == self.formCreate.id_liste){
                toaster.pop('error', toasterMsg.submitError_id_liste.title,"", 5000, 'trustedHtml');
                flow = false;
                break;
            }

    }

}]);