import winreg as reg
import ctypes
import logging

def crear_dword_en_registro():
    try:
        # Verificar permisos
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("Advertencia: Este programa podría requerir permisos de administrador.")
        
        # Configuración del log
        logging.basicConfig(filename="registro_modificaciones.log", level=logging.INFO)

        # Ruta del registro
        ruta = r"SOFTWARE\\Autodesk\\Inventor\\RegistryVersion28.0\\System\\Preferences"
        clave = reg.CreateKey(reg.HKEY_CURRENT_USER, ruta)

        # Solicitar entrada del usuario
        nombre_dword = input("Ingresa el nombre de tu DWORD: ").strip()
        if not nombre_dword:
            raise ValueError("El nombre del DWORD no puede estar vacío.")

        valor_dword = int(input("Ingresa el valor DWORD (0 a 4294967295): "))
        if not (0 <= valor_dword <= 4294967295):
            raise ValueError("El valor debe estar entre 0 y 4294967295.")
        
        # Verificar si el DWORD ya existe
        try:
            valor_existente = reg.QueryValueEx(clave, nombre_dword)
            print(f"El DWORD '{nombre_dword}' ya existe con el valor {valor_existente[0]}.")
            actualizar = input("¿Deseas actualizar su valor? (s/n): ").lower()
            if actualizar != 's':
                return
        except FileNotFoundError:
            pass  # Si no existe, se procederá a crearlo

        # Establecer el valor DWORD
        reg.SetValueEx(clave, nombre_dword, 0, reg.REG_DWORD, valor_dword)
        reg.CloseKey(clave)
        
        print(f"DWORD '{nombre_dword}' creado/modificado con éxito en {ruta}")
        logging.info(f"DWORD '{nombre_dword}' creado/modificado con valor {valor_dword} en {ruta}.")
    except ValueError as ve:
        print(f"Error de entrada: {ve}")
    except PermissionError:
        print("No tienes permisos suficientes para modificar el registro.")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    crear_dword_en_registro()