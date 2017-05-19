app.controller('bibListeDetailCtrl',[ '$scope','$filter', '$http','$uibModal','$routeParams','bibListesDetailSrv','NgTableParams', 'backendCfg','loginSrv',
  function($scope,$filter, $http,$uibModal, $routeParams,bibListesDetailSrv,NgTableParams,backendCfg,loginSrv) {
    var self = this;
    self.listTaxonsByID = [];
    self.route='listes';
    self.showSpinner = true;
    //----------------------Gestion des droits---------------//
    self.userRights = loginSrv.getCurrentUserRights();

    //-----------------------Compter le nombre de taxons dans une liste-----------------------------------------------
    $http.get(backendCfg.api_url+"biblistes/countnoms/"+$routeParams.id).then(function(response) {
        self.count_detailliste = response.data;
    });

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
        }
        else {
          //@TODO traiter et envoyer un message
          alert("le taxon demandé n'existe pas");
        }
        self.showSpinner = false;
      }
    );

//--------------- Exporter detail de la liste --------------------------------
  self.getArray = function(id){
    return bibListesDetailSrv.getExportArray(id).then(function(res){
      return res;
    });
  }

}]);

/*---------------------SERVICES : Appel à l'API biblistes detail--------------------------*/
app.service('bibListesDetailSrv', ['$http', '$q', 'backendCfg', function ($http, $q, backendCfg) {
    this.getExportArray = function(id) {
      var defer = $q.defer();
      $http.get(backendCfg.api_url+"biblistes/exportnoms/" + id).then(function(response){
          defer.resolve(response.data);
      });
      return defer.promise;
    };

}]);
