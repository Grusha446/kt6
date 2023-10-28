import sqlite3
import pytest
import os


os.remove('dogs.db')

try:
    sqlite_connection = sqlite3.connect('dogs.db')
    cursor = sqlite_connection.cursor()

    sqlite_create_table_query_dogs = '''CREATE TABLE dogs( 
    id INTEGER PRIMARY KEY, 
    name TEXT NOT NULL, 
    breed TEXT NOT NULL, 
    subbreed TEXT);'''

    sqlite_create_table_query_nursery = '''CREATE TABLE nursery( 
        id INTEGER PRIMARY KEY, 
        county TEXT NOT NULL, 
        city TEXT NOT NULL);'''

    sqlite_create_table_query_buyers = '''CREATE TABLE buyers( 
        id INTEGER PRIMARY KEY, 
        name TEXT NOT NULL, 
        surname TEXT NOT NULL, 
        preferred_breeds TEXT NOT NULL,
        dog_id INTEGER,
        nursery_id INTEGER);'''

    print("База данных подключена к БД")

    cursor.execute(sqlite_create_table_query_dogs)
    cursor.execute(sqlite_create_table_query_nursery)
    cursor.execute(sqlite_create_table_query_buyers)

    sqlite_connection.commit()
    print("Таблицы созданы")

    sqlite_select_query = "select sqlite_version();"
    cursor.execute(sqlite_select_query)
    record = cursor.fetchall()
    print("Версия БД:", record)

except sqlite3.Error as error:
    print("Ошибка при подключении", error)

finally:
    if (sqlite_connection):
        sqlite_connection.close()
        print("Соединение с БД закрыто")


@pytest.fixture(scope='session')
def db_connection():
    connection = sqlite3.connect(':memory:')
    yield connection
    connection.close()


@pytest.fixture(scope='function')
def create_table(db_connection):
    cursor = db_connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS test_table (
                       id INTEGER PRIMARY KEY,
                       name TEXT NOT NULL);''')
    db_connection.commit()
    yield
    cursor.execute('''DROP TABLE IF EXISTS test_table;''')
    db_connection.commit()



def test_insert(db_connection, create_table):
    cursor = db_connection.cursor()
    cursor.execute('''INSERT INTO test_table (name) VALUES ('Alice');''')
    db_connection.commit()

    cursor.execute('''SELECT * FROM test_table;''')
    result = cursor.fetchall()

    assert len(result) == 1
    assert result[0][1] == 'Grigoriy'


def test_update(db_connection, create_table):
    cursor = db_connection.cursor()
    cursor.execute('''INSERT INTO test_table (name) VALUES ('Bob');''')
    db_connection.commit()

    cursor.execute('''UPDATE test_table SET name = 'Charlie' WHERE name = 'Bob';''')
    db_connection.commit()

    cursor.execute('''SELECT * FROM test_table WHERE name = 'Charlie';''')
    result = cursor.fetchall()

    assert len(result) == 1
    assert result[0][1] == 'David'


def test_delete(db_connection, create_table):
    cursor = db_connection.cursor()
    cursor.execute('''INSERT INTO test_table (name) VALUES ('Dave');''')
    db_connection.commit()

    cursor.execute('''DELETE FROM test_table WHERE name = 'Dave';''')
    db_connection.commit()

    cursor.execute('''SELECT * FROM test_table WHERE name = 'Dave';''')
    result = cursor.fetchall()

    assert len(result) == 0


def test_select(db_connection, create_table):
    cursor = db_connection.cursor()
    cursor.execute('''INSERT INTO test_table (name) VALUES ('Eve');''')
    db_connection.commit()

    cursor.execute('''SELECT * FROM test_table WHERE name = 'Eve';''')
    result = cursor.fetchall()

    assert len(result) == 1
    assert result[0][1] == 'AAAAA'