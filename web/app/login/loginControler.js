app.service('loginSrv', function () {
    var currentUser;
    return {
        getCurrentUser: function () {
            return currentUser;
        },
        setCurrentUser: function(value) {
            currentUser = value;
        }
    };
});

app.controller('loginFormCtrl', [ '$scope','loginSrv','$location','toaster',
  function($scope, loginSrv, $location, toaster) {
    var self = this;
    self.route='login';

    var toasterMsg = {
      'saveSuccess':{"title":"Connexion réussi"},
      'saveError':{"title":"Erreur d'identification"},
    }

    self.users = {
      1: {"name":"admin", "login":"demo.admin", "password":"admin", "droit":6},
      2: {"name":"user", "login":"demo.user", "password":"user", "droit":2}
    };

    self.log =function () {
      loginSrv.setCurrentUser(null);
      angular.forEach(self.users, function(value, key) {
        if ((value.login == self.login) && (value.password == self.password)) {
          loginSrv.setCurrentUser(value);
        }
      });

      if (loginSrv.getCurrentUser()) {
        toaster.pop('success', toasterMsg.saveSuccess.title, toasterMsg.saveSuccess.msg, 5000, 'trustedHtml');
        $location.path('/');
      }
      else {
        toaster.pop('error', toasterMsg.saveError.title, '', 5000, 'trustedHtml');
        console.log("login error");
      }
    };
}]);
