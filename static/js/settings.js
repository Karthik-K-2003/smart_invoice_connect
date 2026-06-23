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

// BUSINESS PROFILE
let originalShopName = "";
let originalPhone = "";
let originalBusinessEmail = "";
let originalGST = "";
let originalAddress = "";

function enableBusinessEdit() {

    const shopName = document.getElementById("shop_name");
    const phone = document.getElementById("phone");
    const email = document.getElementById("business_email");
    const gst = document.getElementById("gst_number");
    const address = document.getElementById("address");

    originalShopName = shopName.value;
    originalPhone = phone.value;
    originalBusinessEmail = email.value;
    originalGST = gst.value;
    originalAddress = address.value;

    shopName.removeAttribute("readonly");
    phone.removeAttribute("readonly");
    email.removeAttribute("readonly");
    gst.removeAttribute("readonly");
    address.removeAttribute("readonly");

    document
        .getElementById("businessEditBtn")
        .classList.add("hidden");

    document
        .getElementById("businessActionButtons")
        .classList.remove("hidden");
}


function cancelBusinessEdit() {

    const shopName = document.getElementById("shop_name");
    const phone = document.getElementById("phone");
    const email = document.getElementById("business_email");
    const gst = document.getElementById("gst_number");
    const address = document.getElementById("address");

    shopName.value = originalShopName;
    phone.value = originalPhone;
    email.value = originalBusinessEmail;
    gst.value = originalGST;
    address.value = originalAddress;

    shopName.setAttribute("readonly", true);
    phone.setAttribute("readonly", true);
    email.setAttribute("readonly", true);
    gst.setAttribute("readonly", true);
    address.setAttribute("readonly", true);

    document
        .getElementById("businessEditBtn")
        .classList.remove("hidden");

    document
        .getElementById("businessActionButtons")
        .classList.add("hidden");
}