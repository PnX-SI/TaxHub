app.service('loginSrv', ['$cookies', function ($cookies) {
    var currentUser={};
    var token;
    return {
        getCurrentUser: function () {
          return $cookies.getObject('currentUser');
        },
        setCurrentUser: function(value) {
          $cookies.putObject('currentUser', value);
        },
        getToken: function() {
          return $cookies.get('token');
        },
        setToken: function(value) {
          $cookies.put('token', value);
        }
    };
}]);
app.directive('loginFormDirective', ['$http', 'loginSrv', 'backendCfg', '$uibModal','toaster',
function ($http, loginSrv, backendCfg, $uibModal,toaster) {
  return {
    restrict: 'AE',
    templateUrl:'static/app/login/loginlogout-template.html',
    scope : {
    },
    link:function($scope, $element, $attrs) {
      var toasterMsg = {
        'saveSuccess':{"title":"Connexion réussi"},
        'saveError':{"title":"Erreur d'identification"},
      }


      $scope.user = loginSrv.getCurrentUser();
      $scope.logout= function () {
        $scope.user = loginSrv.setCurrentUser();
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
            toaster.pop('success', toasterMsg.saveSuccess.title, toasterMsg.saveSuccess.msg, 1000, 'trustedHtml');
          }
          else {
            toaster.pop('error', toasterMsg.saveError.title, '', 1000, 'trustedHtml');
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
      ).success(function(response) {
        loginSrv.setCurrentUser(response.user);
      })
      .error(function(data, status) {
        console.error('Repos error', status, data);
      })
      .finally(function() {
        $uibModalInstance.close($scope.login);
      });
  };

  $scope.cancel = function () {
    $uibModalInstance.dismiss('cancel');
  };
}]);
