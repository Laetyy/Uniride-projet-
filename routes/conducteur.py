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
                v.modele AS vehicule,
                t.date_trajet,
                t.heure_trajet,
                t.prix,
                t.places_disponibles,
                t.ambiance,
                t.statut
            FROM Trajet t
            JOIN Ville vd ON t.id_ville_depart = vd.id_ville
            JOIN Ville va ON t.id_ville_arrivee = va.id_ville
            JOIN Vehicule v ON t.id_vehicule = v.id_vehicule
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


@conducteur_bp.route("/reservations-conducteur/<int:id_conducteur>", methods=["GET"])
def reservations_conducteur(id_conducteur):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                r.id_reservation,
                u.nom_utilisateur AS passager,
                u.id_utilisateur AS id_passager,
                t.id_trajet,
                t.date_trajet,
                t.heure_trajet,
                t.statut AS statut_trajet,
                vd.nom_ville AS depart,
                va.nom_ville AS arrivee,
                r.nb_places,
                r.statut,
                c.id_conversation,
                COALESCE(SUM(
                    CASE
                        WHEN m.id_expediteur = r.id_passager AND m.lu = FALSE THEN 1
                        ELSE 0
                    END
                ), 0) AS messages_non_lus
            FROM Reservation r
            JOIN Trajet t ON r.id_trajet = t.id_trajet
            JOIN Utilisateur u ON r.id_passager = u.id_utilisateur
            JOIN Ville vd ON t.id_ville_depart = vd.id_ville
            JOIN Ville va ON t.id_ville_arrivee = va.id_ville
            LEFT JOIN Conversation c
                ON c.id_trajet = t.id_trajet
               AND c.id_passager = r.id_passager
               AND c.id_conducteur = t.id_conducteur
            LEFT JOIN Message m
                ON m.id_conversation = c.id_conversation
            WHERE t.id_conducteur = %s
            GROUP BY
                r.id_reservation,
                u.nom_utilisateur,
                u.id_utilisateur,
                t.id_trajet,
                t.date_trajet,
                t.heure_trajet,
                t.statut,
                vd.nom_ville,
                va.nom_ville,
                r.nb_places,
                r.statut,
                c.id_conversation
            ORDER BY r.date_reservation DESC
        """, (id_conducteur,))

        reservations = cursor.fetchall()

        for reservation in reservations:
            if reservation.get("date_trajet"):
                reservation["date_trajet"] = str(reservation["date_trajet"])
            if reservation.get("heure_trajet"):
                reservation["heure_trajet"] = str(reservation["heure_trajet"])
            reservation["messages_non_lus"] = int(reservation.get("messages_non_lus", 0))

        return jsonify(reservations), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@conducteur_bp.route("/conducteur/vehicule/<int:id_utilisateur>", methods=["GET"])
def get_vehicule_conducteur(id_utilisateur):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id_vehicule,
                modele,
                type_vehicule,
                couleur,
                annee,
                plaque_immatriculation
            FROM Vehicule
            WHERE id_utilisateur = %s
            ORDER BY id_vehicule DESC
            LIMIT 1
        """, (id_utilisateur,))

        vehicule = cursor.fetchone()

        if not vehicule:
            return jsonify({"error": "Aucun véhicule trouvé pour ce conducteur"}), 404

        return jsonify(vehicule), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@conducteur_bp.route("/conducteur/trajet/<int:id_trajet>/terminer", methods=["PUT"])
def terminer_trajet(id_trajet):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        connection.begin()

        cursor.execute("""
            SELECT id_trajet, id_conducteur, prix, statut
            FROM Trajet
            WHERE id_trajet = %s
        """, (id_trajet,))
        trajet = cursor.fetchone()

        if not trajet:
            connection.rollback()
            return jsonify({"error": "Trajet introuvable"}), 404

        if trajet["statut"] == "termine":
            connection.rollback()
            return jsonify({"error": "Ce trajet est déjà terminé"}), 400

        cursor.execute("""
            SELECT COALESCE(SUM(nb_places), 0) AS total_places_reservees
            FROM Reservation
            WHERE id_trajet = %s AND statut = 'confirmee'
        """, (id_trajet,))
        total_places_row = cursor.fetchone()
        total_places_reservees = int(total_places_row["total_places_reservees"] or 0)

        montant_total = float(trajet["prix"]) * total_places_reservees

        cursor.execute("""
            UPDATE Trajet
            SET statut = 'termine'
            WHERE id_trajet = %s
        """, (id_trajet,))

        cursor.execute("""
            SELECT id_wallet
            FROM Wallet
            WHERE id_utilisateur = %s
        """, (trajet["id_conducteur"],))
        wallet = cursor.fetchone()

        if not wallet:
            cursor.execute("""
                INSERT INTO Wallet (id_utilisateur, solde_argent, solde_points)
                VALUES (%s, 0.00, 0)
            """, (trajet["id_conducteur"],))
            id_wallet = cursor.lastrowid
        else:
            id_wallet = wallet["id_wallet"]

        if montant_total > 0:
            cursor.execute("""
                UPDATE Wallet
                SET solde_argent = solde_argent + %s
                WHERE id_wallet = %s
            """, (montant_total, id_wallet))

            cursor.execute("""
                INSERT INTO HistoriqueWallet (
                    id_wallet,
                    type_operation,
                    montant_argent,
                    montant_points,
                    description
                )
                VALUES (%s, 'reception', %s, 0, %s)
            """, (
                id_wallet,
                montant_total,
                f"Paiement reçu pour le trajet #{id_trajet}"
            ))

        connection.commit()

        return jsonify({
            "message": "Trajet marqué comme terminé avec succès",
            "montant_recu": montant_total
        }), 200

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()