app.service('taxrefTaxonListSrv', ['$http', 'backendCfg', function ($http, backendCfg) {
    var txs = this;
    this.isDirty = true;
    this.taxonsTaxref;
    this.filterTaxref;

    this.getTaxrefApiResponse = function() {
      if (!this.filterTaxref) this.filterTaxref = {};
      var queryparam = {params :{
        'is_ref':(this.filterTaxref.isRef) ? true : false,
        'is_inbibtaxons':(this.filterTaxref.isInBibtaxon) ? true : false,
        'limit' : 500
      }};
      if (this.filterTaxref.hierarchy) {
        queryparam.params.limit = (this.filterTaxref.hierarchy.limit) ? this.filterTaxref.hierarchy.limit : '500';
      }

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
      $http.get(backendCfg.api_url+"taxref",  queryparam).success(function(response) {
          txs.taxonsTaxref = response;
          txs.isDirty = false;
      });
    };

    this.getTaxonsTaxref = function () {
      if (this.isDirty) {
        this.getTaxrefApiResponse();
      }
    };
}]);

app.controller('taxrefCtrl', [ '$scope', '$http', '$filter','$uibModal', 'ngTableParams','taxrefTaxonListSrv','backendCfg','loginSrv',
  function($scope, $http, $filter,$uibModal, ngTableParams,taxrefTaxonListSrv,backendCfg, loginSrv) {
    var self = this;
    self.route='taxref';
    self.isAllowedToEdit=false;

    //----------------------Gestion des droits---------------//
    if (loginSrv.getCurrentUser()) {
      if (loginSrv.getCurrentUser().id_droit_max >= backendCfg.user_edit_privilege) self.isAllowedToEdit = true;
    }

    //---------------------Valeurs par défaut ------------------------------------
    self.isRef = false; // Rechercher uniquement les enregistrements de taxref ou cd_nom=cd_ref
    self.isInBibtaxon = false; // Rechercher uniquement les taxons qui sont dans bibtaxon

    //---------------------Chargement initiale des données sans paramètre------------------------------------
    taxrefTaxonListSrv.getTaxonsTaxref();
    self.findInTaxref = function() {
      taxrefTaxonListSrv.getTaxonsTaxref();
    };
    self.filterTaxref = taxrefTaxonListSrv.filterTaxref;
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

    //Initialisation des paramètres de ng-table
    self.tableParams = new ngTableParams(
    {
        page: 1            // show first page
        ,count: 50           // count per page
        ,sorting: {
            nom_complet: 'asc'     // initial sorting
        }
    },{
        total: taxrefTaxonListSrv.taxonsTaxref ?  taxrefTaxonListSrv.taxonsTaxref.length : 0 // length of data
        ,getData: function($defer, params) {
            if (taxrefTaxonListSrv.taxonsTaxref) {
                // use build-in angular filter
                var filteredData = params.filter() ?
                    $filter('filter')(taxrefTaxonListSrv.taxonsTaxref, params.filter()) :
                    taxrefTaxonListSrv.taxonsTaxref;
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


    //---------------------WATCHS------------------------------------
    //Ajout d'un watch sur taxonsTaxref de façon à recharger la table
    $scope.$watch(
      function () { return taxrefTaxonListSrv.taxonsTaxref;},
      function(newValue, oldValue) {
        if (taxrefTaxonListSrv.taxonsTaxref) {
          self.tableParams.total( taxrefTaxonListSrv.taxonsTaxref ?  taxrefTaxonListSrv.taxonsTaxref.length : 0);
          self.tableParams.reload();
        }
      },
      true
    );

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

    //--------------------rechercher un taxon---------------------------------------------------------
    //Cette fonction renvoie un tableau de taxons basé sur la recherche avancée
    self.refreshForm = function() {
      if (taxrefTaxonListSrv.filterTaxref !=  {'hierarchy':{}}){
        taxrefTaxonListSrv.filterTaxref = {'hierarchy':{}};
        taxrefTaxonListSrv.isDirty = true;
        self.filterTaxref = taxrefTaxonListSrv.filterTaxref;
        taxrefTaxonListSrv.getTaxonsTaxref();
      }
    }

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

    /***********************Services d'appel aux données*****************************/
    // Récupérer du détail d'un taxon
    getOneTaxonDetail = function(id){
      return $http.get(backendCfg.api_url+"taxref/"+id)
        .success(function(response) {
             return response;
        })
        .error(function(error) {
           return error;
        });
    };
    //Récupérer une liste de taxons selon cd_nom
    getTaxonsByCdNom = function(cd) {
        var queryparam = {params :{
          'cdNom':cd,
          'is_ref':(self.isRef) ? true : false
        }};
        return $http.get(backendCfg.api_url+"taxref",queryparam)
          .success(function(response) {
              return response;
          })
          .error(function(error) {
              return error;
          });
    };

    //Récupérer une liste de taxons selon nom_latin
    getTaxonsByLbNom = function(lb) {
        var queryparam = {params :{
          'ilike':lb,
          'is_ref':(self.isRef) ? true : false
        }};
        return $http.get(backendCfg.api_url+"taxref",queryparam)
          .success(function(response) {
               return response ;
          })
          .error(function(error) {
              return error;
          });
    };

}]);
