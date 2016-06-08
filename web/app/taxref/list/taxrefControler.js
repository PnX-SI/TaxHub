app.service('taxrefTaxonListSrv', function () {
    var taxonsTaxref;
    var filterTaxref;

    return {
        getTaxonsTaxref: function () {
            return taxonsTaxref;
        },
        setTaxonsTaxref: function(value) {
            taxonsTaxref = value;
        },
        getfilterTaxref: function () {
            return filterTaxref;
        },
        setfilterTaxref: function(value) {
            filterTaxref = value;
        }
    };
});

app.controller('taxrefCtrl', [ '$scope', '$http', '$filter','$uibModal', 'ngTableParams','taxrefTaxonListSrv','backendCfg',
  function($scope, $http, $filter,$uibModal, ngTableParams,taxrefTaxonListSrv,backendCfg) {
    var self = this;
    self.route='taxref';
    //---------------------Valeurs par défaut ------------------------------------
    self.isRef = false; // Rechercher uniquement les enregistrements de taxref ou cd_nom=cd_ref
    self.isInBibtaxon = false; // Rechercher uniquement les taxons qui sont dans bibtaxon

    //---------------------Chargement initiale des données sans paramètre------------------------------------
    if (taxrefTaxonListSrv.getTaxonsTaxref()) {
        self.taxonsTaxref = taxrefTaxonListSrv.getTaxonsTaxref();
    }
    else {
      $http.get(backendCfg.api_url+"taxref/").success(function(response) {
          self.taxonsTaxref = response;
      });
    }
    if (taxrefTaxonListSrv.getfilterTaxref()) {
        self.filterTaxref = taxrefTaxonListSrv.getfilterTaxref();
    }
    else {
      self.filterTaxref = {};
    }

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
        total: self.taxonsTaxref ?  self.taxonsTaxref.length : 0 // length of data
        ,getData: function($defer, params) {
          if (self.taxonsTaxref) {
            // use build-in angular filter
            var filteredData = params.filter() ?
                $filter('filter')(self.taxonsTaxref, params.filter()) :
                self.taxonsTaxref;
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
    $scope.$watch(function () {
          return self.taxonsTaxref;
      }, function() {
      if (self.taxonsTaxref) {
        taxrefTaxonListSrv.setTaxonsTaxref(self.taxonsTaxref);
        self.tableParams.total( self.taxonsTaxref ?  self.taxonsTaxref.length : 0);
        self.tableParams.reload();
      }
    });
    $scope.$watch(function () {
          return self.filterTaxref;
      }, function() {
      if (self.filterTaxref) {
        taxrefTaxonListSrv.setfilterTaxref(self.filterTaxref);
      }
    }, true);


    //--------------------rechercher un taxon---------------------------------------------------------
    //Cette fonction renvoie un tableau de taxons basé sur la recherche avancée
    self.findInTaxref = function() {
        var queryparam = {params :{
          'is_ref':(self.filterTaxref.isRef) ? true : false,
          'is_inbibtaxons':(self.filterTaxref.isInBibtaxon) ? true : false,
          'limit' : 500
        }};
        if (self.filterTaxref.hierarchy) {
          queryparam.params.limit = (self.filterTaxref.hierarchy.limit) ? self.filterTaxref.hierarchy.limit : '500';
        }

        if (self.filterTaxref.cd){   //Si cd_nom
          queryparam.params.cd_nom = self.filterTaxref.cd;
          self.filterTaxref.lb = null;
          self.filterTaxref.hierarchy = {};
        }
        else if (self.filterTaxref.lb_nom) {//Si lb_nom
          queryparam.params.ilike = self.filterTaxref.lb_nom;
          self.filterTaxref.hierarchy = {};
        }
        else if (self.filterTaxref.hierarchy) {//Si hierarchie
          queryparam.params.famille = (self.filterTaxref.hierarchy.famille) ? self.filterTaxref.hierarchy.famille : '';
          queryparam.params.ordre = (self.filterTaxref.hierarchy.ordre) ? self.filterTaxref.hierarchy.ordre : '';
          queryparam.params.classe = (self.filterTaxref.hierarchy.classe) ? self.filterTaxref.hierarchy.classe : '';
          queryparam.params.phylum = (self.filterTaxref.hierarchy.phylum) ? self.filterTaxref.hierarchy.phylum : '';
          queryparam.params.regne = (self.filterTaxref.hierarchy.regne) ? self.filterTaxref.hierarchy.regne : '';
        }
        $http.get(backendCfg.api_url+"taxref",  queryparam).success(function(response) {
            self.taxonsTaxref = response;
        });
    };
    self.refreshForm = function() {
      self.filterTaxref = {'hierarchy':{}};
      self.findInTaxref();
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
          templateUrl: 'app/taxref/detail/taxrefDetailModal.html',
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
