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
.run(['$rootScope', '$location', 'locationHistoryService','loginSrv','toaster',
  function($rootScope, $location, locationHistoryService,loginSrv, toaster){
    $rootScope.$on('$routeChangeStart', function (event, next, current) {
      if (!next.access) return;
      if (next.access.restricted) {
        (next.access.level === undefined) ? level = 0 : level= next.access.level;
        if ((loginSrv.getToken() !== undefined) && (level <= loginSrv.getCurrentUser().id_droit_max)) return;
        toaster.pop('error', 'Vous devez être logger et avoir un niveau de droit suffisant', '', 2000, 'trustedHtml');
        $location.path(current);
      }
    });
}]);
app.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider
            .when('/login', {
                templateUrl: 'static/app/login/form.html',
                controller: 'loginFormCtrl',
                controllerAs: 'ctrl'
            })
            .when('/taxref', {
                templateUrl: 'static/app/taxref/list/taxref.html',
                controller: 'taxrefCtrl',
                controllerAs: 'ctrl'
            })
            .when('/taxons', {
                templateUrl: 'static/app/bib_taxon/list/taxons.html',
                controller: 'taxonsListCtrl',
                controllerAs: 'ctrl'
            })
            .when('/listes', {
                templateUrl: 'static/app/bib_liste/list/listes.html',
                controller: 'taxonsCtrl'
            })
            .when('/taxonform/:action?/:id?', {
                templateUrl: 'static/app/bib_taxon/edit/taxons-form.html',
                controller: 'taxonsCtrl',
                controllerAs: 'ctrl',
                access: {restricted: true, "level":1}
            })
            .when('/taxon/:id', {
                templateUrl: 'static/app/bib_taxon/detail/taxons-detail.html',
                controller: 'taxonsDetailCtrl',
                controllerAs: 'ctrl'
            }).otherwise({redirectTo: '/taxref'});
    }
]);
