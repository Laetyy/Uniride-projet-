from flask import Blueprint, request, jsonify
from config import get_connection

wallet_bp = Blueprint("wallet", __name__)

# =============================
# GET WALLET + CARTES
# =============================
@wallet_bp.route("/wallet/<int:id_utilisateur>", methods=["GET"])
def get_wallet(id_utilisateur):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # ===== WALLET =====
        cursor.execute("""
            SELECT * FROM Wallet WHERE id_utilisateur = %s
        """, (id_utilisateur,))
        wallet = cursor.fetchone()

        # ===== TRANSACTIONS =====
        cursor.execute("""
            SELECT * FROM HistoriqueWallet
            WHERE id_wallet = %s
            ORDER BY date_operation DESC
        """, (wallet["id_wallet"],))
        transactions = cursor.fetchall()

        # ===== CARTES CREDIT (IMPORTANT FIX) =====
        cursor.execute("""
            SELECT 
                id_carte_credit AS id,
                numero_carte,
                titulaire
            FROM CarteCredit
            WHERE id_utilisateur = %s
        """, (id_utilisateur,))
        cartes_credit = cursor.fetchall()

        # ===== CARTES DEBIT (IMPORTANT FIX) =====
        cursor.execute("""
            SELECT 
                id_carte_debit AS id,
                numero_compte,
                titulaire
            FROM CarteDebit
            WHERE id_utilisateur = %s
        """, (id_utilisateur,))
        cartes_debit = cursor.fetchall()

        return jsonify({
            "wallet": wallet,
            "transactions": transactions,
            "cartes_credit": cartes_credit,
            "cartes_debit": cartes_debit
        })

    finally:
        cursor.close()
        connection.close()
# =============================
# AJOUT CARTE CREDIT
# =============================
@wallet_bp.route("/wallet/ajouter-carte-credit", methods=["POST"])
def ajouter_carte_credit():
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO CarteCredit (id_utilisateur, titulaire, numero_carte, date_expiration)
            VALUES (%s, %s, %s, %s)
        """, (
            data["id_utilisateur"],
            data["titulaire"],
            data["numero"],
            data["expiration"]
        ))

        connection.commit()
        return jsonify({"message": "Carte ajoutée"})

    finally:
        cursor.close()
        connection.close()


# =============================
# AJOUT CARTE DEBIT
# =============================
@wallet_bp.route("/wallet/ajouter-carte-debit", methods=["POST"])
def ajouter_carte_debit():
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO CarteDebit (id_utilisateur, titulaire, numero_compte, numero_transit, institution)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["id_utilisateur"],
            data["titulaire"],
            data["compte"],
            data["transit"],
            data["institution"]
        ))

        connection.commit()
        return jsonify({"message": "Compte ajouté"})

    finally:
        cursor.close()
        connection.close()

# =============================
# SUPPRIMER CARTE CREDIT
@wallet_bp.route("/wallet/supprimer-carte-credit/<int:id>", methods=["DELETE"])
def supprimer_carte_credit(id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM CarteCredit WHERE id_carte_credit = %s", (id,))
        connection.commit()
        return jsonify({"message": "Carte supprimée"})
    finally:
        cursor.close()
        connection.close()


# =============================
# SUPPRIMER CARTE DEBIT
@wallet_bp.route("/wallet/supprimer-carte-debit/<int:id>", methods=["DELETE"])
def supprimer_carte_debit(id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM CarteDebit WHERE id_carte_debit = %s", (id,))
        connection.commit()
        return jsonify({"message": "Carte supprimée"})
    finally:
        cursor.close()
        connection.close()