function togglePassword(inputId, eyeId) {

    const passwordInput = document.getElementById(inputId);
    const eyeIcon = document.getElementById(eyeId);

    if (passwordInput.type === "password") {

        passwordInput.type = "text";
        eyeIcon.innerHTML = "🙈";

    } else {

        passwordInput.type = "password";
        eyeIcon.innerHTML = "👁️";

    }
}