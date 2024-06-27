#!/usr/bin/env python3

def install_packages():
    try:
        import subprocess
        packages = ["unidecode", "pandas", "gspread", "oauth2client"]
        for package in packages:
            subprocess.run(["pip3", "install", package], check=True)
        print("Les packages ont été installés avec succès.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'installation des packages : {str(e)}")

if __name__ == "__main__":
    install_packages()
