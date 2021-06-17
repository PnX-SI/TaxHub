app.controller('listesCtrl',[ '$scope', '$http', '$filter','$uibModal','bibListesSrv', 'NgTableParams','backendCfg','loginSrv',
  function($scope, $http, $filter, $uibModal, bibListesSrv, NgTableParams, backendCfg, loginSrv) {


    //---------------------Valeurs par défaut ------------------------------------
    var self = this;
    self.route='listes';
    self.tableCols = {
      "id_liste" : { title: "id_liste", show: true },
      "code_liste" : { title: "code_liste", show: true },
      "nom_liste" : {title: "nom_liste", show: true },
      "desc_liste" : {title: "desc_liste", show: true },
      "picto" : {title: "picto", show: true },
      "regne" : {title: "Règne", show: true },
      "group2_inpn" : {title: "group2_inpn", show: true },
      "nb_taxons" : {title: "nombre de taxons", show: true }
    };
    self.count_listes = 0;

//----------------------Gestion des droits---------------//
    self.userRights = loginSrv.getCurrentUserRights();

//---------------------Initialisation des paramètres de ng-table---------------------
    self.tableParams = new NgTableParams(
      {
          count: 50,
          sorting: {nom_liste: 'asc'}
      }
    );

//--------------------rechercher liste des taxons---------------------------------------------------------
    self.getBibListes = function() {
      self.showSpinner = true;
      bibListesSrv.getListes().then(
        function(d) {
          self.showSpinner = false;
          self.count_listes = bibListesSrv.listeref.count;
          self.tableParams.settings({dataset:bibListesSrv.listeref.data});
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

    this.getDetailListe = function (idListe) {
      return $http.get(backendCfg.api_url + 'biblistes/' + idListe);
    };

    this.getbibNomsList = function (id, existing, params) {
      params = (params ? params : {});
      if (existing) {
        params['existing'] = true;
      }
      return $http.get(backendCfg.api_url + "biblistes/taxons/" + id, {'params': params});
    };
}]);
