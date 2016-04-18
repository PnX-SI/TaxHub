var app = angular.module('taxonsApp', ['ngRoute','ngTable','ui.bootstrap','angucomplete-alt', 'toaster']);
app.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider
            /*.when('/', {
                templateUrl: 'app/taxref.html',
                controller: 'taxrefCtrl'
            })*/
            .when('/taxref', {
                templateUrl: 'app/taxref.html',
                controller: 'taxrefCtrl'
            }).
            when('/taxons', {
                templateUrl: 'app/taxons.html',
                controller: 'taxonsListCtrl'
            })
            .when('/listes', {
                templateUrl: 'app/listes.html',
                controller: 'taxonsCtrl'
            })
            .when('/addtaxon', {
                templateUrl: 'app/taxons-form.html',
                controller: 'taxonsCtrl'
            }).
            otherwise({
                redirectTo: '/taxref'
            });
    }
]);

