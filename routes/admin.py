from flask import Blueprint, jsonify, request, render_template
from config import get_connection

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin", methods=["GET"])
def admin_page():
    return render_template("admin.html")


# =========================
# STATS
# =========================
@admin_bp.route("/admin/stats", methods=["GET"])
def admin_stats():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        stats = {}

        cursor.execute("SELECT COUNT(*) AS total FROM Utilisateur")
        stats["total_utilisateurs"] = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM Utilisateur WHERE role = 'conducteur'")
        stats["total_conducteurs"] = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM Trajet")
        stats["total_trajets"] = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM Reservation")
        stats["total_reservations"] = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM DemandeCertification
            WHERE statut_demande = 'en_attente'
        """)
        stats["demandes_en_attente"] = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM Plainte
            WHERE statut_plainte IN ('ouverte', 'traitee')
        """)
        stats["plaintes_ouvertes"] = cursor.fetchone()["total"]

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =========================
# UTILISATEURS
# =========================
@admin_bp.route("/admin/utilisateurs", methods=["GET"])
def admin_get_utilisateurs():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id_utilisateur,
                nom_utilisateur,
                nom,
                prenom,
                email,
                telephone,
                role,
                statut,
                date_creation
            FROM Utilisateur
            ORDER BY id_utilisateur DESC
        """)
        utilisateurs = cursor.fetchall()

        for user in utilisateurs:
            if user.get("date_creation"):
                user["date_creation"] = str(user["date_creation"])

        return jsonify(utilisateurs), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@admin_bp.route("/admin/utilisateur/<int:id_utilisateur>/suspendre", methods=["PUT"])
def suspendre_utilisateur(id_utilisateur):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE Utilisateur
            SET statut = 'suspendu'
            WHERE id_utilisateur = %s
        """, (id_utilisateur,))
        connection.commit()

        return jsonify({"message": "Utilisateur suspendu avec succès"}), 200

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@admin_bp.route("/admin/utilisateur/<int:id_utilisateur>/reactiver", methods=["PUT"])
def reactiver_utilisateur(id_utilisateur):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE Utilisateur
            SET statut = 'actif'
            WHERE id_utilisateur = %s
        """, (id_utilisateur,))
        connection.commit()

        return jsonify({"message": "Utilisateur réactivé avec succès"}), 200

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =========================
# DEMANDES DE CERTIFICATION
# =========================
@admin_bp.route("/admin/demandes-certification", methods=["GET"])
def admin_get_demandes():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                d.id_demande,
                d.id_utilisateur,
                u.nom_utilisateur,
                u.email,
                d.numero_permis,
                d.date_expiration_permis,
                d.type_identite,
                d.numero_identite,
                d.date_expiration_identite,
                d.statut_demande,
                d.commentaire_admin,
                d.date_demande
            FROM DemandeCertification d
            JOIN Utilisateur u ON d.id_utilisateur = u.id_utilisateur
            ORDER BY d.date_demande DESC
        """)
        demandes = cursor.fetchall()

        for demande in demandes:
            if demande.get("date_expiration_permis"):
                demande["date_expiration_permis"] = str(demande["date_expiration_permis"])
            if demande.get("date_expiration_identite"):
                demande["date_expiration_identite"] = str(demande["date_expiration_identite"])
            if demande.get("date_demande"):
                demande["date_demande"] = str(demande["date_demande"])

        return jsonify(demandes), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@admin_bp.route("/admin/demande/<int:id_demande>/accepter", methods=["PUT"])
def accepter_demande(id_demande):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        connection.begin()

        cursor.execute("""
            SELECT id_utilisateur
            FROM DemandeCertification
            WHERE id_demande = %s
        """, (id_demande,))
        demande = cursor.fetchone()

        if not demande:
            connection.rollback()
            return jsonify({"error": "Demande introuvable"}), 404

        id_utilisateur = demande["id_utilisateur"]

        cursor.execute("""
            UPDATE DemandeCertification
            SET statut_demande = 'acceptee',
                commentaire_admin = 'Certification acceptée par l’administrateur'
            WHERE id_demande = %s
        """, (id_demande,))

        cursor.execute("""
            UPDATE Utilisateur
            SET role = 'conducteur'
            WHERE id_utilisateur = %s
        """, (id_utilisateur,))

        connection.commit()

        return jsonify({"message": "Demande acceptée avec succès"}), 200

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@admin_bp.route("/admin/demande/<int:id_demande>/refuser", methods=["PUT"])
def refuser_demande(id_demande):
    connection = None
    cursor = None

    data = request.get_json(silent=True) or {}
    commentaire = (data.get("commentaire_admin") or "Certification refusée par l’administrateur").strip()

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE DemandeCertification
            SET statut_demande = 'refusee',
                commentaire_admin = %s
            WHERE id_demande = %s
        """, (commentaire, id_demande))
        connection.commit()

        return jsonify({"message": "Demande refusée avec succès"}), 200

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =========================
# TRAJETS
# =========================
@admin_bp.route("/admin/trajets", methods=["GET"])
def admin_get_trajets():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                t.id_trajet,
                u.nom_utilisateur AS conducteur,
                vd.nom_ville AS ville_depart,
                va.nom_ville AS ville_arrivee,
                t.date_trajet,
                t.heure_trajet,
                t.prix,
                t.places_disponibles,
                t.statut
            FROM Trajet t
            JOIN Utilisateur u ON t.id_conducteur = u.id_utilisateur
            JOIN Ville vd ON t.id_ville_depart = vd.id_ville
            JOIN Ville va ON t.id_ville_arrivee = va.id_ville
            ORDER BY t.date_trajet DESC, t.heure_trajet DESC
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


# =========================
# WALLETS
# =========================
@admin_bp.route("/admin/wallets", methods=["GET"])
def admin_get_wallets():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                w.id_wallet,
                w.id_utilisateur,
                u.nom_utilisateur,
                u.email,
                w.solde_argent,
                w.solde_points,
                w.date_creation
            FROM Wallet w
            JOIN Utilisateur u ON w.id_utilisateur = u.id_utilisateur
            ORDER BY w.id_wallet DESC
        """)
        wallets = cursor.fetchall()

        for wallet in wallets:
            if wallet.get("date_creation"):
                wallet["date_creation"] = str(wallet["date_creation"])

        return jsonify(wallets), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@admin_bp.route("/admin/wallet/<int:id_wallet>/ajuster", methods=["PUT"])
def ajuster_wallet(id_wallet):
    connection = None
    cursor = None

    data = request.get_json(silent=True) or {}

    try:
        montant_argent = float(data.get("montant_argent", 0))
        montant_points = int(data.get("montant_points", 0))
        description = (data.get("description") or "Ajustement administrateur").strip()

        connection = get_connection()
        cursor = connection.cursor()
        connection.begin()

        cursor.execute("""
            UPDATE Wallet
            SET solde_argent = solde_argent + %s,
                solde_points = solde_points + %s
            WHERE id_wallet = %s
        """, (montant_argent, montant_points, id_wallet))

        cursor.execute("""
            INSERT INTO HistoriqueWallet (
                id_wallet,
                type_operation,
                montant_argent,
                montant_points,
                description
            )
            VALUES (%s, 'ajustement', %s, %s, %s)
        """, (id_wallet, abs(montant_argent), abs(montant_points), description))

        connection.commit()

        return jsonify({"message": "Wallet ajusté avec succès"}), 200

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =========================
# PLAINTES
# =========================
@admin_bp.route("/admin/plaintes", methods=["GET"])
def admin_get_plaintes():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                p.id_plainte,
                p.id_utilisateur,
                u.nom_utilisateur,
                u.email,
                p.sujet,
                p.description,
                p.date_plainte,
                p.statut_plainte
            FROM Plainte p
            JOIN Utilisateur u ON p.id_utilisateur = u.id_utilisateur
            ORDER BY p.date_plainte DESC
        """)
        plaintes = cursor.fetchall()

        for plainte in plaintes:
            if plainte.get("date_plainte"):
                plainte["date_plainte"] = str(plainte["date_plainte"])

        return jsonify(plaintes), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@admin_bp.route("/admin/plainte/<int:id_plainte>/statut", methods=["PUT"])
def admin_modifier_statut_plainte(id_plainte):
    connection = None
    cursor = None

    data = request.get_json(silent=True) or {}
    statut = (data.get("statut_plainte") or "").strip()

    if statut not in ["ouverte", "traitee", "fermee"]:
        return jsonify({"error": "Statut de plainte invalide"}), 400

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE Plainte
            SET statut_plainte = %s
            WHERE id_plainte = %s
        """, (statut, id_plainte))
        connection.commit()

        return jsonify({"message": "Statut de la plainte mis à jour"}), 200

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()