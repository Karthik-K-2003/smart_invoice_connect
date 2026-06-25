from flask import render_template, request, redirect, session, flash
from blueprints.auth import auth_bp
from database.db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import random
from flask_mail import Message
from utils.mail import mail
from config import *


# REGISTER
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        shop_type = request.form["shop_type"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # CHECKING PASSWORD MATCH
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect("/register")

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()

        # CHECKING IF USER ALREADY EXISTS
        existing_user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            conn.close()
            flash("Email already registered", "error")
            return redirect("/register")

        # INSERT USER
        conn.execute(
            "INSERT INTO users (name, email, password, shop_type) VALUES (?, ?, ?, ?)",
            (name, email, hashed_password, shop_type)
        )

        conn.commit()
        conn.close()
        flash("Registration successful! Please login.", "success")
        return redirect("/login")
    return render_template("auth/register.html")


# LOGIN
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/dashboard")
    
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        remember = request.form.get("remember")

        conn = get_db_connection()

        # CHECKING USER
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        # VALID LOGIN
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["shop_type"] = user["shop_type"]

            # REMEMBER ME
            if remember:
                session.permanent = True
            else:
                session.permanent = False
            flash("Login successful!", "success")
            return redirect("/dashboard")

        else:
            flash("Invalid email or password", "error")
            return redirect("/login")
    return render_template("auth/login.html")


# LOGOUT
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect("/login")


# FORGOT PASSWORD
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        # EMAIL EXISTS
        if user:
            otp = random.randint(100000, 999999)

            # STORE IN SESSION
            session["reset_otp"] = str(otp)
            session["reset_email"] = email
            msg = Message(
                "Smart Invoice Password Reset OTP",
                sender=MAIL_USERNAME,
                recipients=[email]
            )

            msg.body = f"""
            Hello,

            Your Smart Invoice password reset OTP is:

            {otp}

            Do not share this OTP with anyone.
            
            Regards,
            Smart Invoice Team
            """

            mail.send(msg)
            flash("OTP sent to your email successfully!", "success")
            return redirect("/verify-otp")
        else:
            flash("Email not found", "error")
            return redirect("/forgot-password")
    return render_template("auth/password/forgot_password.html")


# VERIFY OTP
@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered_otp = request.form["otp"]
        session_otp = session.get("reset_otp")

        if not session_otp:
            flash("OTP session expired", "error")
            return redirect("/forgot-password")

        if entered_otp == session_otp:
            flash("OTP verified successfully!", "success")
            return redirect("/reset-password")
        else:
            flash("Invalid OTP", "error")
            return redirect("/verify-otp")
    return render_template("auth/password/verify_otp.html")


# RESET PASSWORD
@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect("/reset-password")

        hashed_password = generate_password_hash(password)
        email = session.get("reset_email")

        conn = get_db_connection()

        conn.execute(
            "UPDATE users SET password = ? WHERE email = ?",
            (hashed_password, email)
        )

        conn.commit()
        conn.close()

        # CLEAR SESSION
        session.pop("reset_otp", None)
        session.pop("reset_email", None)
        flash("Password reset successful!", "success")
        return redirect("/login")

    return render_template("auth/password/reset_password.html")
