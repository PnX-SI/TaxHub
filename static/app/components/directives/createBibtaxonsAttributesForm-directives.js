app.directive('createBibtaxonsAttrFormDir', [function () {
  return {
    restrict: 'AE',
    templateUrl:'static/app/components/directives/createBibtaxonsAttributesForm-template.html',
    scope : {
      attributsDefList:'=',
      attributsValues:'='
    }
  }
}]);
