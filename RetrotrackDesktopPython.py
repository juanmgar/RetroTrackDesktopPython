import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

import requests
from zeep import Client

# URLs
API_REST_URL = "http://localhost:5099/retrotrack/api"
API_SOAP_WSDL = "http://localhost:8085/RetroTrackSoapJava_war_exploded/api/user?wsdl"

# Datos cargados
users = []
games = []

def cargar_usuarios():
    global users
    try:
        client = Client(API_SOAP_WSDL)
        users = client.service.listUsers()
        combo_users['values'] = users
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar usuarios:\n{e}")

def cargar_juegos():
    global games
    try:
        response = requests.get(f"{API_REST_URL}/Games")
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

    # Validar formato hora (HH:MM)
    try:
        hour_obj = datetime.datetime.strptime(hour_text, "%H:%M").time()
    except ValueError:
        messagebox.showerror("Error", "Formato de hora inválido. Usa HH:MM (24h).")
        return

    game_id = games[game_index]['id']

    # Combinar fecha y hora
    played_at = datetime.datetime.combine(selected_date, hour_obj)

    data = {
        "playerId": username,
        "gameId": game_id,
        "playedAt": played_at.isoformat(),
        "minutesPlayed": minutes
    }

    try:
        response = requests.post(f"{API_REST_URL}/GameSessions", json=data)
        if response.status_code in [200, 201]:
            messagebox.showinfo("Éxito", "Sesión registrada correctamente.")
        else:
            messagebox.showerror("Error", f"Error al registrar sesión: {response.status_code}\n{response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al conectar con la API: {e}")

# Crear ventana
root = tk.Tk()
root.title("RetroTrack - Logger de sesiones")
root.geometry("450x400")

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
date_entry = DateEntry(frame_form, width=12, background='darkblue',
                       foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
date_entry.grid(row=3, column=1)

label_hour = tk.Label(frame_form, text="Hora (HH:MM):")
label_hour.grid(row=4, column=0, sticky="e")
entry_hour = tk.Entry(frame_form, width=10)
entry_hour.grid(row=4, column=1)

btn_submit = tk.Button(root, text="Enviar Sesión", command=enviar_sesion)
btn_submit.pack(pady=20)

# Cargar datos al iniciar
cargar_juegos()
cargar_usuarios()

root.mainloop()
