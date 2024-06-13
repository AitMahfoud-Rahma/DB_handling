# Description
The script [check2.py](check2.py) checks the existence of the Jotform data in the Cani-DNA database, verifying the existence of dogs, owners, vets and kennels (affixes), and also compares affixes to detect similarities. The script generates a log file detailing the results of the check.

# Required packages
  - fuzzywuzzy
  - unidecode
  - pandas
  - Levenshtein
  - gspread
  - oauth2client
  - pyarrow
# Usage
Make sure you have Python 3 installed on your machine. If not, follow these instructions : 

  - Install conda or miniconda : https://docs.anaconda.com/free/miniconda/miniconda-install/
  - ```conda create -n python3 python=3.10```
  - ```conda activate python3```
# Installation
The script install the required packages. There are no additional packages to install manually.
# To run
Prepare your files:
  - An Excel file containing the database from Cani-DNA (path_db).
  - An Excel file from the Form (path_jotform).

Run the script:
```bash
python ckeck2.py path/to/db_file path/to/jotform_file
```

