import pymysql

# =============================
# CONFIG BDD
# =============================
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root1234",
        database="uniride",
        cursorclass=pymysql.cursors.DictCursor
    )

# =============================
# COMPTE ADMIN GLOBAL DU PROJET
# Tous les camarades auront accès à ce compte
# =============================
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@uniride.ca"
ADMIN_PASSWORD = "AdminUniRide2026!"

