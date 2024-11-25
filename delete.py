import os

def eliminar_persistencia():
    if os.name == "nt":  # Windows
        comando = 'reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Diagnostico /f'
        os.system(comando)
        print("Persistencia eliminada del registro de inicio.")
    else:
        print("Este script solo es aplicable en sistemas Windows.")

if __name__ == "__main__":
    eliminar_persistencia()
