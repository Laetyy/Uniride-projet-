from flask import Flask, request, jsonify
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root1234",
        database="uniride",
        unix_socket="/tmp/mysql.sock",
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route("/")
def home():
    return "Flask is working"


@app.route("/users")
def users():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_utilisateur, nom_utilisateur, email, role, statut, date_creation FROM Utilisateur")
    result = cursor.fetchall()
    connection.close()
    return jsonify(result)


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    nom_utilisateur = data.get("nom_utilisateur")
    mot_de_passe = data.get("mot_de_passe")
    email = data.get("email")
    nom = data.get("nom")
    prenom = data.get("prenom")
    telephone = data.get("telephone")
    role = data.get("role", "passager")

    if not nom_utilisateur or not mot_de_passe or not email:
        return jsonify({"error": "nom_utilisateur, mot_de_passe et email sont obligatoires"}), 400

    hashed_password = generate_password_hash(mot_de_passe)

    connection = get_connection()
    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO Utilisateur
        (nom_utilisateur, mot_de_passe, nom, prenom, email, telephone, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            nom_utilisateur,
            hashed_password,
            nom,
            prenom,
            email,
            telephone,
            role
        ))
        connection.commit()

        user_id = cursor.lastrowid

        wallet_query = """
        INSERT INTO Wallet (id_utilisateur, solde_argent, solde_points)
        VALUES (%s, %s, %s)
        """
        cursor.execute(wallet_query, (user_id, 0.00, 0))
        connection.commit()

        return jsonify({
            "message": "Utilisateur créé avec succès",
            "id_utilisateur": user_id
        }), 201

    except pymysql.err.IntegrityError:
        return jsonify({"error": "Nom d'utilisateur, email ou téléphone déjà utilisé"}), 409

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    identifiant = data.get("identifiant")
    mot_de_passe = data.get("mot_de_passe")

    if not identifiant or not mot_de_passe:
        return jsonify({"error": "identifiant et mot_de_passe sont obligatoires"}), 400

    connection = get_connection()
    cursor = connection.cursor()

    try:
        query = """
        SELECT *
        FROM Utilisateur
        WHERE nom_utilisateur = %s
           OR email = %s
           OR telephone = %s
        LIMIT 1
        """
        cursor.execute(query, (identifiant, identifiant, identifiant))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404

        if check_password_hash(user["mot_de_passe"], mot_de_passe):
            return jsonify({
                "message": "Connexion réussie",
                "user": {
                    "id_utilisateur": user["id_utilisateur"],
                    "nom_utilisateur": user["nom_utilisateur"],
                    "email": user["email"],
                    "role": user["role"],
                    "statut": user["statut"]
                }
            }), 200

        return jsonify({"error": "Mot de passe incorrect"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()


if __name__ == "__main__":
    app.run(debug=True)