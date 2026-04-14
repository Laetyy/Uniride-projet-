from flask import Blueprint, request, jsonify, session
import pymysql
from config import get_connection

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


@trajets_bp.route("/conversation/<int:id_trajet>", methods=["GET"])
def get_or_create_conversation(id_trajet):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_conversation
            FROM Conversation
            WHERE id_trajet = %s
            LIMIT 1
        """, (id_trajet,))
        conv = cursor.fetchone()

        if conv:
            return jsonify(conv), 200

        cursor.execute("""
            SELECT t.id_conducteur, r.id_passager
            FROM Trajet t
            JOIN Reservation r ON r.id_trajet = t.id_trajet
            WHERE t.id_trajet = %s
            ORDER BY r.date_reservation DESC
            LIMIT 1
        """, (id_trajet,))
        data = cursor.fetchone()

        if not data:
            return jsonify({"error": "Impossible de créer conversation"}), 400

        cursor.execute("""
            INSERT INTO Conversation (id_trajet, id_conducteur, id_passager)
            VALUES (%s, %s, %s)
        """, (
            id_trajet,
            data["id_conducteur"],
            data["id_passager"]
        ))

        conn.commit()

        return jsonify({"id_conversation": cursor.lastrowid}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@trajets_bp.route("/messages/<int:id_conversation>", methods=["GET"])
def get_messages(id_conversation):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                m.id_message,
                m.id_expediteur,
                m.contenu,
                m.date_envoi,
                m.lu,
                u.nom_utilisateur AS auteur
            FROM Message m
            JOIN Utilisateur u ON m.id_expediteur = u.id_utilisateur
            WHERE m.id_conversation = %s
            ORDER BY m.date_envoi ASC
        """, (id_conversation,))

        messages = cursor.fetchall()

        for message in messages:
            if message.get("date_envoi"):
                message["date_envoi"] = str(message["date_envoi"])
            message["lu"] = bool(message.get("lu"))

        return jsonify(messages), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@trajets_bp.route("/message", methods=["POST"])
def send_message():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    id_conversation = data.get("id_conversation")
    id_expediteur = data.get("id_expediteur")
    contenu = (data.get("contenu") or "").strip()

    if not id_conversation or not id_expediteur or not contenu:
        return jsonify({"error": "Données manquantes"}), 400

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Message (id_conversation, id_expediteur, contenu, lu)
            VALUES (%s, %s, %s, FALSE)
        """, (
            id_conversation,
            id_expediteur,
            contenu
        ))

        conn.commit()

        return jsonify({"ok": True}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@trajets_bp.route("/messages/<int:id_conversation>/read", methods=["PUT"])
def mark_messages_as_read(id_conversation):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    id_utilisateur = data.get("id_utilisateur")

    if not id_utilisateur:
        return jsonify({"error": "id_utilisateur manquant"}), 400

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Message
            SET lu = TRUE
            WHERE id_conversation = %s
              AND id_expediteur <> %s
              AND lu = FALSE
        """, (id_conversation, id_utilisateur))

        conn.commit()

        return jsonify({
            "message": "Messages marqués comme lus",
            "updated": cursor.rowcount
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()