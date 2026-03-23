from flask import Flask
from routes.auth import auth_bp
from routes.trajets import trajets_bp
from routes.reservation import reservation_bp

app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(trajets_bp)
app.register_blueprint(reservation_bp)


@app.route("/")
def home():
    return "Flask is working"


if __name__ == "__main__":
    app.run(debug=True)