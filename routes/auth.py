import os
import re
import uuid
from flask import Blueprint, request, jsonify, current_app, session
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


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    nom_utilisateur = (data.get("nom_utilisateur") or "").strip()
    email = (data.get("email") or "").strip().lower()
    mot_de_passe = data.get("mot_de_passe") or ""
    nom = (data.get("nom") or "").strip()
    prenom = (data.get("prenom") or "").strip()
    telephone = (data.get("telephone") or "").strip()

    if not nom_utilisateur:
        return jsonify({"error": "Le nom d'utilisateur est obligatoire"}), 400

    if len(nom_utilisateur) > 10:
        return jsonify({"error": "Le nom d'utilisateur ne doit pas dépasser 10 caractères"}), 400

    if not email:
        return jsonify({"error": "L'email est obligatoire"}), 400

    if not email_valide(email):
        return jsonify({"error": "Adresse email invalide"}), 400

    if not mot_de_passe_valide(mot_de_passe):
        return jsonify({
            "error": "Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre"
        }), 400

    if not telephone_canadien_valide(telephone):
        return jsonify({"error": "Le numéro doit être au format canadien : +1 suivi de 10 chiffres"}), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        connection.begin()

        mot_de_passe_hash = generate_password_hash(mot_de_passe)

        cursor.execute("""
            INSERT INTO Utilisateur (
                nom_utilisateur,
                mot_de_passe,
                nom,
                prenom,
                email,
                telephone
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nom_utilisateur, mot_de_passe_hash, nom, prenom, email, telephone))

        id_utilisateur = cursor.lastrowid

        # Création automatique du wallet pour chaque nouveau compte
        cursor.execute("""
            INSERT INTO Wallet (id_utilisateur, solde_argent, solde_points)
            VALUES (%s, 0.00, 0)
        """, (id_utilisateur,))

        connection.commit()

        return jsonify({"message": "Compte créé avec succès"}), 201

    except pymysql.err.IntegrityError:
        if connection:
            connection.rollback()
        return jsonify({"error": "Nom d'utilisateur, email ou téléphone déjà utilisé"}), 409

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    identifiant = (data.get("identifiant") or "").strip()
    mot_de_passe = data.get("mot_de_passe") or ""

    if not identifiant or not mot_de_passe:
        return jsonify({"error": "Identifiant et mot de passe obligatoires"}), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id_utilisateur,
                nom_utilisateur,
                mot_de_passe,
                nom,
                prenom,
                email,
                telephone,
                bio,
                photo_profil,
                role,
                statut
            FROM Utilisateur
            WHERE nom_utilisateur = %s OR email = %s OR telephone = %s
            LIMIT 1
        """, (identifiant, identifiant, identifiant))

        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404

        if user["statut"] != "actif":
            return jsonify({"error": "Compte non actif"}), 403

        if not check_password_hash(user["mot_de_passe"], mot_de_passe):
            return jsonify({"error": "Mot de passe incorrect"}), 401

        user_data = {
            "id_utilisateur": user["id_utilisateur"],
            "nom_utilisateur": user["nom_utilisateur"],
            "nom": user["nom"],
            "prenom": user["prenom"],
            "email": user["email"],
            "telephone": user["telephone"],
            "bio": user["bio"],
            "photo_profil": user["photo_profil"],
            "role": user["role"],
            "statut": user["statut"]
        }

        session["user"] = user_data

        return jsonify({
            "message": "Connexion réussie",
            "user": user_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Déconnexion réussie"}), 200


@auth_bp.route("/me", methods=["GET"])
def get_me():
    user = session.get("user")

    if not user:
        return jsonify({"error": "Utilisateur non connecté"}), 401

    return jsonify({"user": user}), 200


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

        if session.get("user") and session["user"]["id_utilisateur"] == id_utilisateur:
            session["user"].update({
                "nom": updated_user["nom"],
                "prenom": updated_user["prenom"],
                "email": updated_user["email"],
                "telephone": updated_user["telephone"],
                "bio": updated_user["bio"],
                "photo_profil": updated_user["photo_profil"],
                "role": updated_user["role"],
                "statut": updated_user["statut"]
            })

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

        if session.get("user") and session["user"]["id_utilisateur"] == int(id_utilisateur):
            session["user"]["photo_profil"] = relative_path

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