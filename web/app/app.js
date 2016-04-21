var app = angular.module('taxonsApp', ['ngRoute','ngTable','ui.bootstrap', 'toaster'])
.service('locationHistoryService', function(){
    return {
        previousLocation: null,

        store: function(location){
            this.previousLocation = location;
        },

        get: function(){
            return this.previousLocation;
        }
      }
})
.run(['$rootScope', '$location', 'locationHistoryService', function($rootScope, $location, locationHistoryService){
    $rootScope.$on('$locationChangeSuccess', function(e, newLocation, oldLocation){
        locationHistoryService.store(oldLocation);
    });
}]);
app.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider
            .when('/taxref', {
                templateUrl: 'app/taxref/list/taxref.html',
                controller: 'taxrefCtrl',
                controllerAs: 'ctrl'
            })
            .when('/taxons', {
                templateUrl: 'app/bib_taxon/list/taxons.html',
                controller: 'taxonsListCtrl',
                controllerAs: 'ctrlBibTaxon'
            })
            .when('/listes', {
                templateUrl: 'app/bib_liste/list/listes.html',
                controller: 'taxonsCtrl'
            })
            .when('/taxonform/:action?/:id?', {
                templateUrl: 'app/bib_taxon/edit/taxons-form.html',
                controller: 'taxonsCtrl',
                controllerAs: 'ctrl'
            })
            .when('/taxon/:id', {
                templateUrl: 'app/bib_taxon/detail/taxons-detail.html',
                controller: 'taxonsDetailCtrl',
                controllerAs: 'ctrl'
            }).
            otherwise({
                redirectTo: '/taxref'
            });
    }
]);
