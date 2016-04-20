var app = angular.module('taxonsApp', ['ngRoute','ngTable','ui.bootstrap', 'toaster']);
app.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider
            /*.when('/', {
                templateUrl: 'app/taxref.html',
                controller: 'taxrefCtrl'
            })*/
            .when('/taxref', {
                templateUrl: 'app/taxref/list/taxref.html',
                controller: 'taxrefCtrl',
                controllerAs: 'ctrl'
            }).
            when('/taxons', {
                templateUrl: 'app/bib_taxon/list/taxons.html',
                controller: 'taxonsListCtrl'
            })
            .when('/listes', {
                templateUrl: 'app/bib_liste/list/listes.html',
                controller: 'taxonsCtrl'
            })
            .when('/addtaxon', {
                templateUrl: 'app/bib_taxon/edit/taxons-form.html',
                controller: 'taxonsCtrl'
            }).
            otherwise({
                redirectTo: '/taxref'
            });
    }
]);
