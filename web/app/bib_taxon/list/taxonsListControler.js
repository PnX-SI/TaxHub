app.controller('taxonsListCtrl',[ '$scope', '$http', '$filter','filterFilter', '$uibModal', 'ngTableParams', 'toaster','$rootScope',
  function($scope, $http, $filter, filterFilter, $modal, ngTableParams, toaster, $rootScope) {
    var self = this;
    self.tableCols = {
      "nomFrancais" : { title: "Nom francais", show: true },
      "nomLatin" : {title: "Nom latin", show: true },
      "auteur" : {title: "Auteur", show: true },
      "cdNom" : {title: "cd nom", show: true },
      "idTaxon" : {title: "id Taxon", show: true }
    };

    //---------------------Chargement initiale des données sans paramètre------------------------------------
    $http.get("bibtaxons").success(function(response) {
        self.taxons = response;
    });

    //Initialisation des paramètres de ng-table
    self.tableParams = new ngTableParams(
    {
        page: 1            // show first page
        ,count: 25           // count per page
        ,sorting: {
            nomLatin: 'asc'     // initial sorting
        }
    },{
        total: self.taxons ?  self.taxons.length : 0 // length of data
        ,getData: function($defer, params) {
            if (self.taxons) {
                if (self.taxons) {
                    // use build-in angular filter
                    var filteredData = params.filter() ?
                        $filter('filter')(self.taxons, params.filter()) :
                        self.taxons;
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

    self.findBibTaxonsByHierarchie = function(data) {
        console.log('Recherche des bibtaxons');
    };
    //---------------------FORMULAIRE de RECHERCHE ---------------------------------------------------
    self.getTaxrefIlike = function(val) {
      return $http.get('taxref/bibtaxons/', {params:{'ilike':val}}).then(function(response){
        return response.data.map(function(item){
          return item.lb_nom;
        });
      });
    };

    //---------------------WATCHS------------------------------------
    //Watch sur taxonsTaxref de façon a recharger la table
    $scope.$watch(function () {
          return self.taxons;
      }, function() {
        if (self.taxons) {
            self.tableParams.total( self.taxons ?  self.taxons.length : 0);
            self.tableParams.reload();
        }
    });

    /***********************FENETRES MODALS*****************************/
    //-------------------suppression d'un taxon en base----------------------
    self.deleteTaxon = function(id) {
        // self.errors.splice(0, self.errors.length); // remove all error messages
        // self.oks.splice(0, self.oks.length);
        var params = {'id_taxon': id}
        $http.delete('bibtaxons/'+ id,params)
        .success(function(data, status, headers, config) {
            if (data.success == true){
                // self.oks.push(data.message);
                toaster.pop('success', "Ok !", data.message);
                for(var i=0;i<self.taxons.length;i++){
                    if(self.taxons[i].idTaxon==id){
                        self.taxons[i].customClass = 'deleted'; //mise en rouge barré dans le tableau (classe="deleted")
                        self.taxons[i].customBtnClass = 'btn-hide'; //masquer les boutons dans le tableau (classe="btn-hide")
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
    //gestion du bandeau de recherche  - Position LEFT
    self.isCollapsedSearchTaxon = false;
    self.labelSearchTaxon = "Masquer la Recherche";
    self.toggleSearchTaxon = function(){
        self.isCollapsedSearchTaxon = !self.isCollapsedSearchTaxon;
        self.labelSearchTaxon = (self.isCollapsedSearchTaxon ? "Afficher la Recherche" : "Masquer la Recherche") ;
    }


    self.findLbNomB = function(lb) {
        getTaxonsByLbNom(lb).then(function(response) {
            self.taxons = response.data;
            $rootScope.$broadcast('hierachieDir:refreshHierarchy',{});
            self.lb = null;
        });
    };

    //Récupérer une liste de taxons selon nom_latin
    getTaxonsByLbNom = function(lb) {
        self.validName == 'txRef' ? self.txRef = true : self.txRef = '';
        return $http.get("taxref/bibtaxons/?ilike="+lb+"&nom_valide="+self.txRef)
        .success(function(response) {
             return response ;
        })
        .error(function(error) {
            return error;
        });
    };


}]);
