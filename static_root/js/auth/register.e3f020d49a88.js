const usernameField = document.querySelector("#usernameField");
const userFeedback = document.querySelector(".invalidUsernameFeedback");
const emailField = document.querySelector("#emailField");
const emailFeedback = document.querySelector(".invalidEmailFeedback");
const passField = document.querySelector("#passwordField");
const showPassword = document.querySelector("#showPassword");

// ------------------+>>
// username validator
// ------------------+>>
usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;
    // console.log("usernameVal", usernameVal);


    if (usernameVal.length > 0) {
        fetch('/user/validate/username/', {
            body: JSON.stringify({username: usernameVal}),
            method: "POST",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log('data', data);
            if (data.username_error){
                usernameField.classList.remove("is-valid");
                usernameField.classList.add("is-invalid");
                userFeedback.style.display = "block";
                userFeedback.innerHTML=`<small><p class="text-danger mt-1"><i class="fas fa-times-circle"></i> ${data.username_error}<p></small>`
            }else{
                usernameField.classList.remove("is-invalid");
                usernameField.classList.add("is-valid");
                userFeedback.style.display = "block";
                userFeedback.value = "Mark";
                userFeedback.innerHTML=`<small><p class="text-success mt-1"><i class="fas fa-check-circle"></i> username looks good </p></small>`
            }
        });
    } else {
        userFeedback.style.display = "none";
    }
});

// ------------------+>>
// email validator
// ------------------+>>
emailField.addEventListener("keyup", (e) => {
    const emailVal = e.target.value;
    // console.log("emailVal", emailVal);


    if (emailVal.length > 0) {
        fetch('/user/validate/email/', {
            body: JSON.stringify({email: emailVal}),
            method: "POST",
        })
        .then((res) => res.json())
        .then((dataI) => {
            console.log('dataI', dataI);
            if (dataI.email_error){
                emailField.classList.add("is-invalid");
                emailField.classList.remove("is-valid");
                emailFeedback.style.display = "block";
                emailFeedback.innerHTML=`<small><p class="text-danger mt-1"><i class="fas fa-times-circle"></i> ${dataI.email_error}<p></small>`
            }else{
                emailField.classList.remove("is-invalid");
                emailField.classList.add("is-valid");
                emailFeedback.style.display = "block";
                emailFeedback.innerHTML=`<small><p class="text-success mt-1"><i class="fas fa-check-circle"></i> email looks good</p></small>`
            }
        });
    } else {
        emailFeedback.style.display = "none";
    }
});


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