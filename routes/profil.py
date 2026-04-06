from flask import Blueprint, jsonify
from config import get_connection

profil_bp = Blueprint("profil", __name__)


@profil_bp.route("/profil-conducteur/<int:id_utilisateur>", methods=["GET"])
def get_profil_conducteur(id_utilisateur):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Infos principales du conducteur
        cursor.execute("""
            SELECT
                u.id_utilisateur,
                u.nom,
                u.prenom,
                u.nom_utilisateur,
                u.email,
                u.photo_profil,
                u.bio
            FROM Utilisateur u
            WHERE u.id_utilisateur = %s
        """, (id_utilisateur,))
        conducteur = cursor.fetchone()

        if not conducteur:
            return jsonify({"error": "Conducteur introuvable"}), 404

        # Nombre de trajets publiés
        cursor.execute("""
            SELECT COUNT(*) AS nb_trajets
            FROM Trajet
            WHERE id_conducteur = %s
        """, (id_utilisateur,))
        nb_trajets_result = cursor.fetchone()
        nb_trajets = nb_trajets_result["nb_trajets"] if nb_trajets_result else 0

        # Total des places publiées
        cursor.execute("""
            SELECT COALESCE(SUM(places_disponibles), 0) AS total_places
            FROM Trajet
            WHERE id_conducteur = %s
        """, (id_utilisateur,))
        total_places_result = cursor.fetchone()
        total_places = total_places_result["total_places"] if total_places_result else 0

        # Dernier véhicule utilisé
        cursor.execute("""
            SELECT vehicule
            FROM Trajet
            WHERE id_conducteur = %s
            ORDER BY date_trajet DESC, heure_trajet DESC
            LIMIT 1
        """, (id_utilisateur,))
        vehicule_row = cursor.fetchone()
        vehicule = vehicule_row["vehicule"] if vehicule_row and vehicule_row.get("vehicule") else "Non renseigné"

        # Infos du dernier trajet publié
        cursor.execute("""
            SELECT
                ambiance,
                musique,
                telephone_autorise,
                date_trajet,
                heure_trajet
            FROM Trajet
            WHERE id_conducteur = %s
            ORDER BY date_trajet DESC, heure_trajet DESC
            LIMIT 1
        """, (id_utilisateur,))
        trajet_info = cursor.fetchone()

        if trajet_info:
            if trajet_info.get("date_trajet"):
                trajet_info["date_trajet"] = str(trajet_info["date_trajet"])
            if trajet_info.get("heure_trajet"):
                trajet_info["heure_trajet"] = str(trajet_info["heure_trajet"])

        # Avis clients = table Evaluation
        cursor.execute("""
            SELECT
                e.note,
                e.commentaire,
                u.nom_utilisateur AS auteur
            FROM Evaluation e
            JOIN Utilisateur u ON e.id_passager = u.id_utilisateur
            WHERE e.id_conducteur = %s
            ORDER BY e.date_evaluation DESC
        """, (id_utilisateur,))
        avis = cursor.fetchall()

        moyenne_avis = 0
        if avis and len(avis) > 0:
            moyenne_avis = round(sum(float(a["note"]) for a in avis) / len(avis), 1)

        return jsonify({
            "conducteur": {
                "id_utilisateur": conducteur.get("id_utilisateur"),
                "nom": conducteur.get("nom"),
                "prenom": conducteur.get("prenom"),
                "nom_utilisateur": conducteur.get("nom_utilisateur"),
                "email": conducteur.get("email"),
                "photo_profil": conducteur.get("photo_profil"),
                "bio": conducteur.get("bio")
            },
            "stats": {
                "nb_trajets": nb_trajets,
                "total_places": total_places,
                "vehicule": vehicule,
                "trajet_info": trajet_info,
                "moyenne_avis": moyenne_avis,
                "nb_avis": len(avis)
            },
            "avis": avis
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()