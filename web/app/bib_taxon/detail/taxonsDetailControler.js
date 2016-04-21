app.controller('taxonsDetailCtrl',[ '$scope', '$http','$routeParams',
  function($scope, $http,$routeParams) {
    var self = this;
    self.route='taxons';

    $http.get('bibtaxons/'+$routeParams.id).then(
      function(response) {
        if (response.data) {
          self.bibTaxon = response.data;
        }
        else {
          alert("le taxon demandé n'existe pas");
        }
        console.log(response);
      }
    )


}]);
