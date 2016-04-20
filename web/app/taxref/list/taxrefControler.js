app.controller('taxrefCtrl', [ '$scope', '$http', '$filter','$uibModal', 'ngTableParams','$rootScope',
  function($scope, $http, $filter,$modal, ngTableParams, $rootScope) {
    //Initialisation
    $scope.searchedRegne = null;
    $scope.searchedPhylum = null;
    $scope.searchedClasse = null;
    $scope.searchedOrdre = null;
    $scope.searchedFamille = null;
    //Initialisation des paramètres de ng-table
    $scope.tableParams = new ngTableParams(
    {
        page: 1            // show first page
        ,count: 50           // count per page
        ,sorting: {
            nom_complet: 'asc'     // initial sorting
        }
    },{
        total: $scope.taxonsTaxref ?  $scope.taxonsTaxref.length : 0 // length of data
        ,getData: function($defer, params) {
          if ($scope.taxonsTaxref) {
            // use build-in angular filter
            var filteredData = params.filter() ?
                $filter('filter')($scope.taxonsTaxref, params.filter()) :
                $scope.taxonsTaxref;
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
    $scope.$watch('taxonsTaxref', function() {
      if ($scope.taxonsTaxref) {
        $scope.tableParams.total( $scope.taxonsTaxref ?  $scope.taxonsTaxref.length : 0);
        $scope.tableParams.reload();
      }
    });

    //---------------------Chargement initiale des données sans paramètre------------------------------------
    $http.get("taxref/").success(function(response) {
        $scope.taxonsTaxref = response;
    });

    //--------------------rechercher un taxon---------------------------------------------------------
    //Cette fonction renvoie un tableau avec toutes les infos d'un seul taxon en recherchant sur le champ lb_nom
    $scope.validName = 'txAll';

    $scope.findLbNom = function(lb) {
        getTaxonsByLbNom(lb).then(function(response) {
            $scope.taxonsTaxref = response.data;
            $rootScope.$broadcast('hierachieDir:refreshHierarchy',{});
            $scope.lb = null;
        });
    };
    //Cette fonction renvoie un tableau avec toutes les infos d'un seul taxon en recherchant sur le champ cd_nom
    $scope.findCdNom = function(cd) {
        getTaxonsByCdNom(cd).then(function(response) {
            $scope.taxonsTaxref = response.data;
            $rootScope.$broadcast('hierachieDir:refreshHierarchy',{});
            $scope.cd = null;
        });
    };



    //-----------------------Bandeau recherche-----------------------------------------------
    //gestion du bandeau de recherche  - Position LEFT
    $scope.isCollapsedSearchTaxon = false;
    $scope.labelSearchTaxon = "Masquer la Recherche";
    $scope.toggleSearchTaxon = function(){
        $scope.isCollapsedSearchTaxon = !$scope.isCollapsedSearchTaxon
        $scope.isCollapsedSearchTaxon ? $scope.labelSearchTaxon = "Afficher la Recherche" : $scope.labelSearchTaxon = "Masquer la Recherche";
    }

    $scope.getTaxrefIlike = function(val) {
      return $http.get('taxref', {params:{'ilike':val}}).then(function(response){
        return response.data.map(function(item){
          return item.lb_nom;
        });
      });
    };

    //Cette fonction renvoie un tableau de taxons basé sur la recherche avancée
    $scope.findTaxonsByHierarchie = function(data) {
        if (!data) return false;
        $scope.taxHierarchieSelected = data;
        $scope.validName == 'txRef' ? $scope.nomValid = "&nom_valide=true" : $scope.nomValid = "";
        // $http.get("taxref/?famille="+$scope.searchedFamille+"&ordre="+$scope.searchedOrdre+"&classe="+$scope.searchedClasse+"&phylum="+$scope.searchedPhylum+"&regne="+$scope.searchedRegne+"&limit="+$scope.limit+$scope.nomValid).success(function(response) {
        //@ ?? Pourquoi  $scope.taxHierarchieSelected.limit+$scope.nomValid
        var queryparam = {params :{
          'famille':($scope.taxHierarchieSelected.famille) ? $scope.taxHierarchieSelected.famille : '',
          'ordre':($scope.taxHierarchieSelected.ordre) ? $scope.taxHierarchieSelected.ordre : '',
          'classe':($scope.taxHierarchieSelected.classe) ? $scope.taxHierarchieSelected.classe : '',
          'phylum':($scope.taxHierarchieSelected.phylum) ? $scope.taxHierarchieSelected.phylum : '',
          'regne':($scope.taxHierarchieSelected.regne) ? $scope.taxHierarchieSelected.regne : '',
          'limit':($scope.taxHierarchieSelected.limit) ? $scope.taxHierarchieSelected.limit : ''
        }};
        $http.get("taxref",  queryparam).success(function(response) {
            $scope.taxonsTaxref = response;
        });
    };


    /***********************FENETRES MODALS*****************************/

    //---------------------Gestion de l'ajout d'un taxon depuis taxref en modal------------------------------------
    $scope.addTaxon = function (id) {
      if(id!=null){
        getOneTaxonDetail(id).then(function(response) {
            $scope.selectedTaxon = response.data;
            var modalInstance = $modal.open({
                templateUrl: 'modalFormContent.html'
                ,controller: 'ModalFormCtrl'
                ,size: 'lg'
                ,resolve: {
                    taxon: function () {
                        return $scope.selectedTaxon;
                    }
                    ,action: function () {
                        return 'add';
                    }
                }
            });
            modalInstance.opened.then(function () {
                // console.log($modalInstance)
            });
        },
        function(error) {
            console.log('getTaxon error', error);
        });
      }
    };

    //---------------------Gestion de l'info taxon en modal------------------------------------
    $scope.open = function (id) {
        if(id!=null){
          getOneTaxonDetail(id).then(function(response) {
                $scope.selectedTaxon = response.data;
                for (var i=0; i < $scope.selectedTaxon.synonymes.length; i++) {
                    if($scope.selectedTaxon.synonymes[i].cd_nom==$scope.selectedTaxon.cd_ref){
                        $scope.selectedTaxon.synonymes[i].btnClasse='btn-warning';
                        $scope.selectedTaxon.synonymes[i].nameClasse='cdref';

                    }
                    else{
                        $scope.selectedTaxon.synonymes.btnClasse='btn-info';
                        $scope.selectedTaxon.synonymes[i].nameClasse='cdnom';
                    }
                }
                var modalInstance = $modal.open({
                    templateUrl: 'modalInfoContent.html',
                    controller: 'ModalInfoCtrl',
                    size: 'lg',
                    resolve: {
                        taxon: function () {
                            return $scope.selectedTaxon;
                        }
                    }
                });
                modalInstance.result.then(function (returnedTaxon) {
                    for(var i=0;i<$scope.taxonsTaxref.length;i++){
                        if($scope.taxonsTaxref[i].cd_nom==returnedTaxon.cdNom){
                            $scope.taxonsTaxref[i].customClass = 'updated'; //mise en vert dans le tableau (classe="updated")
                            toaster.pop('success', $scope.taxons[i].nom_complet, " a été ajouté à la table bib_taxons");
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
        $scope.validName == 'txRef' ? $scope.txRef = true : $scope.txRef = '';
        return $http.get("taxref/?cdNom="+cd+"&nom_valide="+$scope.txRef)
        .success(function(response) {
            return response;
        })
        .error(function(error) {
            return error;
        });
    };

    //Récupérer une liste de taxons selon nom_latin
    getTaxonsByLbNom = function(lb) {
        $scope.validName == 'txRef' ? $scope.txRef = true : $scope.txRef = '';
        return $http.get("taxref/?ilike="+lb+"&nom_valide="+$scope.txRef)
        .success(function(response) {
             return response ;
        })
        .error(function(error) {
            return error;
        });
    };

}]);
