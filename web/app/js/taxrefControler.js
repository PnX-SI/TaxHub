app.controller('taxrefCtrl', [ '$scope', '$http', '$filter','$modal', '$q', 'ngTableParams',
  function($scope, $http, $filter,$modal, $q, ngTableParams) {
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
            $scope.taxonsTaxref = response;
            $scope.selectedregne = null;
            $scope.selectedphylum = null;
            $scope.selectedClasse = null;
            $scope.selectedOrdre = null;
            $scope.selectedFamille = null;
            $scope.lb = null;
        });
    };
    //Cette fonction renvoie un tableau avec toutes les infos d'un seul taxon en recherchant sur le champ cd_nom
    $scope.findCdNom = function(cd) {
        getTaxonsByCdNom(cd).then(function(response) {
            $scope.taxonsTaxref = response;
            $scope.selectedregne = null;
            $scope.selectedphylum = null;
            $scope.selectedClasse = null;
            $scope.selectedOrdre = null;
            $scope.selectedFamille = null;
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

    //familles 
    $scope.urlFamille = "taxref/hierarchie/FM?ilike=";
    $scope.familleSelected = function(selected) {
        selected.originalObject.nb_tx_fm <500 ? $scope.limit = selected.originalObject.nb_tx_fm+1 : $scope.limit = 500;
        document.getElementById('fOrdres_value').value = selected.originalObject.ordre +' ' + selected.originalObject.nb_tx_or;
        document.getElementById('fClasses_value').value = selected.originalObject.classe +' ' + selected.originalObject.nb_tx_cl;
        document.getElementById('fPhylums_value').value = selected.originalObject.phylum +' ' + selected.originalObject.nb_tx_ph;
        document.getElementById('fRegnes_value').value = selected.originalObject.regne +' ' + selected.originalObject.nb_tx_kd;
        selected.originalObject.famille ? $scope.searchedFamille = selected.originalObject.famille : $scope.searchedFamille ='';
        selected.originalObject.ordre ? $scope.searchedOrdre = selected.originalObject.ordre : $scope.searchedOrdre ='';
        selected.originalObject.classe ? $scope.searchedClasse = selected.originalObject.classe : $scope.searchedClasse ='';
        selected.originalObject.phylum ? $scope.searchedPhylum = selected.originalObject.phylum : $scope.searchedPhylum ='';
        selected.originalObject.regne ? $scope.searchedRegne = selected.originalObject.regne : $scope.searchedRegne ='';
    };
    //ordres
    $scope.urlOrdre = "taxref/hierarchie/OR?ilike=";
    $scope.ordreSelected = function(selected) {
        selected.originalObject.nb_tx_or <500 ? $scope.limit = selected.originalObject.nb_tx_or+1 : $scope.limit = 500;
        document.getElementById('fFamilles_value').value = '';
        document.getElementById('fClasses_value').value = selected.originalObject.classe +' ' + selected.originalObject.nb_tx_cl;
        document.getElementById('fPhylums_value').value = selected.originalObject.phylum +' ' + selected.originalObject.nb_tx_ph;
        document.getElementById('fRegnes_value').value = selected.originalObject.regne +' ' + selected.originalObject.nb_tx_kd;
        selected.originalObject.famille ? $scope.searchedFamille = selected.originalObject.famille : $scope.searchedFamille ='';
        selected.originalObject.ordre ? $scope.searchedOrdre = selected.originalObject.ordre : $scope.searchedOrdre ='';
        selected.originalObject.classe ? $scope.searchedClasse = selected.originalObject.classe : $scope.searchedClasse ='';
        selected.originalObject.phylum ? $scope.searchedPhylum = selected.originalObject.phylum : $scope.searchedPhylum ='';
        selected.originalObject.regne ? $scope.searchedRegne = selected.originalObject.regne : $scope.searchedRegne ='';
        $scope.urlFamille = "taxref/hierarchie/FM?regne="+$scope.searchedRegne+"&phylum="+$scope.searchedPhylum+"&classe="+$scope.searchedClasse+"&ordre="+$scope.searchedOrdre+"&ilike=";
    };
    //classes
    $scope.urlClasse = "taxref/hierarchie/CL?ilike=";
    $scope.classeSelected = function(selected) {
        selected.originalObject.nb_tx_cl <500 ? $scope.limit = selected.originalObject.nb_tx_cl+1 : $scope.limit = 500;
        document.getElementById('fFamilles_value').value = '';
        document.getElementById('fOrdres_value').value = '';
        document.getElementById('fPhylums_value').value = selected.originalObject.phylum +' ' + selected.originalObject.nb_tx_ph;
        document.getElementById('fRegnes_value').value = selected.originalObject.regne +' ' + selected.originalObject.nb_tx_kd;
        selected.originalObject.famille ? $scope.searchedFamille = selected.originalObject.famille : $scope.searchedFamille ='';
        selected.originalObject.ordre ? $scope.searchedOrdre = selected.originalObject.ordre : $scope.searchedOrdre ='';
        selected.originalObject.classe ? $scope.searchedClasse = selected.originalObject.classe : $scope.searchedClasse ='';
        selected.originalObject.phylum ? $scope.searchedPhylum = selected.originalObject.phylum : $scope.searchedPhylum ='';
        selected.originalObject.regne ? $scope.searchedRegne = selected.originalObject.regne : $scope.searchedRegne ='';
        $scope.urlOrdre = "taxref/hierarchie/OR?regne="+$scope.searchedRegne+"&phylum="+$scope.searchedPhylum+"&classe="+$scope.searchedClasse+"&ilike=";
        $scope.urlFM = "taxref/hierarchie/OR?regne="+$scope.searchedRegne+"&phylum="+$scope.searchedPhylum+"&classe="+$scope.searchedClasse+"&ilike=";
    };
    //phylums
    $scope.urlPhylum = "taxref/hierarchie/PH?ilike=";
    $scope.phylumSelected = function(selected) {
        selected.originalObject.nb_tx_ph <500 ? $scope.limit = selected.originalObject.nb_tx_ph+1 : $scope.limit = 500;
        document.getElementById('fFamilles_value').value = '';
        document.getElementById('fOrdres_value').value = '';
        document.getElementById('fClasses_value').value = '';
        document.getElementById('fRegnes_value').value = selected.originalObject.regne +' ' + selected.originalObject.nb_tx_kd;
        selected.originalObject.famille ? $scope.searchedFamille = selected.originalObject.famille : $scope.searchedFamille ='';
        selected.originalObject.ordre ? $scope.searchedOrdre = selected.originalObject.ordre : $scope.searchedOrdre ='';
        selected.originalObject.classe ? $scope.searchedClasse = selected.originalObject.classe : $scope.searchedClasse ='';
        selected.originalObject.phylum ? $scope.searchedPhylum = selected.originalObject.phylum : $scope.searchedPhylum ='';
        selected.originalObject.regne ? $scope.searchedRegne = selected.originalObject.regne : $scope.searchedRegne ='';
        $scope.urlClasse = "taxref/hierarchie/CL?regne="+$scope.searchedRegne+"&phylum="+$scope.searchedPhylum+"&ilike=";
        $scope.urlOrdre = "taxref/hierarchie/OR?regne="+$scope.searchedRegne+"&phylum="+$scope.searchedPhylum+"&ilike=";
        $scope.urlFamille = "taxref/hierarchie/FM?regne="+$scope.searchedRegne+"&phylum="+$scope.searchedPhylum+"&ilike=";
    };
    //regnes
    $scope.regneSelected = function(selected) {
        selected.originalObject.nb_tx_kd <500 ? $scope.limit = selected.originalObject.nb_tx_kd+1 : $scope.limit = 500;
        document.getElementById('fFamilles_value').value = '';
        document.getElementById('fOrdres_value').value = '';
        document.getElementById('fClasses_value').value = '';
        document.getElementById('fPhylums_value').value = '';
        selected.originalObject.famille ? $scope.searchedFamille = selected.originalObject.famille : $scope.searchedFamille ='';
        selected.originalObject.ordre ? $scope.searchedOrdre = selected.originalObject.ordre : $scope.searchedOrdre ='';
        selected.originalObject.classe ? $scope.searchedClasse = selected.originalObject.classe : $scope.searchedClasse ='';
        selected.originalObject.phylum ? $scope.searchedPhylum = selected.originalObject.phylum : $scope.searchedPhylum ='';
        selected.originalObject.regne ? $scope.searchedRegne = selected.originalObject.regne : $scope.searchedRegne ='';
        $scope.urlPhylum = "taxref/hierarchie/PH?regne="+$scope.searchedRegne+"&ilike=";
        $scope.urlClasse = "taxref/hierarchie/CL?regne="+$scope.searchedRegne+"&ilike=";
        $scope.urlOrdre = "taxref/hierarchie/OR?regne="+$scope.searchedRegne+"&ilike=";
        $scope.urlFamille = "taxref/hierarchie/FM?regne="+$scope.searchedRegne+"&ilike=";
    };
    
    //Cette fonction renvoie un tableau de taxons basé sur la recherche avancée
    $scope.findTaxonsByHierarchie = function() {
        $scope.validName == 'txRef' ? $scope.nomValid = "&nom_valide=true" : $scope.nomValid = "";
        $http.get("taxref/?famille="+$scope.searchedFamille+"&ordre="+$scope.searchedOrdre+"&classe="+$scope.searchedClasse+"&phylum="+$scope.searchedPhylum+"&regne="+$scope.searchedRegne+"&limit="+$scope.limit+$scope.nomValid).success(function(response) {
            $scope.taxonsTaxref = response;        
        });
    };
    //fonction permettant de vider tous les champs de la recherche hierarchique
    $scope.refresch = function() {
        document.getElementById('fFamilles_value').value = '';
        document.getElementById('fOrdres_value').value = '';
        document.getElementById('fClasses_value').value = '';
        document.getElementById('fPhylums_value').value = '';
        document.getElementById('fRegnes_value').value = '';
        $scope.urlPhylum = "taxref/hierarchie/PH?ilike=";
        $scope.urlClasse = "taxref/hierarchie/CL?ilike=";
        $scope.urlOrdre = "taxref/hierarchie/OR?ilike=";
        $scope.urlFamille = "taxref/hierarchie/FM?ilike=";
    }
    
    /***********************FENETRES MODALS*****************************/
    
    //---------------------Gestion de l'ajout d'un taxon depuis taxref en modal------------------------------------
    $scope.addTaxon = function (id) {
      if(id!=null){
        var dfd = getOneTaxonDetail(id);
        dfd.then(function(response) {
            $scope.selectedTaxon = response;
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
                $scope.selectedTaxon = response;
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
      var deferred = $q.defer();
      $http.get("taxref/"+id)
        .success(function(response) {
            deferred.resolve(response);
        })
        .error(function(error) {
            deferred.reject(error);
        });
      return deferred.promise;
    };
    //Récupérer une liste de taxons selon cd_nom
    getTaxonsByCdNom = function(cd) {
        var deferred = $q.defer();
        $scope.validName == 'txRef' ? $scope.txRef = true : $scope.txRef = '';
        $http.get("taxref/?cdNom="+cd+"&nom_valide="+$scope.txRef)
        .success(function(response) {
            deferred.resolve(response);
        })
        .error(function(error) {
            deferred.reject(error);
        });
      return deferred.promise;
    };
    
    //Récupérer une liste de taxons selon nom_latin
    getTaxonsByLbNom = function(lb) {
        var deferred = $q.defer();
        $scope.validName == 'txRef' ? $scope.txRef = true : $scope.txRef = '';
        $http.get("taxref/?ilike="+lb+"&nom_valide="+$scope.txRef)
        .success(function(response) {
            deferred.resolve(response);
        })
        .error(function(error) {
            deferred.reject(error);
        });
      return deferred.promise;
    };

}]);
