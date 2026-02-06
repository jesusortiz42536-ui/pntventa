"""
MARCAR MEDICAMENTOS CONTROLADOS SEGUN COFEPRIS
Identifica y marca productos controlados por sustancia activa.
Clasificacion basada en la Ley General de Salud Art. 226 y
listados de COFEPRIS de sustancias psicotropicas y estupefacientes.
"""
import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")

# =================================================================
# CATALOGO DE SUSTANCIAS CONTROLADAS POR COFEPRIS
# Basado en LGS Art. 226, Fracciones I-VI
# =================================================================

# ESTUPEFACIENTES (Receta especial con codigo de barras, no surtible mas de 1 vez)
ESTUPEFACIENTES = {
    "MORFINA": "Estupefaciente",
    "OXICODONA": "Estupefaciente",
    "OXIMORFONA": "Estupefaciente",
    "HIDROCODONA": "Estupefaciente",
    "HIDROMORFONA": "Estupefaciente",
    "FENTANILO": "Estupefaciente",
    "FENTANIL": "Estupefaciente",
    "FENTANYL": "Estupefaciente",
    "METADONA": "Estupefaciente",
    "BUPRENORFINA": "Estupefaciente",
    "PETIDINA": "Estupefaciente",
    "MEPERIDINA": "Estupefaciente",
    "SUFENTANILO": "Estupefaciente",
    "SUFENTANIL": "Estupefaciente",
    "ALFENTANILO": "Estupefaciente",
    "ALFENTANIL": "Estupefaciente",
    "REMIFENTANILO": "Estupefaciente",
    "REMIFENTANIL": "Estupefaciente",
    "TAPENTADOL": "Estupefaciente",
    "CODEINA": "Estupefaciente",
    "OPIOIDE": "Estupefaciente",
    "NALBUFINA": "Estupefaciente",
    "DEXTROPROPOXIFENO": "Estupefaciente",
    "PENTAZOCINA": "Estupefaciente",
}

# PSICOTROPICOS FRACCION II (Receta especial, alta restriccion)
PSICOTROPICOS_II = {
    "METILFENIDATO": "Psicotropico Fraccion II",
    "ANFETAMINA": "Psicotropico Fraccion II",
    "DEXANFETAMINA": "Psicotropico Fraccion II",
    "LISDEXANFETAMINA": "Psicotropico Fraccion II",
    "SECOBARBITAL": "Psicotropico Fraccion II",
    "AMOBARBITAL": "Psicotropico Fraccion II",
    "PENTOBARBITAL": "Psicotropico Fraccion II",
    "FLUNITRAZEPAM": "Psicotropico Fraccion II",
    "GAMMA HIDROXIBUTIRATO": "Psicotropico Fraccion II",
    "GHB": "Psicotropico Fraccion II",
    "ATOMOXETINA": "Psicotropico Fraccion II",
    "MODAFINILO": "Psicotropico Fraccion II",
    "ARMODAFINILO": "Psicotropico Fraccion II",
}

# PSICOTROPICOS FRACCION III (Receta medica retenida, surtible hasta 3 veces en 6 meses)
PSICOTROPICOS_III = {
    "FENOBARBITAL": "Psicotropico Fraccion III",
    "BUTALBITAL": "Psicotropico Fraccion III",
    "CLONAZEPAM": "Psicotropico Fraccion III",
    "DIAZEPAM": "Psicotropico Fraccion III",
    "ALPRAZOLAM": "Psicotropico Fraccion III",
    "LORAZEPAM": "Psicotropico Fraccion III",
    "BROMAZEPAM": "Psicotropico Fraccion III",
    "CLOBAZAM": "Psicotropico Fraccion III",
    "CLORAZEPATO": "Psicotropico Fraccion III",
    "CLOTIAZEPAM": "Psicotropico Fraccion III",
    "ESTAZOLAM": "Psicotropico Fraccion III",
    "FLUNITRAZEPAM": "Psicotropico Fraccion III",
    "FLURAZEPAM": "Psicotropico Fraccion III",
    "HALAZEPAM": "Psicotropico Fraccion III",
    "KETAZOLAM": "Psicotropico Fraccion III",
    "MEDAZEPAM": "Psicotropico Fraccion III",
    "MIDAZOLAM": "Psicotropico Fraccion III",
    "NITRAZEPAM": "Psicotropico Fraccion III",
    "OXAZEPAM": "Psicotropico Fraccion III",
    "PRAZEPAM": "Psicotropico Fraccion III",
    "TEMAZEPAM": "Psicotropico Fraccion III",
    "TRIAZOLAM": "Psicotropico Fraccion III",
    "ZOLPIDEM": "Psicotropico Fraccion III",
    "ZOPICLONA": "Psicotropico Fraccion III",
    "ZALEPLON": "Psicotropico Fraccion III",
    "ESZOPICLONA": "Psicotropico Fraccion III",
    "TRAMADOL": "Psicotropico Fraccion III",
    "TESTOSTERONA": "Psicotropico Fraccion III",
    "NANDROLONA": "Psicotropico Fraccion III",
    "OXANDROLONA": "Psicotropico Fraccion III",
    "ESTANOZOLOL": "Psicotropico Fraccion III",
    "BOLDENONA": "Psicotropico Fraccion III",
    "TREMBOLONA": "Psicotropico Fraccion III",
    "KETAMINA": "Psicotropico Fraccion III",
    "TIOPENTAL": "Psicotropico Fraccion III",
    "CARISOPRODOL": "Psicotropico Fraccion III",
}

# PSICOTROPICOS FRACCION IV (Receta medica retenida)
PSICOTROPICOS_IV = {
    "PREGABALINA": "Psicotropico Fraccion IV",
    "GABAPENTINA": "Psicotropico Fraccion IV",
    "CLORDIAZEPOXIDO": "Psicotropico Fraccion IV",
    "DIFENOXILATO": "Psicotropico Fraccion IV",
    "PEMOLINA": "Psicotropico Fraccion IV",
    "FENPROPOREX": "Psicotropico Fraccion IV",
    "MAZINDOL": "Psicotropico Fraccion IV",
    "SIBUTRAMINA": "Psicotropico Fraccion IV",
    "ORLISTAT": "Psicotropico Fraccion IV",
    "LOPERAMIDA": "Psicotropico Fraccion IV",
    "PROPILHEXEDRINA": "Psicotropico Fraccion IV",
    "PSEUDOEFEDRINA": "Psicotropico Fraccion IV",
    "DEXTROCLORFENAMINA": "Psicotropico Fraccion IV",
    "CLORFENIRAMINA": "Psicotropico Fraccion IV",
    "BUTORFANOL": "Psicotropico Fraccion IV",
    "NALOXONA": "Psicotropico Fraccion IV",
    "NALTREXONA": "Psicotropico Fraccion IV",
    "BACLOFENO": "Psicotropico Fraccion IV",
    "TIZANIDINA": "Psicotropico Fraccion IV",
    "CICLOBENZAPRINA": "Psicotropico Fraccion IV",
    "BUSPIRONA": "Psicotropico Fraccion IV",
    "MEPROBAMATO": "Psicotropico Fraccion IV",
    "HIDRATO DE CLORAL": "Psicotropico Fraccion IV",
    "CANNABIDIOL": "Psicotropico Fraccion IV",
    "DRONABINOL": "Psicotropico Fraccion IV",
    "QUETIAPINA": "Psicotropico Fraccion IV",
    "OLANZAPINA": "Psicotropico Fraccion IV",
    "RISPERIDONA": "Psicotropico Fraccion IV",
    "ARIPIPRAZOL": "Psicotropico Fraccion IV",
    "CLOZAPINA": "Psicotropico Fraccion IV",
    "HALOPERIDOL": "Psicotropico Fraccion IV",
    "LEVOMEPROMAZINA": "Psicotropico Fraccion IV",
    "CLORPROMAZINA": "Psicotropico Fraccion IV",
    "SULPIRIDA": "Psicotropico Fraccion IV",
    "TRIFLUOPERAZINA": "Psicotropico Fraccion IV",
    "LITIO": "Psicotropico Fraccion IV",
    "VALPROATO": "Psicotropico Fraccion IV",
    "ACIDO VALPROICO": "Psicotropico Fraccion IV",
    "CARBAMAZEPINA": "Psicotropico Fraccion IV",
    "LAMOTRIGINA": "Psicotropico Fraccion IV",
    "TOPIRAMATO": "Psicotropico Fraccion IV",
    "LEVETIRACETAM": "Psicotropico Fraccion IV",
    "FENITOINA": "Psicotropico Fraccion IV",
    "OXCARBAZEPINA": "Psicotropico Fraccion IV",
    "VIGABATRINA": "Psicotropico Fraccion IV",
    "LACOSAMIDA": "Psicotropico Fraccion IV",
    "FLUOXETINA": "Psicotropico Fraccion IV",
    "SERTRALINA": "Psicotropico Fraccion IV",
    "PAROXETINA": "Psicotropico Fraccion IV",
    "CITALOPRAM": "Psicotropico Fraccion IV",
    "ESCITALOPRAM": "Psicotropico Fraccion IV",
    "VENLAFAXINA": "Psicotropico Fraccion IV",
    "DESVENLAFAXINA": "Psicotropico Fraccion IV",
    "DULOXETINA": "Psicotropico Fraccion IV",
    "MIRTAZAPINA": "Psicotropico Fraccion IV",
    "TRAZODONA": "Psicotropico Fraccion IV",
    "BUPROPION": "Psicotropico Fraccion IV",
    "AMITRIPTILINA": "Psicotropico Fraccion IV",
    "IMIPRAMINA": "Psicotropico Fraccion IV",
    "CLOMIPRAMINA": "Psicotropico Fraccion IV",
    "NORTRIPTILINA": "Psicotropico Fraccion IV",
    "VORTIOXETINA": "Psicotropico Fraccion IV",
    "AGOMELATINA": "Psicotropico Fraccion IV",
    "DEXMEDETOMIDINA": "Psicotropico Fraccion IV",
    "PROPOFOL": "Psicotropico Fraccion IV",
    "SEVOFLURANO": "Psicotropico Fraccion IV",
    "DESFLURANO": "Psicotropico Fraccion IV",
    "ISOFLURANO": "Psicotropico Fraccion IV",
    "VARENICLINA": "Psicotropico Fraccion IV",
}

# PRECURSORES QUIMICOS
PRECURSORES = {
    "EFEDRINA": "Precursor Quimico",
    "ERGOTAMINA": "Precursor Quimico",
    "ACIDO LISERGICO": "Precursor Quimico",
}

# Sustancias que requieren receta pero NO son controlados estrictos
# (Fraccion IV LGS - receta retenida pero no especial)
RECETA_RETENIDA_NO_CONTROLADO = {
    "ANTIBIOTICO",  # Ya no aplica desde reforma, pero algunos aun lo piden
}


def buscar_sustancia_en_nombre(nombre_upper, sustancias_dict):
    """Busca si alguna sustancia del diccionario esta en el nombre del producto."""
    for sustancia, tipo in sustancias_dict.items():
        # Buscar la sustancia como palabra completa o al inicio de otra
        pattern = r'\b' + re.escape(sustancia)
        if re.search(pattern, nombre_upper):
            return sustancia, tipo
    return None, None


def main():
    print("=" * 70)
    print("  MARCAR MEDICAMENTOS CONTROLADOS - COFEPRIS")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Agregar columnas
    c.execute("PRAGMA table_info(productos)")
    columnas = [col[1] for col in c.fetchall()]

    for col_name, col_type in [("controlado", "INTEGER DEFAULT 0"),
                                ("tipo_control", "TEXT DEFAULT ''"),
                                ("requiere_receta_especial", "INTEGER DEFAULT 0")]:
        if col_name not in columnas:
            c.execute(f"ALTER TABLE productos ADD COLUMN {col_name} {col_type}")
            print(f"    + Columna '{col_name}' agregada")
    conn.commit()

    # Resetear valores previos
    c.execute("UPDATE productos SET controlado = 0, tipo_control = '', requiere_receta_especial = 0")
    conn.commit()

    # Obtener todos los productos
    c.execute("SELECT id, nombre FROM productos")
    productos = c.fetchall()
    print(f"\n    Analizando {len(productos)} productos...")

    # Contadores
    stats = {
        "Estupefaciente": 0,
        "Psicotropico Fraccion II": 0,
        "Psicotropico Fraccion III": 0,
        "Psicotropico Fraccion IV": 0,
        "Precursor Quimico": 0,
    }
    detalles = {k: [] for k in stats}
    total_controlados = 0

    # Orden de busqueda: estupefacientes primero (mayor restriccion)
    catalogos = [
        (ESTUPEFACIENTES, True),
        (PSICOTROPICOS_II, True),
        (PSICOTROPICOS_III, True),
        (PSICOTROPICOS_IV, True),
        (PRECURSORES, True),
    ]

    for prod_id, nombre in productos:
        if not nombre:
            continue
        nombre_upper = nombre.upper()

        encontrado = False
        for catalogo, requiere_receta in catalogos:
            sustancia, tipo = buscar_sustancia_en_nombre(nombre_upper, catalogo)
            if sustancia:
                receta_esp = 1 if tipo in ("Estupefaciente",
                                            "Psicotropico Fraccion II",
                                            "Psicotropico Fraccion III") else 0
                c.execute("""UPDATE productos SET
                             controlado = 1,
                             tipo_control = ?,
                             requiere_receta_especial = ?
                             WHERE id = ?""",
                         (tipo, receta_esp, prod_id))
                stats[tipo] += 1
                total_controlados += 1
                if len(detalles[tipo]) < 20:
                    detalles[tipo].append((nombre[:60], sustancia))
                encontrado = True
                break  # Solo la primera coincidencia (mayor restriccion)

    conn.commit()

    # ================================================================
    # REPORTE
    # ================================================================
    print(f"\n{'=' * 70}")
    print(f"  REPORTE DE MEDICAMENTOS CONTROLADOS")
    print(f"{'=' * 70}")
    print(f"  Total productos analizados:  {len(productos)}")
    print(f"  Total controlados:           {total_controlados}")
    print(f"  No controlados:              {len(productos) - total_controlados}")

    print(f"\n  DESGLOSE POR CATEGORIA:")
    print(f"  {'-'*60}")
    for tipo, count in stats.items():
        receta = "SI" if tipo in ("Estupefaciente",
                                   "Psicotropico Fraccion II",
                                   "Psicotropico Fraccion III") else "NO"
        print(f"  {tipo:<30} {count:>5} productos   Receta especial: {receta}")

    # Mostrar ejemplos por categoria
    for tipo, ejemplos in detalles.items():
        if ejemplos:
            print(f"\n  --- {tipo} ({stats[tipo]} productos) ---")
            for nombre, sustancia in ejemplos[:10]:
                print(f"    [{sustancia}] {nombre}")

    # Requisitos de receta
    c.execute("SELECT COUNT(*) FROM productos WHERE requiere_receta_especial = 1")
    con_receta = c.fetchone()[0]
    print(f"\n  RESUMEN DE RECETAS:")
    print(f"  {'-'*60}")
    print(f"  Requieren receta especial (codigo barras): {con_receta}")
    print(f"  Requieren receta retenida:                 {stats['Psicotropico Fraccion IV']}")
    print(f"  Venta libre (resto):                       {len(productos) - total_controlados}")

    # Sustancias mas frecuentes
    print(f"\n  SUSTANCIAS CONTROLADAS MAS FRECUENTES:")
    print(f"  {'-'*60}")
    todos_catalogos = {}
    todos_catalogos.update(ESTUPEFACIENTES)
    todos_catalogos.update(PSICOTROPICOS_II)
    todos_catalogos.update(PSICOTROPICOS_III)
    todos_catalogos.update(PSICOTROPICOS_IV)
    todos_catalogos.update(PRECURSORES)

    conteo_sustancias = {}
    for prod_id, nombre in productos:
        if not nombre:
            continue
        nombre_upper = nombre.upper()
        for sustancia in todos_catalogos:
            pattern = r'\b' + re.escape(sustancia)
            if re.search(pattern, nombre_upper):
                conteo_sustancias[sustancia] = conteo_sustancias.get(sustancia, 0) + 1
                break

    top_sustancias = sorted(conteo_sustancias.items(), key=lambda x: x[1], reverse=True)[:25]
    for sustancia, count in top_sustancias:
        tipo = todos_catalogos[sustancia]
        print(f"    {sustancia:<25} {count:>5} productos  ({tipo})")

    conn.close()

    print(f"\n{'=' * 70}")
    print(f"  MEDICAMENTOS CONTROLADOS MARCADOS EXITOSAMENTE")
    print(f"  Columnas: controlado, tipo_control, requiere_receta_especial")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
