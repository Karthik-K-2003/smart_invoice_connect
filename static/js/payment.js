const paymentForm = document.getElementById("paymentForm");

if (paymentForm) {

    paymentForm.addEventListener("submit", function () {

        document
            .getElementById("loadingSpinner")
            .classList.remove("hidden");

        document.querySelector(
            "button[type='submit']"
        ).disabled = true;

    });

}

document.getElementById("invoiceSelect")
    .addEventListener("change", function () {

        const selected =
            this.options[this.selectedIndex];

        document.getElementById("customerName").innerText =
            selected.dataset.customer || "-";

        document.getElementById("invoiceAmount").innerText =
            selected.dataset.total || "0.00";

        document.getElementById("invoiceId").value =
            selected.value;

        document.getElementById("paidAmount").value =
            selected.dataset.total || "";

    });