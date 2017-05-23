var app = angular.module('taxonsApp', ['ngRoute', 'ngTable', 'ui.bootstrap',
    'angular.filter', 'ngSanitize', 'ngCsv', 'toaster', 'ngCookies',
    'ngFileUpload', 'dialogs.main'
  ])
  .service('locationHistoryService', function() {
    return {
      previousLocation: null,

      store: function(location) {
        //@TODO COMPRENDRE
        this.previousLocation = location.replace('#!/', '');
      },

      get: function() {
        return this.previousLocation;
      }
    }
  })
  .run(['$rootScope', '$location', 'locationHistoryService', 'loginSrv',
    'toaster',
    function($rootScope, $location, locationHistoryService, loginSrv, toaster) {
      $rootScope.$on('$routeChangeStart', function(event, next, current) {
        //Stockage de la dernière route
        if (current) {
          locationHistoryService.store(location.hash);
        } else {
          current = '/';
        }
        if (!next.access) return;

        if (next.access.restricted) {
          (next.access.level === undefined) ? level = 0: level = next.access
            .level;
          if ((loginSrv.getToken() !== undefined) && (level <= loginSrv.getCurrentUser()
              .id_droit_max)) return;
          toaster.pop('error',
            'Vous devez être identifié et avoir un niveau de droit suffisant',
            '', 2000, 'trustedHtml');
          $location.path(current);
        }
      });
    }
  ]);
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
        templateUrl: 'static/app/bib_nom/list/bibNom-list-tpl.html',
        controller: 'bibNomListCtrl',
        controllerAs: 'ctrl'
      })
      .when('/listes', {
        templateUrl: 'static/app/bib_liste/list/bibliste-list-tpl.html',
        controller: 'listesCtrl',
        controllerAs: 'ctrl'
      })
      .when('/listes/add', {
        templateUrl: 'static/app/bib_liste/add/bibliste-add-tpl.html',
        controller: 'bibListeAddCtrl',
        controllerAs: 'ctrl'
      })
      .when('/listes/add/:id?', {
        templateUrl: 'static/app/bib_liste/add/bibliste-add-tpl.html',
        controller: 'bibListeAddCtrl',
        controllerAs: 'ctrl'
      })
      .when('/listes/:action?/:id?', {
        templateUrl: 'static/app/bib_liste/edit/bibliste-edit-tpl.html',
        controller: 'bibListeEditCtrl',
        controllerAs: 'ctrl'
      })
      .when('/listes/:id', {
        templateUrl: 'static/app/bib_liste/detail/bibliste-detail-tpl.html',
        controller: 'bibListeDetailCtrl',
        controllerAs: 'ctrl'
      })
      .when('/taxonform/:action?/:id?', {
        templateUrl: 'static/app/bib_nom/edit/bibNom-form-tpl.html',
        controller: 'bibNomFormCtrl',
        controllerAs: 'ctrl',
        access: {
          restricted: true,
          "level": 1
        }
      })
      .when('/taxon/:id', {
        templateUrl: 'static/app/bib_nom/detail/bibNom-detail-tpl.html',
        controller: 'bibNomDetailCtrl',
        controllerAs: 'ctrl'
      }).otherwise({
        redirectTo: '/taxref'
      });
  }
]);
