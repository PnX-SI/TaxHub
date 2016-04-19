app.directive('searchHierachieDir', ['$http', function ($http) {
  return {
   restrict: 'AE',
   templateUrl:'app/components/directives/searchHierarchie-template.html',
   link:function($scope, $element, $attrs) {
     $scope.onSelect = function ($item, $model, $label) {
       $scope.$item = $item;
       $scope.$model = $model;
       $scope.$label = $label;
    };

     $scope.getTaxonHierarchie = function(rang, val, model) {
      var queryparam = {params : {'ilike': val.trim()}} ;
      if (model) {
        if (model.regne) queryparam.params.regne = model.regne;
        if (model.phylum) queryparam.params.phylum = model.phylum;
        if (model.classe) queryparam.params.classe = model.classe;
        if (model.ordre) queryparam.params.classe = model.ordre;
      }
       return $http.get('taxref/hierarchie/'+rang, queryparam).then(function(response){
         return response.data.map(function(item){
           var object = angular.extend(
             {'famille':' ','regne':' ','phylum':' ','classe':' ','ordre':' '},
             item
           );
           nbitem = (item.nb_tx_fm || item.nb_tx_or || item.nb_tx_cl || item.nb_tx_ph || item.nb_tx_kd);
           object.limit = (nbitem>500) ? 500 : nbitem;
           return object;
         });
       });
     };
   }
  }
}]);
