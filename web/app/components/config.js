app.factory('configService', function () {
    return {
        filterConfig : {
            "filter1":
            {
                "name":"patrimonial"
                ,"type":"checkbox"
                ,"actif":"true"
                ,"label1":"Taxon patrimonial"
                ,"label2":"patrimonialité"
                ,"label2":"test"
                ,"values":""
            }
            ,"filter2":
            {
                "name":"red_list"
                ,"type":"select"
                ,"actif":"true"
                ,"label1":"Liste rouge"
                ,"label2":""
                ,"label2":""
                ,"values":[
                    {"id":"EX"}
                    ,{"id":"EW"}
                    ,{"id":"RE"}
                    ,{"id":"CR"}
                    ,{"id":"EN"}
                    ,{"id":"VU"}
                    ,{"id":"NT"}
                    ,{"id":"LC"}
                    ,{"id":"DD"}
                    ,{"id":"NA"}
                    ,{"id":"NE"}
                ]
            }
            ,"filter3":
            {
                "name":"protection"
                ,"type":"checkbox"
                ,"actif":"true"
                ,"label1":"Taxon protégé"
                ,"label2":"protection"
                ,"label2":"Taxons bénéficiant d'une protection stricte"
                ,"values": ""
            }

            ,"filter4":
            {
                "name":""
                ,"type":"text"
                ,"actif":"false"
                ,"label1":""
                ,"label2":""
                ,"label2":""
            }
            ,"filter5":
            {
                "name":"test"
                ,"type":"text"
                ,"actif":"true"
                ,"label1":"testage"
                ,"label2":""
                ,"label2":""
            }
            ,"filter6":
            {
                "name":""
                ,"type":"text"
                ,"actif":"false"
                ,"label1":""
                ,"label2":""
                ,"label2":""
            }
            ,"filter7":
            {
                "name":""
                ,"type":"text"
                ,"actif":"false"
                ,"label1":""
                ,"label2":""
                ,"label2":""
            }
            ,"filter8":
            {
                "name":""
                ,"type":"text"
                ,"actif":"false"
                ,"label1":""
                ,"label2":""
                ,"label2":""
            }
            ,"filter9":
            {
                "name":""
                ,"type":"text"
                ,"actif":"false"
                ,"label1":""
                ,"label2":""
                ,"label2":""
            }
            ,"filter10":
            {
                "name":""
                ,"type":"text"
                ,"actif":"false"
                ,"label1":""
                ,"label2":""
                ,"label2":""
            }
        },
        gettxConfig : function() {
          return this.txConfig;
        }
    }
});

app.directive('adaptativFilter', function () {

    return {
        restrict: 'AE'
        ,scope: {
            factif: '@',
            ftype: '@',
            flabel: '@',
            fvalues: '@',
            num: '@'
        }
        ,replace: true
        // ,transclude: true
        ,template: '<div class="col-sm-10"></div>'
        ,link: function (scope, element, attrs) {
            scope.myFilter = '';
            if(scope.factif){ //si le filtre est actif
                if(scope.ftype == 'text' || scope.ftype == 'checkbox'){ // si le filtre est de type 'input'
                    scope.myFilter = document.createElement('input'); //on créé un noued de type input
                    scope.myFilter.setAttribute("type", scope.ftype); // on lui affecte ses attributs
                    scope.myFilter.setAttribute("name", "fFiltre"+scope.num);
                    // scope.myFilter.setAttribute("ng-model", "fFiltre"+scope.num);
                }
                if(scope.ftype == 'select'){ // si le filtre est de type 'liste déroulante'
                    scope.myFilter = document.createElement('select'); //on créé un noued de type 'select'
                    scope.myFilter.setAttribute("class", "form-control"); //on lui affecte ses attributs
                    scope.myFilter.setAttribute("name", "fFiltre"+scope.num);
                    // scope.myFilter.setAttribute("ng-model", "fFiltre"+scope.num);
                    scope.tvalues = JSON.parse(scope.fvalues); // la chaine des valeurs est vu comme un text, il faut la transformer en json (ici un tableau d'objet)
                    scope.myOption = document.createElement('option'); //on créé un premier noued de type 'option' vide pour le contenu de la liste dééroulante
                    scope.myOption.setAttribute("value", ""); //on lui affecte comme attribut 'value' une valeur vide
                    scope.myOption.setAttribute("label", ""); //on lui affecte comme attribut 'label' une valeur vide
                    scope.myOption.setAttribute("selected", "selected"); //on le selectionne
                    scope.myOption.appendChild(document.createTextNode("")); //on défini ce qui est affiché comme vide
                    scope.myFilter.appendChild(scope.myOption); // on ajoute le noeud 'option' dans le noeud 'select'
                    for(i=0;i<scope.tvalues.length;i++)
                    { // on boucle sur les objets du tableau de valeurs en json
                        scope.myOption = document.createElement('option'); //on créé un noued de type 'option' pour le contenu de la liste déroulante
                        scope.myOption.setAttribute("value", i); //on lui affecte ses attributs
                        scope.myOption.setAttribute("label", scope.tvalues[i].id);
                        scope.myOption.appendChild(document.createTextNode(scope.tvalues[i].id)); //on défini ce qui est affiché
                        scope.myFilter.appendChild(scope.myOption); // on ajoute le noeud 'option' dans le noeud 'select'
                    }
                }
                element.append(scope.myFilter); // On ajoute notre liste 'select' ou notre 'input' dans l'élément 'div' du template
                // console.log(element);
                // console.log(scope.myFilter);
            }
        }
    };
});
