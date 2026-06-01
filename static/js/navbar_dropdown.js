function toggleDropdown() {

    document
        .getElementById("userDropdown")
        .classList.toggle("hidden");
}

window.onclick = function(event) {

    if (!event.target.closest(".relative")) {

        const dropdown =
            document.getElementById("userDropdown");

        if (!dropdown.classList.contains("hidden")) {

            dropdown.classList.add("hidden");
        }
    }
}