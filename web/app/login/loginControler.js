app.service('loginSrv', function () {
    var currentUser={};
    var token;
    return {
        getCurrentUser: function () {
          return currentUser;
        },
        setCurrentUser: function(value) {
          currentUser = value;
        },
        getToken: function() {
          return token;
        },
        setToken: function(value) {
          token = value;
        }
    };
});

app.controller('loginFormCtrl', [ '$scope','loginSrv','$http', '$location','toaster','backendCfg',
  function($scope, loginSrv, $http, $location, toaster, backendCfg) {
    var self = this;
    self.route='auth/login';

    var toasterMsg = {
      'saveSuccess':{"title":"Connexion réussi"},
      'saveError':{"title":"Erreur d'identification"},
    }

    self.log =function () {
      loginSrv.setCurrentUser(null);

      $http.post(backendCfg.api_url + self.route,
          {"login":self.login, "password": self.password, "id_application":backendCfg.id_application}
        ).success(function(response) {
          loginSrv.setToken(response.token);
          loginSrv.setCurrentUser(response.user);
        })
        .error(function(data, status) {
          console.error('Repos error', status, data);
        })
        .finally(function() {
          if (loginSrv.getToken()) {
            toaster.pop('success', toasterMsg.saveSuccess.title, toasterMsg.saveSuccess.msg, 5000, 'trustedHtml');
            $location.path('/');
          }
          else {
            toaster.pop('error', toasterMsg.saveError.title, '', 500, 'trustedHtml');
            console.log("login error");
          }
        });


    };
}]);
