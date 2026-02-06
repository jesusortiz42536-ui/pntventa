"""
CORREGIR PRECIOS V2 - FARMACIAS MADRID
Precios basados en referencias reales de farmacias mexicanas 2024-2025
Ejemplo: Tempra Jarabe 120ml = $169-276
"""

import sqlite3
import re
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")

# Precios base REALES por forma farmacéutica (pesos mexicanos)
PRECIOS_BASE = {
    'JARABE': 145,
    'SUSPENSION': 135,
    'SUSPENSION ORAL': 135,
    'SOLUCION ORAL': 125,
    'GOTAS': 95,
    'TABLETAS': 85,
    'TABLETAS MASTICABLES': 90,
    'TABLETAS RECUBIERTAS': 95,
    'CAPSULAS': 95,
    'CAPSULAS BLANDAS': 105,
    'GRAGEAS': 90,
    'AMPOLLETAS': 185,
    'INYECTABLE': 220,
    'SOLUCION INYECTABLE': 210,
    'CREMA': 145,
    'GEL': 135,
    'POMADA': 125,
    'UNGÜENTO': 120,
    'SUPOSITORIO': 115,
    'OVULO': 165,
    'POLVO': 95,
    'GRANULADO': 85,
    'SPRAY': 175,
    'INHALADOR': 350,
    'PARCHE': 285,
    'SOLUCION OFTALMICA': 195,
    'COLIRIO': 185,
}

# Multiplicadores por marca (basado en precios reales)
MARCAS_PREMIUM = {
    'BAYER': 1.6,
    'PFIZER': 1.7,
    'ROCHE': 1.65,
    'GSK': 1.5,
    'NOVARTIS': 1.7,
    'MERCK': 1.65,
    'SANOFI': 1.55,
    'ASTRAZENECA': 1.7,
    'JOHNSON': 1.45,
    'ABBOTT': 1.5,
    'SOPHIA': 1.25,
    'PISA': 1.15,
    'GENERICO': 0.65,
}

def extraer_info_producto(nombre):
    """Extrae información del nombre del producto."""
    info = {
        'forma': 'TABLETAS',
        'piezas': 10,
        'ml': 0,
        'mg': 0,
        'g': 0,
        'marca': 'GENERICO',
    }

    nombre_upper = nombre.upper()

    # Detectar forma farmacéutica (orden importa - más específico primero)
    formas_ordenadas = sorted(PRECIOS_BASE.keys(), key=len, reverse=True)
    for forma in formas_ordenadas:
        if forma in nombre_upper:
            info['forma'] = forma
            break

    # Detectar cantidad de piezas
    piezas_match = re.search(r'(\d+)\s*PIEZAS', nombre_upper)
    if piezas_match:
        info['piezas'] = int(piezas_match.group(1))

    # Detectar ml
    ml_match = re.search(r'(\d+)\s*ML', nombre_upper)
    if ml_match:
        info['ml'] = int(ml_match.group(1))

    # Detectar gramos (para jarabes tipo "3.2g/100ml")
    g_match = re.search(r'(\d+(?:\.\d+)?)\s*G[R]?(?:/|\s)', nombre_upper)
    if g_match:
        info['g'] = float(g_match.group(1))

    # Detectar mg
    mg_match = re.search(r'(\d+)\s*MG', nombre_upper)
    if mg_match:
        info['mg'] = int(mg_match.group(1))

    # Detectar ampolletas
    amp_match = re.search(r'(\d+)\s*AMP', nombre_upper)
    if amp_match:
        info['piezas'] = int(amp_match.group(1))

    # Detectar marca
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
    precio = PRECIOS_BASE.get(info['forma'], 95)

    # Ajustar por cantidad de piezas (para tabletas/cápsulas)
    if info['forma'] in ['TABLETAS', 'CAPSULAS', 'CAPSULAS BLANDAS', 'GRAGEAS',
                         'TABLETAS MASTICABLES', 'TABLETAS RECUBIERTAS']:
        if info['piezas'] <= 10:
            precio *= 1.0
        elif info['piezas'] <= 20:
            precio *= 1.8
        elif info['piezas'] <= 30:
            precio *= 2.5
        elif info['piezas'] <= 60:
            precio *= 3.5
        else:
            precio *= 5.0

    # Ajustar por ml (para líquidos)
    if info['ml'] > 0:
        if info['ml'] <= 60:
            precio *= 0.85
        elif info['ml'] <= 100:
            precio *= 1.0
        elif info['ml'] <= 120:
            precio *= 1.25
        elif info['ml'] <= 240:
            precio *= 1.6
        else:
            precio *= 2.0

    # Ajustar por concentración de gramos (jarabes concentrados más caros)
    if info['g'] >= 3:
        precio *= 1.3
    elif info['g'] >= 1:
        precio *= 1.15

    # Ajustar por mg (concentración alta = más caro)
    if info['mg'] >= 1000:
        precio *= 1.4
    elif info['mg'] >= 500:
        precio *= 1.25
    elif info['mg'] >= 250:
        precio *= 1.1

    # Ajustar por cantidad de ampolletas
    if info['forma'] in ['AMPOLLETAS', 'INYECTABLE', 'SOLUCION INYECTABLE']:
        if info['piezas'] <= 1:
            precio *= 1.0
        elif info['piezas'] <= 3:
            precio *= 1.8
        elif info['piezas'] <= 5:
            precio *= 2.5
        else:
            precio *= 3.5

    # Multiplicador por marca
    mult_marca = MARCAS_PREMIUM.get(info['marca'], 1.0)
    precio *= mult_marca

    # Redondear a .50
    precio = round(precio * 2) / 2

    # Límites
    precio = max(35.0, min(precio, 1500.0))

    return precio


def main():
    print("=" * 60)
    print("  CORREGIR PRECIOS V2 - PRECIOS REALES")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, nombre, precio_venta FROM productos WHERE categoria='MEDICAMENTOS'")
    productos = c.fetchall()

    print(f"\nProductos a procesar: {len(productos)}")
    print("\nEjemplos:")
    print("-" * 60)

    actualizados = 0
    ejemplos = 0

    for prod_id, nombre, precio_actual in productos:
        info = extraer_info_producto(nombre)
        nuevo_precio = calcular_precio(info)
        nuevo_costo = round(nuevo_precio * 0.55, 2)  # 45% margen

        if abs(nuevo_precio - precio_actual) > 2.0:
            c.execute("UPDATE productos SET precio_venta=?, precio_costo=? WHERE id=?",
                     (nuevo_precio, nuevo_costo, prod_id))
            actualizados += 1

            if ejemplos < 25:
                print(f"{nombre[:48]:<48} ${precio_actual:>7.2f} -> ${nuevo_precio:>7.2f}")
                ejemplos += 1

    conn.commit()

    # Verificación
    print("\n" + "=" * 60)
    print("  VERIFICACIÓN - TEMPRA/PARACETAMOL")
    print("=" * 60)
    c.execute("""SELECT nombre, precio_venta FROM productos
                 WHERE nombre LIKE '%TEMPRA%' OR nombre LIKE '%PARACETAMOL%'
                 ORDER BY precio_venta DESC LIMIT 15""")
    for nombre, precio in c.fetchall():
        print(f"  {nombre[:52]:<52} ${precio:>7.2f}")

    print("\n" + "-" * 60)
    print("  ASPIRINA")
    print("-" * 60)
    c.execute("""SELECT nombre, precio_venta FROM productos
                 WHERE nombre LIKE '%ASPIRINA%'
                 ORDER BY precio_venta DESC LIMIT 10""")
    for nombre, precio in c.fetchall():
        print(f"  {nombre[:52]:<52} ${precio:>7.2f}")

    print("\n" + "-" * 60)
    print("  JARABES (para comparar)")
    print("-" * 60)
    c.execute("""SELECT nombre, precio_venta FROM productos
                 WHERE nombre LIKE '%JARABE%120ML%'
                 ORDER BY precio_venta DESC LIMIT 10""")
    for nombre, precio in c.fetchall():
        print(f"  {nombre[:52]:<52} ${precio:>7.2f}")

    conn.close()

    print("\n" + "=" * 60)
    print(f"  RESUMEN: {actualizados} productos actualizados")
    print("=" * 60)


if __name__ == "__main__":
    main()
