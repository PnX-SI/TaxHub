var app = angular.module('myApp', ['ngGrid']);
app.controller('MyCtrl', function($scope,$http) {
    $scope.myData = [{name: "Moroni", age: 50},
                     {name: "Tiancum", age: 43},
                     {name: "Jacob", age: 27},
                     {name: "Nephi", age: 29},
                     {name: "Enos", age: 34}];
    $http.get("http://92.222.107.92/damien/MyProject/web/app_dev.php/bibtaxons/").success(function(response) {
            $scope.taxons =  response;
            
    });
    $scope.gridOptions = { 
                data: 'taxons',
                showGroupPanel: true,
                jqueryUIDraggable: true
            };
});