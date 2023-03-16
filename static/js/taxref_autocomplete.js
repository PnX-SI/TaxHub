$(document).ready(function() {
  let search =  document.getElementById("search_value").value;
  $(".taxref-autocomplete").select2({
    ajax: {
      url: function (params) {
        console.log(params)
        if (search !==undefined && params == "") {
          params = search;
        }
        return  "/api/taxref/search/lb_nom/" + params
      },
      results: function (data, page) {
        var data = $.map(data, function (obj) {
          obj.id = obj.id || obj.lb_nom;
          obj.text = obj.text || obj.lb_nom;
          return obj;
        });
        return {results : data}
      },
      dataType: 'json',
      delay: 250,
      placeholder: "Saisir les trois premières lettres du nom d'un taxon",
      minimumInputLength: 3
    },
  });

})