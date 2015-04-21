app.controller('ModalInfoCtrl', function ($scope, $modalInstance, taxon) {

  $scope.monTaxon = taxon;

  $scope.cancel = function () {
    $modalInstance.close();
  };
});
