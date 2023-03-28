import tkinter as tk
from tkinter import filedialog
import openpyxl
import db_mod

def comp_sum(comp_code, state, date, Tables, Sicro):
    '''
    Do the sum of all the costs inherent to a composition: equipments, 
    labor, materials, auxiliary activities, fixed time and transportation.
    '''

    fic_value = Sicro.general_data.get_fic(comp_code)
    unit_cost = (equips_sum(comp_code, state, date, Tables, Sicro) + \
                 labor_sum(comp_code, state, date, Tables, Sicro)
                 ) / \
                 Sicro.general_data.get_productivity(comp_code)
    sum = round(unit_cost + \
                unit_cost * \
                fic_value + \
                materials_sum(comp_code, state, date, Tables, Sicro) + \
                aux_activity_sum(comp_code, state, date, Tables, Sicro) + \
                fixed_time_sum(comp_code, state, date, Tables, Sicro)
                , 2
                )
    
    if not comp_code in Tables.total_comps:
        Tables.total_comps.add(comp_code)
    
    # + SomaTransporte(CompCode)
    # TODO: Find where to put the transport_sum

    return sum

def equips_sum(comp_code, state, date, Tables, Sicro):
    '''
    Returns the sum of all the costs inherent to equipments in a composition.
    '''
    equip_sum = 0

    if not Tables.equipments.db_check(state, date, False):
        Tables.equipments.insert_excel(state, date)
    #TODO: Implement error handling if the equipments table doesn't exists

    comp_equips = Sicro.equipments.get_equipments(comp_code)
    if comp_equips:
        for each in comp_equips:
            equip_code = each[1]
            equip_qtt = float(each[2])
            equip_prod = float(each[3])
            equip_unprod = float(each[4])
            equip_sum = equip_sum + \
                        round(equip_qtt * \
                        (equip_prod * \
                        float(Tables.equipments.search_state_date_code(state, date, equip_code)[0][11]) + \
                        equip_unprod * \
                        float(Tables.equipments.search_state_date_code(state, date, equip_code)[0][12])) \
                        ,4)
            
            #TODO: Change this code to use db

            if not equip_code in Tables.total_equipments:
                Tables.total_equipments[equip_code] = {}
            if not "total_sum" in Tables.total_equipments[equip_code]:
                Tables.total_equipments[equip_code]["total_sum"] = equip_qtt
                Tables.total_equipments[equip_code]["max_qtt"] = equip_qtt
            else:
                Tables.total_equipments[equip_code]["total_sum"] += equip_qtt
                if Tables.total_equipments[equip_code]["max_qtt"] < equip_qtt:
                    Tables.total_equipments[equip_code]["max_qtt"] = equip_qtt

    return round(equip_sum, 4)
    
def labor_sum(comp_code, state, date, Tables, Sicro):
    '''
    Returns the sum of all the costs inherent to labors in a composition.
    '''
    if not Tables.labors.db_check(state, date, False):
        Tables.labors.insert_excel(state, date)

    labor_sum = 0
    comp_labor = Sicro.labors.get_labors(comp_code)
    if comp_labor:
        for each in comp_labor:
            labor_code = each[1]
            labor_qtt = float(each[2])
            labor_sum = labor_sum + \
                        round(labor_qtt * \
                        float(Tables.labors.search_state_date_code(state, date, labor_code)[0][7]) \
                        , 4)

    return round(labor_sum, 4)

def materials_sum(comp_code, state, date, Tables, Sicro):
    '''
    Returns the sum of all the costs inherent to materials in a composition.
    '''
    if not Tables.materials.db_check(state, date, False):
        Tables.materials.insert_excel(state, date)

    material_sum = 0
    materials = Sicro.materials.get_materials(comp_code)
    if materials:
        for each in materials:
            material_code = each[1]
            material_qtt = float(each[2])
            material_sum = material_sum + round(material_qtt * float(Tables.materials.search_state_date_code(state, date, material_code)[0][5]), 4)

    return round(material_sum, 4)


def aux_activity_sum(comp_code, state, date, Tables, Sicro):
    '''
    Returns the sum of all auxiliary activities costs of a composition.
    '''

    aux_activity_sum = 0
    aux_activity = Sicro.aux_activities.get_aux_activity(comp_code)
    if aux_activity:
        for each in aux_activity:
            aux_activity_code = each[1]
            aux_activity_qtt = float(each[2])
            aux_activity_sum = aux_activity_sum + round(aux_activity_qtt * comp_sum(aux_activity_code, state, date, Tables, Sicro), 4)

    return round(aux_activity_sum, 4)


def fixed_time_sum(comp_code, state, date, Tables, Sicro):
    '''
    Returns the sum of all costs inherent to fixed time of a composition.
    '''

    fixed_time_sum = 0
    fixed_time = Sicro.fixed_time.get_fixed_time(comp_code)
    if fixed_time:
        for each in fixed_time:
            fixed_time_code = each[2]
            fixed_time_qtt = float(each[3])
            fixed_time_sum = fixed_time_sum + round(fixed_time_qtt * comp_sum(fixed_time_code, state, date, Tables, Sicro), 4)

    return round(fixed_time_sum, 4)


def transport_sum(comp_code, state, date, Tables, Sicro):
    '''
    Returns the sum of all transportation costs of a composition.
    '''

    transport_sum = 0
    transport = Sicro.transportation.get_transportation(comp_code)
    if transport:
        for each in transport:
            transport_code = each[4]
            transport_qtt = float(each[2])
            transport_sum = transport_sum + round(transport_qtt * comp_sum(transport_code, state, date, Tables, Sicro), 4)

    return round(transport_sum, 4)


class Sicro:
    def __init__(self):
        self.general_data = db_mod.SICROGeneralData()
        self.equipments = db_mod.SICROEquipments()
        self.labors = db_mod.SICROLabors()
        self.materials = db_mod.SICROMaterials()
        self.aux_activities = db_mod.SICROAuxiliaryActivities()
        self.fixed_time = db_mod.SICROFixedTime()
        self.transportation = db_mod.SICROTransportation()
    

class Tables:
    def __init__(self):
        self.materials = db_mod.Materials()
        self.equipments = db_mod.Equipments()
        self.labors = db_mod.Labors()
        self.total_equipments = {}
        self.total_comps = set()

    def wb_prices_import(self, filepath=None):
        # Imports the compositions price data from the *.xlsx file to a dictionary
        if not filepath:
            root = tk.Tk()
            root.withdraw()
            filepath = filedialog.askopenfilename(title='Selecione o arquivo referente ao Relatório Sintético de Composições',
                                                filetypes=[("Excel files", "*.xlsx")])

        ps = openpyxl.load_workbook(filepath)
        sheet = ps.active

        row = 1

        while sheet['A' + str(row)].value != "Código":
            row += 1

        row += 1

        while sheet['A' + str(row)].value is None:
            row += 1

        price = {}

        while row <= sheet.max_row:
            code = sheet['A' + str(row)].value
            data3 = sheet['D' + str(row)].value
            price[code] = data3
            row += 1

        ps.close()
        
        self.prices = price
    

if __name__ == '__main__':
    tables = Tables()
    sicro = Sicro()
    # tables.json_import()
    codes = ['2306726','1416141','1108120','2306730','0407819','2306731','2306014','1106061','3108009','1100657','4507956','3806420','1106088','0307737','0307084','3009024','2408149','2419790','2419705','2419704','2408080','2306671','2306644','2306726','2003767','1901618','1901619','2306269','3106120','2007971','1109669','3107997','3806426','2003652','1106057','3107996','1505879','2003714','2003837','1600405','4915667','4915669','4011278','4011301','4011214']
    state = 'PR'
    date = '01/2022'
    for comp_code in codes:
        # print('Equip: R$', equips_sum(comp_code, state, date, tables, sicro))
        # print('Labor: R$', labor_sum(comp_code, state, date, tables, sicro))
        # print('Material: R$', materials_sum(comp_code, state, date, tables, sicro))
        # print('Auxiliary activities: R$', aux_activity_sum(comp_code, state, date, tables, sicro))
        # print('Fixed Time: R$', fixed_time_sum(comp_code, state, date, tables, sicro))
        # print('Transportation: R$', transport_sum(comp_code, state, date, tables, sicro))

        print('Total: R$', round(comp_sum(comp_code, state, date, tables, sicro), 4))

    #for equip in tables.total_equipments:
    #    print(equip, "|", tables.total_equipments[equip]["total_sum"], "|", tables.total_equipments[equip]["max_qtt"])

    print(tables.total_comps)

# for code in preco:
#    if code != '0919002' and code != '0919210' and code != '7119788':
#        soma = SOMAComp(code)
#        verif = preco[code] == soma
#        if not verif:
#            print(code, preco[code], soma, verif)
#    else:
#        continue


# print(dict)
# file = open("dict.txt", "w")
# str_dictionary = repr(dict)
# file.write(str_dictionary + "\n")
# file.close()
# print(FIC)
# print(materiais)
# print(equips)
# print(maodeobra)
# print(preco)

# print(soma - SomaTransporte(CompCode))