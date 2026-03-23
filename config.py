import pymysql


def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root1234",
        database="uniride",
        unix_socket="/tmp/mysql.sock",
        cursorclass=pymysql.cursors.DictCursor
    )