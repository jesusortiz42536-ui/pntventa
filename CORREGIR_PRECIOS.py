"""
CORREGIR PRECIOS - FARMACIAS MADRID
Ajusta los precios de todos los productos basándose en:
- Forma farmacéutica (jarabe, tabletas, inyectable, etc.)
- Cantidad de piezas
- Concentración (mg/ml)
- Si es genérico o marca
"""

import sqlite3
import re
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")

# Precios base por forma farmacéutica (pesos mexicanos)
PRECIOS_BASE = {
    'TABLETAS': 35,
    'CAPSULAS': 40,
    'CAPSULAS BLANDAS': 45,
    'GRAGEAS': 38,
    'JARABE': 65,
    'SUSPENSION': 55,
    'SOLUCION ORAL': 50,
    'GOTAS': 45,
    'AMPOLLETAS': 95,
    'INYECTABLE': 110,
    'SOLUCION INYECTABLE': 105,
    'CREMA': 85,
    'GEL': 80,
    'POMADA': 75,
    'UNGÜENTO': 70,
    'SUPOSITORIO': 60,
    'OVULO': 85,
    'POLVO': 55,
    'GRANULADO': 50,
    'SPRAY': 95,
    'INHALADOR': 180,
    'PARCHE': 150,
    'SOLUCION OFTALMICA': 120,
    'COLIRIO': 110,
}

# Multiplicadores por marca
MARCAS_PREMIUM = {
    'BAYER': 1.4,
    'PFIZER': 1.5,
    'ROCHE': 1.45,
    'GSK': 1.35,
    'NOVARTIS': 1.5,
    'MERCK': 1.45,
    'SANOFI': 1.4,
    'ASTRAZENECA': 1.5,
    'JOHNSON': 1.3,
    'ABBOTT': 1.35,
    'SOPHIA': 1.2,
    'PISA': 1.1,
    'GENERICO': 0.7,
}

def extraer_info_producto(nombre):
    """Extrae información del nombre del producto."""
    info = {
        'forma': 'TABLETAS',
        'piezas': 10,
        'ml': 0,
        'mg': 0,
        'marca': 'GENERICO',
    }

    # Detectar forma farmacéutica
    nombre_upper = nombre.upper()
    for forma in PRECIOS_BASE.keys():
        if forma in nombre_upper:
            info['forma'] = forma
            break

    # Detectar cantidad de piezas
    piezas_match = re.search(r'(\d+)\s*PIEZAS', nombre_upper)
    if piezas_match:
        info['piezas'] = int(piezas_match.group(1))

    # Detectar ml (para jarabes/suspensiones)
    ml_match = re.search(r'(\d+)\s*ML', nombre_upper)
    if ml_match:
        info['ml'] = int(ml_match.group(1))

    # Detectar mg
    mg_match = re.search(r'(\d+)\s*MG', nombre_upper)
    if mg_match:
        info['mg'] = int(mg_match.group(1))

    # Detectar ampolletas
    amp_match = re.search(r'(\d+)\s*AMP', nombre_upper)
    if amp_match:
        info['piezas'] = int(amp_match.group(1))

    # Detectar marca (al final del nombre después del guión)
    marca_match = re.search(r'-\s*(\w+)\s*$', nombre)
    if marca_match:
        marca = marca_match.group(1).upper()
        if marca in MARCAS_PREMIUM:
            info['marca'] = marca
        elif 'GENERICO' in nombre_upper or 'GENÉRICO' in nombre_upper:
            info['marca'] = 'GENERICO'

    return info


def calcular_precio(info):
    """Calcula el precio basado en la información del producto."""
    # Precio base por forma
    precio = PRECIOS_BASE.get(info['forma'], 40)

    # Ajustar por cantidad de piezas
    if info['piezas'] > 0:
        if info['piezas'] <= 10:
            precio *= 1.0
        elif info['piezas'] <= 20:
            precio *= 1.5
        elif info['piezas'] <= 30:
            precio *= 2.0
        elif info['piezas'] <= 60:
            precio *= 3.0
        else:
            precio *= 4.0

    # Ajustar por ml (para líquidos)
    if info['ml'] > 0:
        if info['ml'] <= 60:
            precio *= 0.9
        elif info['ml'] <= 100:
            precio *= 1.0
        elif info['ml'] <= 120:
            precio *= 1.15
        else:
            precio *= 1.3

    # Ajustar por concentración (mg altos = más caro)
    if info['mg'] >= 500:
        precio *= 1.2
    elif info['mg'] >= 250:
        precio *= 1.1
    elif info['mg'] >= 100:
        precio *= 1.0
    elif info['mg'] > 0:
        precio *= 0.9

    # Multiplicador por marca
    mult_marca = MARCAS_PREMIUM.get(info['marca'], 1.0)
    precio *= mult_marca

    # Redondear a .50 o .00
    precio = round(precio * 2) / 2

    # Límites razonables
    precio = max(15.0, min(precio, 500.0))

    return precio


def main():
    print("=" * 60)
    print("  CORREGIR PRECIOS - FARMACIAS MADRID")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Obtener todos los productos de medicamentos
    c.execute("SELECT id, nombre, precio_venta FROM productos WHERE categoria='MEDICAMENTOS'")
    productos = c.fetchall()

    print(f"\nProductos a procesar: {len(productos)}")
    print("\nEjemplos de corrección:")
    print("-" * 60)

    actualizados = 0
    ejemplos_mostrados = 0

    for prod_id, nombre, precio_actual in productos:
        info = extraer_info_producto(nombre)
        nuevo_precio = calcular_precio(info)
        nuevo_costo = round(nuevo_precio * 0.6, 2)

        # Solo actualizar si hay cambio significativo
        if abs(nuevo_precio - precio_actual) > 1.0:
            c.execute("UPDATE productos SET precio_venta=?, precio_costo=? WHERE id=?",
                     (nuevo_precio, nuevo_costo, prod_id))
            actualizados += 1

            # Mostrar ejemplos
            if ejemplos_mostrados < 30:
                print(f"{nombre[:50]:<50} ${precio_actual:>7.2f} -> ${nuevo_precio:>7.2f}")
                ejemplos_mostrados += 1

    conn.commit()

    # Mostrar algunos ejemplos finales
    print("\n" + "=" * 60)
    print("  VERIFICACIÓN DE PRECIOS CORREGIDOS")
    print("=" * 60)

    c.execute("""SELECT nombre, precio_venta FROM productos
                 WHERE nombre LIKE '%TEMPRA%' OR nombre LIKE '%PARACETAMOL%'
                 ORDER BY precio_venta DESC LIMIT 15""")
    for nombre, precio in c.fetchall():
        print(f"  {nombre[:55]:<55} ${precio:>7.2f}")

    print("\n" + "-" * 60)
    c.execute("""SELECT nombre, precio_venta FROM productos
                 WHERE nombre LIKE '%ASPIRINA%'
                 ORDER BY precio_venta DESC LIMIT 10""")
    for nombre, precio in c.fetchall():
        print(f"  {nombre[:55]:<55} ${precio:>7.2f}")

    conn.close()

    print("\n" + "=" * 60)
    print(f"  RESUMEN: {actualizados} productos actualizados")
    print("=" * 60)


if __name__ == "__main__":
    main()
