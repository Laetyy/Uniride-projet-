from flask import Blueprint, request, jsonify
import pymysql
from config import get_connection
from flask import session 

trajets_bp = Blueprint("trajets", __name__)


@trajets_bp.route("/trajets", methods=["GET"])
def get_trajets():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                t.id_trajet,
                t.id_conducteur,
                u.nom_utilisateur AS conducteur,
                u.photo_profil,
                vd.nom_ville AS ville_depart,
                va.nom_ville AS ville_arrivee,
                v.modele AS vehicule,
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
            JOIN Vehicule v ON t.id_vehicule = v.id_vehicule
            WHERE t.statut = 'actif'
            ORDER BY t.date_trajet, t.heure_trajet
        """)

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


@trajets_bp.route("/villes", methods=["GET"])
def get_villes():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id_ville, nom_ville, province
            FROM Ville
            ORDER BY nom_ville ASC
        """)
        villes = cursor.fetchall()

        return jsonify(villes), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@trajets_bp.route("/trajets", methods=["POST"])
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
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            return jsonify({"error": f"Le champ {field} est obligatoire"}), 400

    if str(data["id_ville_depart"]) == str(data["id_ville_arrivee"]):
        return jsonify({"error": "La ville de départ et la ville d'arrivée doivent être différentes"}), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
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
        """, (
            data["id_conducteur"],
            data["id_ville_depart"],
            data["id_ville_arrivee"],
            data["id_vehicule"],
            data["date_trajet"],
            data["heure_trajet"],
            data["prix"],
            data["places_disponibles"],
            data["ambiance"],
            data.get("musique", False),
            data.get("telephone_autorise", False),
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

@trajets_bp.route("/conversation/<int:id_trajet>")
def get_or_create_conversation(id_trajet):
    user = session.get("user")

    conn = get_connection()
    cursor = conn.cursor()

    # 1. vérifier si conversation existe
    cursor.execute("""
        SELECT id_conversation FROM Conversation
        WHERE id_trajet = %s
    """, (id_trajet,))
    
    conv = cursor.fetchone()

    if conv:
        return jsonify(conv)

    # 2. récupérer conducteur + passager
    cursor.execute("""
        SELECT t.id_conducteur, r.id_passager
        FROM Trajet t
        JOIN Reservation r ON r.id_trajet = t.id_trajet
        WHERE t.id_trajet = %s
        LIMIT 1
    """, (id_trajet,))
    
    data = cursor.fetchone()

    if not data:
        return jsonify({"error": "Impossible de créer conversation"}), 400

    # 3. créer conversation
    cursor.execute("""
        INSERT INTO Conversation (id_trajet, id_conducteur, id_passager)
        VALUES (%s, %s, %s)
    """, (
        id_trajet,
        data["id_conducteur"],
        data["id_passager"]
    ))

    conn.commit()

    return jsonify({"id_conversation": cursor.lastrowid})

@trajets_bp.route("/messages/<int:id_conversation>")
def get_messages(id_conversation):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.contenu, u.nom_utilisateur as auteur
        FROM Message m
        JOIN Utilisateur u ON m.id_expediteur = u.id_utilisateur
        WHERE m.id_conversation = %s
        ORDER BY m.date_envoi
    """, (id_conversation,))

    return jsonify(cursor.fetchall())

@trajets_bp.route("/message", methods=["POST"])
def send_message():
    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Message (id_conversation, id_expediteur, contenu)
        VALUES (%s, %s, %s)
    """, (
        data["id_conversation"],
        data["id_expediteur"],
        data["contenu"]
    ))

    conn.commit()

    return jsonify({"ok": True})