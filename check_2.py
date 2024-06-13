#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import pandas as pd
from unidecode import unidecode
#from fuzzywuzzy import fuzz
import gspread
#from oauth2client.service_account import ServiceAccountCredentials
import logging
import datetime
from difflib import SequenceMatcher

def install_packages():
    try:
        import subprocess
        subprocess.run(["pip", "install", "fuzzywuzzy", "unidecode", "pandas", "Levenshtein", "logging", "gspread", "oauth2client"], check=True)
        print("Les packages ont été installés avec succès.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'installation des packages : {str(e)}")

def check_dog_existence(file_jotform, file_db, log_messages, logger):
    for i, nom_usuel_jotform in enumerate(file_jotform['Nom Usuel (animal)']):
        # Récupérer les informations du chien dans le formulaire JotForm
        #date_naissance_jotform = file_jotform['Date de naissance'][i]
        puce_jotform = file_jotform['Puce'][i]
        tato_jotform = file_jotform['Tatouage'][i]
        # Flag pour vérifier si le chien a été trouvé dans la base de données
        chien_trouve = False

        for j, nom_usuel_db in enumerate(file_db['Nom usuel']):
            # Récupérer les informations du chien dans la base de données
            #date_naissance_db = file_db['Date de naissance'][j]
            puce_db = file_db['Puce'][j]
            tato_db = file_db['Tatouage'][j]
            # Vérifier si le chien existe dans la base de données
            if (nom_usuel_db == nom_usuel_jotform) and \
               (puce_db == puce_jotform) or (tato_db == tato_jotform):
                chien_trouve = True
                break

         if chien_trouve:
            message = "Le chien ({}) existe dans la base de données.".format(nom_usuel_jotform)
            logger.info(message)
        else:
            message = "Le chien ({}) n'existe pas dans la base de données.".format(nom_usuel_jotform)
            logger.warning(message)


def check_existence_and_similarity(field_name, jotform_value, db_data, log_messages, logger, category, i):
    # Extracting relevant columns based on category
    db_nom_column = db_data[f'{category} - Nom'].apply(lambda x: unidecode(str(x)) if pd.notna(x) else x).str.lower()
    db_prenom_column = db_data[f'{category} - Prénom'].apply(lambda x: unidecode(str(x)) if pd.notna(x) else x).str.lower()

    # Jotform modification
    jotform_nom = file_jotform[f'Nom ({category.lower()})'][i]  
    jotform_prenom = file_jotform[f'Prénom ({category.lower()})'][i]  
    #jotform_value_mod = unidecode(f"{jotform_nom} {jotform_prenom}").lower()
    

    # Separate the name and surname for log messages
    jotform_value_name = unidecode(jotform_nom).lower()
    jotform_value_surname = unidecode(jotform_prenom).lower()

    # Check existence
    exists = (jotform_value_name == db_nom_column) & (jotform_value_surname == db_prenom_column)

    if exists.any():
        message = "{} ({}) existe déjà dans la base de données.".format(field_name, jotform_value)
        logger.info(message)
        log_messages.append(message)
    else:
        reverse_check = ((db_nom_column == jotform_value_surname) & (db_prenom_column == jotform_value_name)) | \
                        ((db_nom_column == jotform_value_name) & (db_prenom_column == jotform_value_surname))

        if reverse_check.any():
            message_reverse = "Le {} ({}) semble avoir le nom/prénom inversés dans la base de données.".format(field_name, jotform_value)
            log_messages.append(message_reverse)
            logger.warning(message_reverse)
        else:
            message = "{} ({}) n'existe pas dans la base de données.".format(field_name, jotform_value)
            logger.warning(message)
            log_messages.append(message)
            
def main_verification(file_jotform, file_db, log_path):
    log_messages = []

    logger = logging.getLogger('VerificationLogger')
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    if 'Affixe_Original' not in file_jotform.columns:
        file_jotform['Affixe_Original'] = file_jotform['Affixe']

    affixe_without_nan = file_db['Affixe'].dropna()
    unique_values = affixe_without_nan.unique()
    unique_values_mod = affixe_without_nan.apply(lambda x: unidecode(x).replace(' ', '').lower()).unique()
    file_jotform['Affixe'] = file_jotform['Affixe'].dropna().apply(lambda x: unidecode(x).replace(' ', '').lower())

    result = file_jotform['Affixe'].isin(unique_values_mod)

    for i, affixe_jotform in enumerate(file_jotform['Affixe']):
        affixe_jotform_mod = unidecode(str(affixe_jotform)).lower().strip()
        affixe_original = file_jotform['Affixe_Original'][i]

        # Initialize message for this JotForm line
        message = ""

        if affixe_jotform_mod in unique_values_mod:
            index_base_de_donnees = unique_values_mod.tolist().index(affixe_jotform_mod)
            affixe_base_de_donnees = unique_values[index_base_de_donnees]

            message += f"L'affixe : ({affixe_original}) existe déjà dans la base de données sous le nom : ({affixe_base_de_donnees})\n"
        else:
            max_similarity = 0
            matched_affixe = None

            if affixe_jotform_mod in unique_values_mod:
                index_base_de_donnees = unique_values_mod.tolist().index(affixe_jotform_mod)
                affixe_base_de_donnees = unique_values[index_base_de_donnees]

                message += f"L'affixe : ({affixe_original}) existe déjà dans la base de données sous le nom : ({affixe_base_de_donnees})\n"
            else:
                max_similarity = 0
                matched_affixe = None

                for affixe_base_de_donnees in unique_values_mod:
                    similarity = SequenceMatcher(None, affixe_base_de_donnees, affixe_jotform_mod).ratio()
                    if similarity > max_similarity:
                        max_similarity = similarity
                        matched_affixe = affixe_base_de_donnees

                if max_similarity >= 0.60:  
                    index_base_de_donnees = unique_values_mod.tolist().index(matched_affixe)
                    affixe_base_de_donnees = unique_values[index_base_de_donnees]
                    message += f"L'affixe : ({affixe_original}) n'existe pas dans la base de données, mais peut correspondre à ({affixe_base_de_donnees}) avec une similarité de {max_similarity * 100:.2f}%.\n"
                else:
                    message += f"L'affixe : ({affixe_original}) n'existe pas dans la base de données.\n"

        puce_jotform = file_jotform['Puce'][i]
        if pd.notna(puce_jotform):
            nombre_chiffres_puce = sum(c.isdigit() for c in str(puce_jotform))
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")

            if nombre_chiffres_puce < 15:
                nom_usuel_correspondant = file_jotform['Nom Usuel (animal)'][i]
                message = f"La puce {puce_jotform} de {nom_usuel_correspondant} a {nombre_chiffres_puce} caractères. Numéro de ligne dans file_jotform : {i + 1}.\n"
                log_messages.append(log_message(timestamp, 'WARNING', message))

            check_existence_and_similarity(
                "Le vétérinaire",
                file_jotform['Nom (vétérinaire)'][i] + ' ' + file_jotform['Prénom (vétérinaire)'][i],
                file_db,
                log_messages,
                logger,
                category="Vétérinaire",
                i=i  
            )

            check_existence_and_similarity(
                "Le propriétaire",
                file_jotform['Nom (propriétaire)'][i] + ' ' + file_jotform['Prénom (propriétaire)'][i],
                file_db,
                log_messages,
                logger,
                category="Propriétaire",
                i=i
            )
        
        # Append the message for this JotForm line to the log_messages list
        log_messages.append(message)
        logger.info(message)
    
    # Vérification des chiens à la fin
    check_dog_existence(file_jotform, file_db, log_messages, logger)

    return log_messages

def generate_log_file():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S,%f")
    log_file_name = f"verification_log_{current_time}.log"
    return log_file_name
def log_message(timestamp, level, message):
    return f"{timestamp} [{level}] - {message}"
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script de vérification")
    parser.add_argument("path_db", type=str, help="Chemin vers le fichier de base de données")
    parser.add_argument("path_jotform", type=str, help="Chemin vers le fichier JotForm")
    args = parser.parse_args()

    # Check packages installation
    install_packages()

    # Charger les fichiers à partir des chemins fournis en ligne de commande
    path_db = args.path_db
    path_jotform = args.path_jotform
    file_db = pd.read_excel(path_db, header=0)
    file_jotform = pd.read_excel(path_jotform, sheet_name=0, header=0)


    # Appel de la fonction main_verification avec les fichiers d'entrée
    log_messages = main_verification(file_jotform, file_db, generate_log_file())


    with open('output_file.log', 'w') as log_file:
        for message in log_messages:
            log_file.write(message + '\n')

    print(f"Le fichier de log a été généré avec succès.")


#python3 /Users/aitmahfoud/Desktop/check2.py table-data-5.xls tato.xlsx 
