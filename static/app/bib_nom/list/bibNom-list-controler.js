app.controller('bibNomListCtrl',[ '$scope', '$http', '$filter','filterFilter', 'NgTableParams', 'toaster','bibNomListSrv','backendCfg','loginSrv',
  function($scope, $http, $filter, filterFilter, NgTableParams, toaster,bibNomListSrv,backendCfg, loginSrv) {
    var self = this;
    self.route='taxons';
    self.filters = bibNomListSrv.filters;
    self.count_taxon;
    self.tableCols = {
      "nom_francais" : { title: "Nom français", show: true },
      "nom_complet" : {title: "Nom latin", show: true },
      "lb_auteur" : {title: "Auteur", show: true },
      "cd_nom" : {title: "cd nom", show: true }
    };

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
          self.showSpinner = true;
          bibNomListSrv.filters.tablefilter = {};
          angular.forEach(params.url(), function(value, key){
              if (key == 'count') bibNomListSrv.filters.limit = params.url().count;
              else if (key == 'page') bibNomListSrv.filters.page = params.url().page;
              else if (key.startsWith("sorting")){
                bibNomListSrv.filters.sort = key.replace('sorting[', '').replace(']', '');
                bibNomListSrv.filters.sort_order = value
              }
              else if (key.startsWith("filter")){
                column = key.replace('filter[', '').replace(']', '');
                bibNomListSrv.filters.tablefilter[column] =  value;
              }
          }, bibNomListSrv);

          return bibNomListSrv.getItems().then(function() {
            params.total(bibNomListSrv.nbResults);
            self.showSpinner = false;
            self.nbResultsTotal = bibNomListSrv.nbResultsTotal;
            self.nbResults = bibNomListSrv.nbResults;
            return bibNomListSrv.items;
          });
        }
      }
    );
    self.tableParams.parameters().filter = bibNomListSrv.filters.tablefilter;

    //-----------------------Bandeau recherche-----------------------------------------------
    self.refreshForm = function() {
      if (bibNomListSrv.filters !=  {'hierarchy':{}}){
        bibNomListSrv.filters = {'hierarchy':{}};
        self.filters = bibNomListSrv.filters;
      }
    }

    //---------------------WATCHS------------------------------------

    self.findInbibNom = function() {
      self.showSpinner = true;
      self.tableParams.parameters().filter = {};
      self.tableParams.reload();
    };

    //---------------------FORMULAIRE de RECHERCHE ---------------------------------------------------
    self.getTaxrefIlike = function(val) {
      return $http.get(backendCfg.api_url+'taxref/search/lb_nom/'+val, {params:{'is_inbibnoms':true}}).then(function(response){
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
    this.items= {};
    this.nbResults=0;
    this.nbResultsTotal=0;
    this.filters={
      'page':1 , 'sort':'', 'sort_order':'asc','limit': 1,
      'hierarchy':{},
      'isRef':false, 'is_inbibNoms':false,
      'tablefilter':{}
    };
    this.saveFilters={};

    this.getBibNomApiResponse = function() {
      if (!this.filters) this.filters = {};

      var queryparam = {'params' :{
        'is_ref':(this.filters.isRef) ? this.filters.isRef : false,
        'is_inbibNoms':(this.filters.isInbibNom) ? true : false,
        'limit': (this.filters.limit) ? this.filters.limit : 1,
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
        queryparam.params.ilikelatin = this.filters.lb_nom;
        this.filters.hierarchy = {};
      }
      else if (this.filters.hierarchy){//Si hierarchie
        (this.filters.hierarchy.famille) ? queryparam.params.famille = this.filters.hierarchy.famille : '';
        (this.filters.hierarchy.ordre) ? queryparam.params.ordre = this.filters.hierarchy.ordre : '';
        (this.filters.hierarchy.classe) ? queryparam.params.classe = this.filters.hierarchy.classe : '';
        (this.filters.hierarchy.phylum) ? queryparam.params.phylum = this.filters.hierarchy.phylum : '';
        (this.filters.hierarchy.regne) ? queryparam.params.regne = this.filters.hierarchy.regne : '';
      }

      if(this.filters.tablefilter) {
        (this.filters.tablefilter.ilikeauteur) ? queryparam.params.ilikeauteur = this.filters.tablefilter.ilikeauteur : '';
        (this.filters.tablefilter.ilikelfr) ? queryparam.params.ilikelfr = this.filters.tablefilter.ilikelfr : '';
        (this.filters.tablefilter.ilikelatin) ? queryparam.params.ilikelatin = this.filters.tablefilter.ilikelatin : '';
      }
      this.saveFilters = angular.copy(this.filters);

      return $http.get(backendCfg.api_url+"bibnoms/",  queryparam).then(function(response) {
        bns.items = response.data.items;
        bns.nbResults = response.data.total_filtered;
        bns.nbResultsTotal = response.data.total;
        bns.isDirty=false;
      });
    };

    this.getItems = function () {
      if ((this.isDirty)  || (!angular.equals(this.saveFilters,this.filters))) {
        return this.getBibNomApiResponse();
      }
      var deferred = $q.defer();
      deferred.resolve();
      return deferred.promise;
    };

}]);
