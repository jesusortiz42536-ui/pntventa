"""
ACTUALIZAR PRECIOS - FARMACIAS MADRID
Busca precios reales en Farmacias Similares (API VTEX)
y actualiza el catalogo local.

USO: python ACTUALIZAR_PRECIOS.py
"""

import sqlite3
import requests
import time
import re
import os
from datetime import datetime

# CONFIG
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")
API_URL = "https://www.farmaciasdesimilares.com/api/catalog_system/pub/products/search/{termino}?map=ft&_from=0&_to=9"
DELAY_ENTRE_BUSQUEDAS = 1.5  # segundos entre cada request
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        f"log_precios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "es-MX,es;q=0.9",
}


def extraer_sustancia(nombre_producto):
    """Extrae la sustancia activa del nombre del producto.
    Formato: 'TEMPRA (PARACETAMOL) 500MG ...' -> 'PARACETAMOL'
    """
    match = re.search(r'\(([A-Z/\s]+)\)', nombre_producto)
    if match:
        return match.group(1).strip()
    return None


def extraer_presentacion(nombre_producto):
    """Extrae mg/ml y forma farmaceutica."""
    mg_match = re.search(r'(\d+(?:\.\d+)?)\s*MG', nombre_producto, re.IGNORECASE)
    ml_match = re.search(r'(\d+(?:\.\d+)?)\s*ML', nombre_producto, re.IGNORECASE)

    dosis = None
    if mg_match:
        dosis = f"{mg_match.group(1)}MG"
    elif ml_match:
        dosis = f"{ml_match.group(1)}ML"

    es_tableta = any(t in nombre_producto.upper() for t in ["TABLETA", "CAPSULA", "GRAGEA", "COMPRIMIDO"])
    es_jarabe = any(t in nombre_producto.upper() for t in ["JARABE", "SUSPENSION", "SOLUCION ORAL"])
    es_inyectable = any(t in nombre_producto.upper() for t in ["INYECTABLE", "AMPOLLETA", "AMP"])

    forma = "tableta"
    if es_jarabe:
        forma = "jarabe"
    elif es_inyectable:
        forma = "inyectable"

    return dosis, forma


def buscar_en_similares(termino):
    """Busca un producto en la API de Farmacias Similares."""
    try:
        url = API_URL.format(termino=requests.utils.quote(termino))
        resp = requests.get(url, headers=HEADERS, timeout=15)

        if resp.status_code in (200, 206):
            datos = resp.json()
            if datos and isinstance(datos, list):
                return datos
        elif resp.status_code == 429:
            print("  [!] Rate limited. Esperando 30 segundos...")
            time.sleep(30)
            return None
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"  [!] Error de conexion: {e}")
        return None

    return None


def obtener_precio_similar(producto_api):
    """Extrae el precio de un producto de la API."""
    try:
        items = producto_api.get("items", [])
        if items:
            sellers = items[0].get("sellers", [])
            if sellers:
                precio = sellers[0].get("commertialOffer", {}).get("Price", 0)
                if precio > 0:
                    return precio

            # Alternativa: buscar en otro campo
            precio = items[0].get("price", 0)
            if precio and precio > 0:
                return precio
    except (IndexError, KeyError, TypeError):
        pass
    return None


def encontrar_mejor_match(nombre_local, resultados_api):
    """Encuentra el producto de la API que mejor coincide con el local."""
    sustancia = extraer_sustancia(nombre_local)
    dosis, forma = extraer_presentacion(nombre_local)

    if not sustancia:
        return None, None

    mejor_match = None
    mejor_precio = None
    mejor_score = 0

    for prod in resultados_api:
        nombre_api = prod.get("productName", "").upper()
        precio = obtener_precio_similar(prod)

        if not precio or precio <= 0:
            continue

        score = 0

        # La sustancia debe aparecer en el nombre
        if sustancia.upper() in nombre_api:
            score += 10
        else:
            continue  # Sin la sustancia, no es match

        # Coincidencia de dosis
        if dosis and dosis.upper() in nombre_api:
            score += 5

        # Coincidencia de forma
        if forma == "tableta" and any(t in nombre_api for t in ["TABLETA", "TAB", "CAPSULA", "CAP"]):
            score += 3
        elif forma == "jarabe" and any(t in nombre_api for t in ["JARABE", "JBE", "SUSPENSION", "SUSP"]):
            score += 3
        elif forma == "inyectable" and any(t in nombre_api for t in ["INYECTABLE", "INY", "AMPOLLETA", "AMP"]):
            score += 3

        if score > mejor_score:
            mejor_score = score
            mejor_match = prod
            mejor_precio = precio

    return mejor_match, mejor_precio


def main():
    print("=" * 60)
    print("  ACTUALIZAR PRECIOS - FARMACIAS MADRID")
    print("  Fuente: Farmacias Similares (API VTEX)")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Obtener sustancias unicas para no repetir busquedas
    c.execute("SELECT DISTINCT nombre FROM productos WHERE categoria='MEDICAMENTOS'")
    todos = c.fetchall()

    # Extraer sustancias unicas
    sustancias_unicas = {}
    for (nombre,) in todos:
        sustancia = extraer_sustancia(nombre)
        if sustancia and sustancia not in sustancias_unicas:
            sustancias_unicas[sustancia] = nombre  # guardar un ejemplo

    print(f"\nProductos totales: {len(todos)}")
    print(f"Sustancias unicas a buscar: {len(sustancias_unicas)}")
    print(f"Delay entre busquedas: {DELAY_ENTRE_BUSQUEDAS}s")
    print(f"Log: {LOG_FILE}")
    print()

    input("Presiona ENTER para iniciar (Ctrl+C para cancelar)...")
    print()

    actualizados = 0
    no_encontrados = 0
    errores = 0
    precios_encontrados = {}  # sustancia -> {dosis -> precio}

    log = open(LOG_FILE, "w", encoding="utf-8")
    log.write(f"ACTUALIZACION DE PRECIOS - {datetime.now()}\n")
    log.write(f"Fuente: Farmacias Similares\n")
    log.write("=" * 60 + "\n\n")

    total_sustancias = len(sustancias_unicas)
    for idx, (sustancia, ejemplo) in enumerate(sustancias_unicas.items(), 1):
        print(f"[{idx}/{total_sustancias}] Buscando: {sustancia}...", end=" ", flush=True)

        resultados = buscar_en_similares(sustancia.lower())

        if not resultados:
            print("No encontrado")
            log.write(f"[X] {sustancia}: No encontrado\n")
            no_encontrados += 1
            time.sleep(DELAY_ENTRE_BUSQUEDAS)
            continue

        # Guardar todos los precios encontrados para esta sustancia
        precios_sustancia = []
        for prod in resultados:
            precio = obtener_precio_similar(prod)
            nombre_api = prod.get("productName", "")
            if precio and precio > 0:
                precios_sustancia.append((nombre_api, precio))

        if precios_sustancia:
            # Calcular precio promedio como referencia
            precio_promedio = sum(p for _, p in precios_sustancia) / len(precios_sustancia)
            precios_encontrados[sustancia] = precios_sustancia

            print(f"OK - {len(precios_sustancia)} resultados, precio ref: ${precio_promedio:.2f}")
            log.write(f"[OK] {sustancia}: {len(precios_sustancia)} resultados\n")
            for nombre_api, precio in precios_sustancia:
                log.write(f"     ${precio:.2f} - {nombre_api}\n")
        else:
            print("Sin precios")
            log.write(f"[X] {sustancia}: Resultados sin precio\n")
            no_encontrados += 1

        time.sleep(DELAY_ENTRE_BUSQUEDAS)

    # FASE 2: Actualizar base de datos
    print()
    print("=" * 60)
    print("  ACTUALIZANDO BASE DE DATOS...")
    print("=" * 60)

    log.write(f"\n{'=' * 60}\nACTUALIZACIONES:\n{'=' * 60}\n\n")

    c.execute("SELECT id, nombre, precio_venta, precio_costo FROM productos WHERE categoria='MEDICAMENTOS'")
    medicamentos = c.fetchall()

    for prod_id, nombre, precio_actual, costo_actual in medicamentos:
        sustancia = extraer_sustancia(nombre)
        if not sustancia or sustancia not in precios_encontrados:
            continue

        precios = precios_encontrados[sustancia]
        dosis, forma = extraer_presentacion(nombre)

        # Buscar el mejor match por dosis
        mejor_precio = None
        for nombre_api, precio_api in precios:
            if dosis and dosis.upper() in nombre_api.upper():
                mejor_precio = precio_api
                break

        # Si no hay match por dosis, usar el promedio
        if mejor_precio is None:
            mejor_precio = sum(p for _, p in precios) / len(precios)

        # Ajustar: tu farmacia no es Similares, aplicar margen
        # Similares vende generico barato; tu precio sera ~1.5x-2.5x segun presentacion
        piezas_match = re.search(r'CAJA\s+(\d+)\s+PIEZAS', nombre)
        num_piezas = int(piezas_match.group(1)) if piezas_match else 10

        # Precio por caja: precio unitario de Similares * (piezas_tu / piezas_similares)
        # Similares suele vender cajas de 10-20 piezas
        factor = num_piezas / 10.0
        nuevo_precio = round(mejor_precio * factor * 1.2, 2)  # 20% margen sobre Similares

        # No bajar de $15 ni exceder razonablemente
        nuevo_precio = max(15.0, min(nuevo_precio, 800.0))
        nuevo_costo = round(nuevo_precio * 0.6, 2)

        if abs(nuevo_precio - precio_actual) > 1.0:  # solo si hay cambio significativo
            c.execute("UPDATE productos SET precio_venta=?, precio_costo=? WHERE id=?",
                     (nuevo_precio, nuevo_costo, prod_id))
            actualizados += 1

            if actualizados <= 50:  # Mostrar los primeros 50
                print(f"  {nombre[:55]:<55} ${precio_actual:>8.2f} -> ${nuevo_precio:>8.2f}")

            log.write(f"  {nombre[:60]}: ${precio_actual:.2f} -> ${nuevo_precio:.2f}\n")

    conn.commit()
    conn.close()

    print()
    print("=" * 60)
    print(f"  RESUMEN")
    print("=" * 60)
    print(f"  Sustancias buscadas:    {total_sustancias}")
    print(f"  Con precio encontrado:  {len(precios_encontrados)}")
    print(f"  No encontrados:         {no_encontrados}")
    print(f"  Productos actualizados: {actualizados}")
    print(f"  Log guardado en:        {LOG_FILE}")
    print("=" * 60)

    log.write(f"\n{'=' * 60}\n")
    log.write(f"Sustancias buscadas: {total_sustancias}\n")
    log.write(f"Con precio: {len(precios_encontrados)}\n")
    log.write(f"Actualizados: {actualizados}\n")
    log.close()


if __name__ == "__main__":
    main()
