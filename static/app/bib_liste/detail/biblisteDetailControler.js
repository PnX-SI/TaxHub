app.controller('bibListeDetailCtrl',[ '$scope', '$http','$uibModal', '$routeParams','backendCfg','loginSrv',
  function($scope, $http,$uibModal, $routeParams,backendCfg,loginSrv) {
    var self = this;
    self.route='listes';
    //----------------------Gestion des droits---------------//
    self.userRights = loginSrv.getCurrentUserRights();

    $http.get(backendCfg.api_url + 'biblistes/noms/'+$routeParams.id).then(
      function(response) {
        if (response.data) {
          $scope.listTaxonsByID = response.data;
        }
        else {
          //@TODO traiter et envoyer un message
          alert("le taxon demandé n'existe pas");
        }
      }
    );
}]);