from flask import Blueprint, request, jsonify
from config import get_connection

wallet_bp = Blueprint("wallet", __name__)


def get_or_create_wallet(cursor, id_utilisateur):
    cursor.execute("""
        SELECT *
        FROM Wallet
        WHERE id_utilisateur = %s
    """, (id_utilisateur,))
    wallet = cursor.fetchone()

    if wallet:
        return wallet

    cursor.execute("""
        INSERT INTO Wallet (id_utilisateur, solde_argent, solde_points)
        VALUES (%s, 0.00, 0)
    """, (id_utilisateur,))

    cursor.execute("""
        SELECT *
        FROM Wallet
        WHERE id_utilisateur = %s
    """, (id_utilisateur,))
    return cursor.fetchone()


# =============================
# GET WALLET + CARTES
# =============================
@wallet_bp.route("/wallet/<int:id_utilisateur>", methods=["GET"])
def get_wallet(id_utilisateur):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        connection.begin()

        wallet = get_or_create_wallet(cursor, id_utilisateur)

        cursor.execute("""
            SELECT *
            FROM HistoriqueWallet
            WHERE id_wallet = %s
            ORDER BY date_operation DESC
        """, (wallet["id_wallet"],))
        transactions = cursor.fetchall()

        cursor.execute("""
            SELECT 
                id_carte_credit AS id,
                numero_carte,
                titulaire,
                date_expiration
            FROM CarteCredit
            WHERE id_utilisateur = %s
            ORDER BY id_carte_credit DESC
        """, (id_utilisateur,))
        cartes_credit = cursor.fetchall()

        cursor.execute("""
            SELECT 
                id_carte_debit AS id,
                numero_compte,
                titulaire,
                numero_transit,
                institution
            FROM CarteDebit
            WHERE id_utilisateur = %s
            ORDER BY id_carte_debit DESC
        """, (id_utilisateur,))
        cartes_debit = cursor.fetchall()

        connection.commit()

        return jsonify({
            "wallet": wallet,
            "transactions": transactions,
            "cartes_credit": cartes_credit,
            "cartes_debit": cartes_debit
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


# =============================
# AJOUT CARTE CREDIT
# =============================
@wallet_bp.route("/wallet/ajouter-carte-credit", methods=["POST"])
def ajouter_carte_credit():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    id_utilisateur = data.get("id_utilisateur")
    titulaire = (data.get("titulaire") or "").strip()
    numero = (data.get("numero") or "").strip()
    expiration = (data.get("expiration") or "").strip()

    if not id_utilisateur or not titulaire or not numero or not expiration:
        return jsonify({"error": "Tous les champs sont obligatoires"}), 400

    if not numero.isdigit() or len(numero) != 16:
        return jsonify({"error": "Le numéro de carte doit contenir exactement 16 chiffres"}), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        connection.begin()

        get_or_create_wallet(cursor, id_utilisateur)

        cursor.execute("""
            INSERT INTO CarteCredit (id_utilisateur, titulaire, numero_carte, date_expiration)
            VALUES (%s, %s, %s, %s)
        """, (
            id_utilisateur,
            titulaire,
            numero,
            expiration
        ))

        connection.commit()
        return jsonify({"message": "Carte ajoutée avec succès"}), 201

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =============================
# AJOUT CARTE DEBIT
# =============================
@wallet_bp.route("/wallet/ajouter-carte-debit", methods=["POST"])
def ajouter_carte_debit():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    id_utilisateur = data.get("id_utilisateur")
    titulaire = (data.get("titulaire") or "").strip()
    compte = (data.get("compte") or "").strip()
    transit = (data.get("transit") or "").strip()
    institution = (data.get("institution") or "").strip()

    if not id_utilisateur or not titulaire or not compte or not transit or not institution:
        return jsonify({"error": "Tous les champs sont obligatoires"}), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        connection.begin()

        get_or_create_wallet(cursor, id_utilisateur)

        cursor.execute("""
            INSERT INTO CarteDebit (
                id_utilisateur,
                titulaire,
                numero_compte,
                numero_transit,
                institution
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            id_utilisateur,
            titulaire,
            compte,
            transit,
            institution
        ))

        connection.commit()
        return jsonify({"message": "Compte ajouté avec succès"}), 201

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =============================
# SUPPRIMER CARTE CREDIT
# =============================
@wallet_bp.route("/wallet/supprimer-carte-credit/<int:id>", methods=["DELETE"])
def supprimer_carte_credit(id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM CarteCredit
            WHERE id_carte_credit = %s
        """, (id,))

        connection.commit()
        return jsonify({"message": "Carte supprimée"}), 200

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =============================
# SUPPRIMER CARTE DEBIT
# =============================
@wallet_bp.route("/wallet/supprimer-carte-debit/<int:id>", methods=["DELETE"])
def supprimer_carte_debit(id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM CarteDebit
            WHERE id_carte_debit = %s
        """, (id,))

        connection.commit()
        return jsonify({"message": "Carte supprimée"}), 200

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =============================
# DEPOT ARGENT
# =============================
@wallet_bp.route("/wallet/depot", methods=["POST"])
def depot_wallet():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    id_utilisateur = data.get("id_utilisateur")

    try:
        montant = float(data.get("montant", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Montant invalide"}), 400

    if not id_utilisateur:
        return jsonify({"error": "id_utilisateur obligatoire"}), 400

    if montant <= 0:
        return jsonify({"error": "Le montant doit être supérieur à 0"}), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        connection.begin()

        wallet = get_or_create_wallet(cursor, id_utilisateur)

        cursor.execute("""
            UPDATE Wallet
            SET solde_argent = solde_argent + %s
            WHERE id_wallet = %s
        """, (montant, wallet["id_wallet"]))

        cursor.execute("""
            INSERT INTO HistoriqueWallet (
                id_wallet,
                type_operation,
                montant_argent,
                montant_points,
                description
            )
            VALUES (%s, 'depot', %s, 0, %s)
        """, (
            wallet["id_wallet"],
            montant,
            "Dépôt vers le wallet"
        ))

        connection.commit()

        return jsonify({
            "message": "Dépôt effectué avec succès",
            "nouveau_solde": float(wallet["solde_argent"]) + montant
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


# =============================
# RETRAIT ARGENT
# =============================
@wallet_bp.route("/wallet/retrait", methods=["POST"])
def retrait_wallet():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    id_utilisateur = data.get("id_utilisateur")

    try:
        montant = float(data.get("montant", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Montant invalide"}), 400

    if not id_utilisateur:
        return jsonify({"error": "id_utilisateur obligatoire"}), 400

    if montant <= 0:
        return jsonify({"error": "Le montant doit être supérieur à 0"}), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        connection.begin()

        wallet = get_or_create_wallet(cursor, id_utilisateur)

        solde_actuel = float(wallet["solde_argent"])

        if solde_actuel < montant:
            connection.rollback()
            return jsonify({"error": "Solde insuffisant"}), 400

        cursor.execute("""
            UPDATE Wallet
            SET solde_argent = solde_argent - %s
            WHERE id_wallet = %s
        """, (montant, wallet["id_wallet"]))

        cursor.execute("""
            INSERT INTO HistoriqueWallet (
                id_wallet,
                type_operation,
                montant_argent,
                montant_points,
                description
            )
            VALUES (%s, 'retrait', %s, 0, %s)
        """, (
            wallet["id_wallet"],
            montant,
            "Retrait depuis le wallet"
        ))

        connection.commit()

        return jsonify({
            "message": "Retrait effectué avec succès",
            "nouveau_solde": solde_actuel - montant
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