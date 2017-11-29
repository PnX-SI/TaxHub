app.controller('bibListeDetailCtrl',[ '$scope','$filter', '$http', '$uibModal', '$routeParams', 'NgTableParams', 'backendCfg', 'loginSrv','bibListesSrv',
  function($scope, $filter, $http, $uibModal, $routeParams, NgTableParams, backendCfg, loginSrv, bibListesSrv) {
    var self = this;
    self.infoListe={};
    self.nomsListe=[];
    self.nbNoms=0;
    self.route='listes';
    self.showSpinner = true;
    self.showSpinnerListe = true;
    //----------------------Gestion des droits---------------//
    self.userRights = loginSrv.getCurrentUserRights();

    //---------------------Initialisation des paramètres de ng-table---------------------
    self.tableParams = new NgTableParams(
      {
          count: 50,
          sorting: {'taxref.nom_complet': 'asc'}
      },
      {
        getData: function (params) {
          self.showSpinnerListe = true;
          filters = {}
          angular.forEach(params.url(), function(value, key){
              if (key == 'count') filters.limit = params.url().count;
              else if (key == 'page') filters.page = params.url().page;
              else if (key.startsWith("sorting")){
                filters.orderby = key.replace('sorting[', '').replace(']', '');
                filters.order = value
              }
              else if (key.startsWith("filter")){
                column = key.replace('filter[', '').replace(']', '');
                filters[column] = value;
              }
          }, params);

          return bibListesSrv.getbibNomsList($routeParams.id, true, filters).then(function(results) {
              params.total(results.data.total);

              self.nbNoms = results.data.total
              self.showSpinnerListe = false;
              self.nomsListe = results.data.items;

              return  self.nomsListe || [];
          });
        }
      }
    );


    $http.get(backendCfg.api_url + 'biblistes/'+$routeParams.id).then(
      function(response) {
        if (response.data) {
          self.infoListe = response.data;
        }
        else {
          //@TODO traiter et envoyer un message
          alert("le taxon demandé n'existe pas");
        }
        self.showSpinner = false;
      }
    );
}]);
