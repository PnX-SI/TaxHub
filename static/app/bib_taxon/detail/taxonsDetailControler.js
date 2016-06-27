app.controller('taxonsDetailCtrl',[ '$scope', '$http','$uibModal', '$routeParams','backendCfg',
  function($scope, $http,$uibModal, $routeParams, backendCfg) {
    var self = this;
    self.route='taxons';

    $http.get(backendCfg.api_url + 'bibtaxons/'+$routeParams.id).then(
      function(response) {
        if (response.data) {
          self.bibTaxon = response.data;
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
