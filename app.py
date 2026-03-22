from flask import Flask
import pymysql

app = Flask(__name__)

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root1234",
        database="uniride",
        unix_socket="/tmp/mysql.sock"
    )

@app.route("/")
def home():
    return "Flask is working"

@app.route("/users")
def users():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Utilisateur")
    result = cursor.fetchall()
    connection.close()
    return str(result)

if __name__ == "__main__":
    app.run(debug=True)