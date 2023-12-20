import os
import csv
import xml.etree.ElementTree as ET
import pickle
import random

# Load the cross-language dictionary from the pickle file
with open('resultPelis.pkl', 'rb') as file:
    cross_language_dict = pickle.load(file)

# Define the paths
xml_es_folder = './datasets/OpenSubtitles/OpenSubtitles_latest_raw_es/OpenSubtitles/raw/'
xml_en_folder = './datasets/OpenSubtitles/OpenSubtitles_latest_raw_en/OpenSubtitles/raw/'
csv_file_path = 'OpenSubtitlesDataset.csv'

# Función para extraer el texto más largo ya que a veces hay texto en el elemento y a veces en el tail
def extract_longest_text(element):
    longest_text = ""
    if element.text and len(element.text.strip()) > len(longest_text):
        longest_text = element.text.strip()
    for child in element:
        if child.tail and len(child.tail.strip()) > len(longest_text):
            longest_text = child.tail.strip()
    return longest_text

# Create the CSV file
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file, delimiter='~')
    writer.writerow(['From Document', 'To Document', 'EN Section', 'SP Section'])

    for entry in cross_language_dict:
        from_doc = os.path.splitext(entry['fromDoc'])[0]
        to_doc = os.path.splitext(entry['toDoc'])[0]

        xml_en_file_path = os.path.join(xml_en_folder, from_doc)
        xml_sp_file_path = os.path.join(xml_es_folder, to_doc)

        try:
            tree_en = ET.parse(xml_en_file_path)
            root_en = tree_en.getroot()
        except:
            print(f"Error: {xml_en_file_path} not found")
            continue

        try:
            tree_sp = ET.parse(xml_sp_file_path)
            root_sp = tree_sp.getroot()
        except:
            print(f"Error: {xml_sp_file_path} not found")
            continue

        sections = entry['sections']

        en_anterior = 0
        sp_anterior = 0
        while sections:
            advance_steps = min(random.randint(1, 8), len(sections))

            for _ in range(advance_steps):
                if sections:
                    section = sections.pop(0)

            en_to_section = section['EN'] if sections else float('inf')
            sp_to_section = section['SP'] if sections else float('inf')

            en_text = ""
            for elem in root_en.iter('s'):
                if int(float(elem.attrib['id'])) >= en_anterior and int(float(elem.attrib['id'])) < en_to_section:
                    en_text += extract_longest_text(elem) + " "

            sp_text = ""
            for elem in root_sp.iter('s'):
                if int(float(elem.attrib['id'])) >= sp_anterior and int(float(elem.attrib['id'])) < sp_to_section:
                    sp_text += extract_longest_text(elem) + " "

            # si la longitud del texto es menor que 2000 caracteres no lo añadimos (eliminamos textos muy largos fruto de la concatenación de varios textos que no se han podido alinear bien)
            if len(en_text) < 2000 and len(sp_text) < 2000:
                writer.writerow([from_doc, to_doc, en_text.strip(), sp_text.strip()])
            en_anterior = en_to_section
            sp_anterior = sp_to_section

print(f"CSV file created: {csv_file_path}")
