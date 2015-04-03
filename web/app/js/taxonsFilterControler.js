var app = angular.module('taxonsApp', []);
app.controller('taxonsFilterControler', function($scope, $http) {
        //liste taxons   
        // $http.get("js/bib_taxons.json").success(function(response) {$scope.taxons = response;});
        $http.get("http://92.222.107.92/damien/MyProject/web/app_dev.php/bibtaxons/taxonomie").success(function(response) {
            $scope.taxonomie = response;
			//$scope.regne = taxonomie.regne;
            });
});
