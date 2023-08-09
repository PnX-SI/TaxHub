$(document).ready(function () {
  $("#login-submit").click(function () {
    const login_data = {
      login: $("#identifiant").val(),
      password: $("#password").val(),
      id_application: $("#id-app").val(),
    };

    fetch(URL_LOGIN, {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      method: "POST",
      body: JSON.stringify(login_data),
    })
      .then((response) => {
        $("#login-error").hide();
        if (!response.ok) {
          return Promise.reject(response.json());
        }

        return response.json();
      })
      .then((data) => {
        location.href = $("#return-url").val();
      })
      .catch((error) => {
        console.error("There was an error!", error);
        $("#login-error").show();
      });
  });
});
