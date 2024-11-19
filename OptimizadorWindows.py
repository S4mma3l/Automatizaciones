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

# Lista de aplicaciones y servicios críticos que no deben desactivarse
APLICACIONES_ESENCIALES = [
    "OptimizadorWindows",  # El optimizador no debe desactivarse
    "OneDrive",  # Sincronización en la nube (opcional según configuración del usuario)
    "SecurityHealth",  # Seguridad de Windows
    "Windows Defender",  # Antivirus predeterminado
    "AudioEndpointBuilder",  # Sonido
    "DisplaySwitch",  # Pantallas múltiples
    "ctfmon",  # Gestión de idioma y teclado
]

SERVICIOS_ESENCIALES = [
    "WinDefend",  # Antivirus de Windows
    "wuauserv",  # Actualizaciones automáticas de Windows
    "BITS",  # Servicio de transferencia inteligente en segundo plano
    "AudioSrv",  # Servicio de audio de Windows
    "Spooler",  # Impresión
    "EventLog",  # Registro de eventos del sistema
]

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

# Verificar si un elemento es esencial
def es_aplicacion_esencial(nombre):
    for app in APLICACIONES_ESENCIALES:
        if app.lower() in nombre.lower():
            return True
    return False

def es_servicio_esencial(nombre):
    for servicio in SERVICIOS_ESENCIALES:
        if servicio.lower() in nombre.lower():
            return True
    return False

# Desactivar aplicaciones de inicio innecesarias
def desactivar_aplicaciones_inicio():
    resultados = []

    claves_registro = [
        (reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (reg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
    ]

    for hive, subclave in claves_registro:
        try:
            clave = reg.OpenKey(hive, subclave, 0, reg.KEY_ALL_ACCESS)
            num_valores = reg.QueryInfoKey(clave)[1]
            for i in range(num_valores):
                nombre, _, _ = reg.EnumValue(clave, 0)
                if not es_aplicacion_esencial(nombre):
                    reg.DeleteValue(clave, nombre)
                    resultados.append(f"Desactivada aplicación de inicio: {nombre}")
                else:
                    resultados.append(f"Aplicación esencial preservada: {nombre}")
            reg.CloseKey(clave)
        except Exception as e:
            resultados.append(f"Error al procesar clave del registro: {subclave} - {e}")

    carpeta_inicio = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    try:
        for archivo in os.listdir(carpeta_inicio):
            archivo_path = os.path.join(carpeta_inicio, archivo)
            if not es_aplicacion_esencial(archivo):
                os.remove(archivo_path)
                resultados.append(f"Eliminado acceso directo: {archivo}")
            else:
                resultados.append(f"Acceso directo esencial preservado: {archivo}")
    except Exception as e:
        resultados.append(f"Error al limpiar accesos directos: {e}")

    return resultados

# Detener servicios innecesarios
def detener_servicios():
    servicios = ["DiagTrack", "SysMain", "WSearch", "CDPUserSvc"]
    resultados = []
    for servicio in servicios:
        if es_servicio_esencial(servicio):
            resultados.append(f"Servicio esencial preservado: {servicio}")
            continue
        try:
            subprocess.run(["sc", "stop", servicio], check=True, capture_output=True)
            subprocess.run(["sc", "config", servicio, "start=disabled"], check=True, capture_output=True)
            resultados.append(f"Servicio '{servicio}' detenido y deshabilitado.")
        except subprocess.CalledProcessError:
            resultados.append(f"No se pudo detener/deshabilitar el servicio '{servicio}'.")
    return resultados

# Ajustar el plan de energía a alto rendimiento
def ajustar_plan_energia():
    try:
        subprocess.run(["powercfg", "-setactive", "SCHEME_MIN"], check=True)
        return "Plan de energía cambiado a Alto Rendimiento."
    except subprocess.CalledProcessError as e:
        return f"Error al cambiar el plan de energía: {e}"

# Mostrar la ventana gráfica con los resultados
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

# Función principal
def optimizar_sistema():
    if not verificar_administrador():
        messagebox.showerror("Error", "El programa debe ejecutarse como administrador.")
        return
    
    agregar_a_inicio()
    resultados = []
    resultados.extend(limpiar_archivos())
    resultados.extend(desactivar_aplicaciones_inicio())
    resultados.extend(detener_servicios())
    resultados.append(ajustar_plan_energia())
    
    resumen = "\n".join(resultados)
    logging.info(resumen)
    mostrar_ventana(resumen)

# Ejecutar el programa
if __name__ == "__main__":
    optimizar_sistema()