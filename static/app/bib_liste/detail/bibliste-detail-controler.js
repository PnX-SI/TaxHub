app.controller('bibListeDetailCtrl',[ '$scope','$filter', '$http', '$uibModal', '$routeParams', 'NgTableParams', 'backendCfg', 'loginSrv',
  function($scope, $filter, $http, $uibModal, $routeParams, NgTableParams, backendCfg, loginSrv) {
    var self = this;
    self.listTaxonsByID = [];
    self.route='listes';
    self.showSpinner = true;
    //----------------------Gestion des droits---------------//
    self.userRights = loginSrv.getCurrentUserRights();

    //---------------------Initialisation des paramètres de ng-table---------------------
    self.tableParams = new NgTableParams(
      {
          count: 50,
          sorting: {'taxref.nom_complet': 'asc'}
      },
      {dataset:self.listTaxonsByID[1]}
    );


    $http.get(backendCfg.api_url + 'biblistes/info/'+$routeParams.id).then(
      function(response) {
        if (response.data) {
          self.listTaxonsByID = response.data;
          self.tableParams.settings({dataset:self.listTaxonsByID[1]});
          self.count_detailliste = self.listTaxonsByID[2];
        }
        else {
          //@TODO traiter et envoyer un message
          alert("le taxon demandé n'existe pas");
        }
        self.showSpinner = false;
      }
    );
}]);