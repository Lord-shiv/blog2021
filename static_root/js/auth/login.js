const emailField = document.querySelector("#emailField");
const emailFeedback = document.querySelector(".invalidEmailFeedback");
const passField = document.querySelector("#passwordField");
const showPassword = document.querySelector("#showPassword");



// --------------------------+>>
// toggle password show/hide
// --------------------------+>>

$(".toggle-password").click(function() {

    $(this).toggleClass("fa-eye fa-eye-slash");
    var input = $($(this).attr("toggle"));
    if (input.attr("type") == "password") {
      input.attr("type", "text");
    } else {
      input.attr("type", "password");
    }
  });