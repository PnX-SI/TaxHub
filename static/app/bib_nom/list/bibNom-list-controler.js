app.controller('bibNomListCtrl',[ '$scope', '$http', '$filter','filterFilter', 'ngTableParams', 'toaster','bibNomListSrv','backendCfg','loginSrv',
  function($scope, $http, $filter, filterFilter, ngTableParams, toaster,bibNomListSrv,backendCfg, loginSrv) {
    var self = this;
    self.isAllowedToEdit=false;
    self.filterbibNoms = bibNomListSrv.filterbibNoms;
    self.tableCols = {
      "nom_francais" : { title: "Nom français", show: true },
      "nom_complet" : {title: "Nom latin", show: true },
      "lb_auteur" : {title: "Auteur", show: true },
      "cd_nom" : {title: "cd nom", show: true },
      "id_nom" : {title: "id nom", show: true }
    };


    //----------------------Gestion des droits---------------//
    if (loginSrv.getCurrentUser()) {
      if (loginSrv.getCurrentUser().id_droit_max >= backendCfg.user_edit_privilege) self.isAllowedToEdit = true;
    }

    //---------------------Initialisation des paramètres de ng-table---------------------
    self.tableParams = new ngTableParams(
    {
        page: 1            // show first page
        ,count: 25           // count per page
        ,sorting: {
            nom_complet: 'asc'     // initial sorting
        }
    },{
        total: bibNomListSrv.bibNomsList ?  bibNomListSrv.bibNomsList.length : 0 // length of data
        ,getData: function($defer, params) {
            if (bibNomListSrv.bibNomsList) {
                // use build-in angular filter
                var filteredData = params.filter() ?
                    $filter('filter')(bibNomListSrv.bibNomsList, params.filter()) :
                    bibNomListSrv.bibNomsList;
                var orderedData = params.sorting() ?
                    $filter('orderBy')(filteredData, params.orderBy()) :
                    filteredData;
                $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
            }
            else {
                $defer.resolve();
            }
        }
    });

    //-----------------------Bandeau recherche-----------------------------------------------
    self.refreshForm = function() {
      if (bibNomListSrv.filterbibNoms !=  {'hierarchy':{}}){
        bibNomListSrv.filterbibNoms = {'hierarchy':{}};
        bibNomListSrv.isDirty = true;
        self.filterbibNoms = bibNomListSrv.filterbibNoms;
        self.findInbibNom();
      }
    }
    self.findInbibNom = function() {
      self.showSpinner = true;
      bibNomListSrv.getbibNomsList().then(
        function(d) {
        self.showSpinner = false;
      });
    };

    //---------------------Chargement initiale des données sans paramètre------------------------------------
    self.findInbibNom();


    //---------------------WATCHS------------------------------------
    $scope.$watch(function () {
          return bibNomListSrv.bibNomsList;
      }, function (newValue, oldValue) {
        if (bibNomListSrv.bibNomsList) {
          self.tableParams.total( bibNomListSrv.bibNomsList ?  bibNomListSrv.bibNomsList.length : 0);
          self.tableParams.reload();
        }
    }, true);
    $scope.$watch(function () {
          return bibNomListSrv.filterbibNoms;
      }, function (newValue, oldValue) {
        if (newValue == oldValue) return;
        if (bibNomListSrv.filterbibNoms) {
          bibNomListSrv.isDirty = true;
        }
    }, true);

    //---------------------FORMULAIRE de RECHERCHE ---------------------------------------------------
    self.getTaxrefIlike = function(val) {
      return $http.get(backendCfg.api_url+'taxref/bibnoms/', {params:{'ilike':val}}).then(function(response){
        return response.data.map(function(item){
          return item.lb_nom;
        });
      });
    };

}]);


/*---------------------SERVICES : Appel à l'API bib_noms--------------------------*/
app.service('bibNomListSrv', ['$http', '$q', 'backendCfg', function ($http, $q, backendCfg) {
    var bns = this;
    this.isDirty = true;
    this.bibNomsList;
    this.filterbibNoms={'hierarchy':{'limit': backendCfg.nb_results_limit }, 'is_ref':false, 'is_inbibNoms':false};

    this.getBibNomApiResponse = function() {
      if (!this.filterbibNoms) this.filterbibNoms = {};

      var queryparam = {'params' :{
        'is_ref':(this.filterbibNoms.isRef) ? true : false,
        'is_inbibNoms':(this.filterbibNoms.isInbibNom) ? true : false,
        'limit': (this.filterbibNoms.hierarchy.limit) ? this.filterbibNoms.hierarchy.limit : backendCfg.nb_results_limit
      }};

      if (this.filterbibNoms.cd){   //Si cd_nom
        queryparam.params.cd_nom = this.filterbibNoms.cd;
        this.filterbibNoms.lb = null;
        this.filterbibNoms.hierarchy = {};
      }
      else if (this.filterbibNoms.lb_nom) {//Si lb_nom
        queryparam.params.ilikelatin = this.filterbibNoms.lb_nom;
        this.filterbibNoms.hierarchy = {};
      }
      else if (this.filterbibNoms.hierarchy) {//Si hierarchie
        (this.filterbibNoms.hierarchy.famille) ? queryparam.params.famille = this.filterbibNoms.hierarchy.famille : '';
        (this.filterbibNoms.hierarchy.ordre) ? queryparam.params.ordre = this.filterbibNoms.hierarchy.ordre : '';
        (this.filterbibNoms.hierarchy.classe) ? queryparam.params.classe = this.filterbibNoms.hierarchy.classe : '';
        (this.filterbibNoms.hierarchy.phylum) ? queryparam.params.phylum = this.filterbibNoms.hierarchy.phylum : '';
        (this.filterbibNoms.hierarchy.regne) ? queryparam.params.regne = this.filterbibNoms.hierarchy.regne : '';
      }
      return $http.get(backendCfg.api_url+"bibnoms/",  queryparam).success(function(response) {
          bns.bibNomsList = response;
          bns.isDirty = false;
      });
    };

    this.getbibNomsList = function () {
      if (this.isDirty) {
        return this.getBibNomApiResponse();
      }
      var deferred = $q.defer();
      deferred.resolve();
      return deferred.promise;
    };

}]);
