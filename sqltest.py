import requests
import json
import pandas as pd
import psycopg2
from config import config

def connect_db():
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        con = psycopg2.connect(**params)
        con.autocommit = True
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    return con

def create_db(con, db_name):
    cursor = con.cursor()
    sql = "CREATE database " + db_name
    cursor.execute(sql)
    print("Database created successfully...")

def create_tables():
    '''
    Create tables in the PostgreSQL database
    '''
    commands=(
        '''
        CREATE TABLE materials(
            material_serial VARCHAR(16) GENERATED ALWAYS AS (material_state || '-' || material_date || '-' || material_code) STORED,
            material_state VARCHAR(2),
            material_date VARCHAR(7),
            material_code VARCHAR(5) NOT NULL,
            material_description VARCHAR(255) NOT NULL,
            material_unit VARCHAR(10) NOT NULL,
            material_price DECIMAL(10,4)
        )
        ''')
    conn = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(commands)
        cur.close()
        conn.commit()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def insert_materials(items):
    conn = connect_db()
    cursor = conn.cursor()

    postgres_insert_query = "INSERT INTO materials (material_state, material_date, material_code, material_description, material_unit, material_price) VALUES (%s,%s,%s,%s,%s,%s)"
    for item in items:
        try:
            cursor.execute(postgres_insert_query, item)
            conn.commit()
        except(Exception, psycopg2.Error) as error:
            print('Failed to insert record into table', error)
    
    if conn:
        cursor.close()
        conn.close()
        print('PostgreSQL connection is closed')

if __name__ == '__main__':
    
