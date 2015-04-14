 // Please note that $modalInstance represents a modal window (instance) dependency.
// It is not the same as the $modal service used above.

angular.module('ui.bootstrap').controller('ModalInstanceCtrl', function ($scope, $modalInstance, taxon) {

  $scope.monTaxon = taxon;

  $scope.cancel = function () {
    $modalInstance.close();
  };
});
