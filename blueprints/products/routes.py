from flask import render_template, session, redirect, request, flash
from database.db import get_db_connection
from blueprints.products import products_bp


# View
@products_bp.route("/products")
def products():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    products = conn.execute(
        """
        SELECT * FROM products
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "products/products.html",
        products=products,
        active_page="products"
    )


# Add Product
@products_bp.route("/products/add", methods=["POST"])
def add_product():
    if "user_id" not in session:
        return redirect("/login")

    product_name = request.form["product_name"]
    category = request.form["category"]
    price = request.form["price"]
    gst_percentage = request.form["gst_percentage"]
    stock = request.form["stock"]

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO products (user_id, product_name, category, price, gst_percentage, stock)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (session["user_id"], product_name,
         category, price, gst_percentage, stock)
    )

    conn.commit()
    conn.close()

    return redirect("/products")


# Edit Product
@products_bp.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    product = conn.execute(
        """
        SELECT * FROM products
        WHERE id = ? AND user_id = ?
        """,
        (product_id, session["user_id"])
    ).fetchone()

    if request.method == "POST":

        product_name = request.form["product_name"]
        category = request.form["category"]
        price = request.form["price"]
        gst_percentage = request.form["gst_percentage"]
        stock = request.form["stock"]

        conn.execute(
            """
            UPDATE products
            SET product_name = ?,
                category = ?,
                price = ?,
                gst_percentage = ?,
                stock = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                product_name,
                category,
                price,
                gst_percentage,
                stock,
                product_id,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        return redirect("/products")

    conn.close()

    return render_template(
        "products/edit_product.html",
        product=product,
        active_page="products"
    )


# Delete Product
@products_bp.route("/products/delete/<int:product_id>")
def delete_product(product_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    conn.execute(
        """
        DELETE FROM products
        WHERE id = ? AND user_id = ?
        """,
        (product_id, session["user_id"])
    )

    conn.commit()
    flash("Product deleted successfully!", "success")
    conn.close()

    return redirect("/products")
