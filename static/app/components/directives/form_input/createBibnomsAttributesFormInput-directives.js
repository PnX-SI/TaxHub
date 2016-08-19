app.directive('inputMultiselectDir', [function () {
  return {
    restrict: 'AE',
    templateUrl:'static/app/components/directives/form_input/input-multiselect-template.html',
    scope : {
      attrDefList:'=',
      value:'=',
    },
    link:function($scope, $element, $attrs) {
      self = $scope;
      $scope.attrDefList = $scope.attrDefList || [];
      $scope.value = $scope.value || '';
      $scope.attrValues = ($scope.value) ? $scope.value.split('&') : [];

      //Création de la liste active
      $scope.$watch('attrValues', function(newVal, oldVal) {
        if (! $scope.attrValues) return;
        refresh(newVal);
      }, true);

      $scope.$watch('attrDefList', function(newVal, oldVal) {
        if (newVal) refresh($scope.attrValues);
      });

      $scope.remove = function (val) {
        //suppression de l'élément liste
        self.attrValues = self.attrValues.filter(function(a) {return a != val });
      };
      $scope.add = function() {
        //ajout de l'élément liste
        self.attrValues.push(self.selectedAtt)
      };

      refresh = function(newVal) {
        if (newVal) self.value = newVal.join('&');
        newVal = newVal || [];
        $scope.activeListe = $scope.attrDefList.filter(function(allList){
            return newVal.filter(function(current){
                return allList == current
            }).length == 0
        });
      }
    }

  }
}]);

app.directive('inputPhenology', [function () {
  return {
    restrict: 'AE',
    templateUrl:'static/app/components/directives/form_input/input-phenology-template.html',
    scope : {
      stringValue:'=',
    },
    link:function($scope, $element, $attrs) {
      $scope.arr= JSON.parse($scope.stringValue || "{}");
      $scope.$watch('arr', function(newVal, oldVal) {
        $scope.stringValue = JSON.stringify(newVal);
      }, true);
    }
  }
}]);

app.filter('month', function() {
  return function(input) {
    var i = input || 99;
    var month = {99:'ERROR',1:'janv', 2:'fev', 3:'mars',4:'avil',5:'mai',6:'juin',7:'juil',8:'aout',9:'sept',10:'oct',11:'nov',12:'dec'};
    return month[i];
  };
})
