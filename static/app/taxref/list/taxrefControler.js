app.controller('taxrefCtrl', [ '$scope', '$http', '$filter','$uibModal', 'NgTableParams','taxrefTaxonListSrv','backendCfg','loginSrv',
  function($scope, $http, $filter,$uibModal, NgTableParams,taxrefTaxonListSrv,backendCfg, loginSrv) {

    //---------------------Valeurs par défaut ------------------------------------
    var self = this;
    self.filters = taxrefTaxonListSrv.filters;
    this.nbResults=0;
    this.nbResultsTotal=0;
    self.route='taxref';
    self.tableCols = {
      "cd_nom" : { title: "cd_nom", show: true },
      "cd_ref" : {title: "cd_ref", show: true },
      "nom_complet" : {title: "Nom complet", show: true },
      "nom_vern" : {title: "Nom vernaculaire", show: true },
      "regne" : {title: "Règne", show: true },
      "phylum" : {title: "Phylum", show: true },
      "classe" : {title: "Classe", show: true },
      "ordre" : {title: "Ordre", show: true },
      "famille" : {title: "Famille", show: false },
      "group1_inpn" : {title: "group1_inpn", show: false },
      "group2_inpn" : {title: "group2_inpn", show: false }
    };

    //----------------------Gestion des droits---------------//
    self.userRights = loginSrv.getCurrentUserRights();


    //---------------------Initialisation des paramètres de ng-table---------------------
    self.tableParams = new NgTableParams(
      {
          count: 25,
          sorting: {nom_complet: 'asc'}
      },
      {
        getData: function (params) {
          self.showSpinner = true;
          taxrefTaxonListSrv.filters.tablefilter = {};
          angular.forEach(params.url(), function(value, key){
              if (key == 'count') taxrefTaxonListSrv.filters.limit = params.url().count;
              else if (key == 'page') taxrefTaxonListSrv.filters.page = params.url().page;
              else if (key.startsWith("sorting")){
                taxrefTaxonListSrv.filters.sort = key.replace('sorting[', '').replace(']', '');
                taxrefTaxonListSrv.filters.sort_order = value
              }
              else if (key.startsWith("filter")){
                column = key.replace('filter[', '').replace(']', '');
                taxrefTaxonListSrv.filters.tablefilter['ilike-'+column] =  value;
              }
          }, taxrefTaxonListSrv);

          return taxrefTaxonListSrv.getItems().then(function() {
            params.total(taxrefTaxonListSrv.nbResults);
            self.showSpinner = false;
            self.nbResultsTotal = taxrefTaxonListSrv.nbResultsTotal;
            self.nbResults = taxrefTaxonListSrv.nbResults;
            return taxrefTaxonListSrv.items;
          });
        }
      }
    );

    //--------------------rechercher liste des taxons---------------------------------------------------------
    self.findInTaxref = function() {
      self.showSpinner = true;
      self.tableParams.parameters().filter = {};
      self.tableParams.reload();
    };

    self.refreshForm = function() {
      if (taxrefTaxonListSrv.filters !=  {'hierarchy':{}}){
        taxrefTaxonListSrv.filters = {'hierarchy':{}};
        taxrefTaxonListSrv.isDirty = true;
        self.filters = taxrefTaxonListSrv.filters;
        self.findInTaxref();
      }
    }

    //-----------------------Bandeau recherche-----------------------------------------------
    //gestion du bandeau de recherche  - Position LEFT
    self.getTaxrefIlike = function(val) {
      return $http.get(backendCfg.api_url+'taxref/search/lb_nom/'+val).then(function(response){
        return response.data.map(function(item){
          return item.lb_nom;
        });
      });
    };

    /***********************FENETRES MODALS*****************************/
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
}]);

/*---------------------SERVICES : Appel à l'API taxref--------------------------*/
app.service('taxrefTaxonListSrv', ['$http', '$q', 'backendCfg', function ($http, $q, backendCfg) {
    var txs = this;
    this.isDirty = true;
    this.nbResults=0;
    this.nbResultsTotal=0;
    this.items;
    this.filters={
      'page':1 , 'sort':'', 'sort_order':'asc','limit': backendCfg.nb_results_limit,
      'hierarchy':{},
      'isRef':false, 'is_inbibtaxons':false,
      'tablefilter':{}
    };
    this.saveFilters={};

    this.getTaxrefApiResponse = function() {
      if (!this.filters) this.filters = {};
      var queryparam = {"params" :{
        'is_ref':(this.filters.isRef) ? true : false,
        'is_inbibtaxons':(this.filters.isInBibtaxon) ? true : false,
        'limit': (this.filters.limit) ? this.filters.limit : backendCfg.nb_results_limit,
        'page': (this.filters.page) ? this.filters.page :1,
        'orderby' : this.filters.sort,
        'order':this.filters.sort_order
      }};

      if (this.filters.cd){   //Si cd_nom
        queryparam.params.cd_nom = this.filters.cd;
        this.filters.lb = null;
        this.filters.hierarchy = {};
      }
      else if (this.filters.lb_nom) {//Si lb_nom
        queryparam.params.ilike = this.filters.lb_nom;
        this.filters.hierarchy = {};
      }
      else if (this.filters.hierarchy) {//Si hierarchie
        queryparam.params.famille = (this.filters.hierarchy.famille) ? this.filters.hierarchy.famille : '';
        queryparam.params.ordre = (this.filters.hierarchy.ordre) ? this.filters.hierarchy.ordre : '';
        queryparam.params.classe = (this.filters.hierarchy.classe) ? this.filters.hierarchy.classe : '';
        queryparam.params.phylum = (this.filters.hierarchy.phylum) ? this.filters.hierarchy.phylum : '';
        queryparam.params.regne = (this.filters.hierarchy.regne) ? this.filters.hierarchy.regne : '';
      }
      if(this.filters.tablefilter) {
        queryparam.params = angular.extend(queryparam.params,this.filters.tablefilter)
      }
      this.saveFilters = angular.copy(this.filters);

      return $http.get(backendCfg.api_url+"taxref/",  queryparam).then(function(response) {
          txs.items = response.data.items;
          txs.nbResults = response.data.total_filtered;
          txs.nbResultsTotal = response.data.total;
          txs.isDirty=false;
      });
    };

    this.getItems = function () {
      if ((this.isDirty)  || (!angular.equals(this.saveFilters,this.filters))) {
        return this.getTaxrefApiResponse();
      }
      var deferred = $q.defer();
      deferred.resolve();
      return deferred.promise;
    };
}]);
