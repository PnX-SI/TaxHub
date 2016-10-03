app.directive('createBibnomsMediasDir', ['$http', 'toaster', 'backendCfg',  'Upload', '$timeout',
function ($http, toaster, backendCfg, Upload, $timeout) {
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

            var initMediaForm = function() {
                $scope.showform = true;
                my.picFile = null;
                if ((my.selectedMedium.url)  && (my.selectedMedium.url !== ''))  {
                  $scope.localFile = false;
                }
                else {
                  $scope.localFile = true;
                }
            };
            
            // $scope.manageUrlPathValue = function(localFileValue) {
                // console.log('local : ' + localFileValue + ' - url : ' + my.selectedMedium.url+ ' - chemin :' + my.selectedMedium.chemin)
                // if (localFileValue) {
                    // my.selectedMedium.url=null;
                // }
                // else {
                    // my.selectedMedium.chemin=null;
                // }
            // };

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
                      if (my.action =='edit') {
                        angular.forEach(my.mediasValues, function(media, key) {
                          if (media.id_media == data.media.id_media) my.mediasValues[key] = data.media;
                        },data);
                      }
                      else {
                         my.mediasValues.push(data.media);
                      }
                      my.selectedMedium = {};
                      $scope.showform = false;
                      toaster.pop('success', toasterMsg.saveSuccess.title, toasterMsg.saveSuccess.msg, 5000, 'trustedHtml');
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
                  .success(successClb)
                  .error(errorClb)
              }
            }

            $scope.cancel = function() {
                $scope.showform = false;
                my.selectedMedium = {};
            };

            //------------------------------ Suppression d'un médium ----------------------------------/
            $scope.deleteMedium = function (id) {
                var url = backendCfg.api_url +"tmedias/"+ id;
                var params = {};
                $http.delete(url, params, { withCredentials: true })
                .success(function(data, status, headers, config) {
                    if (data.success == true) {
                        $scope.mediasValues = $scope.mediasValues.filter(function(a) { return a.id_media != id });
                        toaster.pop('success', "Suppression", "Le medium a été supprimé", 5000, 'trustedHtml');
                    }
                    if (data.success == false){
                        toaster.pop('success', "Erreur lors de la suppression", "Le medium n'a pas été supprimé", 5000, 'trustedHtml');
                    }
                })
                .error(function(data, status, headers, config) {
                    toaster.pop('error', "Erreur", "Le medium n'a pas été supprimé", 5000, 'trustedHtml');
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
