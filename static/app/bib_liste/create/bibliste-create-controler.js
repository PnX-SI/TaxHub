app.controller('bibListeCreateCtrl', ['$scope', '$filter', '$http', '$uibModal',
  '$route', '$routeParams','$location', 'NgTableParams', 'toaster', 'backendCfg',
  'loginSrv','bibListesSrv','locationHistoryService',
  function($scope, $filter, $http, $uibModal, $route, $routeParams,$location,
    NgTableParams, toaster, backendCfg, loginSrv,bibListesSrv,locationHistoryService) {
    var self = this;
    self.route = 'listes';
    self.previousLocation = locationHistoryService.get();
    self.showSpinner = true;
    self.pictos_propose = [];
    self.edit_picto_db = [];
    self.formCreate = {
      "id_liste": "",
      "nom_liste": "",
      "desc_liste": "",
      "picto": "images/pictos/nopicto.gif",
      "regne": "",
      "group2_inpn": "Autres"
    };

    //----------------------Gestion des droits---------------//
    if (loginSrv.getCurrentUser()) {
      self.userRightLevel = loginSrv.getCurrentUser().id_droit_max;
      // gestion de l'onglet actif ; 0 par default
      if (self.userRightLevel == backendCfg.user_low_privilege) {
        self.activeForm = 2;
      }
    }
    self.userRights = loginSrv.getCurrentUserRights();


    //----------------------- Get list of id_liste-------------------------------------------
    $http.get(backendCfg.api_url + "biblistes/liste-de-id-liste").then(function(
      response) {
      self.create_id_liste = response.data;
    });
    //----------------------- Get list of nom_liste-------------------------------------------
    $http.get(backendCfg.api_url + "biblistes/liste-de-nom-liste").then(function(
      response) {
      self.create_nom_liste = response.data;
    });
    //-----------------------Get list of regne-----------------------------------------------
    $http.get(backendCfg.api_url + "biblistes/liste-de-regne").then(function(
      response) {
      self.create_regne = response.data;
    });
    //-----------------------Get list of group2_inpn-----------------------------------------
    $http.get(backendCfg.api_url + "biblistes/liste-de-group2_inpn").then(
      function(response) {
        self.create_group2_inpn = response.data;
      });
    //-----------------------Get list of picto  in database biblistes -------------------------
    $http.get(backendCfg.api_url + "biblistes/liste-de-picto-biblistes").then(
      function(response) {
        self.create_picto_db = response.data;
      });
    //-----------------------Get list of picto in dossier ./static/images/pictos --------------
    $http.get(backendCfg.api_url + "biblistes/liste-de-picto-projet").then(function(
      response) {
      self.create_picto_projet = response.data;

      //---- filter pictos
      self.pictos_propose = filterPics(self.create_picto_projet, self.create_picto_db);
      //----- stop spinner ------
      self.showSpinner = false;
    });


    var toasterMsg = {
      'createSuccess': {
        "title": "Taxon enregistré",
        "msg": "Le taxon a été enregistré avec succès"
      },
      'submitError_nom_liste': {
        "title": "Nom de la liste existe déjà"
      },
      'submitError_id_liste': {
        "title": "Id de la liste existe déjà"
      },
      'submitInfo_nothing_change': {
        "title": "L'Information de la liste ne change pas"
      },
      'createError': {
        "title": "Erreur de création"
      },
    }

    self.submit = function() {
      var flow = true;

      //-- traiter id_liste, si il existe déjà, ne faire pas submit
      for (i = 0; i < self.create_id_liste.length; i++)
        if (self.create_id_liste[i] == self.formCreate.id_liste) {
          toaster.pop('error', toasterMsg.submitError_id_liste.title, "",
            5000, 'trustedHtml');
          flow = false;
          break;
        }

        //-- traiter nom_liste, si il existe déjà, ne faire pas submit
      if (flow)
        for (i = 0; i < self.create_nom_liste.length; i++)
          if (self.create_nom_liste[i] == self.formCreate.nom_liste) {
            toaster.pop('error', toasterMsg.submitError_nom_liste.title,
              "", 5000, 'trustedHtml');
            flow = false;
            break;
          }

          // -- Submit
      if (flow) {
        var url = backendCfg.api_url + "biblistes/" + self.formCreate
          .id_liste;
        var res = $http.post(url, self.formCreate, {
            withCredentials: true
          })
          .then(
            function(response) {
              var data = response.data;
              toaster.pop('success', toasterMsg.createSuccess.title,
                toasterMsg.createSuccess.msg + " Id liste: " + data.id_liste +
                " Nom liste: " + data.nom_liste, 5000, 'trustedHtml');
                if (self.previousLocation){ 
                  nextPath = self.previousLocation;
                  $location.path(nextPath).replace();
                }
                bibListesSrv.isDirty = true; // recharger interface liste-bibliste
            },
            function(response) {
              toaster.pop('error', toasterMsg.createError.title, response
                .data.message, 5000, 'trustedHtml');
            }
          );
        $route.reload();
      }
    }

    //---- filter pictos
    function filterPics(picto_projet, picto_db) {
      var pictos_propose = [];

      // ----- compare the difference into 2 pictos listes: on database and in projet
      // ----- then save the differeces pictos into an array.
      // ----- use this array as the options for selection list on interface

      for (i = 0; i < picto_projet.length; i++) {
        var path = "images/pictos/" + picto_projet[i];
        for (j = 0; j < picto_db.length; j++) {
          if (path.localeCompare(picto_db[j]) == 0) {
            break;
          }
          if (j == picto_db.length - 1)
            pictos_propose.push(picto_projet[i]);
        }
      }
      // -- add nopicto
      for (i = 0; i < pictos_propose.length; i++) {
        if (pictos_propose[i] === "nopicto.gif")
          break;
        if (i === pictos_propose.length - 1)
          pictos_propose.push("nopicto.gif");
      }

      return pictos_propose;
    }

  }
]);
