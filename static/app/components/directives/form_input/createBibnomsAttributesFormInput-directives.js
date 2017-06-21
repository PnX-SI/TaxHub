app.directive('inputCheckboxDir', [function () {
  return {
    restrict: 'AE',
    templateUrl:'static/app/components/directives/form_input/input-checkbox-template.html',
    scope : {
      attrDefList:'=',
      value:'='
    },
    link:function(scope, $element, $attrs) {
      //fonction privée permettant la création d'un objet avec les propriétés text et selected
      function makeObj(val,sel){
        this.text = val;
        this.selected = sel;
      }
      //initialisation à partir des valeurs reçues par la directive
      scope.attrDefList = scope.attrDefList || [];
      scope.value = scope.value || '';
      scope.attrValues = (scope.value) ? scope.value.split('&') : [];

      //détermination si l'item doit être selectionné ou pas ("sel")
      //construction d'un objet par item reçu depuis le tableau des valeurs de l'attribut (champ valeur_attribut de taxonomie.bib_attributs) ; new makeObj(scope.attrDefList[i],sel)
      //puis contruction d'un tableau d'objet avec les propriétés des checkboxes ; scope.myAttr.push
      //scope.myAttr est utilisé par le template de la directive pour construire chaque checkbox
      scope.myAttr = [];
      for ( var i = 0; i < scope.attrDefList.length; ++i ) {
        var sel = false;
        for ( var j = 0; j < scope.attrValues.length; ++j ) {
          if(scope.attrValues[j]==scope.attrDefList[i]){
            sel=true;
          }
        }
        scope.myAttr.push(new makeObj(scope.attrDefList[i],sel));
      }

      //écouter les actions sur les checboxes et construire la valeur de sortie du champ du formulaire
      scope.$watch('myAttr', function(arr) {
          scope.attrValues =[];
          for ( var i = 0; i < arr.length; ++i ) {
              if(arr[i].selected == true){
                scope.attrValues.push(arr[i].text)
              }
          }
          if (scope.attrValues) scope.value = scope.attrValues.join('&');
      }, true );
    }
  }
}]);

app.directive('inputMultiselectDir', [function () {
  return {
    restrict: 'AE',
    templateUrl:'static/app/components/directives/form_input/input-multiselect-template.html',
    scope : {
      attrDefList:'=',
      value:'='
    },
    link:function(scope, $element, $attrs) {
      scope.attrDefList = scope.attrDefList || [];
      scope.value = scope.value || '';
      scope.attrValues = (scope.value) ? scope.value.split('&') : [];

      //Création de la liste active
      scope.$watch('attrValues', function(newVal, oldVal) {
        if (! scope.attrValues) return;
        scope.refresh(newVal);
      }, true);

      scope.remove = function (val) {
        //suppression de l'élément liste
        scope.attrValues = scope.attrValues.filter(function(a) {return a != val });
      };
      scope.add = function() {
          scope.attrValues.push(scope.selectedAtt);
      };

      scope.refresh = function(newVal) {
        if (newVal) scope.value = newVal.join('&');
        newVal = newVal || [];
        scope.activeListe = scope.attrDefList.filter(function(allList){
            return newVal.filter(function(current){
                return allList == current
            }).length == 0
        });
      }
    }

  }
}]);

app.directive('inputPhenology', [function () {
  return {
    restrict: 'AE',
    templateUrl:'static/app/components/directives/form_input/input-phenology-template.html',
    scope : {
      stringValue:'=',
    },
    link:function(scope, $element, $attrs) {
      scope.arr= JSON.parse(scope.stringValue || "{}");
      scope.$watch('arr', function(newVal, oldVal) {
        scope.stringValue = JSON.stringify(newVal);
      }, true);
    }
  }
}]);

app.filter('month', function() {
  return function(input) {
    var i = input || 99;
    var month = {99:'ERROR',1:'janv', 2:'fev', 3:'mars',4:'avil',5:'mai',6:'juin',7:'juil',8:'aout',9:'sept',10:'oct',11:'nov',12:'dec'};
    return month[i];
  };
})
