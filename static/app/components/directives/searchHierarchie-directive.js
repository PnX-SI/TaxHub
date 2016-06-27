app.directive('searchHierachieDir', ['$http', 'backendCfg', function ($http,backendCfg) {
  return {
    restrict: 'AE',
    templateUrl:'static/app/components/directives/searchHierarchie-template.html',
    scope : {
      taxHierarchieSelected:'=',
      searchUrl:'@',
    },
    link:function($scope, $element, $attrs) {
      var defaultLimit = 1000;
      //Initialisation
      $scope.$watch('taxHierarchieSelected', function(newVal, oldVal) {
        if ($scope.taxHierarchieSelected) {
          if ($scope.taxHierarchieSelected.regne) $scope.taxHierarchieSelectedKD = {'regne': $scope.taxHierarchieSelected.regne, 'nb_tx_kd': $scope.taxHierarchieSelected.nb_tx_kd };
          else $scope.taxHierarchieSelectedKD = undefined;
          if ($scope.taxHierarchieSelected.phylum) $scope.taxHierarchieSelectedPH = {'phylum': $scope.taxHierarchieSelected.phylum, 'nb_tx_ph': $scope.taxHierarchieSelected.nb_tx_ph };
          else $scope.taxHierarchieSelectedPH = undefined;
          if ($scope.taxHierarchieSelected.classe) $scope.taxHierarchieSelectedCL = {'classe': $scope.taxHierarchieSelected.classe, 'nb_tx_cl': $scope.taxHierarchieSelected.nb_tx_cl };
          else $scope.taxHierarchieSelectedCL = undefined;
          if ($scope.taxHierarchieSelected.ordre) $scope.taxHierarchieSelectedOR = {'ordre': $scope.taxHierarchieSelected.ordre, 'nb_tx_or': $scope.taxHierarchieSelected.nb_tx_or };
          else $scope.taxHierarchieSelectedOR = undefined;
          if ($scope.taxHierarchieSelected.famille) $scope.taxHierarchieSelectedFM = {'famille': $scope.taxHierarchieSelected.famille, 'nb_tx_fm': $scope.taxHierarchieSelected.nb_tx_fm };
          else $scope.taxHierarchieSelectedFM = undefined;
        }
      }, true);

      $scope.onSelect = function ($item, $model, $label) {
        $scope.$item = $item;
        $scope.$model = $model;
        $scope.$label = $label;
        this.taxHierarchieSelected = $item;
      };

      $scope.getTaxonHierarchie = function(rang, val, model) {
        var queryparam = {params : {'ilike': val.trim()}} ;
        if (model) {
            if ((model.regne) && (rang !=='KD')) queryparam.params.regne = model.regne.trim();
            if ((model.phylum) && ((rang !=='PH') && (rang !=='KD')))  queryparam.params.phylum = model.phylum.trim();
            if ((model.classe) && ((rang !=='CL') && (rang !=='PH') && (rang !=='KD'))) queryparam.params.classe = model.classe.trim();
            if ((model.ordre) && ((rang !=='OR') && (rang !=='CL') && (rang !=='PH') && (rang !=='KD'))) queryparam.params.ordre = model.ordre.trim();
        }
        return $http.get(backendCfg.api_url+this.searchUrl+rang, queryparam).then(function(response){
          return response.data.map(function(item){
            nbitem = (item.nb_tx_fm || item.nb_tx_or || item.nb_tx_cl || item.nb_tx_ph || item.nb_tx_kd);
            item.limit = (nbitem>defaultLimit) ? defaultLimit : nbitem;
            return item;
          });
        });
      };
    }
  }
}]);
