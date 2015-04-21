app.controller('taxonsCtrl', function($scope, $http, $filter, filterFilter, ngTableParams) {
        //liste taxons   
        // $http.get("js/bib_taxons.json").success(function(response) {$scope.taxons = response;});
        $http.get("http://92.222.107.92/damien/MyProject/web/app_dev.php/bibtaxons/").success(function(response) {
            $scope.taxons = response;
            $scope.tableParams = new ngTableParams({
                page: 1            // show first page
                ,count: 10           // count per page
                ,sorting: {
                    nomLatin: 'asc'     // initial sorting
                }
            }, {
                total: $scope.taxons.length, // length of data
                getData: function($defer, params) {
                    // use build-in angular filter
                    var orderedData = params.sorting() ?
                        $filter('orderBy')($scope.taxons, params.orderBy()) :
                        $scope.taxons;
                    $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
                }
            });
            $scope.gridOptions = { 
                data: 'taxons',
                showGroupPanel: true,
                jqueryUIDraggable: true
            };
        });
        
        //bouton add taxons
        $scope.addTaxon = function() {
            // alert('Todo : ajouter le taxon '+tax.lb_nom+' à bib_taxons.');
            $scope.modal = {
              "title": "Todo",
              "content": "Ajouter un taxon depuis le taxref !"
            };
        };
		
		// Filtre sur la taxonomie
		$http.get("http://92.222.107.92/damien/MyProject/web/app_dev.php/bibtaxons/taxonomie").success(function(response) {
            $scope.taxonomie = response;
			
			// filtre des lb_nom sur id_rang = KD (=regne) pour remplir la liste regne
			$scope.regne = $scope.taxonomie.filter(function (el) {
                return el.id_rang == 'KD';
            });
			
			// filtre des lb_nom sur id_rang = PH (=phylum) pour remplir la liste phylum
			$scope.phylum = $scope.taxonomie.filter(function (el) {
                return el.id_rang == 'PH';
            });
			
			// filtre des lb_nom sur id_rang = CL (=classe) pour remplir la liste classe
			$scope.classe = $scope.taxonomie.filter(function (el) {
                return el.id_rang == 'CL';
            });
			
			// filtre des lb_nom sur id_rang = OR (=ordre) pour remplir la liste ordre
			$scope.ordre = $scope.taxonomie.filter(function (el) {
                return el.id_rang == 'OR';
            });
			
			// filtre des lb_nom sur id_rang = FM (=famille) pour remplir la liste famille
			$scope.famille = $scope.taxonomie.filter(function (el) {
                return el.id_rang == 'FM';
            });
			
            });
        
        
    });