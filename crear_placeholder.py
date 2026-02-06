"""
Crear imagen placeholder genérica para productos sin imagen
"""
from PIL import Image, ImageDraw, ImageFont
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
img_dir = os.path.join(base_dir, "imagenes", "productos")

# Crear placeholder genérico
size = (150, 150)
img = Image.new('RGB', size, '#E3F2FD')
draw = ImageDraw.Draw(img)

# Borde
draw.rectangle([2, 2, 147, 147], outline='#1976D2', width=3)

# Icono de caja/medicamento
draw.rectangle([45, 35, 105, 95], fill='#1976D2', outline='#0D47A1', width=2)
draw.rectangle([55, 55, 95, 85], fill='white')
draw.line([60, 70, 90, 70], fill='#1976D2', width=2)
draw.line([75, 60, 75, 80], fill='#1976D2', width=2)

# Texto
try:
    font = ImageFont.truetype("arial.ttf", 14)
except:
    font = ImageFont.load_default()

draw.text((75, 115), "PRODUCTO", font=font, fill='#1976D2', anchor='mm')

# Guardar
placeholder_path = os.path.join(img_dir, "_placeholder.png")
img.save(placeholder_path)
print(f"Placeholder creado: {placeholder_path}")

# También crear placeholders por categoría
categorias = {
    'medicamento': ('#2196F3', '💊'),
    'perfumeria': ('#E91E63', '🧴'),
    'abarrotes': ('#4CAF50', '🛒'),
    'bebes': ('#FF9800', '👶'),
    'especialidad': ('#9C27B0', '⚕️'),
}

for cat, (color, emoji) in categorias.items():
    img = Image.new('RGB', size, '#FAFAFA')
    draw = ImageDraw.Draw(img)
    draw.rectangle([2, 2, 147, 147], outline=color, width=4)

    # Círculo central
    draw.ellipse([40, 30, 110, 100], fill=color)

    try:
        font_big = ImageFont.truetype("arial.ttf", 36)
        font_small = ImageFont.truetype("arial.ttf", 11)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Texto de categoría
    draw.text((75, 125), cat.upper()[:12], font=font_small, fill=color, anchor='mm')

    cat_path = os.path.join(img_dir, f"_cat_{cat}.png")
    img.save(cat_path)
    print(f"Categoría '{cat}': {cat_path}")

print("\nPlaceholders creados correctamente!")
