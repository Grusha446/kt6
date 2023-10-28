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

@pytest.fixture(scope='session')
def db_connection():
    connection = sqlite3.connect(':memory:')
    yield connection
    connection.close()


@pytest.fixture(scope='function')
def create_tables(db_connection):
    cursor = db_connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS dogs (
                       id INTEGER PRIMARY KEY,
                       name TEXT NOT NULL,
                       breed TEXT NOT NULL);''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS nursery (
                       id INTEGER PRIMARY KEY,
                       name TEXT NOT NULL);''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS buyers (
                       id INTEGER PRIMARY KEY,
                       name TEXT NOT NULL,
                       preferred_breeds TEXT NOT NULL);''')

    db_connection.commit()
    yield
    cursor.execute('''DROP TABLE IF EXISTS dogs;''')
    cursor.execute('''DROP TABLE IF EXISTS nursery;''')
    cursor.execute('''DROP TABLE IF EXISTS buyers;''')
    db_connection.commit()


def test_dogs_limit(db_connection, create_tables):
    cursor = db_connection.cursor()

    # Вставляем 5 собак в питомник
    for i in range(5):
        cursor.execute(f"INSERT INTO dogs (name, breed) VALUES ('Dog {i}', 'Breed {i}');")
    db_connection.commit()

    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("INSERT INTO dogs (name, breed) VALUES ('Dog 6', 'Breed 6');")
        db_connection.commit()


def test_dogs_sorted_by_name(db_connection, create_tables):
    cursor = db_connection.cursor()

    cursor.execute("INSERT INTO dogs (name, breed) VALUES ('Bob', 'Breed1');")
    cursor.execute("INSERT INTO dogs (name, breed) VALUES ('Alice', 'Breed2');")
    cursor.execute("INSERT INTO dogs (name, breed) VALUES ('Charlie', 'Breed3');")
    db_connection.commit()

    cursor.execute("SELECT name FROM dogs ORDER BY name;")
    result = cursor.fetchall()
    expected_result = [('Alice',), ('Bob',), ('Charlie',)]
    assert result == expected_result


def test_buyers_preferred_breeds_limit(db_connection, create_tables):
    cursor = db_connection.cursor()

    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("INSERT INTO buyers (name, preferred_breeds) VALUES ('Buyer1', 'Breed1, Breed2, Breed3, Breed4');")
        db_connection.commit()


    cursor.execute("INSERT INTO buyers (name, preferred_breeds) VALUES ('Buyer2', 'Breed1, Breed2, Breed3');")
    db_connection.commit()

    cursor.execute("SELECT * FROM buyers;")
    result = cursor.fetchall()
    assert len(result) == 1
