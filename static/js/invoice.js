let subtotal = 0;
let totalGST = 0;

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

            subtotal += itemSubtotal;
            totalGST += gstAmount;

            const tbody =
                document.getElementById("invoiceItemsBody");

            if (tbody.querySelector("td[colspan='5']")) {
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

        });

});