app.controller('bibNomDetailCtrl',[ '$scope', '$http','$uibModal', '$routeParams','backendCfg','loginSrv',
  function($scope, $http,$uibModal, $routeParams, backendCfg,loginSrv) {
    var self = this;
    self.route='taxons';
    self.haveAdminRight=false;
    self.haveHighRight=false;
    self.haveMediumRight=false;
    self.haveLowRight=false;

    //----------------------Gestion des droits---------------//
    if (loginSrv.getCurrentUser()) {
        switch  (loginSrv.getCurrentUser().id_droit_max){
            case backendCfg.user_admin_privilege:
                self.haveAdminRight = true;
                self.haveHighRight=true;
                self.haveMediumRight=true;
                self.haveLowRight=true;
                break;
            case backendCfg.user_high_privilege:
                self.haveHighRight=true;
                self.haveMediumRight=true;
                self.haveLowRight=true;
                break;
            case backendCfg.user_medium_privilege:
                self.haveMediumRight=true;
                self.haveLowRight=true;
                break;
            case backendCfg.user_low_privilege:
                self.haveLowRight=true;
                break;
            default :
                self.haveAdminRight = false;
                self.haveHighRight=false;
                self.haveMediumRight=false;
                self.haveLowRight=false;
        }
    }

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
        return $http.get(backendCfg.api_url + "taxref/"+id)
          .success(function(response) {
               return response;
          })
          .error(function(error) {
             return error;
          });
      };

}]);
