from flask import render_template, session, redirect
from blueprints.products import products_bp

@products_bp.route("/products")
def products():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "products/products.html",
        active_page="products"
    )