app.service('bibNomListSrv', ['$http', 'backendCfg', function ($http, backendCfg) {
    var bns = this;
    this.isDirty = true;
    this.bibNomsList;
    this.filterbibNoms;

    this.getBibNomApiResponse = function() {
      if (!this.filterbibNoms) this.filterbibNoms = {};
      var queryparam = {params :{
        'is_ref':(this.filterbibNoms.isRef) ? true : false,
        'is_inbibNoms':(this.filterbibNoms.isInbibNom) ? true : false
      }};
      if (this.filterbibNoms.hierarchy) {
        queryparam.params.limit = (this.filterbibNoms.hierarchy.limit) ? this.filterbibNoms.hierarchy.limit : '1000';
      }

      if (this.filterbibNoms.cd){   //Si cd_nom
        queryparam.params.cd_nom = this.filterbibNoms.cd;
        this.filterbibNoms.lb = null;
        this.filterbibNoms.hierarchy = {};
      }
      else if (this.filterbibNoms.lb_nom) {//Si lb_nom
        queryparam.params.ilikelatin = this.filterbibNoms.lb_nom;
        this.filterbibNoms.hierarchy = {};
      }
      else if (this.filterbibNoms.hierarchy) {//Si hierarchie
        (this.filterbibNoms.hierarchy.famille) ? queryparam.params.famille = this.filterbibNoms.hierarchy.famille : '';
        (this.filterbibNoms.hierarchy.ordre) ? queryparam.params.ordre = this.filterbibNoms.hierarchy.ordre : '';
        (this.filterbibNoms.hierarchy.classe) ? queryparam.params.classe = this.filterbibNoms.hierarchy.classe : '';
        (this.filterbibNoms.hierarchy.phylum) ? queryparam.params.phylum = this.filterbibNoms.hierarchy.phylum : '';
        (this.filterbibNoms.hierarchy.regne) ? queryparam.params.regne = this.filterbibNoms.hierarchy.regne : '';
      }
      $http.get(backendCfg.api_url+"bibnoms/",  queryparam).success(function(response) {
          bns.bibNomsList = response;
          bns.isDirty = false;
      });
    };

    this.getbibNomsList = function () {
      if (this.isDirty) {
        this.getBibNomApiResponse();
      }
    };

}]);

app.controller('bibNomListCtrl',[ '$scope', '$http', '$filter','filterFilter', 'ngTableParams', 'toaster','bibNomListSrv','backendCfg','loginSrv',
  function($scope, $http, $filter, filterFilter, ngTableParams, toaster,bibNomListSrv,backendCfg, loginSrv) {
    var self = this;
    self.route='taxons';
    self.isAllowedToEdit=false;

    //----------------------Gestion des droits---------------//
    if (loginSrv.getCurrentUser()) {
      if (loginSrv.getCurrentUser().id_droit_max >= backendCfg.user_edit_privilege) self.isAllowedToEdit = true;
    }

    //---------------------Chargement initiale des données sans paramètre------------------------------------
    bibNomListSrv.getbibNomsList();
    self.filterbibNoms = bibNomListSrv.filterbibNoms;
    self.findInbibNom = function() {
        bibNomListSrv.getbibNomsList();
    }

    self.tableCols = {
      "nom_francais" : { title: "Nom français", show: true },
      "nom_complet" : {title: "Nom latin", show: true },
      "lb_auteur" : {title: "Auteur", show: true },
      "cd_nom" : {title: "cd nom", show: true },
      "id_nom" : {title: "id nom", show: true }
    };

    //Initialisation des paramètres de ng-table
    self.tableParams = new ngTableParams(
    {
        page: 1            // show first page
        ,count: 25           // count per page
        ,sorting: {
            nom_complet: 'asc'     // initial sorting
        }
    },{
        total: bibNomListSrv.bibNomsList ?  bibNomListSrv.bibNomsList.length : 0 // length of data
        ,getData: function($defer, params) {
            if (bibNomListSrv.bibNomsList) {
                // use build-in angular filter
                var filteredData = params.filter() ?
                    $filter('filter')(bibNomListSrv.bibNomsList, params.filter()) :
                    bibNomListSrv.bibNomsList;
                var orderedData = params.sorting() ?
                    $filter('orderBy')(filteredData, params.orderBy()) :
                    filteredData;
                $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
            }
            else {
                $defer.resolve();
            }
        }
    });

    //---------------------WATCHS------------------------------------
    //Ajout d'un watch sur bibNomsList de façon à recharger la table
    $scope.$watch(function () {
          return bibNomListSrv.bibNomsList;
      }, function (newValue, oldValue) {
        if (bibNomListSrv.bibNomsList) {
          self.tableParams.total( bibNomListSrv.bibNomsList ?  bibNomListSrv.bibNomsList.length : 0);
          self.tableParams.reload();
        }
    }, true);
    $scope.$watch(function () {
          return bibNomListSrv.filterbibNoms;
      }, function (newValue, oldValue) {
        if (newValue == oldValue) return;
        if (bibNomListSrv.filterbibNoms) {
          bibNomListSrv.isDirty = true;
        }
    }, true);




    //---------------------FORMULAIRE de RECHERCHE ---------------------------------------------------
    self.getTaxrefIlike = function(val) {
      return $http.get(backendCfg.api_url+'taxref/bibnoms/', {params:{'ilike':val}}).then(function(response){
        return response.data.map(function(item){
          return item.lb_nom;
        });
      });
    };

    /***********************FENETRES MODALS*****************************/
    //-------------------suppression d'un taxon en base----------------------
    self.deleteTaxon = function(id) {
        // self.errors.splice(0, self.errors.length); // remove all error messages
        // self.oks.splice(0, self.oks.length);
        var params = {'id_nom': id}
        $http.delete(backendCfg.api_url+'bibnoms/'+ id,params)
        .success(function(data, status, headers, config) {
            if (data.success == true){
                // self.oks.push(data.message);
                toaster.pop('success', "Ok !", data.message);
                for(var i=0;i<self.bibNomsList.length;i++){
                    if(self.bibNomsList[i].id_nom==id){
                        self.bibNomsList[i].customClass = 'deleted'; //mise en rouge barré dans le tableau (classe="deleted")
                        self.bibNomsList[i].customBtnClass = 'btn-hide'; //masquer les boutons dans le tableau (classe="btn-hide")
                    }
                }
            }
            if (data.success == false){
                // self.errors.push(data.message);
                toaster.pop('warning', "Attention !", data.message);
            }
        })
        .error(function(data, status, headers, config) { // called asynchronously if an error occurs or server returns response with an error status.
            toaster.pop('warning', "Attention !", data.message);
        });
    };


    //-----------------------Bandeau recherche-----------------------------------------------
    self.refreshForm = function() {
      if (bibNomListSrv.filterbibNoms !=  {'hierarchy':{}}){
        bibNomListSrv.filterbibNoms = {'hierarchy':{}};
        bibNomListSrv.isDirty = true;
        self.filterbibNoms = bibNomListSrv.filterbibNoms;
        self.findInbibNom();
      }
    }

}]);
