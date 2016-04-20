app.service('taxrefTaxonListSrv', function () {
    var taxonsTaxref;

    return {
        getTaxonsTaxref: function () {
            return taxonsTaxref;
        },
        setTaxonsTaxref: function(value) {
            taxonsTaxref = value;
        }
    };
});

app.controller('taxrefCtrl', [ '$scope', '$http', '$filter','$uibModal', 'ngTableParams','$rootScope','taxrefTaxonListSrv',
  function($scope, $http, $filter,$uibModal, ngTableParams, $rootScope,taxrefTaxonListSrv) {
    var self = this;

    //---------------------Chargement initiale des données sans paramètre------------------------------------
    if (taxrefTaxonListSrv.getTaxonsTaxref()) {
        self.taxonsTaxref = taxrefTaxonListSrv.getTaxonsTaxref();
    }
    else {
      $http.get("taxref/").success(function(response) {
          self.taxonsTaxref = response;
      });
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


    //--------------------rechercher un taxon---------------------------------------------------------
    //Cette fonction renvoie un tableau avec toutes les infos d'un seul taxon en recherchant sur le champ lb_nom
    self.validName = 'txAll';

    self.findLbNom = function(lb) {
        getTaxonsByLbNom(lb).then(function(response) {
            self.taxonsTaxref = response.data;
            $rootScope.$broadcast('hierachieDir:refreshHierarchy',{});
            self.lb = null;
        });
    };

    //Cette fonction renvoie un tableau avec toutes les infos d'un seul taxon en recherchant sur le champ cd_nom
    self.findCdNom = function(cd) {
        getTaxonsByCdNom(cd).then(function(response) {
            self.taxonsTaxref = response.data;
            $rootScope.$broadcast('hierachieDir:refreshHierarchy',{});
            self.cd = null;
        });
    };

    //-----------------------Bandeau recherche-----------------------------------------------
    //gestion du bandeau de recherche  - Position LEFT
    self.isCollapsedSearchTaxon = false;
    self.labelSearchTaxon = "Masquer la Recherche";

    self.toggleSearchTaxon = function(){
        self.isCollapsedSearchTaxon = !self.isCollapsedSearchTaxon
        self.isCollapsedSearchTaxon ? self.labelSearchTaxon = "Afficher la Recherche" : self.labelSearchTaxon = "Masquer la Recherche";
    }

    self.getTaxrefIlike = function(val) {
      return $http.get('taxref', {params:{'ilike':val}}).then(function(response){
        return response.data.map(function(item){
          return item.lb_nom;
        });
      });
    };

    //Cette fonction renvoie un tableau de taxons basé sur la recherche avancée
    self.findTaxonsByHierarchie = function(data) {
        if (!data) return false;
        self.taxHierarchieSelected = data;
        self.validName == 'txRef' ? self.nomValid = "&nom_valide=true" : self.nomValid = "";
        // $http.get("taxref/?famille="+self.searchedFamille+"&ordre="+self.searchedOrdre+"&classe="+self.searchedClasse+"&phylum="+self.searchedPhylum+"&regne="+self.searchedRegne+"&limit="+self.limit+self.nomValid).success(function(response) {
        //@ ?? Pourquoi  self.taxHierarchieSelected.limit+self.nomValid
        var queryparam = {params :{
          'famille':(self.taxHierarchieSelected.famille) ? self.taxHierarchieSelected.famille : '',
          'ordre':(self.taxHierarchieSelected.ordre) ? self.taxHierarchieSelected.ordre : '',
          'classe':(self.taxHierarchieSelected.classe) ? self.taxHierarchieSelected.classe : '',
          'phylum':(self.taxHierarchieSelected.phylum) ? self.taxHierarchieSelected.phylum : '',
          'regne':(self.taxHierarchieSelected.regne) ? self.taxHierarchieSelected.regne : '',
          'limit':(self.taxHierarchieSelected.limit) ? self.taxHierarchieSelected.limit : ''
        }};
        $http.get("taxref",  queryparam).success(function(response) {
            self.taxonsTaxref = response;
        });
    };


    /***********************FENETRES MODALS*****************************/

    //---------------------Gestion de l'ajout d'un taxon depuis taxref en modal------------------------------------
    // self.addTaxon = function (id) {
    //   if(id!=null){
    //     getOneTaxonDetail(id).then(function(response) {
    //         self.selectedTaxon = response.data;
    //         var modalInstance = $modal.open({
    //             templateUrl: 'modalFormContent.html'
    //             ,controller: 'ModalFormCtrl'
    //             ,size: 'lg'
    //             ,resolve: {
    //                 taxon: function () {
    //                     return self.selectedTaxon;
    //                 }
    //                 ,action: function () {
    //                     return 'add';
    //                 }
    //             }
    //         });
    //         modalInstance.opened.then(function () {
    //             // console.log($modalInstance)
    //         });
    //     },
    //     function(error) {
    //         console.log('getTaxon error', error);
    //     });
    //   }
    // };

    //---------------------Gestion de l'info taxon en modal------------------------------------
    self.open = function (id) {
        if(id!=null){
          getOneTaxonDetail(id).then(function(response) {
                self.selectedTaxon = response.data;
                for (var i=0; i < self.selectedTaxon.synonymes.length; i++) {
                    if(self.selectedTaxon.synonymes[i].cd_nom==self.selectedTaxon.cd_ref){
                        self.selectedTaxon.synonymes[i].btnClasse='btn-warning';
                        self.selectedTaxon.synonymes[i].nameClasse='cdref';

                    }
                    else{
                        self.selectedTaxon.synonymes.btnClasse='btn-info';
                        self.selectedTaxon.synonymes[i].nameClasse='cdnom';
                    }
                }
                var modalInstance = $uibModal.open({
                    templateUrl: 'app/taxref/detail/taxrefDetailModal.html',
                    controller: 'ModalInfoCtrl',
                    size: 'lg',
                    resolve: {
                        taxon: function () {
                            return self.selectedTaxon;
                        }
                    }
                });
                modalInstance.result.then(function (returnedTaxon) {
                    for(var i=0;i<self.taxonsTaxref.length;i++){
                        if(self.taxonsTaxref[i].cd_nom==returnedTaxon.cdNom){
                            self.taxonsTaxref[i].customClass = 'updated'; //mise en vert dans le tableau (classe="updated")
                            toaster.pop('success', self.taxons[i].nom_complet, " a été ajouté à la table bib_taxons");
                        }
                    }
                });

            }, function(error) {
              console.log('getTaxon error', error);
            });
        }

      };

    /***********************Services d'appel aux données*****************************/
    // Récupérer du détail d'un taxon
    getOneTaxonDetail = function(id){
      return $http.get("taxref/"+id)
        .success(function(response) {
             return response;
        })
        .error(function(error) {
           return error;
        });
    };
    //Récupérer une liste de taxons selon cd_nom
    getTaxonsByCdNom = function(cd) {
        self.validName == 'txRef' ? self.txRef = true : self.txRef = '';
        return $http.get("taxref/?cdNom="+cd+"&nom_valide="+self.txRef)
        .success(function(response) {
            return response;
        })
        .error(function(error) {
            return error;
        });
    };

    //Récupérer une liste de taxons selon nom_latin
    getTaxonsByLbNom = function(lb) {
        self.validName == 'txRef' ? self.txRef = true : self.txRef = '';
        return $http.get("taxref/?ilike="+lb+"&nom_valide="+self.txRef)
        .success(function(response) {
             return response ;
        })
        .error(function(error) {
            return error;
        });
    };

}]);
