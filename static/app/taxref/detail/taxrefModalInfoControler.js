app.controller('ModalInfoCtrl', function ($scope, $uibModalInstance, $http, backendCfg, idtaxon) {
    
    $scope.getTaxon = function (id) {
        $scope.showSpinner = true;
        $http.get(backendCfg.api_url+"taxref/"+id).then(function(response) {
            $scope.monTaxon = response.data;
            //@TODO passer ce test en ng-class
            for (var i=0; i < $scope.monTaxon.synonymes.length; i++) {
                if($scope.monTaxon.synonymes[i].cd_nom==$scope.monTaxon.cd_ref){
                    $scope.monTaxon.synonymes[i].nameClasse='cdref';
                }
                else{
                    $scope.monTaxon.synonymes[i].nameClasse='cdnom';
                }
            }
            $scope.showSpinner = false;
        });
    };
    $scope.getTaxon(idtaxon);

    $scope.cancel = function () {
        $uibModalInstance.close();
    };
});
