app.controller('bibListeEditCtrl', ['$scope',  '$http', '$uibModal',
  '$route', '$routeParams', 'NgTableParams', 'toaster', 'backendCfg',
  'loginSrv', 'bibListesSrv','$location', '$q',
  function($scope, $http, $uibModal, $route, $routeParams,
    NgTableParams, toaster, backendCfg, loginSrv, bibListesSrv,$location, $q) {
    var self = this;
    self.route = 'listes';
    self.showSpinner = true;
    self.pictos_propose = [];
    self.edit_detailliste = {
      "id_liste": "",
      "code_liste": "",
      "nom_liste": "",
      "desc_liste": "",
      "picto": "images/pictos/nopicto.gif",
      "regne": "",
      "group2_inpn": ""
    };
    self.edit_picto_db = [];
    self.edit_picto_projet = [];
    list_prototype = {};


    self.action = $routeParams.action;


    //----------------------Gestion des droits---------------//
    if (loginSrv.getCurrentUser()) {
      self.userRightLevel = loginSrv.getCurrentUser().id_droit_max;
      // gestion de l'onglet actif ; 0 par default
      if (self.userRightLevel == backendCfg.user_low_privilege) {
        self.activeForm = 2;
      }
    }
    self.userRights = loginSrv.getCurrentUserRights();

    $q.all(
      [
        (function () {
          if ((self.action == 'edit') && ($routeParams.id)) {
            return $http.get(backendCfg.api_url + "biblistes/" + $routeParams.id).then(
              function(res) {
                self.edit_detailliste = res.data;
                list_prototype = angular.copy(self.edit_detailliste);
                if (res.data.regne == null) res.data.regne = "";
              });
          }
          else {
            var deferred = $q.defer();
            deferred.resolve();
            return deferred.promise;
          }
        })(),
        //----------------------- Get list of id_list and nom_list
        bibListesSrv.getListes().then(
          function() {
            self.edit_nom_liste = [];
            self.existing_id_liste = [];
            bibListesSrv.listeref.data.forEach(function(v, k, map){
              self.edit_nom_liste.push(v.nom_liste);
              self.existing_id_liste.push(v.id_liste);
            })
          }
        ),
        //-----------------------Get list inpn regne and group-----------------------------------------
        $http.get(backendCfg.api_url + "taxref/regnewithgroupe2").then(function(response) {
            self.taxref_regne_group = response.data;
        }),
        //-----------------------Get list of picto in dossier ./static/images/pictos -----------------------------------------------
        $http.get(backendCfg.api_url + "biblistes/pictosprojet").then(function(response) {
            self.pictos_propose = response.data;
        })
      ]
    ).then(function(value) {
      //----- stop spinner ------
      self.showSpinner = false;
    }, function(error) {
        console.log(error);
    });


    var toasterMsg = {
      'saveSuccess': {
        "title": "Liste enregistré",
        "msg": "La liste a été enregistré avec succès"
      },
      'submitError_nom_liste': {
        "title": "Nom de la liste existe déjà"
      },
      'submitInfo_nothing_change': {
        "title": "L'Information de la liste ne change pas"
      },
      'submitError_id_liste': {
        "title": "Id de la liste existe déjà"
      },
      'saveError': {
        "title": "Erreur d'enregistrement"
      },
    }

    self.submit = function() {
      var flow = true;

      // -- if data in form doesn't change -> toaster L'Information de la liste ne change pas
      if (JSON.stringify(list_prototype) === JSON.stringify(self.edit_detailliste)) {
        toaster.pop('info', toasterMsg.submitInfo_nothing_change.title, "", 5000, 'trustedHtml');
        flow = false;
      }
      //-- traiter id_liste, si il existe déjà, ne faire pas submit
      if (self.action == 'new') {
        var id = self.edit_detailliste.id_liste;
        if (self.existing_id_liste.filter(function(v) { return v == id }).length > 0) {
          toaster.pop('error', toasterMsg.submitError_id_liste.title, "", 5000, 'trustedHtml');
          flow = false;
        }
      }

      //-- traiter le nom, si il existe déjà, ne faire pas submit
      if (flow) {
        var new_list_name = self.edit_nom_liste.filter(removeCurrentListName);
        for (i = 0; i < new_list_name.length; i++){
          if (new_list_name[i] == self.edit_detailliste.nom_liste) {
            toaster.pop('error', toasterMsg.submitError_nom_liste.title, "", 5000, 'trustedHtml');
            flow = false;
            break;
          }
        }
      }

      // -- Submit
      if (flow) {
        var url = backendCfg.api_url + "biblistes/" + self.edit_detailliste   .id_liste;
        var res = $http.put(url, self.edit_detailliste, { withCredentials: true })
          .then(
            function(response) {
              toaster.pop('success', toasterMsg.saveSuccess.title, toasterMsg.saveSuccess.msg, 5000, 'trustedHtml');
              bibListesSrv.isDirty = true; // recharger interface liste-bibliste
              self.comebackListes();
            },
            function(response) {
              toaster.pop('error', toasterMsg.saveError.title, response.data.message, 5000, 'trustedHtml');
            }
          );
        }
    }

    self.cancel = function() {
      if (JSON.stringify(list_prototype) !== JSON.stringify(self.edit_detailliste)) {
        $route.reload();
      }
    };

    // ----- come back listes after success update
    self.comebackListes = function() {
        $location.path('listes').replace();
      }
      //--- a paramettre of javascript array.filtre(para)
    function removeCurrentListName(value) {
      return value != list_prototype.nom_liste;
    };
}
]);
