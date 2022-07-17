import tkinter as tk
from tkinter import filedialog
import numpy as np
import openpyxl


class Composition:
    # Creates the composition class, where the data, imported by the sicro_xlsx_import module, is stored.
    def __init__(self, name, productivity, equipment, labor, material, auxactivity, fixedtime, transport, fic):
        self.name = name
        self.prod = productivity
        self.equipment = equipment
        self.labor = labor
        self.material = material
        self.auxactivity = auxactivity
        self.fixedtime = fixedtime
        self.transport = transport
        self.fic = int(fic)


def comp_sum(comp_code):
    # Do the sum of all the costs inherent to a composition: equipments, labor, materials, auxiliary activities, fixed
    # time and transportation
    fic_value = comps[comp_code].fic
    unit_cost = (equips_sum(comp_code) + labor_sum(comp_code)) / comps[comp_code].prod[0]
    sum = round(
        unit_cost + unit_cost * fic_value + materials_sum(comp_code) + auxactivity_sum(comp_code) + fixedtime_sum(
            comp_code), 2)  # + SomaTransporte(CompCode)
    # TODO: Find where to put the transport_sum

    return sum


def wb_equip_import():
    # Imports the equipments data from the *.xlsx file to a dictionary
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title='Selecione o arquivo referente ao Relatório Sintético de Equipamentos',
                                          filetypes=[("Excel files", "*.xlsx")])

    ps = openpyxl.load_workbook(filepath)
    sheet = ps.active

    equips = {}

    row = 1

    while sheet['A' + str(row)].value != "Código":
        row = row + 1

    row = row + 1

    while sheet['A' + str(row)].value is None:
        row = row + 1

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

    return equips


def wb_labor_import():
    # Imports the labors data from the *.xlsx file to a dictionary
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title='Selecione o arquivo referente ao Relatório Sintético de Mão de Obra',
                                          filetypes=[("Excel files", "*.xlsx")])

    ps = openpyxl.load_workbook(filepath)
    sheet = ps.active

    labor = {}

    row = 1

    while sheet['A' + str(row)].value != "Código":
        row = row + 1

    row = row + 1

    while sheet['A' + str(row)].value is None:
        row = row + 1

    while row <= sheet.max_row:
        code = sheet['A' + str(row)].value
        data1 = sheet['B' + str(row)].value
        data2 = sheet['C' + str(row)].value
        data3 = sheet['D' + str(row)].value
        data4 = sheet['E' + str(row)].value
        data5 = sheet['F' + str(row)].value
        data6 = sheet['G' + str(row)].value
        labor[code] = (data1, data2, data3, data4, data5, data6)
        row = row + 1

    ps.close()
    return labor


def wb_material_import():
    # Imports the materials data from the *.xlsx file to a dictionary
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title='Selecione o arquivo referente ao Relatório Sintético de Materiais',
                                          filetypes=[("Excel files", "*.xlsx")])

    ps = openpyxl.load_workbook(filepath)
    sheet = ps.active

    materials = {}

    row = 1

    while sheet['A' + str(row)].value != "Código":
        row = row + 1

    row = row + 1

    while sheet['A' + str(row)].value is None:
        row = row + 1

    while row <= sheet.max_row:
        code = sheet['A' + str(row)].value
        data1 = sheet['B' + str(row)].value
        data2 = sheet['C' + str(row)].value
        if sheet['D' + str(row)].value == '-':
            data3 = 0
        else:
            data3 = sheet['D' + str(row)].value
        materials[code] = (data1, data2, data3)
        row = row + 1

    ps.close()

    return materials


def wb_prices_import():
    # Imports the compositions price data from the *.xlsx file to a dictionary
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title='Selecione o arquivo referente ao Relatório Sintético de Composições',
                                          filetypes=[("Excel files", "*.xlsx")])

    ps = openpyxl.load_workbook(filepath)
    sheet = ps.active

    price = {}

    row = 1

    while sheet['A' + str(row)].value != "Código":
        row = row + 1

    row = row + 1

    while sheet['A' + str(row)].value is None:
        row = row + 1

    while row <= sheet.max_row:
        code = sheet['A' + str(row)].value
        data3 = sheet['D' + str(row)].value
        price[code] = data3
        row = row + 1

    ps.close()
    return price


def equips_sum(comp_code):
    # Returns the sum of all the costs inherent to equipments in a composition
    equip_sum = 0

    comp_equips = comps[comp_code].equipment
    if len(comp_equips) != 0:
        for each in comp_equips:
            equip_code = each[0]
            equip_qtt = each[1]
            equip_prod = each[2]
            equip_unprod = each[3]
            equip_sum = equip_sum + round(
                equip_qtt * (equip_prod * equipments_table[equip_code][8] + equip_unprod * equipments_table[equip_code][
                    9]), 4)

    return round(equip_sum, 4)


def labor_sum(comp_code):
    # Returns the sum of all the costs inherent to labors in a composition
    labor_sum = 0
    comp_labor = comps[comp_code].labor
    if len(comp_labor) != 0:
        for each in comp_labor:
            labor_code = each[0]
            labor_qtt = each[1]
            labor_sum = labor_sum + round(labor_qtt * labor_table[labor_code][4], 4)

    return round(labor_sum, 4)


def materials_sum(comp_code):
    # Returns the sum of all the costs inherent to materials in a composition
    material_sum = 0
    materials = comps[comp_code].material
    if len(materials) != 0:
        for each in materials:
            material_code = each[0]
            material_qtt = each[1]
            material_sum = material_sum + round(material_qtt * materials_table[material_code][2], 4)

    return round(material_sum, 4)


def auxactivity_sum(comp_code):
    # Returns the sum of all auxiliary activities costs of a composition
    auxactivity_sum = 0
    auxactivity = comps[comp_code].auxactivity
    if len(auxactivity) != 0:
        for each in auxactivity:
            auxactivity_code = each[0]
            auxactivity_qtt = each[1]
            auxactivity_sum = auxactivity_sum + round(auxactivity_qtt * comp_sum(auxactivity_code), 4)

    return round(auxactivity_sum, 4)


def fixedtime_sum(comp_code):
    # Returns the sum of all costs inherent to fixed time of a composition
    fixedtime_sum = 0
    fixedtime = comps[comp_code].fixedtime
    if len(fixedtime) != 0:
        for each in fixedtime:
            fixedtime_code = each[1]
            fixedtime_qtt = each[2]
            fixedtime_sum = fixedtime_sum + round(fixedtime_qtt * comp_sum(fixedtime_code), 4)

    return round(fixedtime_sum, 4)


def transport_sum(comp_code):
    # Returns the sum of all transportation costs of a composition
    transport_sum = 0
    transport = comps[comp_code].transport
    if len(transport) != 0:
        for each in transport:
            transport_code = each[4]
            transport_qtt = each[1]
            transport_sum = transport_sum + round(transport_qtt * comp_sum(transport_code), 4)

    return round(transport_sum, 4)


comps = dict()
# TODO: Implement a list, that informs if a workbook was imported or not, than, put the tables imports inside the
#  functions that use it, but first, verify if the workbook is already loaded

equipments_table = wb_equip_import()
labor_table = wb_labor_import()
materials_table = wb_material_import()
price_table = wb_prices_import()

# TODO: Do the npy import inside a function
list_import = np.load("comps.npy", allow_pickle=True)
dict_import = list_import[()]
for key in dict_import:
    comps[key] = Composition(dict_import[key][0], dict_import[key][1], dict_import[key][2], dict_import[key][3],
                             dict_import[key][4], dict_import[key][5],
                             dict_import[key][6], dict_import[key][7], dict_import[key][8])

CompCode = '0308265'
print('Equip', equips_sum(CompCode))
print('Mão de obra', labor_sum(CompCode))
print('Material', materials_sum(CompCode))
print('Atividades Auxiliares', auxactivity_sum(CompCode))
print('Tempo Fixo', fixedtime_sum(CompCode))
print('Momento de Transporte', transport_sum(CompCode))

print(round(comp_sum(CompCode), 4))

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
