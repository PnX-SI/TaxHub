var app = angular.module('taxonsApp', ['ngRoute','ngTable','ui.bootstrap', 'toaster', 'ngCookies'])
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
    $rootScope.$on('$routeChangeStart', function (event, next, current) {
      if (!next.access) return;
      if (next.access.restricted) {
        (next.access.level === undefined) ? level = 0 : level= next.access.level;
        if ((loginSrv.getToken() !== undefined) && (level <= loginSrv.getCurrentUser().id_droit_max)) return;
        $location.path('/login');
      }
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
                controllerAs: 'ctrl',
                access: {restricted: true, "level":1}
            })
            .when('/taxon/:id', {
                templateUrl: 'app/bib_taxon/detail/taxons-detail.html',
                controller: 'taxonsDetailCtrl',
                controllerAs: 'ctrl'
            }).otherwise({redirectTo: '/taxref'});
    }
]);
