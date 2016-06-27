app.directive('createBibtaxonsListesFormDir', [function () {
  return {
    restrict: 'AE',
    templateUrl:'static/app/components/directives/createBibtaxonsListesForm-template.html',
    scope : {
      listesDefList:'=',
      listesValues:'='
    },
    link:function($scope, $element, $attrs) {
      self = $scope;
      //Création de la liste active
      $scope.$watch('listesValues', function(newVal, oldVal) {
        if (! $scope.listesDefList) return;
        refreshListes(newVal);
      }, true);
      $scope.$watch('listesDefList', function(newVal, oldVal) {
        if (newVal) refreshListes($scope.listesValues);
      });

      $scope.removeFromList = function (id_liste) {
        //suppression de l'élément liste
        self.listesValues = self.listesValues.filter(function(a) { return a.id_liste != id_liste });
      };
      $scope.addList = function() {
        //ajout de l'élément liste
        self.listesValues.push(self.selectedList)
      };
      refreshListes = function(newVal) {
        $scope.activeListe = $scope.listesDefList.filter(function(allList){
            return newVal.filter(function(current){
                return allList.id_liste == current.id_liste
            }).length == 0
        });
      }
    }
  }
}]);
