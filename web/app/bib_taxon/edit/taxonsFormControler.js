
app.controller('taxonsCtrl', [ '$scope', '$routeParams','$http','locationHistoryService','$location',
function($scope, $routeParams, $http, locationHistoryService, $location) {
  $scope.errors= [];
  var self = this;
  $scope.previousLocation = locationHistoryService.get();
  self.bibTaxon = {};
  self.attrVal = {};
  var action = $routeParams.action;
  var self = this;
  if ($routeParams.id) {
    if (action == 'new') self.cd_nom = $routeParams.id;
    else {
      self.id_taxon = $routeParams.id;
      $http.get("bibtaxons/"+self.id_taxon).then(function(response) {
        if (response.data) {
          self.bibTaxon = response.data;
          self.cd_nom = response.data.taxref.cd_nom;
          self.bibTaxon.cdNom = response.data.taxref.cd_nom;
        }
      });
    }
  }
  $scope.$watch(function () {
    return self.cd_nom;
  }, function(newVal, oldVal) {
    if (newVal) {
      $http.get("taxref/"+self.cd_nom).then(function(response) {
        self.taxref = response.data;
        self.bibTaxon.cdNom = response.data.cd_nom;
        self.bibTaxon.nom_latin = response.data.nom_complet;
        self.bibTaxon.auteur = response.data.lb_auteur;
        self.bibTaxon.nom_francais = response.data.nom_vern;
      });
    }
  });

  self.refreshTaxrefData = function() {
    self.cd_nom = self.bibTaxon.cdNom;
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
    var params = self.bibTaxon;
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
