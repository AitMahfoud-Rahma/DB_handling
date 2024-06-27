# Description

- The script [packages.py](packages.py) install all required packages.
- The script [check_data_form.py](check_data_form.py) checks the existence of the Jotform data in the Cani-DNA database, verifying the existence of dogs, owners, vets and kennels (affixes), and also compares affixes to detect similarities. The script generates a log file detailing the results of the check.

# Usage
Make sure you have Python 3 installed on your machine. If not, follow these instructions : 

  - Install conda or miniconda : https://docs.anaconda.com/free/miniconda/miniconda-install/
  - ```conda create -n python3 python=3.10```
  - ```conda activate python3```


# To run
Prepare your files:
  - An Excel file containing the database from Cani-DNA (path_db).
  - An Excel file from the Form (path_jotform).

Run the scripts respectively:

First Script to install all required packages.
Once you've installed the packages, you don't have to re-run it every time. Only for the first time :

```bash
python3 /path/to/packages.py 
```
And for the verification you have to run:

```bash
python3 ckeck_data_form.py path/to/db_file.xls path/to/jotform_file.xlsx
```
# Output 
An output [verification.log](verification.log) file will be created, containing all relevant information 