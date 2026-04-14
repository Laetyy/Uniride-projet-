import os
import flask
from flask import session, redirect, url_for
from routes.auth import auth_bp
from routes.trajets import trajets_bp
from routes.reservation import reservation_bp
from routes.conducteur import conducteur_bp
from routes.admin import admin_bp
from routes.profil import profil_bp
from routes.wallet import wallet_bp

app = flask.Flask(__name__)
app.secret_key = "uniride_secret_key_2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

app.register_blueprint(auth_bp)
app.register_blueprint(trajets_bp)
app.register_blueprint(reservation_bp)
app.register_blueprint(conducteur_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(profil_bp)
app.register_blueprint(wallet_bp)


@app.route("/")
def home():
    return flask.render_template("index.html")


@app.route("/home")
def home_page():
    return flask.render_template("index.html")


@app.route("/login-page")
def login_page():
    return flask.render_template("login.html")


@app.route("/register-page")
def register_page():
    return flask.render_template("register.html")


@app.route("/trajets-page")
def trajets_page():
    return flask.render_template("trajets.html")


@app.route("/test")
def test():
    return "ok"


@app.route("/profil-page")
def profile_page():
    return flask.render_template("profil.html")


@app.route("/profil-conducteur-page")
def profil_conducteur_page():
    return flask.render_template("profil_conducteur.html")


@app.route("/conducteur-page")
def conducteur_page():
    return flask.render_template("conducteur.html")


@app.route("/mes-reservations-page")
def mes_reservations_page():
    return flask.render_template("mes_reservations.html")


@app.route("/admin-page")
def admin_page_redirect():
    user = session.get("user")

    if not user:
        return redirect(url_for("login_page"))

    if user.get("role") != "admin":
        return flask.jsonify({"error": "Accès refusé : admin uniquement"}), 403

    if user.get("statut") != "actif":
        return flask.jsonify({"error": "Compte non actif"}), 403

    return redirect("/admin")

@app.route("/wallet-page")
def wallet_page():
    return flask.render_template("wallet.html")

@app.route("/conversation-page")
def conversation_page():
    return flask.render_template("conversation.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)