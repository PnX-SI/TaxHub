app.directive('returnBackDir', ['locationHistoryService', function (locationHistoryService) {
  return {
    restrict: 'AE',
    templateUrl:'static/app/components/directives_generiques/returnToBack-template.html',

    link:function($scope, $element, $attrs) {
      var nomRoute = {
        'taxons': 'Mes taxons',
        'taxref' : 'Taxref',
        'listes' : 'Listes'
      }
      $scope.previousLocation = locationHistoryService.get()
      console.log(locationHistoryService)
    }
  }

}]);
