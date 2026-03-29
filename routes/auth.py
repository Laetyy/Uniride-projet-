import os
import re
import uuid
from flask import Blueprint, request, jsonify, current_app
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import get_connection

auth_bp = Blueprint("auth", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def mot_de_passe_valide(mot_de_passe):
    if len(mot_de_passe) < 8:
        return False
    if not re.search(r"[A-Z]", mot_de_passe):
        return False
    if not re.search(r"[a-z]", mot_de_passe):
        return False
    if not re.search(r"\d", mot_de_passe):
        return False
    return True


def telephone_canadien_valide(telephone):
    return re.fullmatch(r"\+1\d{10}", telephone) is not None


def email_valide(email):
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is not None


@auth_bp.route("/profil/<int:id_utilisateur>", methods=["GET"])
def get_profile(id_utilisateur):
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
                bio,
                photo_profil,
                role,
                statut
            FROM Utilisateur
            WHERE id_utilisateur = %s
        """, (id_utilisateur,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404

        return jsonify(user), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@auth_bp.route("/profil/<int:id_utilisateur>", methods=["PUT"])
def update_profile(id_utilisateur):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    nom = (data.get("nom") or "").strip()
    prenom = (data.get("prenom") or "").strip()
    email = (data.get("email") or "").strip().lower()
    telephone = (data.get("telephone") or "").strip()
    bio = (data.get("bio") or "").strip()

    if not email:
        return jsonify({"error": "L'email est obligatoire"}), 400

    if not email_valide(email):
        return jsonify({"error": "Adresse email invalide"}), 400

    if telephone and not telephone_canadien_valide(telephone):
        return jsonify({"error": "Le numéro doit être au format canadien : +1 suivi de 10 chiffres"}), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE Utilisateur
            SET nom = %s,
                prenom = %s,
                email = %s,
                telephone = %s,
                bio = %s
            WHERE id_utilisateur = %s
        """, (nom, prenom, email, telephone, bio, id_utilisateur))

        connection.commit()

        cursor.execute("""
            SELECT
                id_utilisateur,
                nom_utilisateur,
                nom,
                prenom,
                email,
                telephone,
                bio,
                photo_profil,
                role,
                statut
            FROM Utilisateur
            WHERE id_utilisateur = %s
        """, (id_utilisateur,))
        updated_user = cursor.fetchone()

        return jsonify({
            "message": "Profil mis à jour avec succès",
            "user": updated_user
        }), 200

    except pymysql.err.IntegrityError:
        return jsonify({"error": "Email ou téléphone déjà utilisé"}), 409

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@auth_bp.route("/upload-photo", methods=["POST"])
def upload_photo():
    if "photo" not in request.files:
        return jsonify({"error": "Aucune photo envoyée"}), 400

    file = request.files["photo"]
    id_utilisateur = request.form.get("id_utilisateur")

    if not id_utilisateur:
        return jsonify({"error": "id_utilisateur manquant"}), 400

    if file.filename == "":
        return jsonify({"error": "Nom de fichier vide"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Format invalide. Utilise png, jpg, jpeg ou webp"}), 400

    filename = secure_filename(file.filename)
    extension = filename.rsplit(".", 1)[1].lower()
    unique_filename = f"user_{id_utilisateur}_{uuid.uuid4().hex}.{extension}"

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    filepath = os.path.join(upload_dir, unique_filename)
    relative_path = f"uploads/{unique_filename}"

    connection = None
    cursor = None

    try:
        file.save(filepath)

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE Utilisateur
            SET photo_profil = %s
            WHERE id_utilisateur = %s
        """, (relative_path, id_utilisateur))

        connection.commit()

        return jsonify({
            "message": "Photo uploadée avec succès",
            "photo_profil": relative_path
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()