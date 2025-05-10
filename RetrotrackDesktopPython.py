import sys
import os
import io
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import ImageGrab
import requests
from zeep import Client, Transport

# URLs
API_REST_URL = "https://localhost:9095/rest/api"
API_SOAP_WSDL = "https://localhost:8095/soap/api/user?wsdl"

# Datos cargados
users = []
games = []

def get_resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def cargar_usuarios():
    global users
    try:
        session = requests.Session()
        session.verify = get_resource_path('certs/apiSoap.pem')

        transport = Transport(session=session)
        client = Client(API_SOAP_WSDL, transport=transport)

        users = client.service.listUsers()
        combo_users['values'] = users
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar usuarios:\n{e}")

def cargar_juegos():
    global games
    try:
        response = requests.get(f"{API_REST_URL}/Games", verify=get_resource_path('certs/apiRest.pem'))
        response.raise_for_status()
        games = response.json()
        combo_games['values'] = [g['title'] for g in games]
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar juegos:\n{e}")

def enviar_sesion():
    username = combo_users.get()
    game_index = combo_games.current()
    minutes = entry_minutes.get()
    selected_date = date_entry.get_date()
    hour_text = entry_hour.get()

    if not username or game_index == -1 or not minutes or not hour_text:
        messagebox.showerror("Error", "Completa todos los campos.")
        return

    try:
        minutes = int(minutes)
    except ValueError:
        messagebox.showerror("Error", "Los minutos deben ser un número.")
        return

    try:
        hour_obj = datetime.datetime.strptime(hour_text, "%H:%M").time()
    except ValueError:
        messagebox.showerror("Error", "Formato de hora inválido. Usa HH:MM (24h).")
        return

    played_at = datetime.datetime.combine(selected_date, hour_obj)
    game_id = games[game_index]['id']

    data = {
        "playerId": username,
        "gameId": str(game_id),
        "playedAt": played_at.isoformat(),
        "minutesPlayed": str(minutes)
    }

    files = {}
    if send_screenshot_var.get():
        screenshot = ImageGrab.grab()
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        buffer.seek(0)
        files["screenshot"] = ("screenshot.png", buffer, "image/png")

    try:
        response = requests.post(
            f"{API_REST_URL}/GameSessions",
            data=data,
            files=files if files else None,
            verify=get_resource_path('certs/apiRest.pem')
        )
        if response.status_code in [200, 201]:
            messagebox.showinfo("Éxito", "Sesión registrada correctamente.")
        else:
            messagebox.showerror("Error", f"Error al registrar sesión: {response.status_code}\n{response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al conectar con la API: {e}")

# Crear ventana
root = tk.Tk()
root.title("RetroTrack - Logger de sesiones")
root.geometry("450x450")

label_title = tk.Label(root, text="Registrar Sesión de Juego", font=("Arial", 16))
label_title.pack(pady=10)

frame_form = tk.Frame(root)
frame_form.pack(pady=10)

label_user = tk.Label(frame_form, text="Usuario:")
label_user.grid(row=0, column=0, sticky="e")
combo_users = ttk.Combobox(frame_form, state="readonly")
combo_users.grid(row=0, column=1)

label_game = tk.Label(frame_form, text="Juego:")
label_game.grid(row=1, column=0, sticky="e")
combo_games = ttk.Combobox(frame_form, state="readonly")
combo_games.grid(row=1, column=1)

label_minutes = tk.Label(frame_form, text="Minutos jugados:")
label_minutes.grid(row=2, column=0, sticky="e")
entry_minutes = tk.Entry(frame_form, width=10)
entry_minutes.grid(row=2, column=1)

label_date = tk.Label(frame_form, text="Fecha:")
label_date.grid(row=3, column=0, sticky="e")
date_entry = DateEntry(frame_form, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
date_entry.grid(row=3, column=1)

label_hour = tk.Label(frame_form, text="Hora (HH:MM):")
label_hour.grid(row=4, column=0, sticky="e")
entry_hour = tk.Entry(frame_form, width=10)
entry_hour.grid(row=4, column=1)

# Checkbox para incluir screenshot
send_screenshot_var = tk.BooleanVar(value=True)
check_screenshot = tk.Checkbutton(root, text="Incluir captura de pantalla", variable=send_screenshot_var)
check_screenshot.pack(pady=5)

btn_submit = tk.Button(root, text="Enviar Sesión", command=enviar_sesion)
btn_submit.pack(pady=20)

# Cargar datos al iniciar
cargar_juegos()
cargar_usuarios()

# Hora actual por defecto
current_time = datetime.datetime.now().strftime("%H:%M")
entry_hour.insert(0, current_time)

root.mainloop()
