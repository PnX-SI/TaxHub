app.controller('bibListeAddCtrl',[ '$scope','$filter', '$http','$uibModal','$route','$routeParams','NgTableParams','toaster','bibListeAddSrv', 'backendCfg','loginSrv',
  function($scope,$filter, $http,$uibModal,$route, $routeParams,NgTableParams,toaster,bibListeAddSrv, backendCfg,loginSrv) {
    var self = this;
    self.showSpinnerSelectList = true;
    self.showSpinnerTaxons = true;
    self.showSpinnerListe = true;
    self.isSelected = false;
    self.listName = {
    selectedList: {
      'id_liste': null,
    },
    availableOptions: {}
   };
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
          count: 50,
          sorting: {'nom_francais': 'asc'}
      }
    );
    self.tableParamsDetailListe = new NgTableParams(
      {
          count: 50,
          sorting: {'nom_francais': 'asc'}
      }
    );
    //---------------------Get taxons------------------------------------
    self.getTaxons = function() {
      self.showSpinnerTaxons = true;
      bibListeAddSrv.getbibNomsList().then(
        function(res) {
          self.showSpinnerTaxons = false;
          self.tableParamsTaxons.settings({dataset:res});
        });
    };
    self.getDetailListe = function(id) {
      self.showSpinnerListe = true;
      bibListeAddSrv.getDetailListe(id).then(
        function(res) {
          self.showSpinnerListe = false;
          self.tableParamsDetailListe.settings({dataset:res});
        });
    };
    //--------------------- Selected Liste Change ---------------------
    self.listSelected = function(){
      self.isSelected = true;
      // Get taxons
      self.getTaxons();
      console.log(self.listName.selectedList.id_liste);
      self.getDetailListe(self.listName.selectedList.id_liste);
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
      $http.get(backendCfg.api_url+"biblistes/noms/" + id).then(function successCallback(response) {
        defer.resolve(response.data);
      }, function errorCallback(response) {
        alert('Failed: ' + response);
      });
      return defer.promise;
    };
}]);