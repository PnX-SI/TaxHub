app.controller('taxrefCtrl', [ '$scope', '$http', '$filter','$uibModal', 'NgTableParams','taxrefTaxonListSrv','backendCfg','loginSrv',
  function($scope, $http, $filter,$uibModal, NgTableParams,taxrefTaxonListSrv,backendCfg, loginSrv) {

    //---------------------Valeurs par défaut ------------------------------------
    var self = this;
    self.filterTaxref = taxrefTaxonListSrv.filterTaxref;
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
    self.haveAdminRight=loginSrv.haveAdminRight;
    self.haveHighRight=loginSrv.haveHighRight;
    self.haveMediumRight=loginSrv.haveMediumRight;
    self.haveLowRight=loginSrv.haveLowRight;

    //---------------------Initialisation des paramètres de ng-table---------------------
    self.tableParams = new NgTableParams(
      {
          count: 50,
          sorting: {nom_complet: 'asc'}
      },
      {dataset:taxrefTaxonListSrv.taxonsTaxref}
    );

    //--------------------rechercher liste des taxons---------------------------------------------------------
    self.findInTaxref = function() {
      self.showSpinner = true;
      taxrefTaxonListSrv.getTaxonsTaxref().then(
        function(d) {
          self.showSpinner = false;
          self.tableParams.settings({dataset:taxrefTaxonListSrv.taxonsTaxref});
        }
      );
    };

    self.refreshForm = function() {
      if (taxrefTaxonListSrv.filterTaxref !=  {'hierarchy':{}}){
        taxrefTaxonListSrv.filterTaxref = {'hierarchy':{}};
        taxrefTaxonListSrv.isDirty = true;
        self.filterTaxref = taxrefTaxonListSrv.filterTaxref;
        self.findInTaxref();
      }
    }

    //---------------------WATCHS------------------------------------

    $scope.$watch(
      function () { return taxrefTaxonListSrv.filterTaxref;},
      function (newValue, oldValue) {
        if (newValue == oldValue) return;
        if (taxrefTaxonListSrv.filterTaxref) {
          taxrefTaxonListSrv.isDirty = true;
        }
      },
      true
    );

    //---------------------Chargement initiale des données------------------------------------

    self.findInTaxref();

    //-----------------------Bandeau recherche-----------------------------------------------
    //gestion du bandeau de recherche  - Position LEFT
    self.getTaxrefIlike = function(val) {
      return $http.get(backendCfg.api_url+'taxref', {params:{'ilike':val}}).then(function(response){
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
    this.taxonsTaxref;
    this.filterTaxref={'hierarchy':{'limit': backendCfg.nb_results_limit }, 'is_ref':false,'is_inbibtaxons':false};

    this.getTaxrefApiResponse = function() {
      if (!this.filterTaxref) this.filterTaxref = {};
      var queryparam = {"params" :{
        'is_ref':(this.filterTaxref.isRef) ? true : false,
        'is_inbibtaxons':(this.filterTaxref.isInBibtaxon) ? true : false,
        'limit': (this.filterTaxref.hierarchy.limit) ? this.filterTaxref.hierarchy.limit : backendCfg.nb_results_limit
      }};

      if (this.filterTaxref.cd){   //Si cd_nom
        queryparam.params.cd_nom = this.filterTaxref.cd;
        this.filterTaxref.lb = null;
        this.filterTaxref.hierarchy = {};
      }
      else if (this.filterTaxref.lb_nom) {//Si lb_nom
        queryparam.params.ilike = this.filterTaxref.lb_nom;
        this.filterTaxref.hierarchy = {};
      }
      else if (this.filterTaxref.hierarchy) {//Si hierarchie
        queryparam.params.famille = (this.filterTaxref.hierarchy.famille) ? this.filterTaxref.hierarchy.famille : '';
        queryparam.params.ordre = (this.filterTaxref.hierarchy.ordre) ? this.filterTaxref.hierarchy.ordre : '';
        queryparam.params.classe = (this.filterTaxref.hierarchy.classe) ? this.filterTaxref.hierarchy.classe : '';
        queryparam.params.phylum = (this.filterTaxref.hierarchy.phylum) ? this.filterTaxref.hierarchy.phylum : '';
        queryparam.params.regne = (this.filterTaxref.hierarchy.regne) ? this.filterTaxref.hierarchy.regne : '';
      }
      return $http.get(backendCfg.api_url+"taxref",  queryparam).success(function(response) {
          txs.taxonsTaxref = response;
          txs.isDirty = false;
      });
    };

    this.getTaxonsTaxref = function () {
      if (this.isDirty) {
        return this.getTaxrefApiResponse();
      }
      var deferred = $q.defer();
      deferred.resolve();
      return deferred.promise;
    };
}]);
