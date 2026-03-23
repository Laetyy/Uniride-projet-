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


@app.route("/users", methods=["GET"])
def users():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id_utilisateur, nom_utilisateur, email, role, statut, date_creation
            FROM Utilisateur
        """)
        result = cursor.fetchall()

        for user in result:
            if user.get("date_creation"):
                user["date_creation"] = str(user["date_creation"])

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    nom_utilisateur = data.get("nom_utilisateur")
    mot_de_passe = data.get("mot_de_passe")
    email = data.get("email")
    nom = data.get("nom")
    prenom = data.get("prenom")
    telephone = data.get("telephone")
    role = data.get("role", "passager")

    if not nom_utilisateur or not mot_de_passe or not email:
        return jsonify({
            "error": "nom_utilisateur, mot_de_passe et email sont obligatoires"
        }), 400

    hashed_password = generate_password_hash(mot_de_passe)

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

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
        return jsonify({
            "error": "Nom d'utilisateur, email ou téléphone déjà utilisé"
        }), 409

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    identifiant = data.get("identifiant")
    mot_de_passe = data.get("mot_de_passe")

    if not identifiant or not mot_de_passe:
        return jsonify({
            "error": "identifiant et mot_de_passe sont obligatoires"
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

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
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route("/trajets", methods=["GET"])
def get_trajets():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        SELECT
            t.id_trajet,
            u.nom_utilisateur AS conducteur,
            vd.nom_ville AS ville_depart,
            va.nom_ville AS ville_arrivee,
            t.date_trajet,
            t.heure_trajet,
            t.prix,
            t.places_disponibles,
            t.ambiance,
            t.musique,
            t.telephone_autorise,
            t.statut
        FROM Trajet t
        JOIN Utilisateur u ON t.id_conducteur = u.id_utilisateur
        JOIN Ville vd ON t.id_ville_depart = vd.id_ville
        JOIN Ville va ON t.id_ville_arrivee = va.id_ville
        ORDER BY t.date_trajet, t.heure_trajet
        """
        cursor.execute(query)
        trajets = cursor.fetchall()

        for trajet in trajets:
            if trajet.get("date_trajet"):
                trajet["date_trajet"] = str(trajet["date_trajet"])
            if trajet.get("heure_trajet"):
                trajet["heure_trajet"] = str(trajet["heure_trajet"])

        return jsonify(trajets), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route("/trajets", methods=["POST"])
def create_trajet():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    required_fields = [
        "id_conducteur",
        "id_ville_depart",
        "id_ville_arrivee",
        "id_vehicule",
        "date_trajet",
        "heure_trajet",
        "prix",
        "places_disponibles",
        "ambiance"
    ]

    for field in required_fields:
        if data.get(field) is None:
            return jsonify({"error": f"Le champ {field} est obligatoire"}), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO Trajet (
            id_conducteur,
            id_ville_depart,
            id_ville_arrivee,
            id_vehicule,
            date_trajet,
            heure_trajet,
            prix,
            places_disponibles,
            ambiance,
            musique,
            telephone_autorise,
            statut
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            data["id_conducteur"],
            data["id_ville_depart"],
            data["id_ville_arrivee"],
            data["id_vehicule"],
            data["date_trajet"],
            data["heure_trajet"],
            data["prix"],
            data["places_disponibles"],
            data["ambiance"],
            data.get("musique", True),
            data.get("telephone_autorise", True),
            data.get("statut", "actif")
        ))

        connection.commit()

        return jsonify({
            "message": "Trajet créé avec succès",
            "id_trajet": cursor.lastrowid
        }), 201

    except pymysql.err.IntegrityError as e:
        return jsonify({"error": f"Erreur d'intégrité : {str(e)}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    app.run(debug=True)

@app.route("/reservation", methods=["POST"])
def create_reservation():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    id_trajet = data.get("id_trajet")
    id_passager = data.get("id_passager")
    nb_places = data.get("nb_places", 1)

    if not id_trajet or not id_passager:
        return jsonify({"error": "id_trajet et id_passager sont obligatoires"}), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # 1️⃣ Vérifier le trajet
        cursor.execute("SELECT places_disponibles FROM Trajet WHERE id_trajet = %s", (id_trajet,))
        trajet = cursor.fetchone()

        if not trajet:
            return jsonify({"error": "Trajet introuvable"}), 404

        # 2️⃣ Vérifier les places
        if trajet["places_disponibles"] < nb_places:
            return jsonify({"error": "Pas assez de places disponibles"}), 400

        # 3️⃣ Créer réservation
        cursor.execute("""
            INSERT INTO Reservation (id_trajet, id_passager, nb_places)
            VALUES (%s, %s, %s)
        """, (id_trajet, id_passager, nb_places))

        # 4️⃣ Mettre à jour les places
        cursor.execute("""
            UPDATE Trajet
            SET places_disponibles = places_disponibles - %s
            WHERE id_trajet = %s
        """, (nb_places, id_trajet))

        connection.commit()

        return jsonify({
            "message": "Réservation créée avec succès"
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()