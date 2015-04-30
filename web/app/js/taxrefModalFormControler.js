 // Please note that $modalInstance represents a modal window (instance) dependency.
// It is not the same as the $modal service used above.
app.controller('ModalFormCtrl', 

function ($scope,$http, $modalInstance, taxon, configService) {

    //récupération des données taxref du taxon,
    //reçu par le $http et transmise au controleur 'ModalFormCtrl' par la variable 'taxon'
    $scope.monTaxon = taxon;
    
    //temp formulaire taxons
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
      
      //gestion des propriétés des filtres depuis la config
      $scope.labelFiltre0 = configService.filterConfig.filter0.label1
      $scope.typeFiltre0 = configService.filterConfig.filter0.type
      $scope.actifFiltre0 = configService.filterConfig.filter0.actif
      $scope.valuesFiltre0 = configService.filterConfig.filter0.values
      
      $scope.labelFiltre1 = configService.filterConfig.filter1.label1
      $scope.typeFiltre1 = configService.filterConfig.filter1.type
      $scope.actifFiltre1 = configService.filterConfig.filter1.actif
      $scope.valuesFiltre1 = configService.filterConfig.filter1.values
      
      $scope.labelFiltre2 = configService.filterConfig.filter2.label1
      $scope.typeFiltre2 = configService.filterConfig.filter2.type
      $scope.actifFiltre2 = configService.filterConfig.filter2.actif
      $scope.valuesFiltre2 = configService.filterConfig.filter2.values
      
      $scope.labelFiltre3 = configService.filterConfig.filter3.label1
      $scope.typeFiltre3 = configService.filterConfig.filter3.type
      $scope.actifFiltre3 = configService.filterConfig.filter3.actif
      $scope.valuesFiltre3 = configService.filterConfig.filter3.values
      
      $scope.labelFiltre4 = configService.filterConfig.filter4.label1
      $scope.typeFiltre4 = configService.filterConfig.filter4.type
      $scope.actifFiltre4 = configService.filterConfig.filter4.actif
      $scope.valuesFiltre4 = configService.filterConfig.filter4.values
      
      $scope.labelFiltre5 = configService.filterConfig.filter5.label1
      $scope.typeFiltre5 = configService.filterConfig.filter5.type
      $scope.actifFiltre5 = configService.filterConfig.filter5.actif
      $scope.valuesFiltre5 = configService.filterConfig.filter5.values
      
      $scope.labelFiltre6 = configService.filterConfig.filter6.label1
      $scope.typeFiltre6 = configService.filterConfig.filter6.type
      $scope.actifFiltre6 = configService.filterConfig.filter6.actif
      $scope.valuesFiltre6 = configService.filterConfig.filter6.values
      
      $scope.labelFiltre7 = configService.filterConfig.filter7.label1
      $scope.typeFiltre7 = configService.filterConfig.filter7.type
      $scope.actifFiltre7 = configService.filterConfig.filter7.actif
      $scope.valuesFiltre7 = configService.filterConfig.filter7.values
      
      $scope.labelFiltre8 = configService.filterConfig.filter8.label1
      $scope.typeFiltre8 = configService.filterConfig.filter8.type
      $scope.actifFiltre8 = configService.filterConfig.filter8.actif
      $scope.valuesFiltre8 = configService.filterConfig.filter8.values
      
      $scope.labelFiltre9 = configService.filterConfig.filter9.label1
      $scope.typeFiltre9 = configService.filterConfig.filter9.type
      $scope.actifFiltre9 = configService.filterConfig.filter9.actif
      $scope.valuesFiltre9 = configService.filterConfig.filter9.values
      
      //initialisation des champs du formulaire avec les valeurs reçues du taxref
      //si pas de nom vernaculaire, on utilise le nom scientifique
      $scope.fFrName = $scope.monTaxon.nom_vern ? $scope.monTaxon.nom_vern : $scope.monTaxon.lb_nom;
      $scope.fLatinName = $scope.monTaxon.lb_nom;
      $scope.fAuteur = $scope.monTaxon.lb_auteur;
      $scope.fCdnom = $scope.monTaxon.cd_nom;
      $scope.fFiltre0 = '';
      $scope.fFiltre1 = '';
      $scope.fFiltre2 = '';

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
              ,'Filtre2': $scope.fFiltre2
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
                  $scope.fFiltre2 = '';
              }
              if (data.success == false){
                  $scope.errors.push(data.message);
              }
          }).error(function(data, status, headers, config) { // called asynchronously if an error occurs or server returns response with an error status.
              $scope.errors.push(data.message);
          });
      };
      
    //fermeture du modal
    $scope.cancel = function () {
        $modalInstance.close();
    };
    //lancer une première fois après le chargement du formulaire sinon il faut faire des modifications pour que les $scope.$watch lance la fonction
    $modalInstance.result.then(function() {
      // console.log('Fermeture du modal');
    });
    $modalInstance.opened.then(function(){
          // console.log(configService.filterConfig.filter0.name);
          // console.log('Ouverture du modal');
          // $scope.test();
    })
    .finally(function() {
          // console.log('Modal Chargé');
    });
});
