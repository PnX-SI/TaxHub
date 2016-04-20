app.controller('taxonsListCtrl',[ '$scope', '$http', '$filter','filterFilter', '$uibModal', '$q', 'ngTableParams', 'toaster',
  function($scope, $http, $filter, filterFilter, $modal, $q, ngTableParams, toaster) {
    //Initialisation des paramètres de ng-table
    $scope.tableParams = new ngTableParams(
    {
        page: 1            // show first page
        ,count: 25           // count per page
        ,sorting: {
            nomLatin: 'asc'     // initial sorting
        }
    },{
        total: $scope.taxons ?  $scope.taxons.length : 0 // length of data
        ,getData: function($defer, params) {
            if ($scope.taxons) {
                if ($scope.taxons) {
                    // use build-in angular filter
                    var filteredData = params.filter() ?
                        $filter('filter')($scope.taxons, params.filter()) :
                        $scope.taxons;
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


        //Cette fonction renvoie un tableau de taxons basésur la recherche avancée
        $scope.findTaxonsByHierarchie = function(data) {
            console.log('Recher');
        };
    //---------------------Chargement initiale des données sans paramètre------------------------------------
    $http.get("bibtaxons").success(function(response) {
        $scope.taxons = response;
    });

    //---------------------WATCHS------------------------------------
    //Watch sur taxonsTaxref de façon a recharger la table
    $scope.$watch('taxons', function() {
        if ($scope.taxons) {
            $scope.tableParams.total( $scope.taxons ?  $scope.taxons.length : 0);
            $scope.tableParams.reload();
        }
    });

    /***********************FENETRES MODALS*****************************/

    //---------------------Gestion de l'update d'un taxon en modal------------------------------------
    $scope.editTaxon = function (tx) {
        if(tx!=null){
            var modalInstance = $modal.open({
                templateUrl: 'modalFormContent.html'
                ,controller: 'ModalFormCtrl'
                ,size: 'lg'
                ,resolve: {
                    taxon: function () {
                        return tx;
                    }
                    ,action: function () {
                        return 'edit';
                    }
                }
            });
            modalInstance.result.then(function (returnedTaxon) {
                for(var i=0;i<$scope.taxons.length;i++){
                    if($scope.taxons[i].idTaxon==returnedTaxon.idTaxon){
                        $scope.taxons[i].nomLatin=returnedTaxon.lb_nom;
                        $scope.taxons[i].nomFrancais=returnedTaxon.nom_vern;
                        $scope.taxons[i].auteur=returnedTaxon.lb_auteur;
                        $scope.taxons[i].customClass = 'updated'; //mise en vert dans le tableau (classe="updated")
                        toaster.pop('success', "Ok !", $scope.taxons[i].nomLatin+" a été mise à jour");
                    }
                }
            });
        }
    };

    //-------------------suppression d'un taxon en base----------------------
    $scope.deleteTaxon = function(id) {
        // $scope.errors.splice(0, $scope.errors.length); // remove all error messages
        // $scope.oks.splice(0, $scope.oks.length);
        var params = {'id_taxon': id}
        $http.delete('bibtaxons/'+ id,params)
        .success(function(data, status, headers, config) {
            if (data.success == true){
                // $scope.oks.push(data.message);
                toaster.pop('success', "Ok !", data.message);
                for(var i=0;i<$scope.taxons.length;i++){
                    if($scope.taxons[i].idTaxon==id){
                        $scope.taxons[i].customClass = 'deleted'; //mise en rouge barré dans le tableau (classe="deleted")
                        $scope.taxons[i].customBtnClass = 'btn-hide'; //masquer les boutons dans le tableau (classe="btn-hide")
                    }
                }
            }
            if (data.success == false){
                // $scope.errors.push(data.message);
                toaster.pop('warning', "Attention !", data.message);
            }
        })
        .error(function(data, status, headers, config) { // called asynchronously if an error occurs or server returns response with an error status.
            toaster.pop('warning', "Attention !", data.message);
        });
    };

    // Filtre sur la taxonomie
    // $http.get("bibtaxons/taxonomie").success(function(response) {
        // $scope.taxonomie = response;
    // });

    //-----------------------Bandeau recherche-----------------------------------------------
    //gestion du bandeau de recherche  - Position LEFT
    $scope.isCollapsedSearchTaxon = true;
    $scope.labelSearchTaxon = "Afficher la Recherche";
    $scope.toggleSearchTaxon = function(){
        $scope.isCollapsedSearchTaxon = !$scope.isCollapsedSearchTaxon
        $scope.isCollapsedSearchTaxon ? $scope.labelSearchTaxon = "Afficher la Recherche" : $scope.labelSearchTaxon = "Masquer la Recherche";
    }

}]);
