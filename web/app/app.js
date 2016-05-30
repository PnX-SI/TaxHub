var app = angular.module('taxonsApp', ['ngRoute','ngTable','ui.bootstrap', 'toaster'])
.service('locationHistoryService', function(){
    return {
        previousLocation: null,

        store: function(location){
            //@TODO COMPRENDRE
            this.previousLocation = location.replace('#/', '');;
        },

        get: function(){
            return this.previousLocation;
        }
      }
})
.run(['$rootScope', '$location', 'locationHistoryService','loginSrv',
  function($rootScope, $location, locationHistoryService,loginSrv ){
    $rootScope.$on('$locationChangeStart', function(e, newLocation, oldLocation, newState, oldState){
        locationHistoryService.store(window.location.hash);
        if (! loginSrv.getCurrentUser()) $location.path('/login');
    });
}]);
app.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider
            .when('/login', {
                templateUrl: 'app/login/form.html',
                controller: 'loginFormCtrl',
                controllerAs: 'ctrl'
            })
            .when('/taxref', {
                templateUrl: 'app/taxref/list/taxref.html',
                controller: 'taxrefCtrl',
                controllerAs: 'ctrl'
            })
            .when('/taxons', {
                templateUrl: 'app/bib_taxon/list/taxons.html',
                controller: 'taxonsListCtrl',
                controllerAs: 'ctrl'
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
            }).otherwise({redirectTo: '/taxref'});
    }
]);
