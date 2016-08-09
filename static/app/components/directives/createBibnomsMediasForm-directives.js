app.directive('createBibnomsMediasFormDir', ['$routeParams', '$http', 'locationHistoryService', 'toaster', 'backendCfg', '$location', 
function ($routeParams, $http, locationHistoryService, toaster, backendCfg, $location) {
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
                //mise à jour du medium : TODO
                $scope.formPanelHeading = 'Modifier le medium '  + medium.titre
                my.action = 'edit';
                if(medium.id_type == 3) {$scope.localFile = false;}
                else{$scope.localFile = true;}
                my.selectedMedium = medium;
            };
            
            $scope.addMedium = function() {
                my.formPanelHeading = 'Ajout d\'un nouveau média';
                my.selectedMedium = {};
                my.action = 'new';
                $scope.localFile = true;
                
            };
            
            $scope.uploadFile = function() {
                //TODO
                alert('TODO');
            };
            
            //------------------------------ Sauvegarde du formulaire ----------------------------------/
            $scope.saveMedium = function() {
                my.selectedMedium['chemin'] = $scope.mediasPath;
                my.selectedMedium['cd_ref'] = $scope.mediasCdref;
                var params = my.selectedMedium;
                var url = backendCfg.api_url +"tmedias/";
                if(my.action == 'edit'){url = url + my.selectedMedium.id_media;}
                $http.post(url, params, { withCredentials: true })
                .success(function(data, status, headers, config) {
                    if (data.success == true) {
                        my.mediasValues.push(my.selectedMedium);
                        my.selectedMedium = {};
                        $scope.localFile = true;
                        $scope.formPanelHeading = 'Ajouter ou modifier un medium '
                        toaster.pop('success', toasterMsg.saveSuccess.title, toasterMsg.saveSuccess.msg, 5000, 'trustedHtml');
                        // var nextPath = 'taxon/'+data.id_media;
                        // if (my.previousLocation) nextPath = my.previousLocation;
                        // $location.path(nextPath).replace();
                        // taxrefTaxonListSrv.isDirty = true;
                        // bibNomListSrv.isDirty = true;
                    }
                    if (data.success == false){
                        toaster.pop('success', toasterMsg.saveError.title, data.message, 5000, 'trustedHtml');
                    }
                })
                .error(function(data, status, headers, config) {
                    toaster.pop('error', toasterMsg.saveError.title, data.message, 5000, 'trustedHtml');
                });
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
