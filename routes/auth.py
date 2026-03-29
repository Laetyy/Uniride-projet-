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


@auth_bp.route("/users", methods=["GET"])
def users():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id_utilisateur, nom_utilisateur, email, photo_profil, role, statut, date_creation
            FROM Utilisateur
        """)
        result = cursor.fetchall()

        for user in result:
            if user.get("date_creation"):
                user["date_creation"] = str(user["date_creation"])

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    nom_utilisateur = (data.get("nom_utilisateur") or "").strip()
    mot_de_passe = data.get("mot_de_passe") or ""
    email = (data.get("email") or "").strip().lower()
    nom = (data.get("nom") or "").strip()
    prenom = (data.get("prenom") or "").strip()
    telephone = (data.get("telephone") or "").strip()
    role = data.get("role", "passager")

    if not nom_utilisateur or not mot_de_passe or not email or not telephone:
        return jsonify({
            "error": "nom_utilisateur, mot_de_passe, email et telephone sont obligatoires"
        }), 400

    if len(nom_utilisateur) > 10:
        return jsonify({
            "error": "Le nom d'utilisateur ne doit pas dépasser 10 caractères"
        }), 400

    if not mot_de_passe_valide(mot_de_passe):
        return jsonify({
            "error": "Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre"
        }), 400

    if not telephone_canadien_valide(telephone):
        return jsonify({
            "error": "Le numéro doit être au format canadien : +1 suivi de 10 chiffres"
        }), 400

    if not email_valide(email):
        return jsonify({
            "error": "Adresse email invalide"
        }), 400

    hashed_password = generate_password_hash(mot_de_passe)

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO Utilisateur
        (nom_utilisateur, mot_de_passe, nom, prenom, email, telephone, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            nom_utilisateur,
            hashed_password,
            nom,
            prenom,
            email,
            telephone,
            role
        ))

        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO Wallet (id_utilisateur, solde_argent, solde_points)
            VALUES (%s, %s, %s)
        """, (user_id, 0.00, 0))

        connection.commit()

        return jsonify({
            "message": "Utilisateur créé avec succès",
            "id_utilisateur": user_id
        }), 201

    except pymysql.err.IntegrityError:
        return jsonify({
            "error": "Nom d'utilisateur, email ou téléphone déjà utilisé"
        }), 409

    except Exception as e:
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

    identifiant = data.get("identifiant")
    mot_de_passe = data.get("mot_de_passe")

    if not identifiant or not mot_de_passe:
        return jsonify({
            "error": "identifiant et mot_de_passe sont obligatoires"
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM Utilisateur
            WHERE nom_utilisateur = %s
               OR email = %s
               OR telephone = %s
            LIMIT 1
        """, (identifiant, identifiant, identifiant))

        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404

        if check_password_hash(user["mot_de_passe"], mot_de_passe):
            return jsonify({
                "message": "Connexion réussie",
                "user": {
                    "id_utilisateur": user["id_utilisateur"],
                    "nom_utilisateur": user["nom_utilisateur"],
                    "nom": user["nom"],
                    "prenom": user["prenom"],
                    "email": user["email"],
                    "telephone": user["telephone"],
                    "photo_profil": user["photo_profil"],
                    "role": user["role"],
                    "statut": user["statut"]
                }
            }), 200

        return jsonify({"error": "Mot de passe incorrect"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()