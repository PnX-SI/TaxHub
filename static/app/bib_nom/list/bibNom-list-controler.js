app.controller('bibNomListCtrl',[ '$scope', '$http', '$filter','filterFilter', 'NgTableParams', 'toaster','bibNomListSrv','backendCfg','loginSrv',
  function($scope, $http, $filter, filterFilter, NgTableParams, toaster,bibNomListSrv,backendCfg, loginSrv) {
    var self = this;
    self.route='taxons';
    self.filterbibNoms = bibNomListSrv.filterbibNoms;
    self.count_taxon;
    self.tableCols = {
      "nom_francais" : { title: "Nom français", show: true },
      "nom_complet" : {title: "Nom latin", show: true },
      "lb_auteur" : {title: "Auteur", show: true },
      "cd_nom" : {title: "cd nom", show: true },
      "id_nom" : {title: "id nom", show: true }
    };

    //----------------------Gestion des droits---------------//
    self.userRights = loginSrv.getCurrentUserRights();

    //-----------------------Compter le nombre de taxons dans bib_noms-----------------------------------------------
    $http.get(backendCfg.api_url+"bibnoms/count").then(function(response) {
        self.count_taxon = response.data;
    });

    //---------------------Initialisation des paramètres de ng-table---------------------

    self.tableParams = new NgTableParams(
      {
          count: 50,
          sorting: {'taxref.nom_complet': 'asc'}
      },
      {
        getData: function (params) {
          self.showSpinner = true;
          bibNomListSrv.filterbibNoms.tablefilter = {};
          angular.forEach(params.url(), function(value, key){
              if (key == 'count') bibNomListSrv.filterbibNoms.limit = params.url().count;
              else if (key == 'page') bibNomListSrv.filterbibNoms.page = params.url().page;
              else if (key.startsWith("sorting")){
                bibNomListSrv.filterbibNoms.sort = key.replace('sorting[', '').replace(']', '');
                bibNomListSrv.filterbibNoms.sort_order = value
              }
              else if (key.startsWith("filter")){
                column = key.replace('filter[', '').replace(']', '');
                bibNomListSrv.filterbibNoms.tablefilter[column] =  value;
              }
          }, bibNomListSrv);

          return bibNomListSrv.getbibNomsList().then(function() {
            params.total(bibNomListSrv.nbResults);
            self.showSpinner = false;
            self.nbResultsTotal = bibNomListSrv.nbResultsTotal;
            self.nbResults = bibNomListSrv.nbResults;
            return bibNomListSrv.bibNomsList;
          });
        }
      }
    );
    self.tableParams.parameters().filter = bibNomListSrv.filterbibNoms.tablefilter;

    //-----------------------Bandeau recherche-----------------------------------------------
    self.refreshForm = function() {
      if (bibNomListSrv.filterbibNoms !=  {'hierarchy':{}}){
        bibNomListSrv.filterbibNoms = {'hierarchy':{}};
        self.filterbibNoms = bibNomListSrv.filterbibNoms;
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
    this.bibNomsList= {};
    this.nbResults=0;
    this.nbResultsTotal=0;
    this.filterbibNoms={
      'page':1 , 'sort':'', 'sort_order':'asc','limit': backendCfg.nb_results_limit,
      'hierarchy':{},
      'is_ref':false, 'is_inbibNoms':false,
      'tablefilter':{}
    };
    this.saveFilterbibNoms={};

    this.getBibNomApiResponse = function() {
      if (!this.filterbibNoms) this.filterbibNoms = {};

      var queryparam = {'params' :{
        'is_ref':(this.filterbibNoms.isRef) ? this.filterbibNoms.isRef : false,
        'is_inbibNoms':(this.filterbibNoms.isInbibNom) ? true : false,
        'limit': (this.filterbibNoms.limit) ? this.filterbibNoms.limit : backendCfg.nb_results_limit,
        'page': (this.filterbibNoms.page) ? this.filterbibNoms.page :1,
        'sort' : this.filterbibNoms.sort,
        'sort_order':this.filterbibNoms.sort_order
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
      else if (this.filterbibNoms.hierarchy){//Si hierarchie
        (this.filterbibNoms.hierarchy.famille) ? queryparam.params.famille = this.filterbibNoms.hierarchy.famille : '';
        (this.filterbibNoms.hierarchy.ordre) ? queryparam.params.ordre = this.filterbibNoms.hierarchy.ordre : '';
        (this.filterbibNoms.hierarchy.classe) ? queryparam.params.classe = this.filterbibNoms.hierarchy.classe : '';
        (this.filterbibNoms.hierarchy.phylum) ? queryparam.params.phylum = this.filterbibNoms.hierarchy.phylum : '';
        (this.filterbibNoms.hierarchy.regne) ? queryparam.params.regne = this.filterbibNoms.hierarchy.regne : '';
      }

      if(this.filterbibNoms.tablefilter) {
        (this.filterbibNoms.tablefilter.ilikeauteur) ? queryparam.params.ilikeauteur = this.filterbibNoms.tablefilter.ilikeauteur : '';
        (this.filterbibNoms.tablefilter.ilikelfr) ? queryparam.params.ilikelfr = this.filterbibNoms.tablefilter.ilikelfr : '';
        (this.filterbibNoms.tablefilter.ilikelatin) ? queryparam.params.ilikelatin = this.filterbibNoms.tablefilter.ilikelatin : '';
      }
      this.saveFilterbibNoms = angular.copy(this.filterbibNoms);

      return $http.get(backendCfg.api_url+"bibnoms/",  queryparam).then(function(response) {
        bns.bibNomsList = response.data.data;
        bns.nbResults = response.data.countfiltered;
        bns.nbResultsTotal = response.data.count;
        bns.isDirty=false;
      });
    };

    this.getbibNomsList = function () {
      if ((this.isDirty) || (this.saveFilterbibNoms !=this.filterbibNoms))  {
        return this.getBibNomApiResponse();
      }
      var deferred = $q.defer();
      deferred.resolve();
      return deferred.promise;
    };

}]);
