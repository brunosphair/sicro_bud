import tkinter as tk
from tkinter import filedialog
import json
import openpyxl
import db_mod
import decimal


class Composition:
    '''
    Creates the composition class, where the data, imported by the 
    sicro_xlsx_import module, is stored.
    '''
    def __init__(self,
                 name,
                 productivity,
                 equipment,
                 labor,
                 material,
                 aux_activity,
                 fixed_time,
                 transport,
                 fic):
        self.name = name
        self.prod = productivity
        self.equipment = equipment
        self.labor = labor
        self.material = material
        self.aux_activity = aux_activity
        self.fixed_time = fixed_time
        self.transport = transport
        self.fic = int(fic)
    
    def __str__(self):
        return self.name

    def comp_sum(self, state, date, Tables):
        '''
        Do the sum of all the costs inherent to a composition: equipments, 
        labor, materials, auxiliary activities, fixed time and transportation.
        '''
        if not hasattr(Tables, 'comps'):
            Tables.json_import()

        fic_value = self.fic
        unit_cost = (self.equips_sum(Tables) + self.labor_sum(Tables)) / self.prod[0]
        sum = round(unit_cost + unit_cost * fic_value + self.materials_sum(state, date, Tables) \
            + self.aux_activity_sum(state, date, Tables) + self.fixed_time_sum(state, date, Tables), 2)
        
        # + SomaTransporte(CompCode)
        # TODO: Find where to put the transport_sum

        return sum
    
    def equips_sum(self, Tables):
        '''
        Returns the sum of all the costs inherent to equipments in a composition.
        '''
        equip_sum = 0

        if not hasattr(Tables, 'equipments_table'):
            Tables.wb_equip_import()
        if not hasattr(Tables, 'comps'):
            Tables.json_import()

        comp_equips = self.equipment
        if len(comp_equips) != 0:
            for each in comp_equips:
                equip_code = each[0]
                equip_qtt = each[1]
                equip_prod = each[2]
                equip_unprod = each[3]
                equip_sum = equip_sum + round(
                    equip_qtt * (equip_prod * Tables.equipments_table[equip_code][8] + equip_unprod * Tables.equipments_table[equip_code][
                        9]), 4)

        return round(equip_sum, 4)
    
    def labor_sum(self, Tables):
        '''
        Returns the sum of all the costs inherent to labors in a composition.
        '''
        if not hasattr(Tables, 'comps'):
            Tables.json_import()
        if not hasattr(Tables, 'labor_table'):
            Tables.wb_labor_import()

        labor_sum = 0
        comp_labor = self.labor
        if len(comp_labor) != 0:
            for each in comp_labor:
                labor_code = each[0]
                labor_qtt = each[1]
                labor_sum = labor_sum + round(labor_qtt * Tables.labor_table[labor_code][4], 4)

        return round(labor_sum, 4)

    def materials_sum(self, state, date, Tables):
        '''
        Returns the sum of all the costs inherent to materials in a composition.
        '''
        if not hasattr(Tables, 'comps'):
            Tables.json_import()
        if not Tables.materials.db_check(state, date, False):
            Tables.materials.insert_excel(state, date)

        material_sum = 0
        materials = self.material
        if len(materials) != 0:
            for each in materials:
                material_code = each[0]
                material_qtt = each[1]
                material_sum = material_sum + round(material_qtt * float(Tables.materials.search_state_date_code(state, date, material_code)[0][6]), 4)

        return round(material_sum, 4)


    def aux_activity_sum(self, state, date, Tables):
        '''
        Returns the sum of all auxiliary activities costs of a composition.
        '''
        if not hasattr(Tables, 'comps'):
            Tables.json_import()

        aux_activity_sum = 0
        aux_activity = self.aux_activity
        if len(aux_activity) != 0:
            for each in aux_activity:
                aux_activity_code = each[0]
                aux_activity_qtt = each[1]
                aux_activity_sum = aux_activity_sum + round(aux_activity_qtt * Tables.comps[aux_activity_code].comp_sum(state, date, Tables), 4)

        return round(aux_activity_sum, 4)


    def fixed_time_sum(self, state, date, Tables):
        '''
        Returns the sum of all costs inherent to fixed time of a composition.
        '''
        if not hasattr(Tables, 'comps'):
            Tables.json_import()

        fixed_time_sum = 0
        fixed_time = self.fixed_time
        if len(fixed_time) != 0:
            for each in fixed_time:
                fixed_time_code = each[1]
                fixed_time_qtt = each[2]
                fixed_time_sum = fixed_time_sum + round(fixed_time_qtt * Tables.comps[fixed_time_code].comp_sum(state, date, Tables), 4)

        return round(fixed_time_sum, 4)


    def transport_sum(self, state, date, Tables):
        '''
        Returns the sum of all transportation costs of a composition.
        '''
        if not hasattr(Tables, 'comps'):
            Tables.json_import()

        transport_sum = 0
        transport = self.transport
        if len(transport) != 0:
            for each in transport:
                transport_code = each[4]
                transport_qtt = each[1]
                transport_sum = transport_sum + round(transport_qtt * Tables.comps[transport_code].comp_sum(state, date, Tables), 4)

        return round(transport_sum, 4)


class Tables:
    def __init__(self):
        self.materials = db_mod.Materials()

    def json_import(self):

        comps = dict()
        with open('comps.json', 'r') as fp:
            dict_import = json.load(fp)
        for key in dict_import:
            comps[key] = Composition(dict_import[key][0], dict_import[key][1], dict_import[key][2], dict_import[key][3],
                                    dict_import[key][4], dict_import[key][5],
                                    dict_import[key][6], dict_import[key][7], dict_import[key][8])
        
        self.comps = comps
    
    def wb_equip_import(self, filepath=None):
        '''
        Imports the equipments data from the *.xlsx file to a dictionary.
        '''

        if not filepath:
            root = tk.Tk()
            root.withdraw()
            filepath = filedialog.askopenfilename(title='Selecione o arquivo referente ao Relatório Sintético de Equipamentos',
                                                filetypes=[("Excel files", "*.xlsx")])

        ps = openpyxl.load_workbook(filepath)
        sheet = ps.active

        equips = {}

        row = 1

        while sheet['A' + str(row)].value != "Código":
            row += 1

        row += 1

        while sheet['A' + str(row)].value is None:
            row += 1

        while row <= sheet.max_row:
            code = sheet['A' + str(row)].value
            data1 = sheet['B' + str(row)].value
            data2 = sheet['C' + str(row)].value
            data3 = sheet['D' + str(row)].value
            data4 = sheet['E' + str(row)].value
            data5 = sheet['F' + str(row)].value
            data6 = sheet['G' + str(row)].value
            data7 = sheet['H' + str(row)].value
            data8 = sheet['I' + str(row)].value
            data9 = sheet['J' + str(row)].value
            data10 = sheet['K' + str(row)].value
            equips[code] = (data1, data2, data3, data4, data5, data6, data7, data8, data9, data10)
            row = row + 1

        ps.close()

        self.equipments_table = equips

    def wb_labor_import(self, filepath=None):
        '''
        Imports the labors data from the *.xlsx file to a dictionary.
        '''

        if not filepath:
            root = tk.Tk()
            root.withdraw()
            filepath = filedialog.askopenfilename(title='Selecione o arquivo referente ao Relatório Sintético de Mão de Obra',
                                                filetypes=[("Excel files", "*.xlsx")])

        ps = openpyxl.load_workbook(filepath)
        sheet = ps.active

        labor = {}

        row = 1

        while sheet['A' + str(row)].value != "Código":
            row += 1

        row += 1

        while sheet['A' + str(row)].value is None:
            row += 1

        while row <= sheet.max_row:
            code = sheet['A' + str(row)].value
            data1 = sheet['B' + str(row)].value
            data2 = sheet['C' + str(row)].value
            data3 = sheet['D' + str(row)].value
            data4 = sheet['E' + str(row)].value
            data5 = sheet['F' + str(row)].value
            data6 = sheet['G' + str(row)].value
            labor[code] = (data1, data2, data3, data4, data5, data6)
            row += 1

        ps.close()

        self.labor_table = labor

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
    tables.json_import()
    comp_code = '0308265'
    state = 'PR'
    date = '01/2021'
    print('Equip: R$', tables.comps[comp_code].equips_sum(tables))
    print('Labor: R$', tables.comps[comp_code].labor_sum(tables))
    print('Material: R$', tables.comps[comp_code].materials_sum(state, date, tables))
    print('Auxiliary activities: R$', tables.comps[comp_code].aux_activity_sum(state, date, tables))
    print('Fixed Time: R$', tables.comps[comp_code].fixed_time_sum(state, date, tables))
    print('Transportation: R$', tables.comps[comp_code].transport_sum(state, date, tables))

    print('Total: R$', round(tables.comps[comp_code].comp_sum(state, date, tables), 4))

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
