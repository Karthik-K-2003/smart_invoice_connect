let subtotal = 0;
let totalGST = 0;
let invoiceItems = []
let discountPercent = 0;
let discountAmount = 0;

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
                        onclick="removeItem(this, ${price}, ${gst}, ${quantity}, '${selectedOption.value}')"
                        class="bg-red-500 text-white px-3 py-1 rounded">
                        Remove
                    </button>
                </td>
            </tr>
            `;

            updateTotals();

            loadRecommendations(selectedOption.value, invoiceItems.map(item => item.product_id));

            productSelect.selectedIndex = 0;
            quantityInput.value = 1;

        });

    document
        .getElementById("discountPercent")
        .addEventListener("input", updateTotals);

    const invoiceForm = document.querySelector("form");

    invoiceForm.addEventListener("submit", function (e) {

        const customer = document.getElementById("customerSelect").value;

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

function removeItem(button, price, gst, quantity, productId) {

    const row = button.closest("tr");
    row.remove();

    const itemSubtotal = price * quantity;
    const gstAmount = itemSubtotal * gst / 100;

    subtotal -= itemSubtotal;
    totalGST -= gstAmount;

    invoiceItems = invoiceItems.filter(item =>
        !(item.product_id == productId && item.quantity == quantity)
    );

    if (invoiceItems.length === 0) {

        document.getElementById("invoiceItemsBody").innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-4 text-gray-500">
                    No items added
                </td>
            </tr>
        `;

    }

    updateTotals();

}


async function loadRecommendations(productId, currentProducts = []) {

    if (!productId) {
        document
            .getElementById("recommendationSection")
            .classList.add("hidden");
        return;
    }

const response = await fetch(`/recommendations/${productId}?exclude=${currentProducts.join(",")}`);

    const data = await response.json();

    const list = document.getElementById("recommendationList");

    list.innerHTML = "";

    if (data.products.length === 0) {

        document
            .getElementById("recommendationSection")
            .classList.add("hidden");

        return;
    }

    document
        .getElementById("recommendationSection")
        .classList.remove("hidden");

    data.products.forEach(product => {

        list.innerHTML += `
        <div class="border rounded-lg p-4 shadow bg-gray-50">

            <h4 class="font-semibold">
                ${product.product_name}
            </h4>

            <p class="text-cyan-600 mt-2">
                ₹${product.price}
            </p>

            <button
                type="button"
                onclick="addRecommendedProduct(${product.id})"
                class="mt-3 w-full bg-cyan-500 hover:bg-cyan-600 text-white py-2 rounded">

                Add to Invoice

            </button>

        </div>
        `;

    });

}


function addRecommendedProduct(productId) {

    const productSelect = document.getElementById("productSelect");
    productSelect.value = productId;
    document.getElementById("quantity").value = 1;
    document.getElementById("addItemBtn").click();

}


function updateTotals() {

    discountPercent =
        parseFloat(
            document.getElementById("discountPercent").value
        ) || 0;

    if (discountPercent < 0)
        discountPercent = 0;

    if (discountPercent > 100)
        discountPercent = 100;

    document.getElementById("discountPercent").value =
        discountPercent;

    discountAmount =
        (subtotal + totalGST) * discountPercent / 100;

    const grandTotal =
        (subtotal + totalGST) - discountAmount;

    document.getElementById("subtotal").innerText =
        "₹" + subtotal.toFixed(2);

    document.getElementById("gstAmount").innerText =
        "₹" + totalGST.toFixed(2);

    document.getElementById("discountAmount").innerText =
        "₹" + discountAmount.toFixed(2);

    document.getElementById("grandTotal").innerText =
        "₹" + grandTotal.toFixed(2);

    document.getElementById("subtotalInput").value =
        subtotal.toFixed(2);

    document.getElementById("gstInput").value =
        totalGST.toFixed(2);

    document.getElementById("discountPercentInput").value =
        discountPercent;

    document.getElementById("discountAmountInput").value =
        discountAmount.toFixed(2);

    document.getElementById("grandTotalInput").value =
        grandTotal.toFixed(2);

    document.getElementById("invoiceItems").value =
        JSON.stringify(invoiceItems);

}