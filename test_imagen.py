import os
from PIL import Image

# Test path resolution
print("=" * 50)
print("TEST DE RUTAS DE IMAGENES")
print("=" * 50)

print(f"\n__file__ = {__file__}")
print(f"os.path.abspath(__file__) = {os.path.abspath(__file__)}")

base_dir = os.path.dirname(os.path.abspath(__file__))
print(f"base_dir = {base_dir}")

img_path = "imagenes/productos/aspirina.png"
full_path = os.path.join(base_dir, img_path)
print(f"\nimg_path en DB: {img_path}")
print(f"full_path construido: {full_path}")
print(f"Existe: {os.path.exists(full_path)}")

if os.path.exists(full_path):
    try:
        img = Image.open(full_path)
        print(f"Imagen cargada: {img.size}")
    except Exception as e:
        print(f"Error al cargar: {e}")
else:
    # Intentar listar la carpeta
    productos_dir = os.path.join(base_dir, "imagenes", "productos")
    print(f"\nBuscando en: {productos_dir}")
    if os.path.exists(productos_dir):
        files = os.listdir(productos_dir)[:5]
        print(f"Archivos encontrados: {files}")
    else:
        print("La carpeta imagenes/productos NO existe")

        # Verificar estructura
        print(f"\nContenido de {base_dir}:")
        for item in os.listdir(base_dir)[:10]:
            print(f"  - {item}")
