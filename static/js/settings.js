let originalName = "";
let originalEmail = "";


function showSection(section, element) {

    document.querySelectorAll(".settings-btn").forEach(btn => {

        btn.classList.remove(
            "bg-cyan-500",
            "text-white"
        );

    });

    element.classList.add(
        "bg-cyan-500",
        "text-white"
    );

    document.getElementById("profile-section").classList.add("hidden");
    document.getElementById("security-section").classList.add("hidden");
    document.getElementById("account-section").classList.add("hidden");

    document.getElementById(section + "-section").classList.remove("hidden");
}


function enableEdit() {

    const nameInput = document.getElementById("name");
    const emailInput = document.getElementById("email");

    //STORE OG VALUES
    originalName = nameInput.value;
    originalEmail = emailInput.value;

    //ENABLE EDITING
    nameInput.removeAttribute("readonly");
    emailInput.removeAttribute("readonly");

    // HIDE EDIT BUTTON
    document.getElementById("editBtn").classList.add("hidden");

    //SHOW BUTTONS
    document.getElementById("actionButtons").classList.remove("hidden");
}


function cancelEdit() {

    const nameInput = document.getElementById("name");
    const emailInput = document.getElementById("email");

    //RESTORE OG VALUES
    nameInput.value = originalName;
    emailInput.value = originalEmail;

    //MAKE READ ONLY
    nameInput.setAttribute("readonly", true);
    emailInput.setAttribute("readonly", true);

    // SHOW EDIT BUTTON
    document.getElementById("editBtn").classList.remove("hidden");

    //HIDE BUTTONS
    document.getElementById("actionButtons")
        .classList.add("hidden");
}

function toggleCurrentPassword() {

    const input = document.getElementById("currentPassword");
    const icon = document.getElementById("currentEyeIcon");

    if (input.type === "password") {

        input.type = "text";
        icon.innerHTML = "🙈";

    } else {

        input.type = "password";
        icon.innerHTML = "👁️";

    }
}


function toggleNewPassword() {

    const input = document.getElementById("newPassword");
    const icon = document.getElementById("newEyeIcon");

    if (input.type === "password") {

        input.type = "text";
        icon.innerHTML = "🙈";

    } else {

        input.type = "password";
        icon.innerHTML = "👁️";

    }
}


function toggleConfirmPassword() {

    const input = document.getElementById("confirmPassword");
    const icon = document.getElementById("confirmEyeIcon");

    if (input.type === "password") {

        input.type = "text";
        icon.innerHTML = "🙈";

    } else {

        input.type = "password";
        icon.innerHTML = "👁️";

    }
}