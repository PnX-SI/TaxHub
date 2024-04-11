app.service("loginSrv", [
  "backendCfg",
  function(backendCfg) {
    var currentUser = {};
    var token;
    return {
      logout: function() {
        localStorage.removeItem("current_user");
        //TODO : call logout func
      },
      getCurrentUser: function() {
        let current_user = localStorage.getItem("current_user");
        return JSON.parse(current_user)
      },
      setCurrentUser: function(token, user, expireDate) {
        localStorage.setItem("th_id_token", token)
        localStorage.setItem('expires_at', expireDate);
        localStorage.setItem('current_user', JSON.stringify(user));

      },
      getExpiration() {
        const expiration = localStorage.getItem('expires_at');
        return Date(expiration);
      },
      isLoggedIn() {
        return Date() <= this.getExpiration();
      },
      getToken: function() {
        return localStorage.getItem("th_id_token")
      },
      getCurrentUserRights() {
        userRights = {
          admin: false,
          high: false,
          medium: false,
          low: false
        };
        if (this.isLoggedIn() && this.getCurrentUser()) {
          switch (this.getCurrentUser().max_level_profil) {
            case backendCfg.user_admin_privilege:
              userRights.admin = true;
              userRights.high = true;
              userRights.medium = true;
              userRights.low = true;
              break;
            case backendCfg.user_high_privilege:
              userRights.high = true;
              userRights.medium = true;
              userRights.low = true;
              break;
            case backendCfg.user_medium_privilege:
              userRights.medium = true;
              userRights.low = true;
              break;
            case backendCfg.user_low_privilege:
              userRights.low = true;
              break;
          }
        }
        return userRights;
      }
    };
  }
]);

app.directive("loginFormDirective", [
  "$http",
  "loginSrv",
  "$uibModal",
  "toaster",
  "$route",
  "$timeout",
  function($http, loginSrv, $uibModal, toaster, $route, $timeout) {
    return {
      restrict: "AE",
      templateUrl: "static/app/login/loginlogout-template.html",
      scope: {},
      link: function($scope, $element, $attrs) {
        var toasterMsg = {
          saveSuccess: { title: "Connexion réussie" },
          saveError: { title: "Erreur d'identification" }
        };
        $scope.user = loginSrv.getCurrentUser();

        var refreshPage = function() {
          $timeout(function() {
            $route.reload();
          }, 0);
        };

        $scope.logout = function() {
          $scope.user = loginSrv.logout();
          refreshPage();
        };

        $scope.open = function(size) {
          var modalLoginInstance = $uibModal.open({
            templateUrl: "loginModal.html",
            controller: "ModalLoginFormCtrl",
            size: size
          });
          modalLoginInstance.result.then(
            function() {
              $scope.user = loginSrv.getCurrentUser();
              if (loginSrv.getToken() && $scope.user) {
                toaster.pop(
                  "success",
                  toasterMsg.saveSuccess.title,
                  toasterMsg.saveSuccess.msg,
                  3000,
                  "trustedHtml"
                );
                refreshPage();
              } else {
                toaster.pop(
                  "error",
                  toasterMsg.saveError.title,
                  "",
                  5000,
                  "trustedHtml"
                );
              }
            },
            function() {
              console.log("Modal dismissed at: " + new Date());
            }
          );
        };
      }
    };
  }
]);

app.controller("ModalLoginFormCtrl", [
  "$scope",
  "$http",
  "$uibModalInstance",
  "loginSrv",
  "backendCfg",
  "cstSrv",
  function($scope, $http, $uibModalInstance, loginSrv, backendCfg, cstSrv) {
    $scope.sumbit = function() {
      cstSrv.getConfig().then(
        function (response) {
          $http
          .post(backendCfg.api_url + "auth/login", {
            login: $scope.login,
            password: $scope.password,
            id_application: response.id_application
          })
          .then(function(response) {
            loginSrv.setCurrentUser(response.data.token, response.data.user, response.data.expires);
          })
          .finally(function() {
            $uibModalInstance.close($scope.login);
          });
        }
      )
    };

    $scope.cancel = function() {
      $uibModalInstance.dismiss("cancel");
    };
  }
]);
