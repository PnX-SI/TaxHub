app.service('loginSrv', ['$cookies','backendCfg', function ($cookies, backendCfg) {
    var currentUser={};
    var token;
    return {
        logout: function () {
          $cookies.remove('token',{ path: '/' });
          $cookies.remove('currentUser',{ path: '/' });
        },
        getCurrentUser: function () {
          return $cookies.getObject('currentUser');
        },
        setCurrentUser: function(value, expireDate) {
          $cookies.putObject('currentUser', value, {'expires': expireDate+'Z', path:'/'});
        },
        getToken: function() {
          return $cookies.get('token');
        },
        setToken: function(value) {
          $cookies.put('token', value);
        },
        getCurrentUserRights () {
          userRights = {
            'admin':false,
            'high':false,
            'medium':false,
            'low':false
          }
          if ($cookies.getObject('currentUser')) {
              switch  ($cookies.getObject('currentUser').id_droit_max){
                  case backendCfg.user_admin_privilege:
                      userRights.admin = true;
                      userRights.high=true;
                      userRights.medium=true;
                      userRights.low=true;
                      break;
                  case backendCfg.user_high_privilege:
                      userRights.high=true;
                      userRights.medium=true;
                      userRights.low=true;
                      break;
                  case backendCfg.user_medium_privilege:
                      userRights.medium=true;
                      userRights.low=true;
                      break;
                  case backendCfg.user_low_privilege:
                      userRights.low=true;
                      break;
              }
          }
          return userRights;
        }

    };
}]);

app.directive('loginFormDirective', ['$http', 'loginSrv','$uibModal','toaster','$route','$timeout',
function ($http, loginSrv, $uibModal,toaster, $route,$timeout) {
  return {
    restrict: 'AE',
    templateUrl:'static/app/login/loginlogout-template.html',
    scope : {
    },
    link:function($scope, $element, $attrs) {
      var toasterMsg = {
        'saveSuccess':{"title":"Connexion réussie"},
        'saveError':{"title":"Erreur d'identification"},
      }
      $scope.user = loginSrv.getCurrentUser();

      var refreshPage = function() {
        $timeout(function () {
            $route.reload();
        }, 0);
      }

      $scope.logout= function () {
        $scope.user = loginSrv.logout();
        refreshPage();
      }

      $scope.open = function (size) {
        var modalLoginInstance = $uibModal.open({
          templateUrl: 'loginModal.html',
          controller: 'ModalLoginFormCtrl',
          size: size
        });
        modalLoginInstance.result.then(function () {
          $scope.user = loginSrv.getCurrentUser();
          if (loginSrv.getToken()) {
            toaster.pop('success', toasterMsg.saveSuccess.title, toasterMsg.saveSuccess.msg, 3000, 'trustedHtml');
            refreshPage();
          }
          else {
            toaster.pop('error', toasterMsg.saveError.title, '', 5000, 'trustedHtml');
          }
        }, function () {
          console.log('Modal dismissed at: ' + new Date());
        });
      };

    }
  }
}]);

app.controller('ModalLoginFormCtrl', [ '$scope', '$http', '$uibModalInstance', 'loginSrv','backendCfg',
  function ($scope, $http, $uibModalInstance, loginSrv, backendCfg) {

  $scope.sumbit = function () {
    $http.post(backendCfg.api_url + 'auth/login',
        {"login":$scope.login, "password": $scope.password, "id_application":backendCfg.id_application}
      )
      .then(function(response) {
        loginSrv.setCurrentUser(response.data.user, response.data.expires);
      })
      // .catch(function(response) {
        // console.error('Repos error', response.status, response.data);
      // })
      .finally(function() {
        $uibModalInstance.close($scope.login);
      });
  };

  $scope.cancel = function () {
    $uibModalInstance.dismiss('cancel');
  };
}]);
