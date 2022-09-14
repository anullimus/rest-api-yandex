import psycopg2
from app.db.config import host, user, password, db_name

connection = ""
cursor = ""

def connect_db():
    global connection, cursor
    try:
        # connect to exist database
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        print("[INFO] Successfully connected to db")
    except Exception as ex:
        return "[ERROR] Error while working with PostgresSQL", ex


def init_cursor():
    global cursor
    cursor = connection.cursor()

def disconnect_db():
    global connection, cursor
    connection.close()


def create_table():
    # create a new table
    with connection.cursor() as cursor:
        cursor.execute(
            "CREATE TABLE file_system (" \
            "id varchar(255) NOT NULL PRIMARY KEY, " \
            "url varchar(250), " \
            "parentId varchar(255), " \
            "type varchar(255), " \
            "size integer, " \
            "updateDate timestamp);"
        )
        connection.commit()
        print("[INFO] Table created successfully")


def drop_table():
    # drop a new table
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE file_system;")
        connection.commit()
        print("[INFO] Table droped successfully")


def insert_to_bd(id, url, parentId, type, size, updateDate):
    # insert data into the table -- POST
    # todo: rewrite dt to pattern regular expression
    id = "\'" + str(id) + "\'"
    if (type == 'FOLDER' and size == None):
        size = 'null'
    else:
        size = str(size)
    if (type == 'FOLDER' and url == None):
        url = 'null'
    else:
        url = "\'" + str(url) + "\'"
    if parentId == None:
        parentId = 'null'
    else:
        parentId = "\'" + str(parentId) + "\'"
    type = "\'" + type + "\'"
    updateDate = "\'" + str(updateDate).replace('T', ' ')[:19] + "\'"

    line = "INSERT INTO file_system (id, url, parentId, type, size, updateDate) VALUES (" + id + ", " + url + ", " + parentId + ", " + type + ", " + size + ", " + updateDate + ")"
    print(line)
    cursor.execute(
        line
    )
    connection.commit()
    return "[INFO] Data was successfully inserted"


def update_date_by_id(id, updateDate):
    # insert data into the table -- POST
    # todo: move slice to pattern of regular expression
    id = "\'" + str(id) + "\'"
    updateDate = "\'" + str(updateDate).replace('T', ' ')[:19] + "\'"
    line = "UPDATE file_system SET updateDate = " + updateDate + " WHERE file_system.id = " + id + ";"
    print(line)
    cursor.execute(
        line
    )
    connection.commit()
    return "[INFO] Data was successfully updated"


def update_values_by_id(id, url, parentId, type, size, updateDate):
    # insert data into the table -- POST
    # todo: move slice to pattern of regular expression
    # dt = str(datetime.datetime.now())[:19]
    id = "\'" + str(id) + "\'"
    if (type == 'FOLDER' and size == None):
        size = 'null'
    else:
        size = str(size)
    if (type == 'FOLDER' and url == None):
        url = 'null'
    else:
        url = "\'" + str(url) + "\'"
    if parentId == None:
        parentId = 'null'
    else:
        parentId = "\'" + str(parentId) + "\'"
    type = "\'" + type + "\'"
    updateDate = "\'" + str(updateDate).replace('T', ' ')[:19] + "\'"
    line = "UPDATE file_system SET url = " + url + "," \
                        "parentId = " + parentId  + "," \
                        "type = " + type + "," \
                        "size = " + size + "," \
                        "updateDate = " + updateDate + \
        " WHERE file_system.id = " + id + ";"
    print(line)
    cursor.execute(
        line
    )
    connection.commit()
    return "[INFO] Data was successfully updated"


def get_by_id(id):
    # get data from the table -- GET
    id = "\'" + str(id) + "\'"
    line = "SELECT * FROM file_system WHERE file_system.id = " + id + ";"
    print(line)
    cursor.execute(
        line
    )
    return cursor.fetchone()


def get_by_parentId_and_type(parentId, type):
    # get data from the table -- GET
    if parentId == None:
        parentId = 'null'
    else:
        parentId = "\'" + str(parentId) + "\'"
    type = "\'" + type + "\'"
    cursor.execute(
        "SELECT * FROM file_system WHERE file_system.parentId = " + parentId + " AND file_system.type =" + type + ";"
    )
    return cursor.fetchall()


def delete_by_parentId(parentId):
    # delete data from the table -- POST
    if parentId == None:
        parentId = 'null'
    else:
        parentId = "\'" + str(parentId) + "\'"
    cursor.execute(
        "DELETE FROM file_system WHERE file_system.parentId = " + parentId + ";"
    )
    connection.commit()
    return "[INFO] Data was successfully deleted"


def delete_by_id(id):
    # delete data from the table -- POST
    id = "\'" + str(id) + "\'"
    cursor.execute(
        "DELETE FROM file_system WHERE file_system.id = " + id + ";"
    )
    connection.commit()
    return "[INFO] Data was successfully deleted"