"""
Script para guardar capturas del portapapeles
Instrucciones:
1. Copia una captura (Print Screen o Snipping Tool)
2. Ejecuta este script
3. Elige el nombre del módulo
"""
from PIL import ImageGrab, Image
import os

base = os.path.dirname(os.path.abspath(__file__))
capturas_dir = os.path.join(base, "presentacion", "capturas")
os.makedirs(capturas_dir, exist_ok=True)

modulos = {
    "1": "dashboard",
    "2": "ventas",
    "3": "saturnos",
    "4": "creditos",
    "5": "inventario",
    "6": "ofertas",
    "7": "clientes",
    "8": "domicilio",
    "9": "traspasos",
    "10": "finanzas",
    "11": "compras",
    "12": "caja",
    "13": "alertas",
    "14": "usuarios",
    "15": "ecommerce",
    "16": "vales"
}

print("\n" + "="*50)
print("  GUARDAR CAPTURA DEL PORTAPAPELES")
print("="*50)
print("\nMódulos disponibles:")
for k, v in modulos.items():
    archivo = os.path.join(capturas_dir, f"{v}.png")
    existe = " [YA EXISTE]" if os.path.exists(archivo) else ""
    print(f"  {k}. {v.upper()}{existe}")

print("\n  0. SALIR")
print("\nAsegúrate de tener una captura copiada (Ctrl+C o Print Screen)")

while True:
    opcion = input("\nElige número del módulo: ").strip()

    if opcion == "0":
        break

    if opcion not in modulos:
        print("Opción no válida")
        continue

    nombre = modulos[opcion]

    try:
        img = ImageGrab.grabclipboard()
        if img is None:
            print("No hay imagen en el portapapeles!")
            print("Copia una captura primero (Print Screen o Snipping Tool)")
            continue

        # Redimensionar para que no sea muy grande
        max_width = 800
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        archivo = os.path.join(capturas_dir, f"{nombre}.png")
        img.save(archivo, "PNG")
        print(f"\n✓ Guardado: {archivo}")

    except Exception as e:
        print(f"Error: {e}")

print("\nCapturas guardadas en:", capturas_dir)
print("\nAhora ejecuta: python crear_presentacion.py")
