"""Test de imagen en Tkinter"""
import tkinter as tk
from PIL import Image, ImageTk
import os

root = tk.Tk()
root.title("Test Imagen")
root.geometry("400x200")

# Ruta base
base_dir = os.path.dirname(os.path.realpath(__file__))
img_path = os.path.join(base_dir, "imagenes", "productos", "tempra.png")

print(f"Base dir: {base_dir}")
print(f"Imagen: {img_path}")
print(f"Existe: {os.path.exists(img_path)}")

# Frame
frame = tk.Frame(root, bg="#BBDEFB", relief=tk.RIDGE, bd=2)
frame.pack(fill=tk.X, padx=20, pady=20)

# Label para imagen
img_label = tk.Label(frame, bg="#BBDEFB", text="Cargando...", font=("Arial", 12))
img_label.pack(side=tk.LEFT, padx=10, pady=10)

# Info
info_label = tk.Label(frame, text="TEMPRA - $20.70", font=("Segoe UI", 14, "bold"),
                      bg="#BBDEFB", fg="#2E7D32")
info_label.pack(side=tk.LEFT, padx=10)

# Cargar imagen
if os.path.exists(img_path):
    try:
        pil_img = Image.open(img_path)
        print(f"Imagen abierta: {pil_img.size}")
        pil_img = pil_img.resize((60, 60), Image.LANCZOS)
        photo = ImageTk.PhotoImage(pil_img)
        img_label.config(image=photo, text="")
        img_label.image = photo  # IMPORTANTE: mantener referencia
        print("Imagen configurada!")
    except Exception as e:
        print(f"Error: {e}")
        img_label.config(text="ERROR")
else:
    print("Imagen no encontrada!")
    img_label.config(text="NO IMG")

root.mainloop()
