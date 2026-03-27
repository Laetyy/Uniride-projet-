import flask
from routes.auth import auth_bp
from routes.trajets import trajets_bp
from routes.reservation import reservation_bp

app = flask.Flask(__name__)
app.secret_key = 'uniride_secret_key_2026'  # Clé secrète pour les sessions

# 🔗 Blueprints (backend API)
app.register_blueprint(auth_bp)
app.register_blueprint(trajets_bp)
app.register_blueprint(reservation_bp)


# 🌐 ROUTES FRONTEND (HTML)

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

@app.route("/conducteurs-page")
def conducteur_page():
    return flask.render_template("conducteur.html")




# 🚀 Lancement serveur
if __name__ == "__main__":
    app.run(debug=True, port=5001)