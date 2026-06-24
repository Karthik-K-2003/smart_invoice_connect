function openChartModal() {

    document
        .getElementById("chartModal")
        .classList.remove("hidden");

}

function closeChartModal() {

    document
        .getElementById("chartModal")
        .classList.add("hidden");

}

function closeExportMenu() {

    document
        .getElementById("exportMenu")
        .classList.add("hidden");

}

function toggleExportMenu() {

    document
        .getElementById("exportMenu")
        .classList.toggle("hidden");

}

document.addEventListener("click", function (event) {

    const menu =
        document.getElementById("exportMenu");

    const button =
        document.getElementById("exportBtn");

    if (
        menu &&
        button &&
        !menu.contains(event.target) &&
        !button.contains(event.target)
    ) {

        menu.classList.add("hidden");

    }

});