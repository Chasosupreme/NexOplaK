import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes

# --- Arreglar letras borrosas en Windows ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # DPI Awareness
except Exception:
    pass

# Categorías de archivos
file_types = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Music": [".mp3", ".wav", ".aac", ".flac"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
    "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Programs": [".exe", ".msi", ".apk", ".bat", ".sh"],
    "Launcher": [".lnk"],
    "Others": []
}

backup_moves = []  # Guardará los movimientos hechos
current_folder = None  # Última carpeta organizada

def is_already_organized(folder):
    # Recorre archivos y subcarpetas
    for root_dir, dirs, files in os.walk(folder):
        # Ignorar carpetas de destino
        if root_dir in [os.path.join(folder, cat) for cat in file_types.keys()] + [os.path.join(folder, "Folders")]:
            continue
        if files or dirs:
            return False  # Hay algo fuera de las carpetas principales
    return True  # Todo está organizado

def organize_files(folder):
    global backup_moves, current_folder
    backup_moves = []
    current_folder = folder

    if not os.path.exists(folder):
        messagebox.showerror("Error", "The selected folder does not exist.")
        return

    # Crear carpetas principales si no existen
    for category in file_types.keys():
        os.makedirs(os.path.join(folder, category), exist_ok=True)

    # Crear carpeta especial para subcarpetas
    folders_dir = os.path.join(folder, "Folders")
    os.makedirs(folders_dir, exist_ok=True)

    # Comprobar si ya está organizado
    if is_already_organized(folder):
        messagebox.showinfo("Info", "Already organized!")
        return

    # Recorrer TODOS los archivos dentro del folder (subcarpetas incluidas)
    for root_dir, dirs, files in os.walk(folder, topdown=False):
        # Evitar que organice dentro de las carpetas de destino
        if root_dir in [os.path.join(folder, cat) for cat in file_types.keys()] + [folders_dir]:
            continue

        for file in files:
            file_path = os.path.join(root_dir, file)
            file_ext = os.path.splitext(file)[1].lower()

            moved = False
            for category, extensions in file_types.items():
                if file_ext in extensions:
                    dest = os.path.join(folder, category, file)
                    shutil.move(file_path, dest)
                    backup_moves.append((dest, file_path))  # Guardamos movimiento
                    moved = True
                    break

            # Si no encajó, va a "Others"
            if not moved:
                dest = os.path.join(folder, "Others", file)
                shutil.move(file_path, dest)
                backup_moves.append((dest, file_path))

        # Mover carpetas vacías al final (excepto las principales)
        for dir_name in dirs:
            dir_path = os.path.join(root_dir, dir_name)
            if dir_path not in [folders_dir] and dir_name not in file_types.keys():
                try:
                    dest = os.path.join(folders_dir, dir_name)
                    shutil.move(dir_path, dest)
                    backup_moves.append((dest, dir_path))
                except Exception:
                    pass

    messagebox.showinfo("Success", "Files organized successfully!\nYou can undo the action now.")

def undo_action():
    global backup_moves
    if not backup_moves:
        messagebox.showwarning("Undo", "No actions to undo.")
        return

    for new_path, old_path in reversed(backup_moves):
        try:
            if os.path.exists(new_path):
                shutil.move(new_path, old_path)
        except Exception:
            pass

    backup_moves = []  # Limpiar historial después de deshacer
    messagebox.showinfo("Undo", "Organization undone successfully!")

# GUI
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        organize_files(folder)

root = tk.Tk()
root.title("NexOplak File Organizer")
root.geometry("1200x1200")
root.configure(bg="black")

title = tk.Label(root, text="NexOplak File Organizer", font=("Segoe UI", 18, "bold"), fg="cyan", bg="black")
title.pack(pady=20)

btn1 = tk.Button(root, text="Organize", command=select_folder, font=("Segoe UI", 12), bg="cyan", fg="black", width=20)
btn1.pack(pady=15)

btn2 = tk.Button(root, text="Undo", command=undo_action, font=("Segoe UI", 12), bg="red", fg="white", width=20)
btn2.pack(pady=15)

root.mainloop()
