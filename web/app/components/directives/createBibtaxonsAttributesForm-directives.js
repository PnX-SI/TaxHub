app.directive('createBibtaxonsAttrFormDir', [function () {
  return {
    restrict: 'AE',
    templateUrl:'app/components/directives/createBibtaxonsAttributesForm-template.html',
    scope : {
      attributsDefList:'=',
      attributsValues:'='
    }
  }
}]);
