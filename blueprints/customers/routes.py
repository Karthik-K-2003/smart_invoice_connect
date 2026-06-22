from flask import render_template, session, redirect, request
from database.db import get_db_connection
from blueprints.customers import customers_bp


@customers_bp.route("/customers")
def customers():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    customers = conn.execute(
        """
        SELECT * FROM customers
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "customers/customers.html",
        customers=customers,
        active_page="customers"
    )


# Add Customer
@customers_bp.route("/customers/add", methods=["POST"])
def add_customer():

    if "user_id" not in session:
        return redirect("/login")

    customer_name = request.form["customer_name"]
    phone = request.form["phone"]
    email = request.form["email"]
    address = request.form["address"]

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO customers
        (user_id, customer_name, phone, email, address)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            customer_name,
            phone,
            email,
            address
        )
    )

    conn.commit()
    conn.close()

    return redirect("/customers")


# Edit Customer
@customers_bp.route("/customers/edit/<int:customer_id>", methods=["GET", "POST"])
def edit_customer(customer_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    customer = conn.execute(
        """
        SELECT * FROM customers
        WHERE id = ? AND user_id = ?
        """,
        (customer_id, session["user_id"])
    ).fetchone()

    if request.method == "POST":

        customer_name = request.form["customer_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        conn.execute(
            """
            UPDATE customers
            SET customer_name = ?,
                phone = ?,
                email = ?,
                address = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                customer_name,
                phone,
                email,
                address,
                customer_id,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        return redirect("/customers")

    conn.close()

    return render_template(
        "customers/edit_customer.html",
        customer=customer,
        active_page="customers"
    )


# Delete Customer
@customers_bp.route("/customers/delete/<int:customer_id>")
def delete_customer(customer_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    conn.execute(
        """
        DELETE FROM customers
        WHERE id = ? AND user_id = ?
        """,
        (customer_id, session["user_id"])
    )

    conn.commit()
    conn.close()

    return redirect("/customers")
