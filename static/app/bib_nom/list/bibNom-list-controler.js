app.service('bibNomListSrv', function () {
    var bibNomsList;
    var filterbibNoms;

    return {
        getbibNomsList: function () {
            return bibNomsList;
        },
        setbibNomsList: function(value) {
            bibNomsList = value;
        },
        getFilterbibNoms: function () {
            return filterbibNoms;
        },
        setFilterbibNoms: function(value) {
            filterbibNoms = value;
        }
    };
});

app.controller('bibNomListCtrl',[ '$scope', '$http', '$filter','filterFilter', '$uibModal',
    'ngTableParams', 'toaster','bibNomListSrv','backendCfg',
  function($scope, $http, $filter, filterFilter, $modal, ngTableParams, toaster,bibNomListSrv,backendCfg) {
    var self = this;
    self.route='taxons';

    //---------------------Chargement initiale des données sans paramètre------------------------------------
    if (bibNomListSrv.getbibNomsList()) {
        self.bibNomsList = bibNomListSrv.getbibNomsList();
    }
    else {
      $http.get(backendCfg.api_url+"bibnoms/").success(function(response) {
          self.bibNomsList = response;
      });
    }
    if (bibNomListSrv.getFilterbibNoms()) {
        self.filterbibNoms = bibNomListSrv.getFilterbibNoms();
    }
    else {
      self.filterbibNoms = {};
    }

    self.tableCols = {
      "nom_francais" : { title: "Nom francais", show: true },
      "nom_complet" : {title: "Nom latin", show: true },
      "lb_auteur" : {title: "Auteur", show: true },
      "cd_nom" : {title: "cd nom", show: true },
      "id_nom" : {title: "id Taxon", show: true }
    };


    //---------------------WATCHS------------------------------------
    //Ajout d'un watch sur taxonsTaxref de façon à recharger la table
    $scope.$watch(function () {
          return self.bibNomsList;
      }, function() {
        if (self.bibNomsList) {
          bibNomListSrv.setbibNomsList(self.bibNomsList);
          self.tableParams.total( self.bibNomsList ?  self.bibNomsList.length : 0);
          self.tableParams.reload();
        }
    });

    $scope.$watch(function () {
          return self.filterbibNoms;
      }, function() {
      if (self.filterbibNoms) {
        bibNomListSrv.setFilterbibNoms(self.filterbibNoms);
      }
    }, true);


    //Initialisation des paramètres de ng-table
    self.tableParams = new ngTableParams(
    {
        page: 1            // show first page
        ,count: 25           // count per page
        ,sorting: {
            nomLatin: 'asc'     // initial sorting
        }
    },{
        total: self.bibNomsList ?  self.bibNomsList.length : 0 // length of data
        ,getData: function($defer, params) {
            if (self.bibNomsList) {
                if (self.bibNomsList) {
                    // use build-in angular filter
                    var filteredData = params.filter() ?
                        $filter('filter')(self.bibNomsList, params.filter()) :
                        self.bibNomsList;
                    var orderedData = params.sorting() ?
                        $filter('orderBy')(filteredData, params.orderBy()) :
                        filteredData;
                    $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
                }
            }
            else {
                $defer.resolve();
            }
        }
    });

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
                    if(self.bibNomsList[i].idTaxon==id){
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
    self.findInbibNom = function() {
        var queryparam = {params :{
          'is_ref':(self.filterbibNoms.isRef) ? true : false,
          'is_inbibNoms':(self.filterbibNoms.isInbibNom) ? true : false
        }};
        if (self.filterbibNoms.hierarchy) {
          queryparam.params.limit = (self.filterbibNoms.hierarchy.limit) ? self.filterbibNoms.hierarchy.limit : '1000';
        }

        if (self.filterbibNoms.cd){   //Si cd_nom
          queryparam.params.cd_nom = self.filterbibNoms.cd;
          self.filterbibNoms.lb = null;
          self.filterbibNoms.hierarchy = {};
        }
        else if (self.filterbibNoms.lb_nom) {//Si lb_nom
          queryparam.params.ilikelatin = self.filterbibNoms.lb_nom;
          self.filterbibNoms.hierarchy = {};
        }
        else if (self.filterbibNoms.hierarchy) {//Si hierarchie
          (self.filterbibNoms.hierarchy.famille) ? queryparam.params.famille = self.filterbibNoms.hierarchy.famille : '';
          (self.filterbibNoms.hierarchy.ordre) ? queryparam.params.ordre = self.filterbibNoms.hierarchy.ordre : '';
          (self.filterbibNoms.hierarchy.classe) ? queryparam.params.classe = self.filterbibNoms.hierarchy.classe : '';
          (self.filterbibNoms.hierarchy.phylum) ? queryparam.params.phylum = self.filterbibNoms.hierarchy.phylum : '';
          (self.filterbibNoms.hierarchy.regne) ? queryparam.params.regne = self.filterbibNoms.hierarchy.regne : '';
        }
        $http.get(backendCfg.api_url+"bibnoms/",  queryparam).success(function(response) {
            self.bibNomsList = response;
        });
    }
    self.refreshForm = function() {
      self.filterbibNoms = {'hierarchy' : {}};
      self.findInbibNom();
    }

}]);
