import openpyxl
import numpy as np
import tkinter as tk
from tkinter import filedialog

# This module is destined to import the data of analytical compositions report from the *.xlsx sicro file to a *.npy
# file to be used in the sicro.py module. This *.npy file contains all the information necessary to calculate any
# composition of SICRO.

def sicro_xlsximport():

    # Selection and load of the *.xlsx analytical compositions report
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(
        title='Selecione o arquivo referente ao Relatório Analítico de Composições de Custos',
        filetypes=[("Excel files", "*.xlsx")])
    print("Loading Workbook")
    ps = openpyxl.load_workbook(filepath)
    sheet = ps.active
    comps = {}

    # Mapping all the first rows of the compositions in the Excel file
    TargetRows = []
    for row in sheet.iter_rows(min_row=sheet.min_row, max_row=sheet.max_row, max_col=1):
        for cell in row:
            if cell.value == "CGCIT":
                TargetRows.append(cell.row)
    
    # Search of the necessary data in the Excel file and storing in a dictionary
    for row in TargetRows:
        if sheet['A' + str(row)].value == "CGCIT":
            # Find and store the FIC (Rain Influence Factor)
            if sheet['G' + str(row)].value == "FIC":
                fic = sheet['H' + str(row)].value
            else:
                fic = 0
            row = row + 3

            # Find and store the composition data: number and name
            comp_number = sheet['A' + str(row)].value
            comp_name = sheet['B' + str(row)].value

            # Find and store the composition productivity data
            prod = sheet['H' + str(row - 1)].value
            prod_unit = sheet['I' + str(row - 1)].value
            prod_list = (prod, prod_unit)

            # Find and store the data relating to the composition equipments
            equipment = []
            row = row + 3
            while sheet['A' + str(row)].value is not None:
                equipment_code = sheet['A' + str(row)].value
                equipment_qtt = sheet['C' + str(row)].value
                equip_prod_time = sheet['D' + str(row)].value
                equip_improd_time = sheet['E' + str(row)].value
                equipment.append((equipment_code, equipment_qtt, equip_prod_time, equip_improd_time))
                row = row + 1
            row = row + 2

            # Find and store in a list the data relating to the composition labor
            labor = []
            while sheet['A' + str(row)].value is not None:
                labor_code = sheet['A' + str(row)].value
                labor_qtt = sheet['C' + str(row)].value
                labor.append((labor_code, labor_qtt))
                row = row + 1
            row = row + 6

            # Find and store in a list the data relating to the composition materials
            material = []
            while sheet['A' + str(row)].value is not None:
                material_code = sheet['A' + str(row)].value
                material_qtt = sheet['C' + str(row)].value
                material.append((material_code, material_qtt))
                row = row + 1
            row = row + 2

            # Find and store in a list the data relating to the composition auxiliary activities
            aux_activity = []
            while sheet['A' + str(row)].value is not None:
                aux_activity_code = sheet['A' + str(row)].value
                aux_activity_qtt = sheet['C' + str(row)].value
                aux_activity.append((aux_activity_code, aux_activity_qtt))
                row = row + 1
            row = row + 3

            # Find and store the composition fixed time data
            fixedtime = []
            while sheet['A' + str(row)].value is not None:
                fixedtime_code = sheet['A' + str(row)].value
                fixedtime_materialcode = sheet['C' + str(row)].value
                fixedtime_qtt = sheet['D' + str(row)].value
                fixedtime.append((fixedtime_code, fixedtime_materialcode, fixedtime_qtt))
                row = row + 1
            row = row + 3

            # Find and store the composition transport data
            transport = []
            while sheet['A' + str(row)].value is not None:
                transport_code = sheet['A' + str(row)].value
                transport_qtt = sheet['C' + str(row)].value
                transport_dirtroad = sheet['E' + str(row)].value
                transport_stoneroad = sheet['F' + str(row)].value
                transport_asphalt = sheet['G' + str(row)].value
                transport.append((transport_code, transport_qtt, transport_dirtroad,
                                            transport_stoneroad, transport_asphalt))
                row = row + 1
            # Add all the data in a dictionary, where the key is the composition number
            comps[comp_number] = (
                comp_name, prod_list, equipment, labor, material, aux_activity, fixedtime, transport, fic)

            print(row, " ", row * 100 / sheet.max_row, "%")

    ps.close()
    np.save('comps.npy', comps)
    print("Done!")

sicro_xlsximport()
