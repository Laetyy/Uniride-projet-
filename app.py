from flask import Flask, render_template
from routes.auth import auth_bp
from routes.trajets import trajets_bp
from routes.reservation import reservation_bp

app = Flask(__name__)

# 🔗 Blueprints (backend API)
app.register_blueprint(auth_bp)
app.register_blueprint(trajets_bp)
app.register_blueprint(reservation_bp)


# 🌐 ROUTES FRONTEND (HTML)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/home")
def home_page():
    return render_template("index.html")


@app.route("/login-page")
def login_page():
    return render_template("login.html")


@app.route("/register-page")
def register_page():
    return render_template("register.html")


@app.route("/trajets-page")
def trajets_page():
    return render_template("trajets.html")


# 🚀 Lancement serveur
if __name__ == "__main__":
    app.run(debug=True, port=5001)