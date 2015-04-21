 // Please note that $modalInstance represents a modal window (instance) dependency.
// It is not the same as the $modal service used above.
app.controller('ModalFormCtrl', 

  function ($scope,$http, $modalInstance, taxon, configService) {

    $scope.monTaxon = taxon;
    
    //formulaire taxons
      $scope.listeRouge = [
          {"lrCode":"EX"}
          ,{"lrCode":"EW"}
          ,{"lrCode":"RE"}
          ,{"lrCode":"CR"}
          ,{"lrCode":"EN"}
          ,{"lrCode":"VU"}
          ,{"lrCode":"NT"}
          ,{"lrCode":"LC"}
          ,{"lrCode":"DD"}
          ,{"lrCode":"NA"}
          ,{"lrCode":"NE"}
      ];
      
      // action = '';
      $scope.fFrName = $scope.monTaxon.nom_vern;
      $scope.fLatinName = $scope.monTaxon.lb_nom;
      $scope.fAuteur = $scope.monTaxon.lb_auteur;
      $scope.fCdnom = $scope.monTaxon.cd_nom;
      $scope.fFiltre0 = '';
      $scope.fFiltre1 = '';
      // $scope.fIdtaxon = '';
      $scope.error = false;
      $scope.incomplete = true;
      $scope.errors = [];
      $scope.msgs = [];
      $scope.oks = [];
  
      $scope.$watch('fFrName', function() {$scope.test();});
      $scope.$watch('fLatinName', function() {$scope.test();});
      $scope.$watch('fAuteur', function() {$scope.test();});
      $scope.$watch('fCdnom', function() {$scope.test();});

      $scope.test = function() {
          $scope.incomplete = false;
          if (!$scope.fFrName.length || !$scope.fLatinName.length || !$scope.fAuteur.length || !$scope.fCdnom.toString.length) {
              $scope.incomplete = true;
          }
      };
      
      $scope.save = function() {
          $scope.errors.splice(0, $scope.errors.length); // remove all error messages
          $scope.oks.splice(0, $scope.oks.length);
          $http.post("bibtaxons", {
              'nomFrancais': $scope.fFrName
              ,'nomLatin': $scope.fLatinName
              ,'auteur': $scope.fAuteur
              ,'cdNom': $scope.fCdnom
              ,'Filtre0': $scope.fFiltre0
              ,'Filtre1': $scope.fFiltre1
              // ,'id_taxon': $scope.fIdtaxon
            }
          ).success(function(data, status, headers, config) {
              if (data.success == true){
                  $scope.oks.push(data.message);
                  $scope.incomplete = true;
                  $scope.fFrName = '';
                  $scope.fLatinName = '';
                  $scope.fAuteur = '';
                  $scope.fCdnom = '';
                  $scope.fFiltre0 = '';
                  $scope.fFiltre1 = '';
              }
              if (data.success == false){
                  $scope.errors.push(data.message);
              }
          }).error(function(data, status, headers, config) { // called asynchronously if an error occurs or server returns response with an error status.
              $scope.errors.push(data.message);
          });
      };

    $scope.cancel = function () {
      $modalInstance.close();
    };
    //lancer une première fois après le chargement du formulaire sinon il faut faire des modifications pour que les $scope.$watch lance la fonction
    $modalInstance.result.then(function() {
      console.log('Fermeture du modal');
    });
    $modalInstance.opened.then(function(){
          console.log(configService.txConfig.filter0.name);
          // alert('modalInstance.opened');
          // console.log($modalInstance)
          console.log('Ouverture du modal');
          $scope.test();
      }).finally(function() {
          console.log('Modal Chargé');
      });
      $scope.$on('loaded.bs.modal', function() {
          // $scope.test();
          alert('loaded.bs.modal')
      });
    
  }
);
