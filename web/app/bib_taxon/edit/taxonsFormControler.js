
app.controller('taxonsCtrl', [ '$scope', '$routeParams','$http','locationHistoryService','$location',
function($scope, $routeParams, $http, locationHistoryService, $location) {
  $scope.errors= [];
  var self = this;
  $scope.previousLocation = locationHistoryService.get();
  self.bib_taxon = {};
  self.attrVal = {};
  var action = $routeParams.action;
  var self = this;
  if ($routeParams.id) {
    if (action == 'new') self.cd_nom = $routeParams.id;
    else self.id_taxon = $routeParams.id;
  }
  $scope.$watch(function () {
    return self.cd_nom;
  }, function(newVal, oldVal) {
    if (newVal) {
      $http.get("taxref/"+self.cd_nom).then(function(response) {
        self.taxref = response.data;
        self.bib_taxon.cdNom = response.data.cd_nom;
        self.bib_taxon.nomLatin = response.data.nom_complet;
        self.bib_taxon.auteur = response.data.lb_auteur;
        self.bib_taxon.nomFrancais = response.data.nom_vern;
      });
    }
  });

  self.refreshTaxrefData = function() {
    self.cd_nom = self.bib_taxon.cdNom;
  }

  //------------------------------ Chargement de la listes des attributs ----------------------/
  ///bibattributs/Animalia/Autre
  $scope.$watch(function () {
    return self.taxref;
  }, function(newVal, oldVal) {
    if (newVal) {
      $http.get("bibattributs/"+newVal.regne+"/"+newVal.group2_inpn).then(function(response) {
        self.attributsDefList = response.data;
        angular.forEach(self.attributsDefList, function(value, key) {
          value.listeValeurObj =JSON.parse(value.listeValeurAttribut);
        });
      });
    }
  });
  //------------------------------ Sauvegarde du formulaire ----------------------------------/
  self.submit = function() {
    var params = self.bib_taxon;
    var url = "bibtaxons";
    if(action == 'edit'){url=url+'/'+$scope.id_taxon;}
    $http.post(url, params)
    .success(function(data, status, headers, config) {
      if (data.success == true){
        if ($scope.previousLocation) $location.path($scope.previousLocation);
      }
      if (data.success == false){
        $scope.errors.push(data.message);
      }
    })
    .error(function(data, status, headers, config) {
      $scope.errors.push(data.message);
    });
  }
}
]);
