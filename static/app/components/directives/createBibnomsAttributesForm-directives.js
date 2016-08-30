app.directive('createBibnomsAttrFormDir', [function () {
  return {
    restrict: 'AE',
    templateUrl:'static/app/components/directives/createBibnomsAttributesForm-template.html',
    scope : {
      attributsDefList:'=',
      attributsValues:'=',
      userrightlevel:'='
    }
  }
}]);
