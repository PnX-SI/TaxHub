var app = angular.module('taxonsApp', ['ngTable','ui.bootstrap','angucomplete-alt']);

app.controller('taxrefCtrl', function($scope, $http, $filter,$modal,ngTableParams) {
    //Initialisation
    $scope.searchedRegne = null;
    $scope.searchedPhylum = null;
    $scope.searchedClasse = null;
    $scope.searchedOrdre = null;
    $scope.searchedFamille = null;
    //factorisation de l'url de l'appli
    var url_root = "http://92.222.107.92/taxhub/app_dev.php/";
    //mise à jour de la table ng-table
    var majTable = function(data){    
        $scope.tableData = data;
        $scope.tableParams.total($scope.tableData.length);
        $scope.tableParams.reload();
    }
    
    //chargement initial et construction du tableau de résultats (découverte)
    // Préparation de la table ng-table du tableau de résultat offrant les fonctions de tri par colonne
    $http.get(url_root+"taxref/").success(function(response) {
        $scope.taxonsTaxref = response;
        $scope.tableParams = new ngTableParams({
            page: 1            // show first page
            ,count: 50           // count per page
            ,filter: {
                nom_complet: ''       // initial filter
            } 
            ,sorting: {
                nom_complet: 'asc'     // initial sorting
            }
        },{
            total: $scope.taxonsTaxref.length, // length of data
            getData: function($defer, params) {
                // use build-in angular filter
                var filteredData = params.filter() ? 
                    $filter('filter')($scope.taxonsTaxref, params.filter()) : 
                    $scope.taxonsTaxref;
                var orderedData = params.sorting() ? 
                    $filter('orderBy')(filteredData, params.orderBy()) : 
                    $scope.taxonsTaxref;
                 
                
                $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
            }
        });
        $scope.gridOptions = { 
            data: 'taxonsTaxref',
            showGroupPanel: true,
            jqueryUIDraggable: true
        };
    });
    
    //--------------------rechercher un taxon---------------------------------------------------------
    //Cette fonction renvoie un tableau avec toutes les infos d'un seul taxon en recherchant sur le champ lb_nom
    $scope.validName = 'txAll';
    
    $scope.findLbNom = function(lb) {
        $scope.validName == 'txRef' ? $scope.txRef = true : $scope.txRef = '';
        $http.get(url_root+"taxref/?ilike="+lb+"&nom_valide="+$scope.txRef).success(function(response) {
            $scope.taxonsTaxref = response;
            majTable($scope.taxonsTaxref);
            $scope.selectedregne = null;
            $scope.selectedphylum = null;
            $scope.selectedClasse = null;
            $scope.selectedOrdre = null;
            $scope.selectedFamille = null;
            $scope.cd = null;
        });
    };
     //Cette fonction renvoie un tableau avec toutes les infos d'un seul taxon en recherchant sur le champ cd_nom
    $scope.findCdNom = function(cd) {
        $scope.validName == 'txRef' ? $scope.txRef = true : $scope.txRef = '';
        $http.get(url_root+"taxref/?cdNom="+cd+"&nom_valide="+$scope.txRef).success(function(response) {
            $scope.taxonsTaxref = response;
            majTable($scope.taxonsTaxref);
            $scope.selectedregne = null;
            $scope.selectedphylum = null;
            $scope.selectedClasse = null;
            $scope.selectedOrdre = null;
            $scope.selectedFamille = null;
            $scope.lb = null;
        });
    };
    
    //---------------------Gestion de l'info taxon en modal------------------------------------
      $scope.open = function (id) {
        if(id!=null){
            $http.get(url_root+"taxref/"+id).success(function(response) {
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
                  templateUrl: 'myModalContent.html',
                  controller: 'ModalInstanceCtrl',
                  size: 'lg',
                  resolve: {
                    taxon: function () {
                      return $scope.selectedTaxon;
                    }
                  }
                });
                // modalInstance.result.then(function (selectedItem) {
                  // $scope.selected = selectedItem;
                // }, function () {
                  // $log.info('Modal dismissed at: ' + new Date());
                // });
                
            });
        }
        
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
    $scope.urlFamille = url_root+"taxref/hierarchie/FM?ilike=";
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
    $scope.urlOrdre = url_root+"taxref/hierarchie/OR?ilike=";
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
        $scope.urlFamille = url_root+"taxref/hierarchie/FM?regne="+$scope.searchedRegne+"&phylum="+$scope.searchedPhylum+"&classe="+$scope.searchedClasse+"&ordre="+$scope.searchedOrdre+"&ilike=";
    };
    //classes
    $scope.urlClasse = url_root+"taxref/hierarchie/CL?ilike=";
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
        $scope.urlOrdre = url_root+"taxref/hierarchie/OR?regne="+$scope.searchedRegne+"&phylum="+$scope.searchedPhylum+"&classe="+$scope.searchedClasse+"&ilike=";
        $scope.urlFM = url_root+"taxref/hierarchie/OR?regne="+$scope.searchedRegne+"&phylum="+$scope.searchedPhylum+"&classe="+$scope.searchedClasse+"&ilike=";
    };
    //phylums
    $scope.urlPhylum = url_root+"taxref/hierarchie/PH?ilike=";
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
        $scope.urlClasse = url_root+"taxref/hierarchie/CL?regne="+$scope.searchedRegne+"&phylum="+$scope.searchedPhylum+"&ilike=";
        $scope.urlOrdre = url_root+"taxref/hierarchie/OR?regne="+$scope.searchedRegne+"&phylum="+$scope.searchedPhylum+"&ilike=";
        $scope.urlFamille = url_root+"taxref/hierarchie/FM?regne="+$scope.searchedRegne+"&phylum="+$scope.searchedPhylum+"&ilike=";
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
        $scope.urlPhylum = url_root+"taxref/hierarchie/PH?regne="+$scope.searchedRegne+"&ilike=";
        $scope.urlClasse = url_root+"taxref/hierarchie/CL?regne="+$scope.searchedRegne+"&ilike=";
        $scope.urlOrdre = url_root+"taxref/hierarchie/OR?regne="+$scope.searchedRegne+"&ilike=";
        $scope.urlFamille = url_root+"taxref/hierarchie/FM?regne="+$scope.searchedRegne+"&ilike=";
    };
    
    //Cette fonction renvoie un tableau de taxons basé sur la recherche avancée
    $scope.findTaxonsByHierarchie = function() {
        $scope.validName == 'txRef' ? $scope.nomValid = "&nom_valide=true" : $scope.nomValid = "";
        $http.get(url_root+"taxref/?famille="+$scope.searchedFamille+"&ordre="+$scope.searchedOrdre+"&classe="+$scope.searchedClasse+"&phylum="+$scope.searchedPhylum+"&regne="+$scope.searchedRegne+"&limit="+$scope.limit+$scope.nomValid).success(function(response) {
            $scope.taxonsTaxref = response;
            majTable($scope.taxonsTaxref);            
        });
    };
    //fonction permettant de vider tous les champs de la recherche hierarchique
    $scope.refresch = function() { 
        document.getElementById('fFamilles_value').value = '';
        document.getElementById('fOrdres_value').value = '';
        document.getElementById('fClasses_value').value = '';
        document.getElementById('fPhylums_value').value = '';
        document.getElementById('fRegnes_value').value = '';
        $scope.urlPhylum = url_root+"taxref/hierarchie/PH?ilike=";
        $scope.urlClasse = url_root+"taxref/hierarchie/CL?ilike=";
        $scope.urlOrdre = url_root+"taxref/hierarchie/OR?ilike=";
        $scope.urlFamille = url_root+"taxref/hierarchie/FM?ilike=";
    }
    
    //-------------------------------------modal form todo-------------------------------------
    $scope.addTaxon = function(tax) {
        alert('Todo : ajouter le taxon '+tax.lb_nom+' à bib_taxons.');

    };
});
