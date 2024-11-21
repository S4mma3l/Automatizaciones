import paramiko
import keyring
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import logging
import time

# Configuración de registro (logs)
logging.basicConfig(
    filename="conexion_remota.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# Función para conectar al equipo remoto (SSH)
def conectar_equipo_ssh(host, usuario, password, intentos=3):
    for intento in range(1, intentos + 1):
        try:
            # Crear cliente SSH
            cliente = paramiko.SSHClient()
            cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            cliente.connect(host, username=usuario, password=password, timeout=10)
            messagebox.showinfo("Conexión", f"Conexión SSH exitosa a {host}")
            logging.info(f"Conexión SSH exitosa al host {host} con usuario {usuario}.")
            cliente.close()
            return True
        except paramiko.AuthenticationException:
            logging.error(f"Error de autenticación en {host} con usuario {usuario}.")
            messagebox.showerror("Error de autenticación", "Credenciales incorrectas.")
            return False
        except paramiko.SSHException as e:
            if intento < intentos:
                time.sleep(2)
                continue
            logging.error(f"Error SSH en {host}: {str(e)}.")
            messagebox.showerror("Error SSH", f"No se pudo conectar: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Error inesperado en {host}: {str(e)}.")
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
            return False


# Función para abrir conexión RDP
def conectar_equipo_rdp(host):
    try:
        # Abrir conexión RDP usando mstsc (Windows)
        subprocess.run(["mstsc", f"/v:{host}"], check=True)
        logging.info(f"Conexión RDP iniciada al host {host}.")
    except FileNotFoundError:
        logging.error("Comando mstsc no encontrado. Verifica tu sistema.")
        messagebox.showerror("Error", "mstsc no disponible. Usa un sistema Windows.")
    except Exception as e:
        logging.error(f"Error al iniciar RDP en {host}: {str(e)}.")
        messagebox.showerror("Error", f"No se pudo abrir RDP: {str(e)}")


# Guardar credenciales de manera segura
def guardar_credenciales(host, usuario, password):
    keyring.set_password(f"conexion_remota_{host}", usuario, password)


# Recuperar credenciales de manera segura
def obtener_credenciales(host, usuario):
    return keyring.get_password(f"conexion_remota_{host}", usuario)


# Sistema de roles
def verificar_permiso_rol(rol, accion):
    permisos = {
        "Administrador": ["SSH", "RDP"],
        "Usuario": ["SSH"],  # Los usuarios regulares no tienen acceso a RDP
    }
    return accion in permisos.get(rol, [])


# Crear interfaz gráfica
def interfaz():
    ventana = tk.Tk()
    ventana.title("Conexión Remota Segura")
    ventana.geometry("500x400")
    ventana.resizable(False, False)

    # Contenedor principal
    marco = ttk.Frame(ventana, padding="20")
    marco.pack(fill=tk.BOTH, expand=True)

    # Encabezado
    ttk.Label(marco, text="Conexión Remota Segura", font=("Helvetica", 16, "bold")).pack(pady=10)

    # Sección de entrada de datos
    marco_formulario = ttk.Frame(marco)
    marco_formulario.pack(pady=10, fill=tk.X)

    ttk.Label(marco_formulario, text="Equipo").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    ttk.Label(marco_formulario, text="Usuario").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    ttk.Label(marco_formulario, text="Contraseña").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
    ttk.Label(marco_formulario, text="Rol").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
    ttk.Label(marco_formulario, text="IP Manual").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)

    equipos = {"Servidor 1": "192.168.1.10", "Servidor 2": "192.168.1.20", "Servidor 3": "192.168.1.30"}
    equipo_seleccionado = tk.StringVar()
    usuario = ttk.Entry(marco_formulario)
    password = ttk.Entry(marco_formulario, show="*")
    rol = tk.StringVar(value="Usuario")
    ip_manual = ttk.Entry(marco_formulario)

    equipo_dropdown = ttk.Combobox(
        marco_formulario, textvariable=equipo_seleccionado, values=list(equipos.keys()), state="readonly"
    )
    equipo_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
    usuario.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
    password.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
    rol_dropdown = ttk.Combobox(marco_formulario, textvariable=rol, values=["Administrador", "Usuario"], state="readonly")
    rol_dropdown.grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
    ip_manual.grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)

    # Expandir campos para que ocupen todo el espacio horizontal
    marco_formulario.columnconfigure(1, weight=1)

    # Sección de botones
    marco_botones = ttk.Frame(marco)
    marco_botones.pack(pady=20)

    def conectar_ssh():
        equipo_nombre = equipo_seleccionado.get()
        host = ip_manual.get().strip() if ip_manual.get().strip() else equipos.get(equipo_nombre, None)

        if not host:
            messagebox.showerror("Error", "Por favor, selecciona un equipo o ingresa una IP manual.")
            return

        user = usuario.get()
        passwd = password.get()

        if not passwd:
            passwd = obtener_credenciales(host, user)
            if not passwd:
                messagebox.showerror("Error", "Contraseña no encontrada. Ingresa manualmente.")
                return

        if not verificar_permiso_rol(rol.get(), "SSH"):
            messagebox.showerror("Permiso denegado", "No tienes permiso para realizar esta acción.")
            return

        exito = conectar_equipo_ssh(host, user, passwd)
        if exito:
            guardar_credenciales(host, user, passwd)

    def conectar_rdp():
        equipo_nombre = equipo_seleccionado.get()
        host = ip_manual.get().strip() if ip_manual.get().strip() else equipos.get(equipo_nombre, None)

        if not host:
            messagebox.showerror("Error", "Por favor, selecciona un equipo o ingresa una IP manual.")
            return

        if not verificar_permiso_rol(rol.get(), "RDP"):
            messagebox.showerror("Permiso denegado", "No tienes permiso para realizar esta acción.")
            return

        conectar_equipo_rdp(host)

    ttk.Button(marco_botones, text="Conectar SSH", command=conectar_ssh).pack(side=tk.LEFT, padx=20)
    ttk.Button(marco_botones, text="Conectar RDP", command=conectar_rdp).pack(side=tk.LEFT, padx=20)

    ventana.mainloop()


if __name__ == "__main__":
    interfaz()