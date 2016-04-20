app.controller('ModalInfoCtrl', function ($scope, $uibModalInstance, taxon) {

  $scope.monTaxon = taxon;

  $scope.cancel = function () {
    $uibModalInstance.close();
  };
});
