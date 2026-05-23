import os
import platform
import sys
from datetime import date
import tkinter as tk
from tkinter import messagebox, ttk
import gpxpy
import gpxpy.gpx
from garminconnect import Garmin
import tkintermapview

# --- CONFIGURATIE & SETUP ---
garmin_session = {"client": None, "email": "", "password": ""}
route_points = []  # Hier slaan we de geklikte coördinaten op


# --- RECHTSSTREEKS NAAR USB SCHRIJVEN ---
def get_garmin_usb_path():
    system = platform.system()
    if system == "Windows":
        for drive in range(68, 91):  # D tot Z
            drive_letter = f"{chr(drive)}:\\"
            potential_path = os.path.join(drive_letter, "Garmin", "NewFiles")
            if os.path.exists(os.path.join(drive_letter, "Garmin")):
                return potential_path
    elif system == "Linux":
        base_media = "/run/media"
        if os.path.exists(base_media):
            for user_dir in os.listdir(base_media):
                user_path = os.path.join(base_media, user_dir)
                for mount in os.listdir(user_path):
                    garmin_base = os.path.join(user_path, mount, "Garmin")
                    if os.path.exists(garmin_base):
                        return os.path.join(garmin_base, "NewFiles")
    return None


# --- GPX BESTAND GENEREREN ---
from datetime import datetime, timedelta

def generate_gpx():
    """Zet de geklikte punten om in een GPX bestand met tijdstempels voor Garmin."""
    if len(route_points) < 2:
        return None

    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Garmin eist tijdstempels bij een activiteit-upload.
    # We starten vanaf nu en tellen er per punt 10 seconden bij op.
    start_tijd = datetime.now()

    for i, pt in enumerate(route_points):
        punt_tijd = start_tijd + timedelta(seconds=i * 10)
        gpx_segment.points.append(
            gpxpy.gpx.GPXTrackPoint(
                latitude=pt[0], 
                longitude=pt[1],
                time=punt_tijd
            )
        )

    return gpx.to_xml()
# --- FUNCTIES VOOR DE KNOPPEN ---
def handle_map_click(coords):
    lat, lon = coords
    route_points.append((lat, lon))
    if len(route_points) > 1:
        map_widget.set_path([p for p in route_points])
    map_widget.set_marker(lat, lon, text=f"Punt {len(route_points)}")
    status_label.config(text=f"Aantal punten op de kaart: {len(route_points)}")


def clear_route():
    global route_points
    route_points = []
    map_widget.delete_all_path()
    map_widget.delete_all_marker()
    status_label.config(text="Kaart gewist. Klik om een route te starten.")


def send_via_usb():
    gpx_data = generate_gpx()
    if not gpx_data:
        messagebox.showwarning(
            "Fout", "Teken eerst een route met minimaal 2 punten!"
        )
        return

    usb_path = get_garmin_usb_path()
    if not usb_path:
        messagebox.showerror(
            "Niet gevonden",
            "Garmin horloge niet gevonden via USB.\nSluit de kabel aan of controleer of hij is gekoppeld.",
        )
        return

    try:
        os.makedirs(usb_path, exist_ok=True)
        file_path = os.path.join(usb_path, "custom_route.gpx")
        with open(file_path, "w") as f:
            f.write(gpx_data)
        messagebox.showinfo(
            "Succes", "Route succesvol via USB op je Garmin gezet!"
        )
    except Exception as e:
        messagebox.showerror(
            "Fout", f"Kon bestand niet naar USB schrijven: {e}"
        )


def login_garmin():
    email = email_entry.get()
    password = pass_entry.get()

    if not email or not password:
        messagebox.showwarning("Inloggen", "Vul je e-mail en wachtwoord in!")
        return

    status_label.config(text="Inloggen bij Garmin Cloud... Even geduld.")
    root.update()

    try:
        # Pas NU wordt er verbinding gemaakt, niet bij het opstarten
        client = Garmin(email, password)
        client.login()
        garmin_session["client"] = client
        garmin_session["email"] = email
        garmin_session["password"] = password
        status_label.config(text="Succesvol ingelogd bij Garmin!")
        messagebox.showinfo("Garmin Cloud", "Succesvol verbonden met Garmin!")
    except Exception as e:
        status_label.config(text="Inloggen mislukt vanwege beveiliging.")
        messagebox.showerror(
            "Garmin Blokade",
            f"Garmin weigert de verbinding op dit moment (429 Rate Limit).\n\n"
            f"Oplossing: Wacht een paar minuten, of zet je telefoon even op 4G-hotspot "
            f"om Garmin te omzeilen.\n\nTechnisch detail: {e}",
        )

def send_via_cloud():
    gpx_data = generate_gpx()
    if not gpx_data:
        messagebox.showwarning(
            "Fout", "Teken eerst een route met minimaal 2 punten!"
        )
        return

    if not garmin_session["client"]:
        messagebox.showwarning(
            "Garmin Cloud", "Log eerst in met je Garmin account aan de rechterkant!"
        )
        return

    status_label.config(text="Route aan het uploaden naar Garmin Cloud...")
    root.update()

    # We gebruiken hier 'route.gpx' in plaats van 'temp_route.gpx'
    # Sommige Garmin servers weigeren bestanden die met 'temp_' beginnen
    temp_filename = "route.gpx"
    try:
        with open(temp_filename, "w", encoding="utf-8") as f:
            f.write(gpx_data)

        client = garmin_session["client"]
        
        # We proberen de officiële upload_activity aanroep
        # Garmin verwacht dat het bestand fysiek op de schijf staat
        client.upload_activity(temp_filename)

        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        status_label.config(text="Route succesvol geüpload!")
        messagebox.showinfo(
            "Succes",
            "Route is succesvol verzonden naar Garmin Connect!\nJe vindt hem nu terug bij je Activiteiten/Koersen.",
        )
    except Exception as e:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        status_label.config(text="Uploaden mislukt.")
        messagebox.showerror(
            "Fout 400 Oplossing", 
            f"Garmin weigert dit specifieke bestand: {e}\n\n"
            f"Tip: Probeer eens een langere route te tekenen (bijvoorbeeld 4 of 5 punten) "
            f"zodat Garmin de route beter herkent als een track!"
        )
# --- DE INTERFACE (GUI) BOUWEN ---
root = tk.Tk()
root.title("Community Garmin Route Planner")
root.geometry("1100x700")

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

left_frame = ttk.Frame(main_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

map_widget = tkintermapview.TkinterMapView(
    left_frame, width=800, height=600, corner_radius=10
)
map_widget.pack(fill=tk.BOTH, expand=True)
map_widget.set_position(51.2194, 4.4025)  # Start op Antwerpen
map_widget.set_zoom(10)
map_widget.add_left_click_map_command(handle_map_click)

right_frame = ttk.LabelFrame(main_frame, text=" Bediening & Inloggen ", padding="15")
right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

ttk.Label(right_frame, text="Garmin Account E-mail:").pack(
    anchor=tk.W, pady=(10, 2)
)
email_entry = ttk.Entry(right_frame, width=30)
email_entry.pack(anchor=tk.W, pady=2)

ttk.Label(right_frame, text="Wachtwoord:").pack(anchor=tk.W, pady=(10, 2))
pass_entry = ttk.Entry(right_frame, show="*", width=30)
pass_entry.pack(anchor=tk.W, pady=2)

login_btn = ttk.Button(
    right_frame, text="Verbind met Garmin Cloud", command=login_garmin
)
login_btn.pack(fill=tk.X, pady=10)

ttk.Separator(right_frame, orient="horizontal").pack(fill=tk.X, pady=15)

ttk.Label(right_frame, text="Route Acties:", font=("Arial", 10, "bold")).pack(
    anchor=tk.W, pady=5
)

usb_btn = ttk.Button(
    right_frame, text="🔌 Zet op horloge via USB", command=send_via_usb
)
usb_btn.pack(fill=tk.X, pady=5)

cloud_btn = ttk.Button(
    right_frame, text="☁️ Verstuur draadloos (Cloud)", command=send_via_cloud
)
cloud_btn.pack(fill=tk.X, pady=5)

clear_btn = ttk.Button(
    right_frame, text="🗑️ Wis huidige route", command=clear_route
)
clear_btn.pack(fill=tk.X, pady=(20, 5))

status_label = ttk.Label(
    root,
    text="Klik op de kaart om punten te plaatsen en een route te maken.",
    relief=tk.SUNKEN,
    anchor=tk.W,
    padding="5",
)
status_label.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()