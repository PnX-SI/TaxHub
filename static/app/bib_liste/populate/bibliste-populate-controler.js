app.controller('bibListePopulateCtrl',[ '$scope','$filter', '$http','$uibModal','$route','$routeParams',
    'NgTableParams','toaster', 'backendCfg','loginSrv','bibListesSrv', '$q',
  function($scope,$filter, $http,$uibModal,$route, $routeParams,NgTableParams,toaster, backendCfg,loginSrv,bibListesSrv, $q) {
    var self = this;
    self.showSpinnerTaxons = true;
    self.showSpinnerListe = true;
    self.idListe = $routeParams.id;
    self.listName = {
      selectedList: [],
      availableOptions:[]
    };
    self.dataNoms = {
      availableNoms : [],
      existingNoms : [],
      existingNomsReserve : []
    };
    self.infoListe={};
    self.corNoms = {
      add : {},
      del : {},
      mvt : {}
    };

    bibListesSrv.getDetailListe(self.idListe).then(
      function(response) {
        self.infoListe = response.data;
      }
    )

    self.tableCols = {
      "nom_francais" : { title: "Nom français", show: true },
      "nom_complet" : {title: "Nom latin", show: true },
      "lb_auteur" : {title: "Auteur", show: true },
      "cd_nom" : {title: "cd nom", show: true },
      "id_nom" : {title: "id nom", show: true },
      "id_rang" : {title: "rang", show: true }
    };
    //----------------------Gestion des droits---------------//
    if (loginSrv.getCurrentUser()) {
        self.userRightLevel = loginSrv.getCurrentUser().id_droit_max;
        // gestion de l'onglet actif ; 0 par default
        if (self.userRightLevel==backendCfg.user_low_privilege) {
        self.activeForm = 2;
        }
    }
    self.userRights = loginSrv.getCurrentUserRights();

    //---------------------Initialisation des paramètres de ng-table---------------------
    self.tableParamsTaxons = new NgTableParams(
      {
          count: 10,
          sorting: {'nom_complet': 'asc'}
      },
      {
        getData: function (params) {
          self.showSpinnerTaxons = true;
          filters = {}
          angular.forEach(params.url(), function(value, key){
              if (key == 'count') filters.limit = params.url().count;
              else if (key == 'page') filters.page = params.url().page;
              else if (key.startsWith("sorting")){
                filters.orderby = key.replace('sorting[', '').replace(']', '');
                filters.order = value
              }
              else if (key.startsWith("filter")){
                column = key.replace('filter[', '').replace(']', '');
                filters[column] = value;
              }
          }, params);

          return bibListesSrv.getbibNomsList(self.idListe, false, filters).then(function(results) {
              params.total(results.data.total);
              self.showSpinnerTaxons = false;
              self.dataNoms.availableNoms = results.data.items

              self.filterDataTableWithDelAdd();
              return self.dataNoms.availableNoms || [];
          });
        }
      }
    );

    self.tableParamsDetailListe = new NgTableParams(
      {
          count: 10,
          sorting: {'nom_complet': 'asc'}
      },
      {
        getData: function (params) {
          self.showSpinnerListe = true;
          filters = {}
          angular.forEach(params.url(), function(value, key){
              if (key == 'count') filters.limit = params.url().count;
              else if (key == 'page') filters.page = params.url().page;
              else if (key.startsWith("sorting")){
                filters.orderby = key.replace('sorting[', '').replace(']', '');
                filters.order = value
              }
              else if (key.startsWith("filter")){
                column = key.replace('filter[', '').replace(']', '');
                filters[column] = value;
              }
          }, params);

          return bibListesSrv.getbibNomsList(self.idListe, true, filters).then(function(results) {
              params.total(results.data.total);

              self.showSpinnerListe = false;
              self.dataNoms.existingNoms = results.data.items

              self.filterDataTableWithDelAdd();
              return  self.dataNoms.existingNoms || [];
          });
        }
      }
    );

    self.init = function () {
      self.corNoms.add={};
      self.corNoms.del={};
      self.corNoms.mvt={};
    }

    //---------------------- Button add taxons click -------------------------
    self.addNom = function(tx){
      self.corNoms.add[tx.id_nom] = tx;
      self.corNoms.mvt[tx.id_nom] = tx
      if (self.corNoms.del[tx.id_nom]) {
        delete self.corNoms.del[tx.id_nom];
      }
      self.filterDataTableWithDelAdd();
    };

    //---------------------- Button delete taxons click -------------------------
    self.delNom = function(tx){
      self.corNoms.del[tx.id_nom] = tx;
      if (self.corNoms.add[tx.id_nom]) {
        delete self.corNoms.add[tx.id_nom];
      }
      self.filterDataTableWithDelAdd();
    };

    self.filterDataTableWithDelAdd = function() {
      //Ajout d'un nom
      for (id_nom in self.corNoms.add){
        for (var i = 0; i < self.dataNoms.availableNoms.length; i++) {
          if (self.dataNoms.availableNoms[i]['id_nom'] == id_nom) {
            self.dataNoms.existingNoms.push(self.corNoms.add[id_nom]);
            self.dataNoms.availableNoms.splice(i,1);
            break;
          }
        }
      }
      //Suppression
      for (id_nom in self.corNoms.del){
        for (var i = 0; i < self.dataNoms.existingNoms.length; i++) {
          if (self.dataNoms.existingNoms[i]['id_nom'] == id_nom) {
            self.dataNoms.availableNoms.push(self.corNoms.del[id_nom]);
            self.dataNoms.existingNoms.splice(i,1);
            break;
          }
        }
      }
    }

    //---------------------- Button Annuler click -------------------------
    self.cancel = function(){
      //Suppression des "faux mouvements" add et del conbiné
      for (id_nom in self.corNoms.del) {
        if (self.corNoms.mvt[id_nom]) {
          delete self.corNoms.del[id_nom]
        }
      }

      if (Object.keys(self.corNoms.add).length > 0 || Object.keys(self.corNoms.del).length > 0) {

        toaster.pop('warning',"Modifications annulées", "", 5000, 'trustedHtml');
        self.init();
        self.tableParamsDetailListe.reload()
        self.tableParamsTaxons.reload()
      }
    }

    //---------------------- Button Valider de changement click -------------------------
    //-- if nothing change do nothing
    //-- if add and delete same time, add first and delete after
    //-- else add or delete
    self.submit = function(){
      //Suppression des "faux mouvements" add et del conbiné
      for (id_nom in self.corNoms.del) {
        if (self.corNoms.mvt[id_nom]) {
          delete self.corNoms.del[id_nom]
        }
      }

      if (Object.keys(self.corNoms.add).length == 0 && Object.keys(self.corNoms.del).length == 0) {
        toaster.pop('info', toasterMsg.submitInfo_nothing_change.title, "", 5000, 'trustedHtml');
      }
      else {
        var defer = $q.defer();
        var promises = [];

          if (Object.keys(self.corNoms.add).length > 0) {
              promises.push($http.post(backendCfg.api_url+"biblistes/addnoms/"+self.idListe, Object.keys(self.corNoms.add),{ withCredentials: true })
                .then(function(response){
                      toaster.pop('success', toasterMsg.addSuccess.title, toasterMsg.addSuccess.msg, 5000, 'trustedHtml');
                 })
                 .catch(function(error){
                      toaster.pop('error', toasterMsg.addError.title, toasterMsg.addError.msg, 5000, 'trustedHtml');
                      throw new Error;
                 })
              );
          }
          if (Object.keys(self.corNoms.del).length > 0) {

              promises.push($http.post(backendCfg.api_url+"biblistes/deletenoms/"+self.idListe,Object.keys(self.corNoms.del),{ withCredentials: true })
                .then(function(response){
                      toaster.pop('success', toasterMsg.deleteSuccess.title, toasterMsg.deleteSuccess.msg, 5000, 'trustedHtml');
                 })
                 .catch(function(error){
                      toaster.pop('error', toasterMsg.deleteError.title, toasterMsg.deleteError.msg, 5000, 'trustedHtml');
                      throw new Error;
                 })
               );
          }
          $q.all(promises)
            .then(function(response) {
              self.comebackListes();
            })
            .catch(function(error) {
              console.log(error);
            });
          return defer.promise;
      }
    };

    var toasterMsg = {
      'addSuccess':{"title":"ADD",
                     "msg": "Les noms de taxon ont été enregistré avec succès"},
      'deleteSuccess':{"title":"DELETE",
                     "msg": "Les noms de taxon ont été enlevé"},
      'addError':{"title":"ADD",
                     "msg": "Les noms de taxon ne peuvent pas enregistrer - Server intenal error"},
      'deleteError':{"title":"DELETE",
                     "msg": "Les noms de taxon ne peuvent pas enlevé - Server intenal error"},
      'submitInfo_nothing_change':{"title":"Il n'y a pas de changement dans la liste"},
    }

    // ----- come back listes after success update
    self.comebackListes = function(){
      window.history.back();
      bibListesSrv.isDirty = true; // recharger interface liste-bibliste
    };
}]);
