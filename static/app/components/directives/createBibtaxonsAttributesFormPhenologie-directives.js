app.directive('createBibtaxonsAttrFormPhenologieDir', [function () {
  return {
    restrict: 'AE',
    templateUrl:'static/app/components/directives/createBibtaxonsAttributesFormPhenologie-template.html',
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
