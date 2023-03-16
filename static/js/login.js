
$(document).ready(function() {


  $("#login-submit").click(function() {
    const login_data = {
      login:  $("#identifiant").val(),
      password: $("#password").val(),
      id_application:  $("#id-app").val()
    };

    fetch("/api/auth/login", {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        method: "POST",
        body:  JSON.stringify(login_data)
      }).then((response) => response.json())
      .then((data) => {
        location.href = $("#return-url").val()
      })
  })
});