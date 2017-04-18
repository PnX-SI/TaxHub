app.controller('bibListeEditCtrl',[ '$scope','$filter', '$http','$uibModal','$routeParams','NgTableParams', 'backendCfg','loginSrv',
  function($scope,$filter, $http,$uibModal, $routeParams,NgTableParams,backendCfg,loginSrv) {
    var self = this;
    self.route='listes';
    self.showSpinner = true;
    self.pictos_propose = [];

    //----------------------Gestion des droits---------------//
    if (loginSrv.getCurrentUser()) {
        self.userRightLevel = loginSrv.getCurrentUser().id_droit_max;
        // gestion de l'onglet actif ; 0 par default
        if (self.userRightLevel==backendCfg.user_low_privilege) {
        self.activeForm = 2;
        }
    }
    self.userRights = loginSrv.getCurrentUserRights();

//-----------------------Get data in list by id liste-----------------------------------------------
    $http.get(backendCfg.api_url+"biblistes/edit/"+$routeParams.id).then(function(response) {
        self.edit_detailliste = response.data;
    });
//-----------------------Get list of regne-----------------------------------------------
    $http.get(backendCfg.api_url+"biblistes/edit/regne").then(function(response) {
        self.edit_regne = response.data;
    });
 //-----------------------Get list of group2_inpn-----------------------------------------------
    $http.get(backendCfg.api_url+"biblistes/edit/group2_inpn").then(function(response) {
        self.edit_group2_inpn = response.data;
    });

//-----------------------Get list of picto  in database biblistes -----------------------------------------------
    $http.get(backendCfg.api_url+"biblistes/edit/picto_biblistes").then(function(response) {
        self.edit_picto_db = response.data;
    });
//-----------------------Get list of picto in dossier ./static/images/pictos -----------------------------------------------
    $http.get(backendCfg.api_url+"biblistes/edit/picto_projet").then(function(response) {
        self.edit_picto_projet = response.data;

        // ----- compare the difference into 2 pictos listes: on database and in projet
        // ----- then save the differeces pictos into an array.
        // ----- use this array as the options for selection list on interface
        
        for(i = 0; i < self.edit_picto_projet.length; i++)
        {
            var path = "images/pictos/"+self.edit_picto_projet[i];
            for(j = 0; j < self.edit_picto_db.length; j++)
            {
                if(path.localeCompare(self.edit_picto_db[j]) == 0)
                {
                    break;
                }
                if(j == self.edit_picto_db.length - 1)
                    self.pictos_propose.push(self.edit_picto_projet[i]) ;
            }
        }
        // -- add nopicto
        self.pictos_propose.push("nopicto.gif");
        // -- add currently picto
        self.pictos_propose.push(self.edit_detailliste.picto.substring(14));

        //----- stop spinner ------
        self.showSpinner = false;
    });

    self.submit = function() {

        var url = backendCfg.api_url +"biblistes/edit/" + self.edit_detailliste.id_liste;
        console.log(url);
        console.log(form_data);
        var res = $http.post(url, self.edit_detailliste,{ withCredentials: true })
        .then(
           function(response){
                console.log(response);
                console.log("toto");
           }, 
           function(response){
             console.log("error");
              //console.log(response);

           }
        );    
    }
    
}]);