
app.controller('bibNomFormCtrl', [ '$scope', '$routeParams', '$http', '$uibModal', 'locationHistoryService',
  '$location', 'toaster', 'backendCfg','taxrefTaxonListSrv','bibNomListSrv', 'loginSrv',
function($scope, $routeParams, $http, $uibModal, locationHistoryService, $location, toaster,backendCfg, taxrefTaxonListSrv,bibNomListSrv, loginSrv) {
  var self = this;
  self.route='taxons';
  self.mediasPath = backendCfg.medias_path;
  self.bibNom = {};
  self.bibNom.attributs_values = {};
  self.previousLocation = locationHistoryService.get();
  self.hideSave = false;
  self.hideSaveButton = function(){self.hideSave = true;}
  self.showSaveButton = function(){self.hideSave = false;}
  self.showMediaForm=false;
  self.form = $scope.form;
  self.userRightLevel = 0;

  //----------------------Gestion des droits---------------//
  if (loginSrv.getCurrentUser()) {
      self.userRightLevel = loginSrv.getCurrentUser().id_droit_max;
      // gestion de l'onglet actif ; 0 par default
      if (self.userRightLevel==backendCfg.user_low_privilege) {
          self.activeForm = 2;
      }
  }
  self.userRights = loginSrv.getCurrentUserRights();


  var toasterMsg = {
    'saveSuccess':{"title":"Taxon enregistré", "msg": "Le taxon a été enregistré avec succès"},
    'saveError':{"title":"Erreur d'enregistrement"},
  }
  var getTaxonsInfo = function (cd_nom) {
    $http.get(backendCfg.api_url + "bibnoms/taxoninfo/"+cd_nom+"?forcePath=True").then(function(response) {
        if (response.data) {
            if (response.data.medias){
              self.disableMediasTab = false;
              self.bibNom.medias = response.data.medias;
            }
            self.bibNom.attributs_values = {};
            if (response.data.attributs) {
                angular.forEach(response.data.attributs, function(value, key) {
                if (value.type_widget==="number") value.valeur_attribut = Number(value.valeur_attribut);
                    self.bibNom.attributs_values[value.id_attribut] =  value.valeur_attribut;
                });
                delete self.bibNom.attributs;
            }
        }
    });
  }


  var action = $routeParams.action;
  var self = this;
  if ($routeParams.id) {
    if (action == 'new') {
        self.cd_nom = $routeParams.id;
        self.disableMediasTab = true;
        getTaxonsInfo(self.cd_nom);
    }
    else {
        self.disableMediasTab = false;
        self.id_nom = $routeParams.id;
        $http.get(backendCfg.api_url + "bibnoms/simple/"+self.id_nom).then(function(response) {
            if (response.data) {
                self.bibNom = response.data;
                self.cd_nom = response.data.cd_nom;
                getTaxonsInfo(self.cd_nom);
            }
        });
    }
  }


  $scope.$watch(function () {
    return self.cd_nom;
  }, function(newVal, oldVal) {
    if (newVal) {
      $http.get(backendCfg.api_url +"taxref/"+self.cd_nom).then(function(response) {
        self.taxref = response.data;
        self.bibNom.cd_nom = response.data.cd_nom;
        self.bibNom.nom_complet = response.data.nom_complet;
        self.bibNom.auteur = response.data.lb_auteur;
        if(!self.bibNom.nom_francais) self.bibNom.nom_francais = response.data.nom_vern;
        self.bibNom.cd_ref = response.data.cd_ref;
      });
    }
  });

  //------------------------------ Chargement de la listes des attributs ----------------------/
  ///bibattributs/Animalia/Autre
  $scope.$watch(function () {
    return self.taxref;
  }, function(newVal, oldVal) {
    if (newVal) {
        $http.get(backendCfg.api_url +"bibattributs/"+newVal.regne+"/"+newVal.group2_inpn)
        .then(function(response) {
          self.attributsDefList = response.data;
          angular.forEach(self.attributsDefList, function(theme, key) {
    				angular.forEach(theme.attributs, function(value, key) {
    					value.listeValeurObj =JSON.parse(value.liste_valeur_attribut);
    				});
          });
        });
        $http.get(backendCfg.api_url +"biblistes/"+newVal.regne+"/"+newVal.group2_inpn)
        .then(function(response) {
          self.listesDefList = response.data;
        });

        $http.get(backendCfg.api_url +"bibtypesmedia/")
        .then(function(response) {
          self.mediasTypes = response.data;
        });
    }
  });
  //------------------------------ Sauvegarde du formulaire ----------------------------------/
  self.submit = function() {
    var params = self.bibNom;
    var url = backendCfg.api_url +"bibnoms/";
    if(action == 'edit'){url=url+self.bibNom.id_nom;}
    $http.post(url, params, { withCredentials: true })
    .then(function(response) {
      var data = response.data
      if (data.success == true) {
        toaster.pop('success', toasterMsg.saveSuccess.title, toasterMsg.saveSuccess.msg, 5000, 'trustedHtml');
        var nextPath = 'taxon/'+data.id_nom;
        if (self.previousLocation) nextPath = self.previousLocation;
        $location.path(nextPath).replace();
        taxrefTaxonListSrv.isDirty = true;
        bibNomListSrv.isDirty = true;
      }
      if (data.success == false){
          toaster.pop('success', toasterMsg.saveError.title, data.message, 5000, 'trustedHtml');
      }
    })
    .catch(function(response) {
        toaster.pop('error', toasterMsg.saveError.title, response.data.message, 5000, 'trustedHtml');
    });
  }
  //---------------------Gestion de l'info taxon en modal------------------------------------
      self.openTaxrefDetail = function (id) {
        if(id!=null){
          var modalInstance = $uibModal.open({
            templateUrl: 'static/app/taxref/detail/taxrefDetailModal.html',
            controller: 'ModalInfoCtrl',
            size: 'lg',
            resolve: {idtaxon: id}
          });
        }
      };

      getOneTaxonDetail = function(id){
        return $http.get(backendCfg.api_url + "taxref/"+id)
          .then(function(response) {
               return response.data;
          });
      };
}
]);
