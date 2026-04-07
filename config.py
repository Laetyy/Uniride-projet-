import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root1234",
        database="uniride",
        cursorclass=pymysql.cursors.DictCursor
    )