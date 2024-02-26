# -*- coding: utf-8 -*-
# Autor: Rahma Ait MAHFOUD
# Date: 05/02/2024
import pandas as pd
import sys

required_packages = ['pandas']

# Check packages installation
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"Le package {package} n'est pas installé. Installation en cours...")
        try:
            from pip._internal import main as pipmain
        except ImportError:
            from pip import main as pipmain
        pipmain(['install', package])

# Get jotform file from args
jotform_file = sys.argv[1]

# Read jotform file
jotform = pd.read_excel(jotform_file, header=0)

# Create a new dataframe called "file_type"
file_type = pd.DataFrame(columns=['Genre', 'Prénom', 'Nom', 'Etablissement', 'Adresse 1', 'Adresse 2',
                                  'CP', 'Ville', 'Pays', 'Projet', 'Unnamed: 10', 'nb', 'kits', 'remarques'])
# Adapt columns
file_type['Nom'] = jotform['Nom (propriétaire)']
file_type['Prénom'] = jotform['Prénom (propriétaire)']
file_type['Adresse 1'] = jotform['Numéro et rue']
file_type['Adresse 2'] = jotform['Complément d\'adresse']
file_type['CP'] = jotform['Code Postal']
file_type['Ville'] = jotform['Ville']
file_type['Pays'] = jotform['Pays']
# We can add gender but not necessary for the moment
# Save the new file
file_type_file = jotform_file.replace(".xlsx", "_output.xlsx")
file_type.to_excel(file_type_file, index=False)
