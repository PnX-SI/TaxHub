$(document).ready(function () {
  // Get value of regne and group_inpn
  let regne_group2 = {};

  fetch(URL_GROUP_REGNE)
    .then((response) => response.json())
    .then((data) => {
      regne_group2 = data;
      changeGroup2DropDown()
    });

  function changeGroup2DropDown() {
    // If regne is selected : populate value of regne 
    let $regneDropdown = $("#regne");
    let $group2_inpnDropdown = $("#group2_inpn");

    if ($regneDropdown.val()) {
    // Populate with regne selected value
      current_value = $group2_inpnDropdown.val();
      $group2_inpnDropdown.empty();
      $group2_inpnDropdown.val("");
      $.each(regne_group2[$regneDropdown.val()], function () {
        if (current_value == this) {
          $group2_inpnDropdown.append($("<option selected/>").val(this).text(this));
        }
        else {
          $group2_inpnDropdown.append($("<option />").val(this).text(this));
        }
      }); 
    }
  }
  $("#regne").on("change", function () {
    changeGroup2DropDown()
  });
});
