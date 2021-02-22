app.directive('createBibnomsMediasDir', ['$http', 'toaster', 'backendCfg',  'Upload', '$timeout', 'dialogs',
function ($http, toaster, backendCfg, Upload, $timeout, dialogs) {
    return {
        restrict: 'AE',
        templateUrl:'static/app/bib_nom/edit/media/createBibnomsMedias-template.html',
        scope : {
          mediasTypes:'=',
          mediasValues:'=',
          mediasPath:'=',
          mediasCdref:'=',
          showform:'='
        },
        link:function($scope, $element, $attrs) {
            my = $scope;
            $scope.mediasTypes = $scope.mediasTypes || [];
            $scope.mediasValues = $scope.mediasValues || [];
            $scope.formPanelHeading = 'Ajouter ou modifier un medium ';
            $scope.localFile = true;
            $scope.showform = false;
            $scope.nomTypeMedia = '';
            my.action = '';


            $scope.changeMediaType = function(){
                $scope.nomTypeMedia = document.getElementById('media-type').options[document.getElementById('media-type').selectedIndex].text;
                my.selectedMedium['nom_type_media'] = $scope.nomTypeMedia;
            }


            var toasterMsg = {
                'saveSuccess':{"title":"Enregistrement réussi", "msg": "Le medium a été enregistré avec succès"},
                'saveError':{"title":"Erreur d'enregistrement"},
            };

            $scope.updateMedium = function (medium) {
                $scope.formPanelHeading = 'Modifier le medium '  + medium.titre
                my.action = 'edit';
                my.selectedMedium = angular.copy(medium);
                initMediaForm();
            };

            $scope.addMedium = function() {
                my.formPanelHeading = 'Ajout d\'un nouveau média';
                my.action = 'new';
                my.selectedMedium = {'is_public':true};
                initMediaForm();
            };

            $scope.getUniqueString = function(){
              return (+new Date).toString(36).slice(-5)
            }

            var initMediaForm = function() {
                $scope.showform = true;
                my.picFile = null;
                if ((my.selectedMedium.chemin)  && (my.selectedMedium.chemin !== ''))  {
                  $scope.localFile = true;
                }
                else {
                  $scope.localFile = false;
                }
            };

            //------------------------------ Sauvegarde du formulaire ----------------------------------/
            $scope.saveMedium = function(file) {

              my.selectedMedium['cd_ref'] = $scope.mediasCdref;
              if (file) my.selectedMedium['isFile'] = true;
              else  my.selectedMedium['isFile'] = false;

              var url = backendCfg.api_url +"tmedias/";
              if(my.action == 'edit'){
                url = url + my.selectedMedium.id_media;
              }

              var successClb = function(data, status, headers, config) {
                  if (data.success == true) {
                      // http://localhost:5000/api/tmedias/bycdref/497
                      $http.get(backendCfg.api_url + "tmedias/bycdref/"+my.mediasCdref+"?forcePath=True").then(function(response) {
                          my.mediasValues = response.data;
                          my.selectedMedium = {};
                          $scope.showform = false;
                          toaster.pop('success', toasterMsg.saveSuccess.title, toasterMsg.saveSuccess.msg, 5000, 'trustedHtml');
                      });
                      // if (my.action =='edit') {
                      //   angular.forEach(my.mediasValues, function(media, key) {
                      //     if (media.id_media == data.media.id_media) my.mediasValues[key] = data.media;
                      //   },data);
                      // }
                      // else {
                      //    my.mediasValues.push(data.media);
                      // }
                  }
                  if (data.success == false){
                      toaster.pop('success', toasterMsg.saveError.title, data.message, 5000, 'trustedHtml');
                  }
              };
              var errorClb = function(data, status, headers, config) {
                toaster.pop('error', toasterMsg.saveError.title, data.message, 5000, 'trustedHtml');
              };

              if (file) {
                my.selectedMedium.file = file
                Upload.upload({
                  "url": url,
                  "data":   my.selectedMedium
                })
                .success(successClb)
                .error(errorClb)
                .then(function (response) {
                  $timeout(function () {
                    file.result = response.data;
                  });
                }, function (response) {
                  if (response.status > 0)
                    $scope.errorMsg = response.status + ': ' + response.data;
                }, function (evt) {
                  // Math.min is to fix IE which reports 200% sometimes
                  file.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
                });
              }
              else {
                $http.post(url, my.selectedMedium, { withCredentials: true })
                .then(
                  function (response) {
                    successClb(response.data, response.status, response.headers, response.config);
                  }
                )
                .catch(
                  function (response) {
                    errorClb(response.data, response.status, response.headers, response.config);
                  }
                );
              }
            }

            $scope.cancel = function() {
                $scope.showform = false;
                my.selectedMedium = {};
            };

            //------------------------------ Suppression d'un médium ----------------------------------/
            $scope.deleteMedium = function (id) {
                var dlg = dialogs.confirm('Confirmation', 'Etes vous sur de vouloir supprimer ce média ?');
                dlg.result.then(function () {
                    var url = backendCfg.api_url +"tmedias/"+ id;
                    var params = {};
                    $http.delete(url, params, { withCredentials: true })
                    .then(function(response) {
                        if (response.data.success == true) {
                            $scope.mediasValues = $scope.mediasValues.filter(function(a) { return a.id_media != id });
                            toaster.pop('success', "Suppression", "Le medium a été supprimé", 5000, 'trustedHtml');
                        }
                        if (response.data.success == false){
                            toaster.pop('success', "Erreur lors de la suppression", "Le medium n'a pas été supprimé", 5000, 'trustedHtml');
                        }
                    })
                    .catch(function(response) {
                        toaster.pop('error', "Erreur", "Le medium n'a pas été supprimé", 5000, 'trustedHtml');
                    });
                });
            };
        }
    }
}]);


app.filter('mediaTypeName', function() {
  return function(idMediaType) {
      var mediaName = (my.mediasTypes.filter(function(a) { return a.id_type == idMediaType }));
      if (mediaName) {
        return mediaName[0].nom_type_media;
      }
  };
})
