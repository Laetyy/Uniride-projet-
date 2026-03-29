from flask import Blueprint, request, jsonify
from config import get_connection

reservation_bp = Blueprint("reservation", __name__)


@reservation_bp.route("/reservation", methods=["POST"])
def create_reservation():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    id_trajet = data.get("id_trajet")
    id_passager = data.get("id_passager")

    try:
        nb_places = int(data.get("nb_places", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "nb_places doit être un entier valide"}), 400

    if not id_trajet or not id_passager:
        return jsonify({"error": "id_trajet et id_passager sont obligatoires"}), 400

    if nb_places <= 0:
        return jsonify({"error": "nb_places doit être supérieur à 0"}), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        connection.begin()

        cursor.execute("""
            SELECT id_conducteur, places_disponibles, statut
            FROM Trajet
            WHERE id_trajet = %s
        """, (id_trajet,))
        trajet = cursor.fetchone()

        if not trajet:
            connection.rollback()
            return jsonify({"error": "Trajet introuvable"}), 404

        if trajet["statut"] != "actif":
            connection.rollback()
            return jsonify({"error": "Ce trajet n'est plus disponible"}), 400

        if trajet["id_conducteur"] == int(id_passager):
            connection.rollback()
            return jsonify({"error": "Tu ne peux pas réserver ton propre trajet"}), 400

        if trajet["places_disponibles"] < nb_places:
            connection.rollback()
            return jsonify({"error": "Pas assez de places disponibles"}), 400

        cursor.execute("""
            SELECT id_reservation
            FROM Reservation
            WHERE id_trajet = %s AND id_passager = %s AND statut <> 'annulee'
        """, (id_trajet, id_passager))
        existing = cursor.fetchone()

        if existing:
            connection.rollback()
            return jsonify({"error": "Tu as déjà réservé ce trajet"}), 409

        cursor.execute("""
            INSERT INTO Reservation (id_trajet, id_passager, nb_places, statut)
            VALUES (%s, %s, %s, 'confirmee')
        """, (id_trajet, id_passager, nb_places))

        cursor.execute("""
            UPDATE Trajet
            SET places_disponibles = places_disponibles - %s,
                statut = CASE
                    WHEN places_disponibles - %s <= 0 THEN 'complet'
                    ELSE statut
                END
            WHERE id_trajet = %s
        """, (nb_places, nb_places, id_trajet))

        connection.commit()

        return jsonify({"message": "Réservation créée avec succès"}), 201

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@reservation_bp.route("/reservations/<int:id_passager>", methods=["GET"])
def get_reservations_passager(id_passager):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                r.id_reservation,
                r.nb_places,
                r.statut,
                r.date_reservation,
                t.id_trajet,
                t.date_trajet,
                t.heure_trajet,
                t.prix,
                vd.nom_ville AS ville_depart,
                va.nom_ville AS ville_arrivee,
                u.nom_utilisateur AS conducteur
            FROM Reservation r
            JOIN Trajet t ON r.id_trajet = t.id_trajet
            JOIN Ville vd ON t.id_ville_depart = vd.id_ville
            JOIN Ville va ON t.id_ville_arrivee = va.id_ville
            JOIN Utilisateur u ON t.id_conducteur = u.id_utilisateur
            WHERE r.id_passager = %s
            ORDER BY r.date_reservation DESC
        """, (id_passager,))

        reservations = cursor.fetchall()

        for reservation in reservations:
            if reservation.get("date_reservation"):
                reservation["date_reservation"] = str(reservation["date_reservation"])
            if reservation.get("date_trajet"):
                reservation["date_trajet"] = str(reservation["date_trajet"])
            if reservation.get("heure_trajet"):
                reservation["heure_trajet"] = str(reservation["heure_trajet"])

        return jsonify(reservations), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()