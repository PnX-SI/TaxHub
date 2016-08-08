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
        $scope.formPanelHeading = 'Ajouter ou modifier un medium ';

        $scope.updateMedium = function (medium) {
            //mise à jour du medium : TODO
            $scope.formPanelHeading = 'Modifier le medium '  + medium.titre
            my.selectedMedium = medium;
        };
        
        $scope.deleteMedium = function (id) {
            //suppression du medium : TODO
        };
      
        $scope.addMedium = function() {
            my.formPanelHeading = 'Ajout d\'un nouveau média';
            my.selectedMedium = {};
            //ajout de l'élément media titre
            my.selectedMedium['chemin'] = $scope.mediasPath;
            my.selectedMedium['cd_ref'] = $scope.mediasCdref;
            // my.mediasValues.push(my.selectedMedium);
            
        };
        
        $scope.saveMedium = function() {
            // TODO
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
