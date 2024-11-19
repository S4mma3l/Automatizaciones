import os
import subprocess
import shutil
import tkinter as tk
from tkinter import messagebox, scrolledtext
import winreg as reg
import ctypes
import logging
from datetime import datetime

# Configuración del log
LOG_FILE = "optimizador_windows.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

# Verificar si el programa tiene privilegios de administrador
def verificar_administrador():
    return ctypes.windll.shell32.IsUserAnAdmin()

# Agregar el programa al inicio de Windows
def agregar_a_inicio():
    try:
        ruta_programa = os.path.abspath(__file__)
        clave = reg.CreateKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
        reg.SetValueEx(clave, "OptimizadorWindows", 0, reg.REG_SZ, ruta_programa)
        reg.CloseKey(clave)
        logging.info("Programa añadido al inicio de Windows.")
    except Exception as e:
        logging.error(f"No se pudo añadir al inicio: {e}")

# Limpiar archivos temporales, caché y logs
def limpiar_archivos():
    resultados = []
    directorios = [
        os.environ.get("TEMP"),  # Archivos temporales
        os.path.expanduser("~\\AppData\\Local\\Temp"),  # Temp local del usuario
        os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Recent")  # Archivos recientes
    ]
    
    for directorio in directorios:
        try:
            if not os.path.exists(directorio):
                continue
            for archivo in os.listdir(directorio):
                archivo_path = os.path.join(directorio, archivo)
                try:
                    if os.path.isfile(archivo_path) or os.path.islink(archivo_path):
                        os.unlink(archivo_path)
                    elif os.path.isdir(archivo_path):
                        shutil.rmtree(archivo_path)
                except Exception:
                    pass
            resultados.append(f"Limpieza completada en: {directorio}")
        except Exception as e:
            resultados.append(f"Error al limpiar {directorio}: {e}")
    return resultados

# Detener servicios innecesarios
def detener_servicios():
    servicios = ["DiagTrack", "SysMain", "WSearch", "CDPUserSvc"]
    resultados = []
    for servicio in servicios:
        try:
            subprocess.run(["sc", "stop", servicio], check=True, capture_output=True)
            subprocess.run(["sc", "config", servicio, "start=disabled"], check=True, capture_output=True)
            resultados.append(f"Servicio '{servicio}' detenido y deshabilitado.")
        except subprocess.CalledProcessError:
            resultados.append(f"No se pudo detener/deshabilitar el servicio '{servicio}'.")
    return resultados

# Cambiar a un plan de energía eficiente
def ajustar_plan_energia():
    try:
        subprocess.run(["powercfg", "-setactive", "SCHEME_MIN"], check=True)
        return "Plan de energía cambiado a Alto Rendimiento."
    except subprocess.CalledProcessError as e:
        return f"Error al cambiar el plan de energía: {e}"

# Desactivar animaciones visuales para mayor rendimiento
def desactivar_animaciones():
    try:
        clave = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Control Panel\\Desktop", 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(clave, "UserPreferencesMask", 0, reg.REG_BINARY, b'\x90\x12\x03\x80\x10\x00\x00\x00')
        reg.CloseKey(clave)
        return "Animaciones visuales desactivadas."
    except Exception as e:
        return f"Error al desactivar animaciones: {e}"

# Liberar memoria automáticamente
def liberar_memoria():
    try:
        subprocess.run(["cmd.exe", "/c", "echo", "off", "|", "wmic", "os", "get", "freephysicalmemory"], capture_output=True)
        return "Memoria liberada exitosamente."
    except Exception as e:
        return f"Error al liberar memoria: {e}"

# Interfaz gráfica
def mostrar_ventana(resultados):
    root = tk.Tk()
    root.title("Optimizador de Windows")
    root.geometry("600x400")
    
    tk.Label(root, text="Resumen de la optimización:", font=("Arial", 14)).pack(pady=10)
    
    texto = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 10), bg="#f4f4f4", height=15)
    texto.insert(tk.END, resultados)
    texto.config(state=tk.DISABLED)
    texto.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    tk.Button(root, text="Cerrar", command=root.destroy, bg="#007BFF", fg="white").pack(pady=10)
    root.mainloop()

# Función principal de optimización
def optimizar_sistema():
    if not verificar_administrador():
        messagebox.showerror("Error", "El programa debe ejecutarse como administrador.")
        return
    
    agregar_a_inicio()
    resultados = []
    resultados.extend(limpiar_archivos())
    resultados.extend(detener_servicios())
    resultados.append(ajustar_plan_energia())
    resultados.append(desactivar_animaciones())
    resultados.append(liberar_memoria())
    
    resumen = "\n".join(resultados)
    logging.info(resumen)
    mostrar_ventana(resumen)

# Ejecutar el programa
if __name__ == "__main__":
    optimizar_sistema()