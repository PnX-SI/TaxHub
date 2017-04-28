app.controller('bibListeAddCtrl',[ '$scope','$filter', '$http','$uibModal','$route','$routeParams','NgTableParams','toaster','bibListeAddSrv', 'backendCfg','loginSrv',
  function($scope,$filter, $http,$uibModal,$route, $routeParams,NgTableParams,toaster,bibListeAddSrv, backendCfg,loginSrv) {
    var self = this;
    self.showSpinnerSelectList = true;
    self.showSpinnerTaxons = true;
    self.showSpinnerListe = true;
    self.isSelected = false;
    self.listName = {
      selectedList: {},
      availableOptions:{}
    };
    self.getData = {
      getTaxons : [],
      getDetailListe : []
    }
    self.tableCols = {
      "nom_francais" : { title: "Nom français", show: true },
      "nom_complet" : {title: "Nom latin", show: true },
      "lb_auteur" : {title: "Auteur", show: true },
      "cd_nom" : {title: "cd nom", show: true },
      "id_nom" : {title: "id nom", show: true }
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
    //---------------------Get list of "nom de la Liste"---------------------
    bibListeAddSrv.getBibListes().then(
      function(res){
        self.listName.availableOptions = res;
        self.showSpinnerSelectList = false;
      });
    //---------------------Initialisation des paramètres de ng-table---------------------
    self.tableParamsTaxons = new NgTableParams(
      {
          count: 12,
          sorting: {'nom_complet': 'asc'}
      }
    );
    self.tableParamsDetailListe = new NgTableParams(
      {
          count: 12,
          sorting: {'nom_complet': 'asc'}
      }
    );
    //---------------------Get taxons------------------------------------
    self.getTaxons = function() {
      self.showSpinnerTaxons = true;
      self.showSpinnerListe = true;

      bibListeAddSrv.getbibNomsList().then(
        function(res1) {
          self.getData.getTaxons = res1;
          bibListeAddSrv.getDetailListe(self.listName.selectedList.id_liste).then(
          function(res2) {
            self.getData.getDetailListe = res2;
            
            self.availableNoms(self.getData.getDetailListe,self.getData.getTaxons);

            self.tableParamsTaxons.settings({dataset:self.getData.getTaxons});
            self.tableParamsDetailListe.settings({dataset:self.getData.getDetailListe});
            
            self.showSpinnerListe = false;
            self.showSpinnerTaxons = false;

          });
        });
    };
    //--------------------- Selected Liste Change ---------------------
    self.listSelected = function(){
      // Get taxons
      self.getTaxons();
      self.isSelected = true;
    };

    self.availableNoms = function(listeNoms,taxons){
      for(i=0; i < listeNoms.length; i++){
        for(j=0; j < taxons.length; j++)
          if(listeNoms[i].cd_nom == taxons[j].cd_nom){
            taxons.splice(j,1);
            break;
          }
      }
    };

}]);

/*---------------------SERVICES : Appel à l'API bib_noms--------------------------*/
app.service('bibListeAddSrv', ['$http', '$q', 'backendCfg', function ($http, $q, backendCfg) {

    this.getbibNomsList = function () {
      var defer = $q.defer();
      $http.get(backendCfg.api_url+"biblistes/add/taxons").then(function successCallback(response) {
        defer.resolve(response.data);
      }, function errorCallback(response) {
        alert('Failed: ' + response);
      });
      return defer.promise;
    };

    this.getBibListes = function () {
      var defer = $q.defer();
      $http.get(backendCfg.api_url+"biblistes").then(function successCallback(response) {
        defer.resolve(response.data);
      }, function errorCallback(response) {
        alert('Failed: ' + response);
      });
      return defer.promise;
    };

    this.getDetailListe = function (id) {
      var defer = $q.defer();
      $http.get(backendCfg.api_url+"biblistes/add/taxons/" + id).then(function successCallback(response) {
        defer.resolve(response.data);
      }, function errorCallback(response) {
        alert('Failed: ' + response);
      });
      return defer.promise;
    };
}]);