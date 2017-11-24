app.controller('bibListePopulateCtrl',[ '$scope','$filter', '$http','$uibModal','$route','$routeParams',
    'NgTableParams','toaster', 'backendCfg','loginSrv','bibListesSrv',
  function($scope,$filter, $http,$uibModal,$route, $routeParams,NgTableParams,toaster, backendCfg,loginSrv,bibListesSrv) {
    var self = this;
    self.showSpinnerSelectList = true;
    self.showSpinnerTaxons = true;
    self.showSpinnerListe = true;
    self.isSelected = false;
    self.listName = {
      selectedList: [],
      availableOptions:[]
    };
    self.getData = {
      getTaxons : [],
      getDetailListe : [],
      getDetailListeReserve : []
    };
    self.corNoms = {
      add : [],
      del : [],
      init: []
    };
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
    //---------------------Get list of "nom de la Liste"---------------------
    bibListesSrv.getListes().then(
      function(res){
        self.listName.availableOptions = bibListesSrv.listeref.data;
        if($routeParams.id){
          self.getListByParamId($routeParams.id);
        }
        self.showSpinnerSelectList = false;
      });
    //---------------------Initialisation des paramètres de ng-table---------------------
    self.tableParamsTaxons = new NgTableParams(
      {
          count: 10,
          sorting: {'nom_complet': 'asc'}
      }
    );
    self.tableParamsDetailListe = new NgTableParams(
      {
          count: 10,
          sorting: {'nom_complet': 'asc'}
      }
    );
    //---------------------Get taxons------------------------------------
    self.getTaxons = function() {
      self.showSpinnerTaxons = true;
      self.showSpinnerListe = true;

      bibListesSrv.getbibNomsList().then(
        function(res1) {
          self.getData.getTaxons = res1.data;
          bibListesSrv.getDetailListe(self.listName.selectedList.id_liste).then(
          function(res2) {
            self.getData.getDetailListe = res2.data;
            self.getData.getDetailListeReserve = angular.copy(res2.data);
            angular.forEach(self.getData.getDetailListeReserve, function(value, key) {
                self.corNoms.init.push(value.id_nom);
            });
            // Delete "noms de taxons" that are alredy presented in list
            self.availableNoms(self.getData.getDetailListe,self.getData.getTaxons);
            // Display the list of "noms de taxons" by regne or/and group2_inpn only
            self.getData.getTaxons = self.displayByRegneGroup2(self.listName.selectedList,self.getData.getTaxons);

            self.tableParamsTaxons.settings({dataset:self.getData.getTaxons});
            self.tableParamsDetailListe.settings({dataset:self.getData.getDetailListe});

            self.showSpinnerListe = false;
            self.showSpinnerTaxons = false;

            self.corNoms.add.length = 0;  //  reinitiation
            self.corNoms.del.length = 0;  //  reinitiation

          });
        });
    };
    //--------------------- When Selected Liste is changed -------------------------------------
    self.listSelected = function(){
      // Get taxons
      self.getTaxons();
      self.isSelected = true;
    };

    self.getListByParamId = function(id){
      angular.forEach(self.listName.availableOptions, function(value, key){
        if(value.id_liste == id){
          self.listName.selectedList = value;
          self.listSelected();
        }
      });
    };

    //--------------------- Delete "noms de taxons" that are alredy presented in list------------
    self.availableNoms = function(listeNoms,taxons){
      for(i=0; i < listeNoms.length; i++){
        for(j=0; j < taxons.length; j++)
          if(listeNoms[i].cd_nom == taxons[j].cd_nom){
            taxons.splice(j,1);
            break;
          }
      }
    };

    //---------------------- Display the list of "noms de taxons" by regne and group2_inpn only--
    self.displayByRegneGroup2 =  function(selectedList,taxons){
      var nomsDeTaxons = [];
      //-- si 2 null affichier tous les noms
      if((selectedList.regne == null) && (selectedList.group2_inpn == null)){
        return taxons;
      }
      else {
        return taxons.filter(function(v, i, map) {
            if (
                ((v.group2_inpn == selectedList.group2_inpn) || (selectedList.group2_inpn==null))
                &&
                (v.regne == selectedList.regne)
            ) {
                return v;
            }
        });
      }
    };
    //---------------------- Button add taxons click -------------------------
    self.addNom = function(id_nom){
      self.addNomsToList(id_nom,self.getData.getTaxons,self.getData.getDetailListe,self.corNoms.add);
      //-- Dont' add duplicate value in Del
      self.cleanAddAndDeleteList(self.corNoms.del,id_nom);
      self.tableParamsTaxons.reload();
      self.tableParamsDetailListe.reload();
    };

    self.addNomsToList = function(id_nom, taxons, detailList,corNoms){
      //-- Dont' add duplicate value to array
      if((!corNoms.includes(id_nom)) && (!self.corNoms.init.includes(id_nom))){
          corNoms.push(id_nom);
      }
      for (i = 0; i < taxons.length; i++) {
        if(taxons[i].id_nom == id_nom){
          detailList.push(taxons[i]); // Add to detailList
          taxons.splice(i,1); // Cut a nom corespont with id in taxons
          break;
        }
      };
    };
    //---------------------- Button delete taxons click -------------------------
    self.delNom = function(id_nom){
      self.delNomsToList(id_nom,self.getData.getTaxons,self.getData.getDetailListe,self.corNoms.del);
      //-- Dont' add duplicate value in Add
      self.cleanAddAndDeleteList(self.corNoms.add,id_nom);
      self.tableParamsTaxons.reload();
      self.tableParamsDetailListe.reload();
    };

    self.delNomsToList = function(id_nom, taxons, detailList,corNoms){
      //-- Dont' add duplicate value to array
      if((!corNoms.includes(id_nom))&&(self.corNoms.init.includes(id_nom))){
        corNoms.push(id_nom);
      };
      for (i = 0; i < detailList.length; i++) {
        if(detailList[i].id_nom == id_nom){
          taxons.push(detailList[i]); // Add to taxons
          detailList.splice(i,1); // Cut a nom corespont with id_nom in detailList
          break;
        }
      };
    };
    self.cleanAddAndDeleteList = function(list,id){
      if (list.includes(id)){
        var index = list.indexOf(id);
        list.splice(index, 1);
      }
    };
    //---------------------- Button Annuler click -------------------------
    self.cancel = function(){
      if(self.corNoms.add.length != 0 || self.corNoms.del.length != 0){
        toaster.pop('warning',"Annuler les modifications", "", 5000, 'trustedHtml');
        self.getTaxons();
      }
    }

    //---------------------- Button Valider de changement click -------------------------
    //-- if nothing change do nothing
    //-- if add and delete same time, add first and delete after
    //-- else add or delete
    self.submit = function(){
      if(self.corNoms.add.length == 0 && self.corNoms.del.length == 0)
        toaster.pop('info', toasterMsg.submitInfo_nothing_change.title, "", 5000, 'trustedHtml');
      else if(self.corNoms.add.length != 0 && self.corNoms.del.length != 0){
        $http.post(backendCfg.api_url+"biblistes/addnoms/"+self.listName.selectedList.id_liste, self.corNoms.add,{ withCredentials: true })
              .then(
                 function(response){
                      toaster.pop('success', toasterMsg.addSuccess.title, toasterMsg.addSuccess.msg, 5000, 'trustedHtml');
                      $http.post(backendCfg.api_url+"biblistes/deletenoms/"+self.listName.selectedList.id_liste,self.corNoms.del,{ withCredentials: true })
                        .then(
                           function(response){
                                toaster.pop('success', toasterMsg.deleteSuccess.title, toasterMsg.deleteSuccess.msg, 5000, 'trustedHtml');
                                self.comebackListes();// come back listes
                           },
                           function(response){
                                toaster.pop('error', toasterMsg.deleteError.title, toasterMsg.deleteError.msg, 5000, 'trustedHtml');
                                self.listSelected(); // reload to update data

                           });
                 },
                 function(response){
                      toaster.pop('error', toasterMsg.addError.title, toasterMsg.addError.msg, 5000, 'trustedHtml');
                      self.listSelected(); // reload to update data
                 })
      }
      else{
          if (self.corNoms.add.length != 0) {
              $http.post(backendCfg.api_url+"biblistes/addnoms/"+self.listName.selectedList.id_liste, self.corNoms.add,{ withCredentials: true })
              .then(
                 function(response){
                      toaster.pop('success', toasterMsg.addSuccess.title, toasterMsg.addSuccess.msg, 5000, 'trustedHtml');
                      self.comebackListes();// come back listes
                 },
                 function(response){
                      toaster.pop('error', toasterMsg.addError.title, toasterMsg.addError.msg, 5000, 'trustedHtml');
                      self.listSelected(); // reload to update data

                 });
          }
          if (self.corNoms.del.length != 0) {
              $http.post(backendCfg.api_url+"biblistes/deletenoms/"+self.listName.selectedList.id_liste,self.corNoms.del,{ withCredentials: true })
              .then(
                 function(response){
                      toaster.pop('success', toasterMsg.deleteSuccess.title, toasterMsg.deleteSuccess.msg, 5000, 'trustedHtml');
                      self.comebackListes();// come back listes
                 },
                 function(response){
                      toaster.pop('error', toasterMsg.deleteError.title, toasterMsg.deleteError.msg, 5000, 'trustedHtml');
                      self.listSelected(); // reload to update data
                 });
          }
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
