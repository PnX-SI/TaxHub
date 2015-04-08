var app = angular.module('taxonsApp', ['mgcrea.ngStrap.modal','ngTable']);
app.controller('taxrefCtrl', function($scope, $http, filterFilter) {
    //taxref
    $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/").success(function(response) {
        $scope.taxonsTaxref = response; 
    });
    $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/distinct/regne").success(function(response) {
        $scope.regnes = response;
    });
    $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/distinct/phylum").success(function(response) {
        $scope.phylums = response;
    });
    $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/distinct/classe").success(function(response) {
        $scope.classes = response;
    });
    $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/distinct/ordre").success(function(response) {
        $scope.ordres = response;
    });
    $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/distinct/famille").success(function(response) {
        $scope.familles = response;
    });
    
    
    $scope.$watch("selectedRegne", function () {
        if($scope.selectedRegne){
            $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/?regne="+$scope.selectedRegne.regne).success(function(response) {
                $scope.taxonsTaxref = response;
                $scope.selectedphylum = null;
                $scope.selectedClasse = null;
                $scope.selectedOrdre = null;
                $scope.selectedFamille = null;
                $scope.lb = null;
                $scope.cd = null;
            });
        }
    },true);
    $scope.$watch("selectedPhylum", function () {
        if($scope.selectedPhylum){
            $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/?phylum="+$scope.selectedPhylum.phylum).success(function(response) {
                $scope.taxonsTaxref = response;
                $scope.selectedregne = null;
                $scope.selectedClasse = null;
                $scope.selectedOrdre = null;
                $scope.selectedFamille = null;
                $scope.lb = null;
                $scope.cd = null;
            });
        }
    },true);
    $scope.$watch("selectedClasse", function () {
        if($scope.selectedClasse){
            $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/?classe="+$scope.selectedClasse.classe).success(function(response) {
                $scope.taxonsTaxref = response;
                $scope.selectedregne = null;
                $scope.selectedphylum = null;
                $scope.selectedOrdre = null;
                $scope.selectedFamille = null;
                $scope.lb = null;
                $scope.cd = null;
            });
        }
    },true);
    $scope.$watch("selectedOrdre", function () {
        if($scope.selectedOrdre){
            $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/?ordre="+$scope.selectedOrdre.ordre).success(function(response) {
                $scope.taxonsTaxref = response;
                $scope.selectedregne = null;
                $scope.selectedphylum = null;
                $scope.selectedClasse = null;
                $scope.selectedFamille = null;
                $scope.lb = null;
                $scope.cd = null;
                
            });
        }
    },true);
    $scope.$watch("selectedFamille", function () {
        if($scope.selectedFamille){
            $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/?famille="+$scope.selectedFamille.famille).success(function(response) {
                $scope.taxonsTaxref = response;
                $scope.selectedregne = null;
                $scope.selectedphylum = null;
                $scope.selectedClasse = null;
                $scope.selectedOrdre = null;
            });
        }
    },true);
    
    $scope.findLbNom = function(lb) {
        $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/?ilike="+lb).success(function(response) {
            $scope.taxonsTaxref = response;
            $scope.selectedregne = null;
            $scope.selectedphylum = null;
            $scope.selectedClasse = null;
            $scope.selectedOrdre = null;
            $scope.selectedFamille = null;
            $scope.cd = null;
            $scope.taxonsTaxref = response;
        });
    };
    
    $scope.findCdNom = function(cd) {
        $http.get("http://92.222.107.92/qtaxhub/web/app_dev.php/taxref/?cdNom="+cd).success(function(response) {
            $scope.taxonsTaxref = response;
            $scope.selectedregne = null;
            $scope.selectedphylum = null;
            $scope.selectedClasse = null;
            $scope.selectedOrdre = null;
            $scope.selectedFamille = null;
            $scope.lb = null;
            $scope.taxonsTaxref = response;
        });
    };
    $scope.addTaxon = function(tax) {
        // alert('Todo : ajouter le taxon '+tax.lb_nom+' à bib_taxons.');
        $scope.modal = {
          "title": "Todo",
          "content": "Ajouter le taxon '"+tax.lb_nom+"' à bib_taxons !"
        };
    };
});