#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import importlib.util

def install_and_import(package):
    try:
        if importlib.util.find_spec(package) is None:
            subprocess.run(["pip", "install", package], check=True)
            print(f"{package} a été installé avec succès.")
        else:
            print(f"{package} est déjà installé.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'installation de {package} : {str(e)}")

# Liste des packages nécessaires
required_packages = ["fuzzywuzzy", "unidecode", "pandas", "Levenshtein", "gspread", "oauth2client", "pyarrow"]

for package in required_packages:
    install_and_import(package)

import pandas as pd
import argparse
from unidecode import unidecode
import gspread
import logging
import datetime
from difflib import SequenceMatcher

def check_dog_existence(file_jotform, file_db, logger):
    for i, nom_usuel_jotform in enumerate(file_jotform['Nom Usuel (animal)']):
        puce_jotform = file_jotform['Puce'][i]
        chien_trouve = False
        for j, nom_usuel_db in enumerate(file_db['Nom usuel']):
            puce_db = file_db['Puce'][j]
            if (nom_usuel_db == nom_usuel_jotform) and (puce_db == puce_jotform):
                chien_trouve = True
                break
        if chien_trouve:
            logger.info(f"Le chien ({nom_usuel_jotform}) existe dans la base de données.")
        else:
            logger.warning(f"Le chien ({nom_usuel_jotform}) n'existe pas dans la base de données.")

def check_existence_and_similarity(field_name, file_jotform, db_data, log_messages, logger, category, i):
    db_nom_column = db_data[f'{category} - Nom'].apply(lambda x: unidecode(str(x)) if pd.notna(x) else x).str.lower()
    db_prenom_column = db_data[f'{category} - Prénom'].apply(lambda x: unidecode(str(x)) if pd.notna(x) else x).str.lower()
    jotform_nom = file_jotform[f'Nom ({category.lower()})'][i]
    jotform_prenom = file_jotform[f'Prénom ({category.lower()})'][i]
    jotform_value_name = unidecode(jotform_nom).lower()
    jotform_value_surname = unidecode(jotform_prenom).lower()
    exists = (jotform_value_name == db_nom_column) & (jotform_value_surname == db_prenom_column)
    if exists.any():
        message = f"{field_name} ({jotform_nom} {jotform_prenom}) existe déjà dans la base de données."
        logger.info(message)
        log_messages.append(message)
    else:
        reverse_check = ((db_nom_column == jotform_value_surname) & (db_prenom_column == jotform_value_name)) | \
                        ((db_nom_column == jotform_value_name) & (db_prenom_column == jotform_value_surname))
        if reverse_check.any():
            message_reverse = f"Le {field_name} ({jotform_nom} {jotform_prenom}) semble avoir le nom/prénom inversés dans la base de données."
            log_messages.append(message_reverse)
            logger.warning(message_reverse)
        else:
            message = f"{field_name} ({jotform_nom} {jotform_prenom}) n'existe pas dans la base de données."
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
        message = ""
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
            if nombre_chiffres_puce < 15:
                nom_usuel_correspondant = file_jotform['Nom Usuel (animal)'][i]
                message = f"La puce {puce_jotform} de {nom_usuel_correspondant} a {nombre_chiffres_puce} caractères. Numéro de ligne dans file_jotform : {i + 1}.\n"
                log_messages.append(message)
                logger.warning(message)

            check_existence_and_similarity(
                "Le vétérinaire",
                file_jotform,
                file_db,
                log_messages,
                logger,
                category="Vétérinaire",
                i=i
            )
            check_existence_and_similarity(
                "Le propriétaire",
                file_jotform,
                file_db,
                log_messages,
                logger,
                category="Propriétaire",
                i=i
            )
        
        log_messages.append(message)
        logger.info(message)
    
    check_dog_existence(file_jotform, file_db, logger)
    return log_messages

def generate_log_file():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_name = f"verification_log_{current_time}.log"
    return log_file_name

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script de vérification")
    parser.add_argument("path_db", type=str, help="Chemin vers le fichier de base de données")
    parser.add_argument("path_jotform", type=str, help="Chemin vers le fichier JotForm")
    args = parser.parse_args()

    # Installation des packages
    install_and_import("pyarrow")

    path_db = args.path_db
    path_jotform = args.path_jotform
    file_db = pd.read_excel(path_db, header=0)
    file_jotform = pd.read_excel(path_jotform, sheet_name=0, header=0)

    log_messages = main_verification(file_jotform, file_db, generate_log_file())

    with open('output_file.log', 'w') as log_file:
        for message in log_messages:
            log_file.write(message + '\n')

    print(f"Le fichier de log a été généré avec succès.")
