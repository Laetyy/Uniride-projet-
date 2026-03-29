import os
import flask
from routes.auth import auth_bp
from routes.trajets import trajets_bp
from routes.reservation import reservation_bp
from routes.conducteur import conducteur_bp

app = flask.Flask(__name__)
app.secret_key = 'uniride_secret_key_2026'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

app.register_blueprint(auth_bp)
app.register_blueprint(trajets_bp)
app.register_blueprint(reservation_bp)
app.register_blueprint(conducteur_bp)


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


@app.route("/conducteur-page")
def conducteur_page():
    return flask.render_template("conducteur.html")


@app.route("/mes-reservations-page")
def mes_reservations_page():
    return flask.render_template("mes_reservations.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)