import psycopg2 as db
from config import config
import xlsx_mod

class Connection():
    def __init__(self):
        try:
            params = config()
            self.conn = db.connect(**params)
            self.cur = self.conn.cursor()
        except Exception as e:
            print('Connection Error', e)
            exit(1)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.connection.close()
    
    @property
    def connection(self):
        return self.conn

    @property
    def cursor(self):
        return self.cur

    def commit(self):
        return self.connection.commit()
    
    def fetchall(self):
        return self.cursor.fetchall()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()

class Materials(Connection):
    def __init__(self):
        Connection.__init__(self)
        sql=(
        '''
        CREATE TABLE IF NOT EXISTS materials(
            material_serial VARCHAR(16) GENERATED ALWAYS AS (material_state || '-' || material_date || '-' || material_code) STORED,
            material_state VARCHAR(2),
            material_date VARCHAR(7),
            material_code VARCHAR(5) NOT NULL,
            material_description VARCHAR(255) NOT NULL,
            material_unit VARCHAR(10) NOT NULL,
            material_price DECIMAL(20,4)
        )
        ''')
        try:
            self.execute(sql)
            self.commit()
        except Exception as e:
            print("Error accessing materials database", e)

    def insert(self, *args):
        try:
            sql = "INSERT INTO materials(material_state, material_date, material_code, material_description, material_unit, material_price) VALUES (%s,%s,%s,%s,%s,%s)"
            self.execute(sql, args)
            self.commit()
        except Exception as e:
            print("Insertion error", e)
    
    def db_check(self, state, date, print_option=False):
        sql_s = f"SELECT * FROM materials WHERE material_state = '{state}' AND material_date = '{date}'"
        if not self.query(sql_s):
            print("State and reference date not found in materials")
            return False
        if print_option:
            print("This state and date already exists in materials database")
        return True

    def insert_excel(self, state, date, filepath=None):
        try:
            table_rows = xlsx_mod.get_xlsx_materials(filepath)
            for row in table_rows:
                self.insert(state,
                            date,
                            row["code"],
                            row["description"],
                            row["unit"],
                            row["price"])
        except Exception as e:
            print("Insertion error", e)

    def search_state_date_code(self, state, date, code):
        sql = f"SELECT * FROM materials WHERE material_state LIKE %s AND material_date LIKE %s AND material_code LIKE %s"
        args = (state, date, code)
        data = self.query(sql, args)
        if data:
            return data
        print("Register not found:" + state + " " + date + " " + code)
        return None

class Equipments(Connection):
    def __init__(self):
        Connection.__init__(self)
        sql=(
        '''
        CREATE TABLE IF NOT EXISTS equipments(
            equipment_serial VARCHAR(16) GENERATED ALWAYS AS (equipment_state || '-' || equipment_date || '-' || equipment_code) STORED,
            equipment_state VARCHAR(2),
            equipment_date VARCHAR(7),
            equipment_code VARCHAR(5) NOT NULL,
            equipment_description VARCHAR(255) NOT NULL,
            equipment_acquisition_price DECIMAL(20,4),
            equipment_depreciation DECIMAL(20, 4),
            equipment_capital_opportunity DECIMAL(20, 4),
            equipment_insurance_and_taxes DECIMAL(20, 4),
            equipment_maintenance DECIMAL(20, 4),
            equipment_operation DECIMAL(20, 4),
            equipment_operation_labor DECIMAL(20, 4),
            equipment_productive_cost DECIMAL(20, 4),
            equipment_unproductive_cost DECIMAL(20, 4)
        )
        ''')
        try:
            self.execute(sql)
            self.commit()
        except Exception as e:
            print("Error accessing equipments database", e)

    def insert(self, *args):
        try:
            sql = "INSERT INTO equipments(equipment_state, equipment_date, equipment_code, equipment_description, equipment_acquisition_price, equipment_depreciation, equipment_capital_opportunity, equipment_insurance_and_taxes, equipment_maintenance, equipment_operation, equipment_operation_labor, equipment_productive_cost, equipment_unproductive_cost) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            self.execute(sql, args)
            self.commit()
        except Exception as e:
            print("Insertion error in equipment code " + args[2], e)
    
    def db_check(self, state, date, print_option=False):
        sql_s = f"SELECT * FROM equipments WHERE equipment_state = '{state}' AND equipment_date = '{date}'"
        if not self.query(sql_s):
            print("State and reference date not found in equipments")
            return False
        if print_option:
            print("This state and date already exists in equipments database")
        return True

    def insert_excel(self, state, date, filepath=None):
        try:
            table_rows = xlsx_mod.get_xlsx_equipments(filepath)
            for row in table_rows:
                self.insert(state,
                            date,
                            row["code"],
                            row["description"],
                            row["acquisition_price"],
                            row["depreciation"],
                            row["capital_opportunity"],
                            row["insurance_and_taxes"],
                            row["maintenance"],
                            row["operation"],
                            row["operation_labor"],
                            row["productive_cost"],
                            row["unproductive_cost"])
        except Exception as e:
            print("Insertion error in equipment code " + row["code"], e)

    def search_state_date_code(self, state, date, code):
        sql = f"SELECT * FROM equipments WHERE equipment_state LIKE %s AND equipment_date LIKE %s AND equipment_code LIKE %s"
        args = (state, date, code)
        data = self.query(sql, args)
        if data:
            return data
        print("Register not found:" + state + " " + date + " " + code)
        return None


if __name__ == '__main__':
    # equipments = Equipments()
    # if not equipments.db_check("PR", "01/2022"):    
    #     equipments.insert_excel("PR", "01/2022")
    materials = Materials()
    if not materials.db_check("PR", "01/2022"):
        materials.insert_excel("PR", "01/2022")
    # print(materials.search_state_date_code("PR", "01/2022", "M0003"))
