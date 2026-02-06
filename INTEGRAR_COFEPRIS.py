"""
INTEGRAR CATALOGO COFEPRIS
Descarga PDFs oficiales de COFEPRIS con registros sanitarios de medicamentos,
extrae los datos, cruza con la BD existente y genera CATALOGO_COMPLETO_COFEPRIS.xlsx
"""
import sqlite3
import os
import re
import ssl
import random
import urllib.request
import pdfplumber
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "CATALOGO_COMPLETO_COFEPRIS.xlsx")
PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cofepris_pdfs")

random.seed(888)

# SSL context for downloads
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# URLs de PDFs de COFEPRIS - Alopaticos por anio (URLs correctas de gob.mx)
URLS_ALOPATICOS = {
    2001: "https://www.gob.mx/cms/uploads/attachment/file/145554/regalopa2001.pdf",
    2002: "https://www.gob.mx/cms/uploads/attachment/file/145556/regalopa2002.pdf",
    2003: "https://www.gob.mx/cms/uploads/attachment/file/145560/regalopa2003.pdf",
    2004: "https://www.gob.mx/cms/uploads/attachment/file/145561/regalopa2004.pdf",
    2005: "https://www.gob.mx/cms/uploads/attachment/file/145562/Regalopa2005.pdf",
    2006: "https://www.gob.mx/cms/uploads/attachment/file/145564/Alopaticos2006.pdf",
    2007: "https://www.gob.mx/cms/uploads/attachment/file/145566/Alop_ticos2007.pdf",
    2008: "https://www.gob.mx/cms/uploads/attachment/file/145567/Alop_ticos2008.pdf",
    2009: "https://www.gob.mx/cms/uploads/attachment/file/145568/Alop_ticos2009.pdf",
    2010: "https://www.gob.mx/cms/uploads/attachment/file/145569/Alop_ticos2010.pdf",
    2011: "https://www.gob.mx/cms/uploads/attachment/file/145570/Alop_ticos_2011.pdf",
    2012: "https://www.gob.mx/cms/uploads/attachment/file/145572/Alop_ticos_2012-2.pdf",
    2013: "https://www.gob.mx/cms/uploads/attachment/file/145573/Alop_ticos_2013.pdf",
    2014: "https://www.gob.mx/cms/uploads/attachment/file/145574/Alop_ticos_2014.pdf",
    2015: "https://www.gob.mx/cms/uploads/attachment/file/303036/Alop_ticos_2015.pdf",
    2016: "https://www.gob.mx/cms/uploads/attachment/file/250044/Alop_ticos_2016.pdf",
    2017: "https://www.gob.mx/cms/uploads/attachment/file/326787/Alop_ticos_2017.pdf",
    2018: "https://www.gob.mx/cms/uploads/attachment/file/436142/Alop_ticos_2018.pdf",
    2019: "https://www.gob.mx/cms/uploads/attachment/file/526719/Alop_ticos_2019.pdf",
    2020: "https://www.gob.mx/cms/uploads/attachment/file/605953/Alop_ticos_2020.pdf",
    2021: "https://www.gob.mx/cms/uploads/attachment/file/789641/Alop_ticos_2021.pdf",
    2022: "https://www.gob.mx/cms/uploads/attachment/file/825334/Alop_ticos_2022.pdf",
    2023: "https://www.gob.mx/cms/uploads/attachment/file/879176/Alop_ticos_2023.pdf",
    2024: "https://www.gob.mx/cms/uploads/attachment/file/969390/Alop_ticos_2024.pdf",
    2025: "https://www.gob.mx/cms/uploads/attachment/file/1045115/Alop_ticos_2025.pdf",
}

# URLs de Revocados y Cancelados (solo los mas recientes disponibles)
URLS_REVOCADOS = {
    2025: "https://www.gob.mx/cms/uploads/attachment/file/998235/Registros_Revocados_2025.pdf",
}

URLS_CANCELADOS = {
    2025: "https://www.gob.mx/cms/uploads/attachment/file/998238/Registros_Cancelados_2025.pdf",
}

MARGENES = {
    "precio_fahorro":     (1.05, 1.20),
    "precio_guadalajara": (1.10, 1.25),
    "precio_sanpablo":    (1.15, 1.35),
    "precio_benavides":   (1.12, 1.28),
    "precio_walmart":     (1.03, 1.15),
    "precio_sams":        (0.95, 1.10),
    "precio_moderna":     (1.02, 1.12),
}

# Precios base estimados por forma farmaceutica
PRECIOS_BASE = {
    "TABLETA": (25, 180),
    "COMPRIMIDO": (25, 180),
    "CAPSULA": (30, 200),
    "SOLUCION": (40, 350),
    "SUSPENSION": (45, 250),
    "JARABE": (50, 200),
    "CREMA": (60, 280),
    "GEL": (55, 250),
    "UNGÜENTO": (50, 220),
    "POLVO": (35, 300),
    "INYECTABLE": (80, 500),
    "SUPOSITORIO": (40, 180),
    "OVULO": (50, 200),
    "AEROSOL": (120, 400),
    "PARCHE": (150, 600),
    "GOTAS": (60, 250),
    "IMPLANTE": (500, 3000),
    "EMULSION": (80, 300),
}


def descargar_pdf(url, filename):
    """Descarga un PDF si no existe."""
    filepath = os.path.join(PDF_DIR, filename)
    if os.path.exists(filepath):
        return filepath
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, context=CTX, timeout=30)
        data = resp.read()
        with open(filepath, 'wb') as f:
            f.write(data)
        return filepath
    except Exception as e:
        print(f"    ERROR descargando {filename}: {e}")
        return None


def extraer_registros_pdf(filepath):
    """Extrae registros sanitarios de un PDF de COFEPRIS."""
    registros = []
    try:
        pdf = pdfplumber.open(filepath)
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 6:
                        continue
                    reg = row[0]
                    if not reg or not isinstance(reg, str):
                        continue
                    # Limpiar saltos de linea
                    reg = reg.replace('\n', ' ').strip()
                    # Verificar que es un registro sanitario (patrón: NNN[M/SSA]YYYY)
                    if not re.match(r'\d{2,4}M?\d{0,4}', reg):
                        continue
                    # Ignorar encabezados
                    if 'Registro' in reg or 'sanitario' in reg:
                        continue

                    titular = (row[1] or "").replace('\n', ' ').strip()
                    nombre_dist = (row[2] or "").replace('\n', ' ').strip()
                    denominacion = (row[3] or "").replace('\n', ' ').strip()
                    clasificacion = (row[4] or "").replace('\n', ' ').strip()
                    forma = (row[5] or "").replace('\n', ' ').strip()
                    vigencia = (row[6] or "").replace('\n', ' ').strip() if len(row) > 6 else ""

                    if nombre_dist and denominacion:
                        registros.append({
                            "registro_sanitario": reg,
                            "titular": titular,
                            "nombre_distintivo": nombre_dist.upper(),
                            "denominacion_generica": denominacion.upper(),
                            "clasificacion": clasificacion,
                            "forma_farmaceutica": forma.upper(),
                            "vigencia": vigencia,
                            "estatus": "VIGENTE",
                        })
        pdf.close()
    except Exception as e:
        print(f"    ERROR procesando {filepath}: {e}")
    return registros


def generar_precio_estimado(forma, denominacion):
    """Genera precio estimado basado en forma farmacéutica."""
    forma_upper = forma.upper() if forma else ""
    precio_range = PRECIOS_BASE.get("TABLETA")  # default

    for key, rng in PRECIOS_BASE.items():
        if key in forma_upper:
            precio_range = rng
            break

    # Ajustar por tipo de medicamento
    denom_upper = denominacion.upper() if denominacion else ""
    factor = 1.0
    if any(k in denom_upper for k in ["TRASTUZUMAB", "BEVACIZUMAB", "RITUXIMAB",
                                       "PEMBROLIZUMAB", "NIVOLUMAB", "ADALIMUMAB"]):
        factor = 15.0  # Biologicos son muy caros
    elif any(k in denom_upper for k in ["CARBOPLATINO", "CISPLATINO", "DOCETAXEL",
                                         "PACLITAXEL", "DOXORRUBICINA"]):
        factor = 5.0  # Quimioterapia
    elif any(k in denom_upper for k in ["INSULINA", "SOMATROPINA", "ERITROPOYETINA"]):
        factor = 4.0  # Hormonas/biologicos
    elif any(k in denom_upper for k in ["VACUNA"]):
        factor = 3.0

    precio = round(random.uniform(*precio_range) * factor, 2)
    return precio


def generar_precios_multi(precio_base):
    """Genera precios para las 8 farmacias."""
    ps = float(precio_base)
    precios = {"precio_similares": ps}
    for col, (lo, hi) in MARGENES.items():
        precios[col] = round(ps * random.uniform(lo, hi), 2)
    return precios


def buscar_producto_bd(c, nombre_dist, denominacion):
    """Busca un producto en la BD por nombre o sustancia."""
    # 1) Match exacto nombre distintivo
    c.execute("SELECT id, nombre FROM productos WHERE UPPER(nombre) LIKE ?",
              (f"%{nombre_dist}%",))
    r = c.fetchone()
    if r:
        return r[0], r[1]

    # 2) Match por denominacion generica (sustancia activa)
    if denominacion and len(denominacion) > 3:
        # Tomar primera sustancia si hay combinacion
        primera = denominacion.split('/')[0].strip()
        if len(primera) > 3:
            c.execute("SELECT id, nombre FROM productos WHERE UPPER(nombre) LIKE ? LIMIT 1",
                      (f"%{primera}%",))
            r = c.fetchone()
            if r:
                return r[0], r[1]

    return None, None


def main():
    print("=" * 70)
    print("  INTEGRAR CATALOGO COFEPRIS")
    print("  Descarga y procesamiento de registros sanitarios oficiales")
    print("=" * 70)

    # Crear directorio para PDFs
    os.makedirs(PDF_DIR, exist_ok=True)

    # ================================================================
    # FASE 1: Descargar PDFs
    # ================================================================
    print("\n  FASE 1: Descargando PDFs de COFEPRIS...")

    todos_registros = []
    registros_revocados = set()
    registros_cancelados = set()

    # Descargar alopaticos (todos los años disponibles)
    for year, url in sorted(URLS_ALOPATICOS.items()):
        filename = f"alopaticos_{year}.pdf"
        print(f"    Descargando Alopaticos {year}...", end=" ")
        filepath = descargar_pdf(url, filename)
        if filepath:
            regs = extraer_registros_pdf(filepath)
            for r in regs:
                r["year"] = year
            todos_registros.extend(regs)
            print(f"{len(regs)} registros")
        else:
            print("FALLO")

    # Descargar revocados
    for year, url in sorted(URLS_REVOCADOS.items()):
        filename = f"revocados_{year}.pdf"
        print(f"    Descargando Revocados {year}...", end=" ")
        filepath = descargar_pdf(url, filename)
        if filepath:
            regs = extraer_registros_pdf(filepath)
            for r in regs:
                registros_revocados.add(r["registro_sanitario"])
            print(f"{len(regs)} registros")
        else:
            print("FALLO")

    # Descargar cancelados
    for year, url in sorted(URLS_CANCELADOS.items()):
        filename = f"cancelados_{year}.pdf"
        print(f"    Descargando Cancelados {year}...", end=" ")
        filepath = descargar_pdf(url, filename)
        if filepath:
            regs = extraer_registros_pdf(filepath)
            for r in regs:
                registros_cancelados.add(r["registro_sanitario"])
            print(f"{len(regs)} registros")
        else:
            print("FALLO")

    print(f"\n  Total registros extraidos: {len(todos_registros)}")
    print(f"  Registros revocados: {len(registros_revocados)}")
    print(f"  Registros cancelados: {len(registros_cancelados)}")

    # Marcar estatus
    for reg in todos_registros:
        rs = reg["registro_sanitario"]
        if rs in registros_revocados:
            reg["estatus"] = "REVOCADO"
        elif rs in registros_cancelados:
            reg["estatus"] = "CANCELADO"

    # Deduplicar por registro sanitario (mantener el más reciente)
    registros_unicos = {}
    for reg in todos_registros:
        rs = reg["registro_sanitario"]
        if rs not in registros_unicos or reg.get("year", 0) > registros_unicos[rs].get("year", 0):
            registros_unicos[rs] = reg

    print(f"  Registros unicos: {len(registros_unicos)}")

    # ================================================================
    # FASE 2: Agregar columna registro_sanitario a BD
    # ================================================================
    print("\n  FASE 2: Actualizando base de datos...")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Verificar si existe columna registro_sanitario
    c.execute("PRAGMA table_info(productos)")
    columnas = [col[1] for col in c.fetchall()]
    if "registro_sanitario" not in columnas:
        c.execute("ALTER TABLE productos ADD COLUMN registro_sanitario TEXT DEFAULT ''")
        print("    Columna 'registro_sanitario' agregada")
    if "estatus_cofepris" not in columnas:
        c.execute("ALTER TABLE productos ADD COLUMN estatus_cofepris TEXT DEFAULT ''")
        print("    Columna 'estatus_cofepris' agregada")
    if "titular_registro" not in columnas:
        c.execute("ALTER TABLE productos ADD COLUMN titular_registro TEXT DEFAULT ''")
        print("    Columna 'titular_registro' agregada")
    if "forma_farmaceutica" not in columnas:
        c.execute("ALTER TABLE productos ADD COLUMN forma_farmaceutica TEXT DEFAULT ''")
        print("    Columna 'forma_farmaceutica' agregada")
    if "clasificacion_cofepris" not in columnas:
        c.execute("ALTER TABLE productos ADD COLUMN clasificacion_cofepris TEXT DEFAULT ''")
        print("    Columna 'clasificacion_cofepris' agregada")

    conn.commit()

    c.execute("SELECT COUNT(*) FROM productos")
    total_original = c.fetchone()[0]
    print(f"    Productos actuales en BD: {total_original}")

    # ================================================================
    # FASE 3: Cruzar registros COFEPRIS con BD
    # ================================================================
    print("\n  FASE 3: Cruzando registros con catalogo existente...")

    matched = 0
    nuevos = 0
    sin_match = 0
    revocados_encontrados = 0

    c.execute("SELECT MAX(id) FROM productos")
    next_id = (c.fetchone()[0] or 0) + 1

    registros_nuevos = []

    for rs, reg in registros_unicos.items():
        nombre_dist = reg["nombre_distintivo"]
        denominacion = reg["denominacion_generica"]
        estatus = reg["estatus"]

        prod_id, nombre_bd = buscar_producto_bd(c, nombre_dist, denominacion)

        if prod_id:
            # Actualizar producto existente con datos COFEPRIS
            c.execute("""UPDATE productos SET
                         registro_sanitario = ?,
                         estatus_cofepris = ?,
                         titular_registro = ?,
                         forma_farmaceutica = ?,
                         clasificacion_cofepris = ?
                         WHERE id = ?""",
                     (rs, estatus, reg["titular"], reg["forma_farmaceutica"],
                      reg["clasificacion"], prod_id))
            matched += 1
            if estatus in ("REVOCADO", "CANCELADO"):
                revocados_encontrados += 1
        else:
            # Solo agregar si esta vigente
            if estatus == "VIGENTE":
                registros_nuevos.append(reg)
                nuevos += 1
            else:
                sin_match += 1

    # Agregar productos nuevos
    for reg in registros_nuevos:
        nombre = f"{reg['nombre_distintivo']} ({reg['denominacion_generica']})"
        codigo = f"COF{next_id:06d}"

        # Determinar categoria
        cat = "MEDICAMENTOS"
        denom = reg["denominacion_generica"].upper()
        if any(k in denom for k in ["CARBOPLATINO", "CISPLATINO", "DOCETAXEL",
                                     "DOXORRUBICINA", "PACLITAXEL", "FLUOROURACILO",
                                     "GEMCITABINA", "IFOSFAMIDA", "METOTREXATO",
                                     "BLEOMICINA", "VINCRISTINA"]):
            cat = "QUIMIOTERAPIA"
        elif any(k in denom for k in ["TRASTUZUMAB", "BEVACIZUMAB", "RITUXIMAB",
                                       "PEMBROLIZUMAB", "NIVOLUMAB"]):
            cat = "INMUNOTERAPIA"
        elif any(k in denom for k in ["PROPOFOL", "SEVOFLURANO", "KETAMINA",
                                       "LIDOCAINA", "BUPIVACAINA", "ROPIVACAINA"]):
            cat = "ANESTESICOS"
        elif any(k in denom for k in ["HEPARINA", "ALBUMINA", "CLORURO DE SODIO",
                                       "GLUCOSA", "SOLUCION"]):
            cat = "SOLUCIONES IV"

        # Generar precio estimado
        precio_venta = generar_precio_estimado(reg["forma_farmaceutica"],
                                                reg["denominacion_generica"])
        precio_costo = round(precio_venta * 0.55, 2)
        precios = generar_precios_multi(precio_venta)

        lote = f"COF{random.randint(20250101, 20261231)}"
        cad = (datetime.now() + timedelta(days=random.randint(365, 1095))).strftime("%Y-%m-%d")
        stock = random.randint(5, 50)

        c.execute("""INSERT INTO productos
            (id, codigo, nombre, categoria, laboratorio, precio_costo, precio_venta,
             aplica_iva, stock, lote, caducidad,
             precio_similares, precio_fahorro, precio_guadalajara, precio_sanpablo,
             precio_benavides, precio_walmart, precio_sams, precio_moderna,
             registro_sanitario, estatus_cofepris, titular_registro,
             forma_farmaceutica, clasificacion_cofepris)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (next_id, codigo, nombre, cat, reg["titular"],
             precio_costo, precio_venta, 1, stock, lote, cad,
             precios["precio_similares"],
             precios["precio_fahorro"],
             precios["precio_guadalajara"],
             precios["precio_sanpablo"],
             precios["precio_benavides"],
             precios["precio_walmart"],
             precios["precio_sams"],
             precios["precio_moderna"],
             reg["registro_sanitario"], "VIGENTE", reg["titular"],
             reg["forma_farmaceutica"], reg["clasificacion"]))
        next_id += 1

    conn.commit()

    # ================================================================
    # FASE 4: Marcar productos sin registro sanitario
    # ================================================================
    print("\n  FASE 4: Identificando productos sin registro sanitario...")

    c.execute("SELECT COUNT(*) FROM productos WHERE registro_sanitario IS NULL OR registro_sanitario = ''")
    sin_registro = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM productos WHERE estatus_cofepris = 'VIGENTE'")
    vigentes = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM productos WHERE estatus_cofepris IN ('REVOCADO', 'CANCELADO')")
    no_vigentes = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM productos")
    total_final = c.fetchone()[0]

    # ================================================================
    # RESUMEN
    # ================================================================
    print(f"\n{'=' * 70}")
    print(f"  RESUMEN DE INTEGRACION COFEPRIS")
    print(f"{'=' * 70}")
    print(f"  Registros COFEPRIS procesados:  {len(registros_unicos):>6}")
    print(f"  {'-'*50}")
    print(f"  Productos actualizados (match): {matched:>6}")
    print(f"  Productos nuevos agregados:     {nuevos:>6}")
    print(f"  Revocados/Cancelados en BD:     {revocados_encontrados:>6}")
    print(f"  Sin match (no vigentes):        {sin_match:>6}")
    print(f"  {'-'*50}")
    print(f"  Catalogo original:              {total_original:>6} productos")
    print(f"  TOTAL FINAL:                    {total_final:>6} productos")
    print(f"  {'-'*50}")
    print(f"  Con registro sanitario:         {vigentes + no_vigentes:>6}")
    print(f"  Sin registro sanitario:         {sin_registro:>6}")
    print(f"  Vigentes COFEPRIS:              {vigentes:>6}")
    print(f"  No vigentes (revocado/cancel):  {no_vigentes:>6}")
    print(f"{'=' * 70}")

    conn.close()

    # ================================================================
    # FASE 5: Generar Excel
    # ================================================================
    print(f"\n  FASE 5: Generando Excel COFEPRIS...")

    import EXPORTAR_EXCEL
    EXPORTAR_EXCEL.OUTPUT = OUTPUT
    EXPORTAR_EXCEL.main()

    size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"\n{'=' * 70}")
    print(f"  ARCHIVO GENERADO: {os.path.basename(OUTPUT)}")
    print(f"  TAMANO: {size_mb:.1f} MB")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
