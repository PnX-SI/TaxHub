var app = angular.module('taxonsApp', ['ngTable','ui.bootstrap','pageslide-directive', 'angucomplete-alt'])
app.controller('taxrefCtrl', function($scope, $http, $filter,filterFilter, ngTableParams) {
    //Initialisation
    $scope.searchedRegne = null;
    $scope.searchedPhylum = null;
    $scope.searchedClasse = null;
    $scope.searchedOrdre = null;
    $scope.searchedFamille = null;
    //factorisation de l'url de l'appli
    var url_root = "http://92.222.107.92/taxhub/app_dev.php/";
    //mise à jour de la table ng-table
    var majTable = function(data){    
        $scope.tableData = data;
        $scope.tableParams.total($scope.tableData.length);
        $scope.tableParams.reload();
    }
    
    //chargement initial et construction du tableau de résultats (découverte)
    // Préparation de la table ng-table du tableau de résultat offrant les fonctions de tri par colonne
    $http.get(url_root+"taxref/").success(function(response) {
        $scope.taxonsTaxref = response;
        $scope.tableParams = new ngTableParams({
            page: 1            // show first page
            ,count: 50           // count per page
            ,sorting: {
                nomLatin: 'asc'     // initial sorting
            }
        }, {
            total: $scope.taxonsTaxref.length, // length of data
            getData: function($defer, params) {
                // use build-in angular filter
                var orderedData = params.sorting() ? $filter('orderBy')($scope.taxonsTaxref, params.orderBy()) : $scope.taxonsTaxref;
                $defer.resolve(orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
            }
        });
        $scope.gridOptions = { 
            data: 'taxonsTaxref',
            showGroupPanel: true,
            jqueryUIDraggable: true
        };
    });
    
    //--------------------------Ecouteurs et rechargement des 5 niveaux taxonomiques-----------------
    //recharge une liste de x taxons du niveau
    //on créé une fonction qui charge des taxons du règne passé en paramètre
    //regnes
 

    
    //--------------------rechercher un taxon---------------------------------------------------------
    //Cette fonction renvoie un tableau avec toutes les infos d'un seul taxon en recherchant sur le champ lb_nom
    $scope.findLbNom = function(lb) {
        $http.get(url_root+"taxref/?ilike="+lb).success(function(response) {
            $scope.taxonsTaxref = response;
            majTable($scope.taxonsTaxref);
            $scope.selectedregne = null;
            $scope.selectedphylum = null;
            $scope.selectedClasse = null;
            $scope.selectedOrdre = null;
            $scope.selectedFamille = null;
            $scope.cd = null;
        });
    };
     //Cette fonction renvoie un tableau avec toutes les infos d'un seul taxon en recherchant sur le champ cd_nom
    $scope.findCdNom = function(cd) {
        $http.get(url_root+"taxref/?cdNom="+cd).success(function(response) {
            $scope.taxonsTaxref = response;
            majTable($scope.taxonsTaxref);
            $scope.selectedregne = null;
            $scope.selectedphylum = null;
            $scope.selectedClasse = null;
            $scope.selectedOrdre = null;
            $scope.selectedFamille = null;
            $scope.lb = null;
        });
    };
    
    
    //-----------------------Pageslide directive -Bandeau recherche et info taxon -----------------------------------------------
    //gestion du bandeau d'information sur le taxon sélectioné - Position TOP
    $scope.isOpenInfoTaxon = false; // This will be binded using the ps-open attribute
    $scope.toggleInfoTaxon = function(id){
        if(id!=null){
            $http.get(url_root+"taxref/"+id).success(function(response) {
                $scope.selectedTaxon = response;
            });
        }
        $scope.isOpenInfoTaxon = true;
        if($scope.isOpenInfoTaxon){
            $scope.isOpenSearchTaxon=false;
            $scope.labelSearchTaxon = "Afficher la Recherche"
        }
    }
    //gestion du bandeau de recherche  - Position LEFT
    $scope.isOpenSearchTaxon = true; // This will be binded using the ps-open attribute
    $scope.labelSearchTaxon = "Masquer la Recherche";
    $scope.toggleSearchTaxon = function(){
        $scope.isOpenSearchTaxon = !$scope.isOpenSearchTaxon
        $scope.isOpenSearchTaxon ? $scope.labelSearchTaxon = "Masquer la Recherche" : $scope.labelSearchTaxon = "Afficher la Recherche";
        $scope.isOpenInfoTaxon=false;
    }
    
    //test de l'autocompletion    
 
    // $scope.famSelected = function (fam) {
        // if(fam.length>2){
            // $http.get(url_root+"taxref/distinct/famille?ilike="+fam).success(function(response) {
                // $scope.fams = response;
            // });
        // }
    // }
    $scope.majHierarchieCombo = function(){
        
    }
    //familles
    $scope.familleSelected = function(selected) {
        selected.originalObject.nb_tx_fm <500 ? $scope.limit = selected.originalObject.nb_tx_fm : $scope.limit = 500;
        document.getElementById('fOrdres_value').value = selected.originalObject.ordre +' ' + selected.originalObject.nb_tx_or;
        document.getElementById('fClasses_value').value = selected.originalObject.classe +' ' + selected.originalObject.nb_tx_cl;
        document.getElementById('fPhylums_value').value = selected.originalObject.phylum +' ' + selected.originalObject.nb_tx_ph;
        document.getElementById('fRegnes_value').value = selected.originalObject.regne +' ' + selected.originalObject.nb_tx_kd;
        selected.originalObject.famille ? $scope.searchedFamille = selected.originalObject.famille : $scope.searchedFamille ='';
        selected.originalObject.ordre ? $scope.searchedOrdre = selected.originalObject.ordre : $scope.searchedOrdre ='';
        selected.originalObject.classe ? $scope.searchedClasse = selected.originalObject.classe : $scope.searchedClasse ='';
        selected.originalObject.phylum ? $scope.searchedPhylum = selected.originalObject.phylum : $scope.searchedPhylum ='';
        selected.originalObject.regne ? $scope.searchedRegne = selected.originalObject.regne : $scope.searchedRegne ='';
    };
    //ordres
    $scope.ordreSelected = function(selected) {
        selected.originalObject.nb_tx_or <500 ? $scope.limit = selected.originalObject.nb_tx_or : $scope.limit = 500;
        document.getElementById('fFamilles_value').value = '';
        document.getElementById('fClasses_value').value = selected.originalObject.classe +' ' + selected.originalObject.nb_tx_cl;
        document.getElementById('fPhylums_value').value = selected.originalObject.phylum +' ' + selected.originalObject.nb_tx_ph;
        document.getElementById('fRegnes_value').value = selected.originalObject.regne +' ' + selected.originalObject.nb_tx_kd;
        selected.originalObject.famille ? $scope.searchedFamille = selected.originalObject.famille : $scope.searchedFamille ='';
        selected.originalObject.ordre ? $scope.searchedOrdre = selected.originalObject.ordre : $scope.searchedOrdre ='';
        selected.originalObject.classe ? $scope.searchedClasse = selected.originalObject.classe : $scope.searchedClasse ='';
        selected.originalObject.phylum ? $scope.searchedPhylum = selected.originalObject.phylum : $scope.searchedPhylum ='';
        selected.originalObject.regne ? $scope.searchedRegne = selected.originalObject.regne : $scope.searchedRegne ='';
    };
    //classes
    $scope.classeSelected = function(selected) {
        selected.originalObject.nb_tx_cl <500 ? $scope.limit = selected.originalObject.nb_tx_cl : $scope.limit = 500;
        document.getElementById('fFamilles_value').value = '';
        document.getElementById('fOrdres_value').value = '';
        document.getElementById('fPhylums_value').value = selected.originalObject.phylum +' ' + selected.originalObject.nb_tx_ph;
        document.getElementById('fRegnes_value').value = selected.originalObject.regne +' ' + selected.originalObject.nb_tx_kd;
        selected.originalObject.famille ? $scope.searchedFamille = selected.originalObject.famille : $scope.searchedFamille ='';
        selected.originalObject.ordre ? $scope.searchedOrdre = selected.originalObject.ordre : $scope.searchedOrdre ='';
        selected.originalObject.classe ? $scope.searchedClasse = selected.originalObject.classe : $scope.searchedClasse ='';
        selected.originalObject.phylum ? $scope.searchedPhylum = selected.originalObject.phylum : $scope.searchedPhylum ='';
        selected.originalObject.regne ? $scope.searchedRegne = selected.originalObject.regne : $scope.searchedRegne ='';
    };
    //phylums
    $scope.phylumSelected = function(selected) {
        selected.originalObject.nb_tx_ph <500 ? $scope.limit = selected.originalObject.nb_tx_ph : $scope.limit = 500;
        document.getElementById('fFamilles_value').value = '';
        document.getElementById('fOrdres_value').value = '';
        document.getElementById('fClasses_value').value = '';
        selected.originalObject.famille ? $scope.searchedFamille = selected.originalObject.famille : $scope.searchedFamille ='';
        selected.originalObject.ordre ? $scope.searchedOrdre = selected.originalObject.ordre : $scope.searchedOrdre ='';
        selected.originalObject.classe ? $scope.searchedClasse = selected.originalObject.classe : $scope.searchedClasse ='';
        selected.originalObject.phylum ? $scope.searchedPhylum = selected.originalObject.phylum : $scope.searchedPhylum ='';
        selected.originalObject.regne ? $scope.searchedRegne = selected.originalObject.regne : $scope.searchedRegne ='';
    };
    //regnes
    $scope.regneSelected = function(selected) {
        selected.originalObject.nb_tx_kd <500 ? $scope.limit = selected.originalObject.nb_tx_kd : $scope.limit = 500;
        document.getElementById('fFamilles_value').value = '';
        document.getElementById('fOrdres_value').value = '';
        document.getElementById('fClasses_value').value = '';
        document.getElementById('fPhylums_value').value = '';
        selected.originalObject.famille ? $scope.searchedFamille = selected.originalObject.famille : $scope.searchedFamille ='';
        selected.originalObject.ordre ? $scope.searchedOrdre = selected.originalObject.ordre : $scope.searchedOrdre ='';
        selected.originalObject.classe ? $scope.searchedClasse = selected.originalObject.classe : $scope.searchedClasse ='';
        selected.originalObject.phylum ? $scope.searchedPhylum = selected.originalObject.phylum : $scope.searchedPhylum ='';
        selected.originalObject.regne ? $scope.searchedRegne = selected.originalObject.regne : $scope.searchedRegne ='';
    };
    //Cette fonction renvoie un tableau de taxons basé sur la recherche avancée
    $scope.findTaxonsByHierarchie = function() {
        $http.get(url_root+"taxref/?famille="+$scope.searchedFamille+"&ordre="+$scope.searchedOrdre+"&classe="+$scope.searchedClasse+"&phylum="+$scope.searchedPhylum+"&regne="+$scope.searchedRegne+"&limit="+$scope.limit+"&nom_valide=true").success(function(response) {
            $scope.taxonsTaxref = response;
            majTable($scope.taxonsTaxref);            
        });
    };
    
    //-------------------------------------modal form todo-------------------------------------
    $scope.addTaxon = function(tax) {
        // alert('Todo : ajouter le taxon '+tax.lb_nom+' à bib_taxons.');
        $scope.modal = {
          "title": "Todo",
          "content": "Ajouter le taxon '"+tax.lb_nom+"' à bib_taxons !"
        };
    };
});