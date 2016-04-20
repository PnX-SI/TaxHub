app.directive('searchHierachieDir', ['$http', function ($http) {
  return {
    restrict: 'AE',
    templateUrl:'app/components/directives/searchHierarchie-template.html',
    scope : {
      taxHierarchieSelected:'=?',
      searchUrl:'@',
      search:'&onSearch'
    },
    link:function($scope, $element, $attrs) {
      $scope.$on('hierachieDir:refreshHierarchy',function(event, data){
             $scope.refreshHierarchy();
      });

      //fonction permettant de vider tous les champs de la recherche hierarchique
      $scope.refreshHierarchy = function() {
        this.taxHierarchieSelected = null;
        this.taxHierarchieSelectedKD = null;
        this.taxHierarchieSelectedPH = null;
        this.taxHierarchieSelectedCL = null;
        this.taxHierarchieSelectedOR = null;
        this.taxHierarchieSelectedFM = null;
      }

      $scope.onSelect = function ($item, $model, $label) {
        $scope.$item = $item;
        $scope.$model = $model;
        $scope.$label = $label;

        this.taxHierarchieSelected = $item;

        this.taxHierarchieSelectedKD = {'regne' : $item.regne, 'nb_tx_kd' : $item.nb_tx_kd };

        if ($item.phylum) this.taxHierarchieSelectedPH = {'phylum' : $item.phylum, 'nb_tx_ph' : $item.nb_tx_ph };
        else this.taxHierarchieSelectedPH = undefined;

        if ($item.classe) this.taxHierarchieSelectedCL = {'classe' : $item.classe, 'nb_tx_cl' : $item.nb_tx_cl };
        else this.taxHierarchieSelectedCL = undefined;

        if ($item.ordre) this.taxHierarchieSelectedOR = {'ordre' : $item.ordre, 'nb_tx_or' : $item.nb_tx_or };
        else this.taxHierarchieSelectedOR = undefined;

        if ($item.famille) this.taxHierarchieSelectedFM = {'famille' : $item.famille, 'nb_tx_fm' : $item.nb_tx_fm };
        else this.taxHierarchieSelectedFM = undefined;

      };

      $scope.getTaxonHierarchie = function(rang, val, model) {
        var queryparam = {params : {'ilike': val.trim()}} ;
        if (model) {
          if ((model.regne) && ((rang !=='OR') || (rang !=='CL') || (rang !=='PH')|| (rang !=='KD'))) queryparam.params.regne = model.regne.trim();
          if ((model.phylum) && ((rang !=='OR') || (rang !=='CL') || (rang !=='PH')))  queryparam.params.phylum = model.phylum.trim();
          if ((model.classe) && ((rang !=='OR') || (rang !=='CL'))) queryparam.params.classe = model.classe.trim();
          if ((model.ordre) && (rang !=='OR')) queryparam.params.classe = model.ordre.trim();
        }
        return $http.get(this.searchUrl+rang, queryparam).then(function(response){
          return response.data.map(function(item){
            nbitem = (item.nb_tx_fm || item.nb_tx_or || item.nb_tx_cl || item.nb_tx_ph || item.nb_tx_kd);
            item.limit = (nbitem>500) ? 500 : nbitem;
            return item;
          });
        });
      };
    }
  }
}]);
