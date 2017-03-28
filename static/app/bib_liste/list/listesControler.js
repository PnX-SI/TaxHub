app.controller('listesCtrl', [ '$scope', '$http', '$filter','$uibModal', 'NgTableParams','backendCfg','loginSrv',
  function($scope, $http, $filter,$uibModal, NgTableParams,backendCfg, loginSrv) {

    //---------------------Valeurs par défaut ------------------------------------
    var self = this;


    //----------------------Gestion des droits---------------//
    self.userRights = loginSrv.getCurrentUserRights();
  
}]);
