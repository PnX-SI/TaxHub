
$(document).ready(function() {
  // Get value of regne and group_inpn
  let regne_group2 = {}

  let url = (APPLICATION_ROOT + "/api/taxref/regnewithgroupe2").replace("//", "/");

  fetch(url)
  .then((response) => response.json())
  .then((data) => {
    regne_group2 = data;

    // Populate value of regne
    let $dropdown = $("#regne");
    $('#regne').empty();
    $dropdown.append($("<option />").val("").text("---"));
    $.each(regne_group2, function(key, value) {
      $dropdown.append($("<option />").val(key).text(key));
    });

  });

  $('#regne').on('change', function() {
    let $dropdown = $("#group2_inpn");

    // Clear group2_inpn
    $('#group2_inpn').empty();
    $("#group2_inpn").val("");

    // Populate with regne selected value
    $.each(regne_group2[$('#regne').val()], function() {
      $dropdown.append($("<option />").val(this).text(this));
    });
  });
});