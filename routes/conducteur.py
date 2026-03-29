from flask import Blueprint, request, jsonify
from config import get_connection
from datetime import datetime

conducteur_bp = Blueprint("conducteur", __name__)


def parse_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


@conducteur_bp.route("/conducteur/demande", methods=["POST"])
def demande_conducteur():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    required_fields = [
        "id_utilisateur",
        "numero_permis",
        "date_expiration_permis",
        "type_identite",
        "numero_identite",
        "date_expiration_identite",
        "modele",
        "type_vehicule",
        "plaque_immatriculation"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Le champ {field} est obligatoire"}), 400

    date_expiration_permis = parse_date(data.get("date_expiration_permis"))
    date_expiration_identite = parse_date(data.get("date_expiration_identite"))
    today = datetime.today().date()

    if not date_expiration_permis:
        return jsonify({"error": "La date d'expiration du permis est invalide"}), 400

    if not date_expiration_identite:
        return jsonify({"error": "La date d'expiration de la pièce d'identité est invalide"}), 400

    if date_expiration_permis <= today:
        return jsonify({"error": "Le permis est expiré"}), 400

    if date_expiration_identite <= today:
        return jsonify({"error": "La pièce d'identité est expirée"}), 400

    if data.get("type_identite") not in ["passeport", "assurance_maladie"]:
        return jsonify({"error": "Le type d'identité est invalide"}), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        connection.begin()

        id_utilisateur = data["id_utilisateur"]

        cursor.execute("""
            SELECT id_demande, statut_demande
            FROM DemandeCertification
            WHERE id_utilisateur = %s
            ORDER BY date_demande DESC
            LIMIT 1
        """, (id_utilisateur,))
        existing_demande = cursor.fetchone()

        if existing_demande and existing_demande["statut_demande"] == "en_attente":
            connection.rollback()
            return jsonify({"error": "Une demande est déjà en attente"}), 409

        cursor.execute("""
            INSERT INTO DemandeCertification (
                id_utilisateur,
                numero_permis,
                date_expiration_permis,
                type_identite,
                numero_identite,
                date_expiration_identite,
                statut_demande
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'en_attente')
        """, (
            id_utilisateur,
            data["numero_permis"],
            data["date_expiration_permis"],
            data["type_identite"],
            data["numero_identite"],
            data["date_expiration_identite"]
        ))

        cursor.execute("""
            INSERT INTO Vehicule (
                id_utilisateur,
                modele,
                type_vehicule,
                couleur,
                annee,
                plaque_immatriculation
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            id_utilisateur,
            data["modele"],
            data["type_vehicule"],
            data.get("couleur"),
            data.get("annee") if data.get("annee") else None,
            data["plaque_immatriculation"]
        ))

        connection.commit()

        return jsonify({"message": "Demande de certification envoyée avec succès"}), 201

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@conducteur_bp.route("/conducteur/statut/<int:id_utilisateur>", methods=["GET"])
def statut_conducteur(id_utilisateur):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                statut_demande,
                numero_permis,
                date_expiration_permis,
                type_identite,
                numero_identite,
                date_expiration_identite,
                commentaire_admin,
                date_demande
            FROM DemandeCertification
            WHERE id_utilisateur = %s
            ORDER BY date_demande DESC
            LIMIT 1
        """, (id_utilisateur,))
        demande = cursor.fetchone()

        if not demande:
            return jsonify({"statut": "aucune_demande"}), 200

        if demande.get("date_expiration_permis"):
            demande["date_expiration_permis"] = str(demande["date_expiration_permis"])
        if demande.get("date_expiration_identite"):
            demande["date_expiration_identite"] = str(demande["date_expiration_identite"])

        return jsonify({
            "statut": demande["statut_demande"],
            "numero_permis": demande["numero_permis"],
            "date_expiration_permis": demande["date_expiration_permis"],
            "type_identite": demande["type_identite"],
            "numero_identite": demande["numero_identite"],
            "date_expiration_identite": demande["date_expiration_identite"],
            "commentaire_admin": demande["commentaire_admin"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@conducteur_bp.route("/conducteur/simuler-validation/<int:id_utilisateur>", methods=["POST"])
def simuler_validation(id_utilisateur):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        connection.begin()

        cursor.execute("""
            UPDATE DemandeCertification
            SET statut_demande = 'acceptee', commentaire_admin = 'Validation simulée'
            WHERE id_utilisateur = %s
        """, (id_utilisateur,))

        cursor.execute("""
            UPDATE Utilisateur
            SET role = 'conducteur'
            WHERE id_utilisateur = %s
        """, (id_utilisateur,))

        connection.commit()

        return jsonify({"message": "Conducteur validé avec succès"}), 200

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@conducteur_bp.route("/conducteur/trajets/<int:id_utilisateur>", methods=["GET"])
def get_trajets_conducteur(id_utilisateur):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                t.id_trajet,
                vd.nom_ville AS ville_depart,
                va.nom_ville AS ville_arrivee,
                t.date_trajet,
                t.heure_trajet,
                t.prix,
                t.places_disponibles,
                t.ambiance,
                t.statut
            FROM Trajet t
            JOIN Ville vd ON t.id_ville_depart = vd.id_ville
            JOIN Ville va ON t.id_ville_arrivee = va.id_ville
            WHERE t.id_conducteur = %s
            ORDER BY t.date_trajet DESC, t.heure_trajet DESC
        """, (id_utilisateur,))

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