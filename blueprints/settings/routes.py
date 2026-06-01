from flask import render_template, request, redirect, session, flash
from blueprints.settings import settings_bp
from database.db import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash


# SETTINGS PAGE
@settings_bp.route("/settings")
def settings():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "settings/settings.html",
        user=user
    )


# UPDATE PROFILE
@settings_bp.route("/update-profile", methods=["POST"])
def update_profile():

    if "user_id" not in session:
        return redirect("/login")

    name = request.form["name"]
    email = request.form["email"]

    conn = get_db_connection()

    # CHECK IF EMAIL ALREADY EXISTS
    existing_user = conn.execute(
        """
        SELECT * FROM users
        WHERE email = ?
        AND id != ?
        """,
        (email, session["user_id"])
    ).fetchone()

    if existing_user:
        conn.close()
        flash("Email already exists", "error")
        return redirect("/settings")

    conn.execute(
        """
        UPDATE users
        SET name = ?, email = ?
        WHERE id = ?
        """,
        (
            name,
            email,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()

    session["user_name"] = name

    flash("Profile updated successfully!", "success")

    return redirect("/settings")


@settings_bp.route("/change-password", methods=["POST"])
def change_password():

    if "user_id" not in session:
        return redirect("/login")

    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    # CHECK CURRENT PASSWORD
    if not check_password_hash(
        user["password"],
        current_password
    ):
        conn.close()
        flash("Current password is incorrect", "error")
        return redirect("/settings")

    # CHECK NEW PASSWORD MATCH
    if new_password != confirm_password:
        conn.close()
        flash("Passwords do not match", "error")
        return redirect("/settings")

    # CHECK IF NEW PASSWORD IS SAME AS CURRENT PASSWORD
    if check_password_hash(
        user["password"],
        new_password
    ):
        conn.close()
        flash(
            "New password must be different from current password",
            "error"
        )
        return redirect("/settings")

    hashed_password = generate_password_hash(
        new_password
    )

    conn.execute(
        """
        UPDATE users
        SET password = ?
        WHERE id = ?
        """,
        (
            hashed_password,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()

    flash(
        "Password updated successfully!",
        "success"
    )

    return redirect("/settings")
