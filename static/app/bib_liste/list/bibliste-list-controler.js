app.controller('listesCtrl',[ '$scope', '$http', '$filter','$uibModal','bibListesSrv', 'NgTableParams','backendCfg','loginSrv',
  function($scope, $http, $filter, $uibModal, bibListesSrv, NgTableParams, backendCfg, loginSrv) {


    //---------------------Valeurs par défaut ------------------------------------
    var self = this;
    self.route='listes';
    self.tableCols = {
      "id_liste" : { title: "id_liste", show: true },
      "nom_liste" : {title: "nom_liste", show: true },
      "desc_liste" : {title: "desc_liste", show: true },
      "picto" : {title: "picto", show: true },
      "regne" : {title: "Règne", show: true },
      "group2_inpn" : {title: "group2_inpn", show: true },
      "nb_taxons" : {title: "nombre de taxons", show: true }
    };

//----------------------Gestion des droits---------------//
    self.userRights = loginSrv.getCurrentUserRights();

//-----------------------Compter le nombre de taxons dans taxref-----------------------------------------------
    $http.get(backendCfg.api_url+"biblistes/count").then(function(response) {
        self.count_listes = response.data;
    });

//---------------------Initialisation des paramètres de ng-table---------------------
    self.tableParams = new NgTableParams(
      {
          count: 50,
          sorting: {nom_liste: 'asc'}
      },
      {dataset:bibListesSrv.listeref}
    );

//--------------------rechercher liste des taxons---------------------------------------------------------
    self.getBibListes = function() {
      self.showSpinner = true;
      bibListesSrv.getListes().then(
        function(d) {
          self.showSpinner = false;
          self.tableParams.settings({dataset:bibListesSrv.listeref});
        }
      );
    };

//---------------------Chargement initiale des données------------------------------------

    self.getBibListes();
  
}]);


/*---------------------SERVICES : Appel à l'API biblistes--------------------------*/
app.service('bibListesSrv', ['$http', '$q', 'backendCfg', function ($http, $q, backendCfg) {
    var txs = this;
    this.isDirty = true;
    this.listeref;

    this.getListesApiResponse = function() {
      return $http.get(backendCfg.api_url+"biblistes/").then(function(response) {
          txs.listeref = response.data;
          txs.isDirty = false;
      });
    };

    this.getListes = function () {
      if (this.isDirty) {
        return this.getListesApiResponse();
      }
      var deferred = $q.defer();
      deferred.resolve();
      return deferred.promise;
    };
}]);