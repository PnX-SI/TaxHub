var app = angular.module('taxonsApp', ['mgcrea.ngStrap.modal']);
app.controller('taxonsCtrl', function($scope, $http) {
        
        
        $scope.alertTaxon = function(tax) {
            $scope.modal = {
              "title": "Todo",
              "content": "Ajouter le taxon '"+tax.lb_nom+"' à bib_taxons !"
            };
        };
        
        
        //formulaire taxons
        $scope.listeRouge = [
            {"lrCode":"EX"}
            ,{"lrCode":"EW"}
            ,{"lrCode":"RE"}
            ,{"lrCode":"CR"}
            ,{"lrCode":"EN"}
            ,{"lrCode":"VU"}
            ,{"lrCode":"NT"}
            ,{"lrCode":"LC"}
            ,{"lrCode":"DD"}
            ,{"lrCode":"NA"}
            ,{"lrCode":"NE"}
        ];
        // action = '';
        $scope.fFrName = '';
        $scope.fLatinName = '';
        $scope.fAuteur = '';
        $scope.fCdnom = '';
        $scope.fFiltre0 = '';
        $scope.fFiltre1 = '';
        // $scope.fIdtaxon = '';
        $scope.edit = true;
        $scope.error = false;
        $scope.incomplete = false;
        $scope.errors = [];
        $scope.msgs = [];
        $scope.oks = [];
        
        $scope.newTaxon = function() {
            // $scope.fIdtaxon = ''; 
            $scope.errors.splice(0, $scope.errors.length); // remove all error messages
            $scope.oks.splice(0, $scope.oks.length);
        };
        
        $scope.$watch('fFrName', function() {$scope.test();});
        $scope.$watch('fLatinName', function() {$scope.test();});
        $scope.$watch('fAuteur', function() {$scope.test();});
        $scope.$watch('fCdnom', function() {$scope.test();});

        // $scope.$watch('fIdtaxon', function() {$scope.test();});

        $scope.test = function() {
            $scope.incomplete = false;
            if ($scope.edit && (!$scope.fFrName.length || !$scope.fLatinName.length || !$scope.fAuteur.length || !$scope.fCdnom.length)) {
                $scope.incomplete = true;
            }
        };
        
        $scope.save = function() {
            $scope.errors.splice(0, $scope.errors.length); // remove all error messages
            $scope.oks.splice(0, $scope.oks.length);
            $http.post("http://92.222.107.92/damien/MyProject/web/app_dev.php/bibtaxons", {
                'nomFrancais': $scope.fFrName
                ,'nomLatin': $scope.fLatinName
                ,'auteur': $scope.fAuteur
                ,'cdNom': $scope.fCdnom
                ,'Filtre0': $scope.fFiltre0
                ,'Filtre1': $scope.fFiltre1
                // ,'id_taxon': $scope.fIdtaxon
            }
            ).success(function(data, status, headers, config) {
                if (data.success == true){
                    $scope.oks.push(data.message);
                    $scope.edit = true;
                    $scope.incomplete = true;
                    $scope.fFrName = '';
                    $scope.fLatinName = '';
                    $scope.fAuteur = '';
                    $scope.fCdnom = '';
                    $scope.fFiltre0 = '';
                    $scope.fFiltre1 = '';
                }
                if (data.success == false){
                    $scope.errors.push(data.message);
                }

            }).error(function(data, status, headers, config) { // called asynchronously if an error occurs or server returns response with an error status.
                $scope.errors.push(data.message);
            });
        };
    });