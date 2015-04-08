var app = angular.module('taxonsApp', ['ngTable','ui.bootstrap','pageslide-directive']);
app.controller('taxrefCtrl', function($scope, $http, $filter,filterFilter, ngTableParams) {
    //Initialisation
    $scope.selectedregne = null;
    $scope.selectedphylum = null;
    $scope.selectedClasse = null;
    $scope.selectedOrdre = null;
    $scope.selectedFamille = null;
    //factorisation de l'url de l'appli
    var url_root = "http://92.222.107.92/taxhub/app_dev.php/";
    //mise à jour de la table ng-table
    var majTable = function(data){    
        $scope.tableData = data;
        $scope.tableParams.total($scope.tableData.length);
        $scope.tableParams.reload();
    }
    // $scope.getTaxons = function (callback) {
        // callback($scope.taxonsTaxref);
    // };

    //chargement initial et construction du tableau de résultats (découverte)
    // Préparation de la table ng-table du tableau de résultat offrant les fonctions de tri par colonne
    $http.get(url_root+"taxref/").success(function(response) {
        $scope.taxonsTaxref = response;
        $scope.tableParams = new ngTableParams({
            page: 1            // show first page
            ,count: 50           // count per page
            ,sorting: {
                nomLatin: 'asc'     // initial sorting
            }
        }, {
            total: $scope.taxonsTaxref.length, // length of data
            getData: function($defer, params) {
                // use build-in angular filter
                var orderedData = params.sorting() ? $filter('orderBy')($scope.taxonsTaxref, params.orderBy()) : $scope.taxonsTaxref;
                $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
            }
        });
        $scope.gridOptions = { 
            data: 'taxonsTaxref',
            showGroupPanel: true,
            jqueryUIDraggable: true
        };
    });
    
    //chargement de la liste des niveaux taxonomiques
    $http.get(url_root+"taxref/distinct/regne").success(function(response) {
        $scope.regnes = response;
    });
    $http.get(url_root+"taxref/distinct/phylum").success(function(response) {
        $scope.phylums = response;
    });
    $http.get(url_root+"taxref/distinct/classe").success(function(response) {
        $scope.classes = response;
    });
    $http.get(url_root+"taxref/distinct/ordre").success(function(response) {
        $scope.ordres = response;
    });
    $http.get(url_root+"taxref/distinct/famille").success(function(response) {
        $scope.familles = response;
    });
    
    //--------Ecouteurs et rechargement des niveaux taxonomiques
    //recharge une liste de x taxons du niveau
    //regnes
    $scope.getTaxonsByRegne = function(regne){
        $http.get(url_root+"taxref/?regne="+regne).success(function(response) {
            $scope.taxonsTaxref = response;
            majTable($scope.taxonsTaxref);
            $scope.selectedPhylum = null;
            $scope.selectedClasse = null;
            $scope.selectedOrdre = null;
            $scope.selectedFamille = null;
            $scope.lb = null;
            $scope.cd = null;
        });
    }
    $scope.$watch("selectedRegne", function () {
        if($scope.selectedRegne){
            getTaxonsByRegne($scope.selectedRegne.regne);
        }
    },true);
    //phylums
    $scope.getTaxonsByPhylum = function(phylum){
        $http.get(url_root+"taxref/?phylum="+phylum).success(function(response) {
            $scope.taxonsTaxref = response;
            majTable($scope.taxonsTaxref);
            $scope.selectedRegne = null;
            $scope.selectedClasse = null;
            $scope.selectedOrdre = null;
            $scope.selectedFamille = null;
            $scope.lb = null;
            $scope.cd = null;
        });
    }
    $scope.$watch("selectedPhylum", function () {
        if($scope.selectedPhylum){
            getTaxonsByPhylum($scope.selectedPhylum.phylum);
        }
    },true);
    //classes
    $scope.getTaxonsByClasse = function(classe){
        $http.get(url_root+"taxref/?classe="+classe).success(function(response) {
            $scope.taxonsTaxref = response;
            majTable($scope.taxonsTaxref);
            $scope.selectedRegne = null;
            $scope.selectedPhylum = null;
            $scope.selectedOrdre = null;
            $scope.selectedFamille = null;
            $scope.lb = null;
            $scope.cd = null;
        });
    }
    $scope.$watch("selectedClasse", function () {
        if($scope.selectedClasse){
            getTaxonsByClasse($scope.selectedClasse.classe);
        }
    },true);
    //ordres
    $scope.getTaxonsByOrdre = function(ordre){
        $http.get(url_root+"taxref/?ordre="+ordre).success(function(response) {
            $scope.taxonsTaxref = response;
            majTable($scope.taxonsTaxref);
            $scope.selectedRegne = null;
            $scope.selectedPhylum = null;
            $scope.selectedClasse = null;
            $scope.selectedFamille = null;
            $scope.lb = null;
            $scope.cd = null;
        });
    }
    $scope.$watch("selectedOrdre", function () {
        if($scope.selectedOrdre){
            getTaxonsByOrdre($scope.selectedOrdre.ordre);
        }
    },true);
    //familles
    $scope.getTaxonsByFamille = function(famille){
        $http.get(url_root+"taxref/?famille="+famille).success(function(response) {
            $scope.taxonsTaxref = response;
            majTable($scope.taxonsTaxref);
            $scope.selectedRegne = null;
            $scope.selectedPhylum = null;
            $scope.selectedClasse = null;
            $scope.selectedOrdre = null;
            $scope.lb = null;
            $scope.cd = null;
        });
    }
    $scope.$watch("selectedFamille", function () {
        if($scope.selectedFamille){
            getTaxonsByFamille($scope.selectedFamille.famille);
        }
    },true);
    
    $scope.findLbNom = function(lb) {
        $http.get(url_root+"taxref/?ilike="+lb).success(function(response) {
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
    
    $scope.findCdNom = function(cd) {
        $http.get(url_root+"taxref/?cdNom="+cd).success(function(response) {
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
    
    
    //-----------------------Pageslide directive-----------------------------------------------
    //gestion du bandeau d'information sur le taxon sélectioné - Position TOP
    $scope.isOpenInfoTaxon = false; // This will be binded using the ps-open attribute
    $scope.toggleInfoTaxon = function(id){
        if(id!=null){
            $http.get(url_root+"taxref/"+id).success(function(response) {
                $scope.selectedTaxon = response;
            });
        }
        $scope.isOpenInfoTaxon = true;
        if($scope.isOpenInfoTaxon){
            $scope.isOpenSearchTaxon=false;
            $scope.labelSearchTaxon = "Afficher la Recherche"
        }
    }
    //gestion du bandeau de recherche  - Position LEFT
    $scope.isOpenSearchTaxon = true; // This will be binded using the ps-open attribute
    $scope.labelSearchTaxon = "Masquer la Recherche";
    $scope.toggleSearchTaxon = function(){
        $scope.isOpenSearchTaxon = !$scope.isOpenSearchTaxon
        $scope.isOpenSearchTaxon ? $scope.labelSearchTaxon = "Afficher la Recherche" : $scope.labelSearchTaxon = "Afficher la Recherche";
        $scope.isOpenInfoTaxon=false;
    }
    
    //-------------------------------------modal form todo-------------------------------------
    $scope.addTaxon = function(tax) {
        // alert('Todo : ajouter le taxon '+tax.lb_nom+' à bib_taxons.');
        $scope.modal = {
          "title": "Todo",
          "content": "Ajouter le taxon '"+tax.lb_nom+"' à bib_taxons !"
        };
    };
});