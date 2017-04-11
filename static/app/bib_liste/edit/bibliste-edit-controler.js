app.controller('bibListeEditCtrl',[ '$scope','$filter', '$http','$uibModal','$routeParams','NgTableParams', 'backendCfg','loginSrv',
  function($scope,$filter, $http,$uibModal, $routeParams,NgTableParams,backendCfg,loginSrv) {
    var self = this;
    self.route='listes';
    //----------------------Gestion des droits---------------//
    self.userRights = loginSrv.getCurrentUserRights();

//-----------------------Get data in list by id liste-----------------------------------------------
    $http.get(backendCfg.api_url+"biblistes/edit/"+$routeParams.id).then(function(response) {
        self.edit_detailliste = response.data;
    });
    
}]);