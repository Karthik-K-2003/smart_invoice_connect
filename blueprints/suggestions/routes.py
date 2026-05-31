from flask import render_template, session, redirect
from blueprints.suggestions import suggestions_bp

@suggestions_bp.route("/suggestions")
def suggestions():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "suggestions/suggestions.html",
        active_page="suggestions"
    )