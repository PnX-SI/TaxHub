app.controller('bibNomDetailCtrl',[ '$scope', '$http','$uibModal', '$routeParams','backendCfg','loginSrv',
  function($scope, $http,$uibModal, $routeParams, backendCfg,loginSrv) {
    var self = this;
    self.route='taxons';

    //----------------------Gestion des droits---------------//
    self.userRights = loginSrv.getCurrentUserRights();

    $http.get(backendCfg.api_url + 'bibnoms/'+$routeParams.id).then(
      function(response) {
        if (response.data) {
          self.bibNom = response.data;
        }
        else {
          //@TODO traiter et envoyer un message
          alert("le taxon demandé n'existe pas");
        }
      }
    );
    //---------------------Gestion de l'info taxon en modal------------------------------------
      self.openTaxrefDetail = function (id) {
        if(id!=null){
          var modalInstance = $uibModal.open({
            templateUrl: 'static/app/taxref/detail/taxrefDetailModal.html',
            controller: 'ModalInfoCtrl',
            size: 'lg',
            resolve: {idtaxon: id}
          });
        }
      };

      getOneTaxonDetail = function(id){
        return $http.get(backendCfg.api_url + "taxref/"+id).then(
          function(response) {
            if (response.data) {
               return response.data;
            }
          })
          // .error(function(error) {
            // return error;
          // });
      };

}]);
