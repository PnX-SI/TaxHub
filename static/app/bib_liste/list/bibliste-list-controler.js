app.controller('listesCtrl',[ '$scope', '$http', '$filter','$q','$uibModal','bibListesSrv', 'NgTableParams','backendCfg','loginSrv',
  function($scope, $http,$q, $filter, $uibModal, bibListesSrv, NgTableParams, backendCfg, loginSrv) {


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

//--------------- Exporter detail de la liste --------------------------------

  self.getArray = function(id){
    // console.log(myDataPromise);

    bibListesSrv.getNoms(id);
    this.export_array = bibListesSrv.exp_array;
    console.log(this.export_array);
    return this.export_array;
  
    // console.log (bibListesSrv.getExportArray(id).then(
    //   function(response) {
    //     self.export_array = response;
    //     console.log(self.export_array);
    // }));
    //console.log(self.export_array);
     //return self.export_array; 
  }
}]);


/*---------------------SERVICES : Appel à l'API biblistes--------------------------*/
app.service('bibListesSrv', ['$http', '$q', 'backendCfg', function ($http, $q, backendCfg) {
    var txs = this;
    this.isDirty = true;
    this.listeref;
    this.exp_array;

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

    // this.getExportArray = function(id){                 
    //   var defer = $q.defer();
    //   $http.get(backendCfg.api_url+"biblistes/noms/" + id).then(function(response){
    //           txs.array=response.data;
    //           defer.resolve(response.data);

    //   });
    //   return defer.promise;
    //}

    this.getExportArray = function(id) {
      $http.get(backendCfg.api_url+"biblistes/noms/" + id).then(function(response) {
        this.exp_array = response.data;
        console.log(this.exp_array);
        txs.isDirty = false; 
      });
    };

    this.getNoms = function(id) {
      this.getExportArray(id);
      var defer = $q.defer();
      defer.resolve();
      console.log(this.exp_array);
      return defer.promise;
    };

    // return {
    //   getExportArray: getExportArray
    // };

}]);