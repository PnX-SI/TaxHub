app.service('bibtaxonListSrv', function () {
    var bibtaxonsList;
    var filterBibtaxons;

    return {
        getBibtaxonsList: function () {
            return bibtaxonsList;
        },
        setBibtaxonsList: function(value) {
            bibtaxonsList = value;
        },
        getFilterBibtaxons: function () {
            return filterBibtaxons;
        },
        setFilterBibtaxons: function(value) {
            filterBibtaxons = value;
        }
    };
});

app.controller('taxonsListCtrl',[ '$scope', '$http', '$filter','filterFilter', '$uibModal',
    'ngTableParams', 'toaster','bibtaxonListSrv','backendCfg',
  function($scope, $http, $filter, filterFilter, $modal, ngTableParams, toaster,bibtaxonListSrv,backendCfg) {
    var self = this;
    self.route='taxons';

    //---------------------Chargement initiale des données sans paramètre------------------------------------
    if (bibtaxonListSrv.getBibtaxonsList()) {
        self.bibtaxonsList = bibtaxonListSrv.getBibtaxonsList();
    }
    else {
      $http.get(backendCfg.api_url+"bibtaxons/").success(function(response) {
          self.bibtaxonsList = response;
      });
    }
    if (bibtaxonListSrv.getFilterBibtaxons()) {
        self.filterBibtaxons = bibtaxonListSrv.getFilterBibtaxons();
    }
    else {
      self.filterBibtaxons = {};
    }

    self.tableCols = {
      "nom_francais" : { title: "Nom francais", show: true },
      "nom_latin" : {title: "Nom latin", show: true },
      "auteur" : {title: "Auteur", show: true },
      "cd_nom" : {title: "cd nom", show: true },
      "id_taxon" : {title: "id Taxon", show: true }
    };


    //---------------------WATCHS------------------------------------
    //Ajout d'un watch sur taxonsTaxref de façon à recharger la table
    $scope.$watch(function () {
          return self.bibtaxonsList;
      }, function() {
        if (self.bibtaxonsList) {
          bibtaxonListSrv.setBibtaxonsList(self.bibtaxonsList);
          self.tableParams.total( self.bibtaxonsList ?  self.bibtaxonsList.length : 0);
          self.tableParams.reload();
        }
    });

    $scope.$watch(function () {
          return self.filterBibtaxons;
      }, function() {
      if (self.filterBibtaxons) {
        bibtaxonListSrv.setFilterBibtaxons(self.filterBibtaxons);
      }
    }, true);


    //Initialisation des paramètres de ng-table
    self.tableParams = new ngTableParams(
    {
        page: 1            // show first page
        ,count: 25           // count per page
        ,sorting: {
            nomLatin: 'asc'     // initial sorting
        }
    },{
        total: self.bibtaxonsList ?  self.bibtaxonsList.length : 0 // length of data
        ,getData: function($defer, params) {
            if (self.bibtaxonsList) {
                if (self.bibtaxonsList) {
                    // use build-in angular filter
                    var filteredData = params.filter() ?
                        $filter('filter')(self.bibtaxonsList, params.filter()) :
                        self.bibtaxonsList;
                    var orderedData = params.sorting() ?
                        $filter('orderBy')(filteredData, params.orderBy()) :
                        filteredData;
                    $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
                }
            }
            else {
                $defer.resolve();
            }
        }
    });

    //---------------------FORMULAIRE de RECHERCHE ---------------------------------------------------
    self.getTaxrefIlike = function(val) {
      return $http.get(backendCfg.api_url+'taxref/bibtaxons/', {params:{'ilike':val}}).then(function(response){
        return response.data.map(function(item){
          return item.lb_nom;
        });
      });
    };

    /***********************FENETRES MODALS*****************************/
    //-------------------suppression d'un taxon en base----------------------
    self.deleteTaxon = function(id) {
        // self.errors.splice(0, self.errors.length); // remove all error messages
        // self.oks.splice(0, self.oks.length);
        var params = {'id_taxon': id}
        $http.delete(backendCfg.api_url+'bibtaxons/'+ id,params)
        .success(function(data, status, headers, config) {
            if (data.success == true){
                // self.oks.push(data.message);
                toaster.pop('success', "Ok !", data.message);
                for(var i=0;i<self.bibtaxonsList.length;i++){
                    if(self.bibtaxonsList[i].idTaxon==id){
                        self.bibtaxonsList[i].customClass = 'deleted'; //mise en rouge barré dans le tableau (classe="deleted")
                        self.bibtaxonsList[i].customBtnClass = 'btn-hide'; //masquer les boutons dans le tableau (classe="btn-hide")
                    }
                }
            }
            if (data.success == false){
                // self.errors.push(data.message);
                toaster.pop('warning', "Attention !", data.message);
            }
        })
        .error(function(data, status, headers, config) { // called asynchronously if an error occurs or server returns response with an error status.
            toaster.pop('warning', "Attention !", data.message);
        });
    };


    //-----------------------Bandeau recherche-----------------------------------------------
    self.findInBibTaxon = function() {
        var queryparam = {params :{
          'is_ref':(self.filterBibtaxons.isRef) ? true : false,
          'is_inbibtaxons':(self.filterBibtaxons.isInBibtaxon) ? true : false
        }};
        if (self.filterBibtaxons.hierarchy) {
          queryparam.params.limit = (self.filterBibtaxons.hierarchy.limit) ? self.filterBibtaxons.hierarchy.limit : '1000';
        }

        if (self.filterBibtaxons.cd){   //Si cd_nom
          queryparam.params.cd_nom = self.filterBibtaxons.cd;
          self.filterBibtaxons.lb = null;
          self.filterBibtaxons.hierarchy = {};
        }
        else if (self.filterBibtaxons.lb_nom) {//Si lb_nom
          queryparam.params.ilikelatin = self.filterBibtaxons.lb_nom;
          self.filterBibtaxons.hierarchy = {};
        }
        else if (self.filterBibtaxons.hierarchy) {//Si hierarchie
          (self.filterBibtaxons.hierarchy.famille) ? queryparam.params.famille = self.filterBibtaxons.hierarchy.famille : '';
          (self.filterBibtaxons.hierarchy.ordre) ? queryparam.params.ordre = self.filterBibtaxons.hierarchy.ordre : '';
          (self.filterBibtaxons.hierarchy.classe) ? queryparam.params.classe = self.filterBibtaxons.hierarchy.classe : '';
          (self.filterBibtaxons.hierarchy.phylum) ? queryparam.params.phylum = self.filterBibtaxons.hierarchy.phylum : '';
          (self.filterBibtaxons.hierarchy.regne) ? queryparam.params.regne = self.filterBibtaxons.hierarchy.regne : '';
        }
        $http.get(backendCfg.api_url+"bibtaxons/",  queryparam).success(function(response) {
            self.bibtaxonsList = response;
        });
    }
    self.refreshForm = function() {
      self.filterBibtaxons = {'hierarchy' : {}};
      self.findInBibTaxon();
    }

}]);
