import psycopg2 as db
from config import config
import db_imports

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
            material_state VARCHAR(2),
            material_date VARCHAR(7),
            material_code VARCHAR(5) NOT NULL,
            material_description VARCHAR(255) NOT NULL,
            material_unit VARCHAR(10) NOT NULL,
            material_price DECIMAL(20,4),
            UNIQUE(material_state, material_date, material_code)
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
            print("Insertion error in material code " + args[2], e)
    
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
            table_rows = db_imports.get_xlsx_materials(filepath)
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
            equipment_unproductive_cost DECIMAL(20, 4),
            UNIQUE(equipment_state, equipment_date, equipment_code)
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
            self.execute("ROLLBACK")
    
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
            table_rows = db_imports.get_xlsx_equipments(filepath)
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


class Labors(Connection):
    def __init__(self):
        Connection.__init__(self)
        sql=(
        '''
        CREATE TABLE IF NOT EXISTS labors(
            labor_state VARCHAR(2),
            labor_date VARCHAR(7),
            labor_code VARCHAR(5) NOT NULL,
            labor_description VARCHAR(255) NOT NULL,
            labor_unit VARCHAR(10) NOT NULL,
            labor_salary DECIMAL(20, 4),
            labor_total_charges DECIMAL(7, 6),
            labor_cost DECIMAL(20, 4),
            labor_dangerousness_insalubrity DECIMAL(7, 6),
            UNIQUE(labor_state, labor_date, labor_code)
        )
        ''')
        try:
            self.execute(sql)
            self.commit()
        except Exception as e:
            print("Error accessing labors database", e)

    def insert(self, *args):
        try:
            sql = "INSERT INTO labors(labor_state, labor_date, labor_code, labor_description, labor_unit, labor_salary, labor_total_charges, labor_cost, labor_dangerousness_insalubrity) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            self.execute(sql, args)
            self.commit()
        except Exception as e:
            print("Insertion error in labor code " + args[2], e)
            self.execute("ROLLBACK")
    
    def db_check(self, state, date, print_option=False):
        sql_s = f"SELECT * FROM labors WHERE labor_state = '{state}' AND labor_date = '{date}'"
        if not self.query(sql_s):
            print("State and reference date not found in labors database")
            return False
        if print_option:
            print("This state and date already exists in labors database")
        return True

    def insert_excel(self, state, date, filepath=None):
        try:
            table_rows = db_imports.get_xlsx_labors(filepath)
            for row in table_rows:
                self.insert(state,
                            date,
                            row["code"],
                            row["description"],
                            row["unit"],
                            row["salary"],
                            row["total_charges"],
                            row["cost"],
                            row["dangerousness_and_insalubrity"])
        except Exception as e:
            print("Insertion error in labor code " + row["code"], e)
    
    # TODO: make a function to each search
    def search_state_date_code(self, state, date, code):
        sql = f"SELECT * FROM labors WHERE labor_state LIKE %s AND labor_date LIKE %s AND labor_code LIKE %s"
        args = (state, date, code)
        data = self.query(sql, args)
        if data:
            return data
        print("Register not found:" + state + " " + date + " " + code)
        return None

class SICROGeneralData(Connection):
    def __init__(self):
        Connection.__init__(self)
        sql=(
        '''
        CREATE TABLE IF NOT EXISTS sicro_general_data(
            comp_code VARCHAR(7) NOT NULL PRIMARY KEY,
            comp_description VARCHAR(255) NOT NULL,
            comp_productivity DECIMAL(20, 4) NOT NULL,
            comp_productivity_unit VARCHAR(10) NOT NULL,
            comp_fic DECIMAL(6, 5)
        )
        ''')
        try:
            self.execute(sql)
            self.commit()
        except Exception as e:
            print("Error accessing SICRO General Data database", e)

    def insert(self, *args):
        try:
            sql = "INSERT INTO sicro_general_data(comp_code, comp_description, comp_productivity, comp_productivity_unit, comp_fic) VALUES (%s,%s,%s,%s,%s)"
            self.execute(sql, args)
            self.commit()
        except Exception as e:
            print("Insertion error in sicro_general_data in comp_code " + args[0], e)
            self.execute("ROLLBACK")

    def insert_items(self, filename="comps.json"):
        comp_dict = db_imports.get_json_gd_sicro(filename)
        try:
            for comp in comp_dict:
                self.insert(comp["comp_code"],
                            comp["description"],
                            comp["productivity"],
                            comp["productivity_unit"],
                            comp["fic"])
        except Exception as e:
            print("Insertion error in comp code " + comp["code"], e)

    def get_productivity(self, code):
        sql = f"SELECT * FROM sicro_general_data WHERE comp_code LIKE '" + code + "'" 
        data = self.query(sql)
        if data:
            return float(data[0][2])
        print("Productivity not found:" + code)
        return None

    def get_fic(self, code):
        sql = "SELECT * FROM sicro_general_data WHERE comp_code LIKE '" + code + "'"
        data = self.query(sql)
        if data:
            return float(data[0][4])
        print("FIC not found:" + code)
        return None

class SICROEquipments(Connection):
    def __init__(self):
        Connection.__init__(self)
        sql=(
        '''
        CREATE TABLE IF NOT EXISTS sicro_equipments(
            comp_code VARCHAR(7) NOT NULL,
            equipment_code VARCHAR(5) NOT NULL,
            equipment_quantity DECIMAL(20, 5) NOT NULL,
            equipment_operative DECIMAL(20,2),
            equipment_inoperative DECIMAL(20,2),
            UNIQUE(comp_code, equipment_code)
        )
        ''')
        try:
            self.execute(sql)
            self.commit()
        except Exception as e:
            print("Error accessing SICRO Equipments database", e)

    def insert(self, *args):
        try:
            sql = "INSERT INTO sicro_equipments(comp_code, equipment_code, equipment_quantity, equipment_operative, equipment_inoperative) VALUES (%s,%s,%s,%s,%s)"
            self.execute(sql, args)
            self.commit()
        except Exception as e:
            print("Insertion error in sicro_equipments in comp_code " + args[0], e)
            self.execute("ROLLBACK")

    def insert_items(self, filename="comps.json"):
        dict = db_imports.get_json_equipments_sicro(filename)
        try:
            for item in dict:
                self.insert(item["comp_code"],
                            item["equipment_code"],
                            item["equipment_quantity"],
                            item["equipment_operative"],
                            item["equipment_inoperative"])
        except Exception as e:
            print("Insertion error in comp code " + item["code"], e)

    def get_equipments(self, code):
        sql = f"SELECT * FROM sicro_equipments WHERE comp_code LIKE '" + code + "'" 
        data = self.query(sql)
        if data:
            return data
        return None

    # def get_fic(self, code):
    #     sql = "SELECT * FROM sicro_general_data WHERE comp_code LIKE '" + code + "'"
    #     data = self.query(sql)
    #     if data:
    #         return float(data[0][4])
    #     print("FIC not found:" + code)
    #     return None

class SICROLabors(Connection):
    def __init__(self):
        Connection.__init__(self)
        sql=(
        '''
        CREATE TABLE IF NOT EXISTS sicro_labors(
            comp_code VARCHAR(7) NOT NULL,
            labor_code VARCHAR(5) NOT NULL,
            labor_quantity DECIMAL(20, 5) NOT NULL,
            UNIQUE(comp_code, labor_code)
        )
        ''')
        try:
            self.execute(sql)
            self.commit()
        except Exception as e:
            print("Error accessing SICRO Labors database", e)

    def insert(self, *args):
        try:
            sql = "INSERT INTO sicro_labors(comp_code, labor_code, labor_quantity) VALUES (%s,%s,%s)"
            self.execute(sql, args)
            self.commit()
        except Exception as e:
            print("Insertion error in sicro_labors in comp_code " + args[0], e)
            self.execute("ROLLBACK")

    def insert_items(self, filename="comps.json"):
        dict = db_imports.get_json_labors_sicro(filename)
        try:
            for item in dict:
                self.insert(item["comp_code"],
                            item["labor_code"],
                            item["labor_quantity"])
        except Exception as e:
            print("Insertion labor error in comp code " + item["comp_code"], e)

    def get_labors(self, code):
        sql = f"SELECT * FROM sicro_labors WHERE comp_code LIKE '" + code + "'" 
        data = self.query(sql)
        if data:
            return data
        return None

class SICROMaterials(Connection):
    def __init__(self):
        Connection.__init__(self)
        sql=(
        '''
        CREATE TABLE IF NOT EXISTS sicro_materials(
            comp_code VARCHAR(7) NOT NULL,
            material_code VARCHAR(5) NOT NULL,
            material_quantity DECIMAL(20, 5) NOT NULL,
            UNIQUE(comp_code, material_code)
        )
        ''')
        try:
            self.execute(sql)
            self.commit()
        except Exception as e:
            print("Error accessing SICRO Materials database", e)

    def insert(self, *args):
        try:
            sql = "INSERT INTO sicro_materials(comp_code, material_code, material_quantity) VALUES (%s,%s,%s)"
            self.execute(sql, args)
            self.commit()
        except Exception as e:
            print("Insertion error in sicro_materials in comp_code " + args[0], e)
            self.execute("ROLLBACK")

    def insert_items(self, filename="comps.json"):
        dict = db_imports.get_json_materials_sicro(filename)
        try:
            for item in dict:
                self.insert(item["comp_code"],
                            item["material_code"],
                            item["material_quantity"])
        except Exception as e:
            print("Insertion material error in comp code " + item["comp_code"], e)

    def get_materials(self, code):
        sql = f"SELECT * FROM sicro_materials WHERE comp_code LIKE '" + code + "'" 
        data = self.query(sql)
        if data:
            return data
        return None

class SICROAuxiliaryActivities(Connection):
    def __init__(self):
        Connection.__init__(self)
        sql=(
        '''
        CREATE TABLE IF NOT EXISTS sicro_auxiliary_activities(
            comp_code VARCHAR(7) NOT NULL,
            auxiliary_activity_code VARCHAR(7) NOT NULL,
            auxiliary_activity_quantity DECIMAL(20, 5) NOT NULL,
            UNIQUE(comp_code, auxiliary_activity_code)
        )
        ''')
        try:
            self.execute(sql)
            self.commit()
        except Exception as e:
            print("Error accessing SICRO Auxiliary Activities database", e)

    def insert(self, *args):
        try:
            sql = "INSERT INTO sicro_auxiliary_activities(comp_code, auxiliary_activity_code, auxiliary_activity_quantity) VALUES (%s,%s,%s)"
            self.execute(sql, args)
            self.commit()
        except Exception as e:
            print("Insertion error in sicro_auxiliary_activities in comp_code " + args[0], e)
            self.execute("ROLLBACK")

    def insert_items(self, filename="comps.json"):
        dict = db_imports.get_json_auxiliary_activities_sicro(filename)
        try:
            for item in dict:
                self.insert(item["comp_code"],
                            item["auxiliary_activity_code"],
                            item["auxiliary_activity_quantity"])
        except Exception as e:
            print("Insertion auxiliary_activity error in comp code " + item["comp_code"], e)

    def get_aux_activity(self, code):
        sql = f"SELECT * FROM sicro_auxiliary_activities WHERE comp_code LIKE '" + code + "'" 
        data = self.query(sql)
        if data:
            return data
        return None

class SICROFixedTime(Connection):
    def __init__(self):
        Connection.__init__(self)
        sql=(
        '''
        CREATE TABLE IF NOT EXISTS sicro_fixed_time(
            comp_code VARCHAR(7) NOT NULL,
            item_code VARCHAR(7) NOT NULL,
            fixed_time_code VARCHAR(7) NOT NULL,
            fixed_time_quantity DECIMAL(20, 5) NOT NULL,
            UNIQUE(comp_code, item_code)
        )
        ''')
        try:
            self.execute(sql)
            self.commit()
        except Exception as e:
            print("Error accessing SICRO Fixed Time database", e)

    def insert(self, *args):
        try:
            sql = "INSERT INTO sicro_fixed_time(comp_code, item_code, fixed_time_code, fixed_time_quantity) VALUES (%s,%s,%s,%s)"
            self.execute(sql, args)
            self.commit()
        except Exception as e:
            print("Insertion error in sicro_fixed_time in comp_code " + args[0], e)
            self.execute("ROLLBACK")

    def insert_items(self, filename="comps.json"):
        dict = db_imports.get_json_fixed_time_sicro(filename)
        try:
            for item in dict:
                self.insert(item["comp_code"],
                            item["item_code"],
                            item["fixed_time_code"],
                            item["fixed_time_quantity"])
        except Exception as e:
            print("Insertion fixed_time error in comp code " + item["comp_code"], e)

    def get_fixed_time(self, code):
        sql = f"SELECT * FROM sicro_fixed_time WHERE comp_code LIKE '" + code + "'" 
        data = self.query(sql)
        if data:
            return data
        return None

class SICROTransportation(Connection):
    def __init__(self):
        Connection.__init__(self)
        sql=(
        '''
        CREATE TABLE IF NOT EXISTS sicro_transportation(
            comp_code VARCHAR(7) NOT NULL,
            item_code VARCHAR(7) NOT NULL,
            transportation_quantity DECIMAL(20,5) NOT NULL,
            transportation_code_ln VARCHAR(7),
            transportation_code_rp VARCHAR(7),
            transportation_code_p VARCHAR(7),
            UNIQUE(comp_code, item_code)
        )
        ''')

        try:
            self.execute(sql)
            self.commit()
        except Exception as e:
            print("Error accessing SICRO Transportation database", e)

    def insert(self, *args):
        try:
            sql = "INSERT INTO sicro_transportation(comp_code, item_code, transportation_quantity, transportation_code_ln, transportation_code_rp, transportation_code_p) VALUES (%s,%s,%s,%s,%s,%s)"
            self.execute(sql, args)
            self.commit()
        except Exception as e:
            print("Insertion error in sicro_transportation in comp_code " + args[0], e)
            self.execute("ROLLBACK")

    def insert_items(self, filename="comps.json"):
        dict = db_imports.get_json_transportation_sicro(filename)
        try:
            for item in dict:
                self.insert(item["comp_code"],
                            item["item_code"],
                            item["transportation_quantity"],
                            item["transportation_code_ln"],
                            item["transportation_code_rp"],
                            item["transportation_code_p"])
        except Exception as e:
            print("Insertion transportation error in comp code " + item["comp_code"], e)

    def get_transportation(self, code):
        sql = f"SELECT * FROM sicro_transportation WHERE comp_code LIKE '" + code + "'" 
        data = self.query(sql)
        if data:
            return data
        return None


if __name__ == '__main__':
    state = "PR"
    date = "01/2022"
    equipments = Equipments()
    # print(equipments.search_state_date_code("PR", "01/2022", "E9001"))
    if not equipments.db_check(state, date):    
        equipments.insert_excel(state, date)
    materials = Materials()
    if not materials.db_check(state, date):
        materials.insert_excel(state, date)
    # print(materials.search_state_date_code("PR", "01/2022", "M0003"))
    labors = Labors()
    if not labors.db_check(state, date):
        labors.insert_excel(state, date)
    # general_data = SICROGeneralData()
    # general_data.insert_items()
    # print(general_data.get_fic('0308265'))
    sicro_equipments = SICROEquipments()
    print(sicro_equipments.get_equipments('0408039'))
    # sicro_equipments.insert_items()
    # sicro_labors = SICROLabors()
    # sicro_labors.insert_items()
    # sicro_materials = SICROMaterials()
    # sicro_materials.insert_items()
    # sicro_aux = SICROAuxiliaryActivities()
    # sicro_aux.insert_items()
    # sicro_fixed_time = SICROFixedTime()
    # sicro_fixed_time.insert_items()
    # sicro_transportation = SICROTransportation()
    # sicro_transportation.insert_items()
