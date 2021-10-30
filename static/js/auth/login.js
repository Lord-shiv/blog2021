const emailField = document.querySelector("#emailField");
const emailFeedback = document.querySelector(".invalidEmailFeedback");
const passField = document.querySelector("#passwordField");
const showPassword = document.querySelector("#showPassword");


// --------------------------+>>
// toggle password show/hide
// --------------------------+>>
$(document).on('click', '#showPassword', function (e) {
    icon = $('#showPassword').find("i");
    icon.toggleClass("fas fa-eye-slash fas fa-eye");
    if (passField.type === "password"){
        passField.type = "text";
    }else{
        passField.type = "password";
    }
})