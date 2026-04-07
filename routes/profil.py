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

        cursor.execute("""
            SELECT COUNT(*) AS nb_trajets
            FROM Trajet
            WHERE id_conducteur = %s
        """, (id_utilisateur,))
        nb_trajets_result = cursor.fetchone()
        nb_trajets = nb_trajets_result["nb_trajets"] if nb_trajets_result else 0

        cursor.execute("""
            SELECT COALESCE(SUM(places_disponibles), 0) AS total_places
            FROM Trajet
            WHERE id_conducteur = %s
        """, (id_utilisateur,))
        total_places_result = cursor.fetchone()
        total_places = total_places_result["total_places"] if total_places_result else 0

        cursor.execute("""
            SELECT
                v.modele,
                v.type_vehicule,
                v.couleur,
                v.annee,
                v.plaque_immatriculation
            FROM Vehicule v
            WHERE v.id_utilisateur = %s
            ORDER BY v.id_vehicule DESC
            LIMIT 1
        """, (id_utilisateur,))
        vehicule_row = cursor.fetchone()

        if vehicule_row:
            vehicule = vehicule_row["modele"] or "Non renseigné"
            if vehicule_row.get("annee"):
                vehicule += f" {vehicule_row['annee']}"
            if vehicule_row.get("couleur"):
                vehicule += f" - {vehicule_row['couleur']}"
        else:
            vehicule = "Non renseigné"

        cursor.execute("""
            SELECT
                t.ambiance,
                t.musique,
                t.telephone_autorise,
                t.date_trajet,
                t.heure_trajet,
                vd.nom_ville AS ville_depart,
                va.nom_ville AS ville_arrivee
            FROM Trajet t
            JOIN Ville vd ON t.id_ville_depart = vd.id_ville
            JOIN Ville va ON t.id_ville_arrivee = va.id_ville
            WHERE t.id_conducteur = %s
            ORDER BY t.date_trajet DESC, t.heure_trajet DESC
            LIMIT 1
        """, (id_utilisateur,))
        trajet_info = cursor.fetchone()

        if trajet_info:
            if trajet_info.get("date_trajet"):
                trajet_info["date_trajet"] = str(trajet_info["date_trajet"])
            if trajet_info.get("heure_trajet"):
                trajet_info["heure_trajet"] = str(trajet_info["heure_trajet"])

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