app.service("loginSrv", [
  "$cookies",
  "backendCfg",
  function ($cookies, backendCfg) {
    return {
      logout: function () {
        localStorage.removeItem("tx_jwt");
        localStorage.removeItem("tx_current_user");
        localStorage.removeItem("tx_expire_at");
      },
      getCurrentUser: function () {
        return localStorage.getItem("tx_current_user");
      },
      setCurrentUser: function (value, expireDate, idToken) {
        localStorage.setItem("tx_jwt", idToken);
        localStorage.setItem("tx_current_user", JSON.stringify(value));
        localStorage.setItem("tx_expire_at", JSON.stringify(expireDate + "Z"));
      },
      getToken: function () {
        return localStorage.getItem("tx_jwt");
      },
      getCurrentUser() {
        var currentUser = localStorage.getItem("tx_current_user");
        if (!currentUser) {
          return null;
        } else {
          return JSON.parse(currentUser);
        }
      },
      _getExpiration() {
        const expiration = localStorage.getItem("tx_expire_at");
        return new Date(expiration);
      },
      isLoggedIn() {
        return new Date() < this._getExpiration();
      },
      getCurrentUserRights() {
        userRights = {
          admin: false,
          high: false,
          medium: false,
          low: false,
        };
        if (!this.isLoggedIn) {
          return userRights;
        }
        var currentUser = this.getCurrentUser();
        if (currentUser) {
          switch (currentUser.id_droit_max) {
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
      },
    };
  },
]);

app.directive("loginFormDirective", [
  "$http",
  "loginSrv",
  "$uibModal",
  "toaster",
  "$route",
  "$timeout",
  function ($http, loginSrv, $uibModal, toaster, $route, $timeout) {
    return {
      restrict: "AE",
      templateUrl: "static/app/login/loginlogout-template.html",
      scope: {},
      link: function ($scope, $element, $attrs) {
        var toasterMsg = {
          saveSuccess: { title: "Connexion réussie" },
          saveError: { title: "Erreur d'identification" },
        };
        $scope.user = loginSrv.getCurrentUser();
        $scope.isLoggedIn = loginSrv.isLoggedIn();

        var refreshPage = function () {
          $timeout(function () {
            $route.reload();
          }, 0);
        };

        $scope.logout = function () {
          $scope.user = loginSrv.logout();
          refreshPage();
        };

        $scope.open = function (size) {
          var modalLoginInstance = $uibModal.open({
            templateUrl: "loginModal.html",
            controller: "ModalLoginFormCtrl",
            size: size,
          });
          modalLoginInstance.result.then(
            function () {
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
            function () {
              console.log("Modal dismissed at: " + new Date());
            }
          );
        };
      },
    };
  },
]);

app.controller("ModalLoginFormCtrl", [
  "$scope",
  "$http",
  "$uibModalInstance",
  "loginSrv",
  "backendCfg",
  "cstSrv",
  function ($scope, $http, $uibModalInstance, loginSrv, backendCfg, cstSrv) {
    $scope.sumbit = function () {
      cstSrv.getConfig().then(function (response) {
        $http
          .post(backendCfg.api_url + "auth/login", {
            login: $scope.login,
            password: $scope.password,
            id_application: response.id_application,
          })
          .then(function (response) {
            loginSrv.setCurrentUser(
              response.data.user,
              response.data.expires,
              response.data.idToken
            );
          })
          .finally(function () {
            $uibModalInstance.close($scope.login);
          });
      });
    };

    $scope.cancel = function () {
      $uibModalInstance.dismiss("cancel");
    };
  },
]);
