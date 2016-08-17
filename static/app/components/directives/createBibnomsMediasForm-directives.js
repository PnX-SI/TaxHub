app.directive('createBibnomsMediasFormDir', ['$http', 'toaster', 'backendCfg',  'Upload', '$timeout',
function ($http, toaster, backendCfg, Upload, $timeout) {
    return {
        restrict: 'AE',
        templateUrl:'static/app/components/directives/createBibnomsMediasForm-template.html',
        scope : {
          mediasTypes:'=',
          mediasValues:'=',
          mediasPath:'=',
          mediasCdref:'='
        },
        link:function($scope, $element, $attrs) {
            my = $scope;
            console.log(my.mediasValues);
            $scope.mediasTypes = $scope.mediasTypes || [];
            $scope.mediasValues = $scope.mediasValues || [];
            $scope.formPanelHeading = 'Ajouter ou modifier un medium ';
            $scope.localFile = true; //TODO watch it to manage medium['url'] value
            my.action = '';
            // my.previousLocation = locationHistoryService.get();
            var toasterMsg = {
                'saveSuccess':{"title":"Enregistrement réussi", "msg": "Le medium a été enregistré avec succès"},
                'saveError':{"title":"Erreur d'enregistrement"},
            }

            $scope.updateMedium = function (medium) {
                $scope.formPanelHeading = 'Modifier le medium '  + medium.titre
                my.action = 'edit';
                my.selectedMedium = medium;
                initMediaForm();
            };

            $scope.addMedium = function() {
                my.formPanelHeading = 'Ajout d\'un nouveau média';
                my.action = 'new';
                my.selectedMedium = {};
                initMediaForm();
            };

            var initMediaForm = function() {
                my.picFile = null;
                if ((my.selectedMedium.url)  && (my.selectedMedium.url !== ''))  {
                  $scope.localFile = false;
                }
            }

            $scope.uploadFile = function() {
                //TODO
                alert('TODO');
            };

            //------------------------------ Sauvegarde du formulaire ----------------------------------/
            $scope.saveMedium = function(file) {
              //my.selectedMedium['chemin'] = $scope.mediasPath;
              my.selectedMedium['cd_ref'] = $scope.mediasCdref;
              my.selectedMedium['isFile'] = $scope.localFile;

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
                      // @TODO réinitialiser le formulaire fichier
                      $scope.localFile = true;
                      $scope.formPanelHeading = 'Ajouter ou modifier un medium '
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
                console.log('file');
                Upload.upload({
                  "url": url,
                  "data":   my.selectedMedium
                }).success(successClb)
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
                console.log('file');
                $http.post(url, my.selectedMedium, { withCredentials: true })
                  .success(successClb)
                  .error(errorClb)
              }

            }

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


                // refreshMedias = function(newVal) {
                    // newVal = newVal || [];
                    // $scope.actifMedium = $scope.mediasValues.filter(function(allList){
                        // return newVal.filter(function(current){
                            // return allList.id_media == current.id_media
                        // }).length == 0
                    // });
                // }
        }
    }
}]);
