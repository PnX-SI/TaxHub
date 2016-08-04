app.directive('createBibnomsMediasFormDir', [function () {
  return {
    restrict: 'AE',
    templateUrl:'static/app/components/directives/createBibnomsMediasForm-template.html',
    scope : {
      mediasTypes:'=',
      mediasValues:'=',
      mediasPath:'=',
      mediasCdref:'='
    },
    link:function($scope, $element, $attrs) {
      my = $scope;
      $scope.mediasTypes = $scope.mediasTypes || [];
      $scope.mediasValues = $scope.mediasValues || [];
      //Création du media actif
      // $scope.$watch('mediasValues', function(newVal, oldVal) {
        // if (! $scope.mediasTypes) return;
        // refreshMedias(newVal);
      // }, true);
      // $scope.$watch('mediasTypes', function(newVal, oldVal) {
        // if (newVal) refreshMedias($scope.mediasValues);
      // });

      $scope.removeFromList = function (titre) {
        //suppression de l'élément media
        my.mediasValues = my.mediasValues.filter(function(a) { return a.titre != titre });
      };
      $scope.addMedium = function() {
        //ajout de l'élément media titre
        my.selectedMedium['chemin'] = $scope.mediasPath;
        my.selectedMedium['cd_ref'] = $scope.mediasCdref;
        my.mediasValues.push(my.selectedMedium);
        my.selectedMedium = {};
      };
      // refreshMedias = function(newVal) {
        // newVal = newVal || [];
        // $scope.actifMedium = $scope.mediasValues.filter(function(allList){
            // return newVal.filter(function(current){
                // return allList.id_media == current.id_media
            // }).length == 0
        // });
      // }
    }
  }
}]);
