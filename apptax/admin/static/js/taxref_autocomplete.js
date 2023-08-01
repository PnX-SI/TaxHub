$(document).ready(function () {
  let search = document.getElementById("search_value").value;
  let url = (APPLICATION_ROOT + "api/taxref/allnamebylist").replace("//", "/");
  $(".taxref-autocomplete").select2({
    ajax: {
      url: function (params) {
        if (search !== undefined && params == "") {
          params = search;
        }
        return url + "?search_name=" + params;
      },
      results: function (data, page) {
        var data = $.map(data, function (obj) {
          var search_name = obj.search_name.replace("<i>", "");
          search_name = search_name.replace("</i>", "");
          obj.id = obj.cd_nom;
          obj.text = search_name;
          return obj;
        });
        return { results: data };
      },
    },
    dataType: "json",
    delay: 250,
    placeholder: "Nom latin, nom vernaculaire, cd_nom",
    minimumInputLength: 3,
  });
});
