# DB_handling

[This Python script](letters_adaptor.py) has been designed to process an Excel file containing data from an online form. It creates a new Excel file with selected columns, adapted as needed. This file will be used to automate the sending of letters to dog owners and/or veterinarians.

## Prerequisites

- Python 3.12.1 : Make sure you have Python installed on your machine. You can download it from [the official Python website](https://www.python.org/).

## Running the script

The script can be run using the command line. Be sure to specify the path to the Excel data file as an argument. Here's an example:

```bash 
python3 letters_adaptor.py /Users/aitmahfoud/Downloads/FICHE_DE_RENSEIGNEMENTS-4.xlsx
```
## Output
The resulting file will be saved with a name similar to the input file, but with the suffix "_output.xlsx" added. For example, if the input file is "jotform.xlsx", the output file will be "jotform_output.xlsx".

### NB
This code has been developed and tested with **Python 3.12.1**. If you have any problems or have any questions, please do not hesitate to contact me at `rahmaaitmahfoud@gmail.com`.
