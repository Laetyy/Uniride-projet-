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

        cursor.execute(
            "SELECT places_disponibles FROM Trajet WHERE id_trajet = %s",
            (id_trajet,)
        )
        trajet = cursor.fetchone()

        if not trajet:
            return jsonify({"error": "Trajet introuvable"}), 404

        if trajet["places_disponibles"] < nb_places:
            return jsonify({"error": "Pas assez de places disponibles"}), 400

        cursor.execute("""
            INSERT INTO Reservation (id_trajet, id_passager, nb_places)
            VALUES (%s, %s, %s)
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
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()