let subtotal = 0;
let totalGST = 0;
let invoiceItems = []

document.addEventListener("DOMContentLoaded", function () {

    document.getElementById("addItemBtn")
        .addEventListener("click", function () {

            const productSelect = document.getElementById("productSelect");
            const quantityInput = document.getElementById("quantity");
            const selectedOption = productSelect.options[productSelect.selectedIndex];

            if (!selectedOption.value) {
                alert("Select a product");
                return;
            }

            const productName = selectedOption.dataset.name;
            const price = parseFloat(selectedOption.dataset.price);
            const gst = parseFloat(selectedOption.dataset.gst);
            const quantity = parseInt(quantityInput.value);
            const itemSubtotal = price * quantity;
            const gstAmount = itemSubtotal * gst / 100;
            const itemTotal = itemSubtotal + gstAmount;
            invoiceItems.push({
                product_id: selectedOption.value,
                product_name: productName,
                quantity: quantity,
                price: price,
                gst_percentage: gst
            });

            subtotal += itemSubtotal;
            totalGST += gstAmount;

            const tbody =
                document.getElementById("invoiceItemsBody");

            if (tbody.querySelector("td[colspan='6']")) {
                tbody.innerHTML = "";
            }

            tbody.innerHTML += `
            <tr class="border-t">
                <td class="px-4 py-3">${productName}</td>
                <td class="px-4 py-3">${quantity}</td>
                <td class="px-4 py-3">₹${price}</td>
                <td class="px-4 py-3">${gst}%</td>
                <td class="px-4 py-3">₹${itemTotal.toFixed(2)}</td>
                <td class="px-4 py-3">
                    <button
                        type="button"
                        onclick="removeItem(this)"
                        class="bg-red-500 text-white px-3 py-1 rounded">
                        Remove
                    </button>
                </td>
            </tr>
            `;

            document.getElementById("subtotal").innerText =
                "₹" + subtotal.toFixed(2);

            document.getElementById("gstAmount").innerText =
                "₹" + totalGST.toFixed(2);

            document.getElementById("grandTotal").innerText =
                "₹" + (subtotal + totalGST).toFixed(2);

            document.getElementById("invoiceItems").value =
                JSON.stringify(invoiceItems);

            document.getElementById("subtotalInput").value =
                subtotal.toFixed(2);

            document.getElementById("gstInput").value =
                totalGST.toFixed(2);

            document.getElementById("grandTotalInput").value =
                (subtotal + totalGST).toFixed(2);

        });

    const invoiceForm = document.querySelector("form");

    invoiceForm.addEventListener("submit", function (e) {

        const customer =
            document.getElementById("customerSelect").value;

        if (!customer) {

            alert("Please select a customer");
            e.preventDefault();
            return;
        }

        if (invoiceItems.length === 0) {

            alert("Please add at least one item");
            e.preventDefault();
            return;
        }

    });

});

function removeItem(button) {
    const row = button.closest("tr");
    row.remove();

}