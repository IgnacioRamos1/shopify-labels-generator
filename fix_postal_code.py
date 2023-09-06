import pandas as pd
import os

base_path = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(base_path, 'Codigos-Postales-Argentina.xlsx')
postal_data = pd.read_excel(excel_path)

province_code = {
    "A": "Salta",
    "B": "Buenos Aires",
    "C": "Capital Federal",
    "D": "San Luis",
    "E": "Entre Rios",
    "F": "La Rioja",
    "G": "Santiago Del Estero",
    "H": "Chaco",
    "J": "San Juan",
    "K": "Catamarca",
    "L": "La Pampa",
    "M": "Mendoza",
    "N": "Misiones",
    "P": "Formosa",
    "Q": "Neuquen",
    "R": "Rio Negro",
    "S": "Santa Fe",
    "T": "Tucuman",
    "U": "Chubut",
    "V": "Tierra Del Fuego",
    "W": "Corrientes",
    "X": "Cordoba",
    "Y": "Jujuy",
    "Z": "Santa Cruz"
}


def correct_province_by_postal_code(province, postal_code):
    try:
        # Convert the postal_code to integer
        postal_code_int = int(postal_code)

        # Convert the province code to province name
        province_name = province_code.get(province, "")

        # Filter the postal data by the given postal code
        filtered_data = postal_data[postal_data['CP'] == postal_code_int]

        # If there's no match in the data, return the original province
        if len(filtered_data) == 0:
            return province

        # If there's a discrepancy between the given province and the data, correct the province
        if province_name not in filtered_data['Provincia'].values:
            correct_province = filtered_data['Provincia'].values[0]
            # Convert the corrected province name back to province code
            correct_province_code = [code for code, name in province_code.items() if name == correct_province][0]
            return correct_province_code
        return province

    except Exception as e:
        raise Exception(f"Error in correct_province_by_postal_code function: {e}")
