"""
AGREGAR PRECIOS MAYORISTAS DE 13 DISTRIBUIDORES FARMACEUTICOS
Agrega columnas de precios mayoristas estimados a la BD.

Distribuidores y sus margenes sobre precio costo estimado:
- GRANDES (mejores precios por volumen):
  NADRO, Casa Saba, Marzam, Farmacos Especializados
- MEDIANOS:
  Pharmamigo, Surtifarma, Vicma, San Amerx
- ESPECIALIZADOS/REGIONALES:
  Medmodt, Generimax, Profam, Farmadepot, Efra
"""
import sqlite3
import os
import random

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")

random.seed(999)

# Margenes mayoristas como fraccion del precio_similares (retail).
# Mayoristas venden por debajo del retail: 60-85% del precio Similares.
# Grandes distribuidores tienen mejores precios que los pequenos.
DISTRIBUIDORES = {
    # GRANDES - Precio mas bajo (60-72% del retail Similares)
    "precio_nadro": {
        "nombre": "NADRO",
        "tipo": "GRANDE",
        "rango": (0.60, 0.70),
        "metodo": "ESTIMADO",
        "notas": "Mayor distribuidor de Mexico. Sin API publica, requiere cuenta comercial en nadro.com.mx",
    },
    "precio_casasaba": {
        "nombre": "CASA SABA",
        "tipo": "GRANDE",
        "rango": (0.61, 0.71),
        "metodo": "ESTIMADO",
        "notas": "Segundo mayor distribuidor. Portal B2B cerrado, sin acceso publico",
    },
    "precio_marzam": {
        "nombre": "MARZAM",
        "tipo": "GRANDE",
        "rango": (0.62, 0.72),
        "metodo": "ESTIMADO",
        "notas": "Tercer distribuidor nacional. Catalogo solo para clientes registrados en marzam.com.mx",
    },
    "precio_farmesp": {
        "nombre": "FARMACOS ESPECIALIZADOS",
        "tipo": "GRANDE",
        "rango": (0.63, 0.73),
        "metodo": "ESTIMADO",
        "notas": "Especializado en medicamentos de alta especialidad. Portal cerrado",
    },
    # MEDIANOS - Precio intermedio (68-78% del retail)
    "precio_pharmamigo": {
        "nombre": "PHARMAMIGO",
        "tipo": "MEDIANO",
        "rango": (0.68, 0.77),
        "metodo": "ESTIMADO",
        "notas": "Distribuidor mediano. Sin sitio web publico con precios",
    },
    "precio_surtifarma": {
        "nombre": "SURTIFARMA",
        "tipo": "MEDIANO",
        "rango": (0.67, 0.76),
        "metodo": "ESTIMADO",
        "notas": "Distribuidor mediano nacional. Catalogo solo para farmacias afiliadas",
    },
    "precio_vicma": {
        "nombre": "VICMA",
        "tipo": "MEDIANO",
        "rango": (0.69, 0.78),
        "metodo": "ESTIMADO",
        "notas": "Distribuidor mediano. Sin API ni catalogo descargable",
    },
    "precio_sanamerx": {
        "nombre": "SAN AMERX",
        "tipo": "MEDIANO",
        "rango": (0.68, 0.77),
        "metodo": "ESTIMADO",
        "notas": "Distribuidor mediano. Acceso solo con cuenta comercial",
    },
    # ESPECIALIZADOS/REGIONALES - Precio mas alto (73-85% del retail)
    "precio_medmodt": {
        "nombre": "MEDMODT",
        "tipo": "ESPECIALIZADO",
        "rango": (0.73, 0.82),
        "metodo": "ESTIMADO",
        "notas": "Distribuidor especializado/regional. Sin presencia web publica",
    },
    "precio_generimax": {
        "nombre": "GENERIMAX",
        "tipo": "ESPECIALIZADO",
        "rango": (0.65, 0.75),
        "metodo": "ESTIMADO",
        "notas": "Especializado en genericos, precios competitivos. Sin API publica",
    },
    "precio_profam": {
        "nombre": "PROFAM",
        "tipo": "ESPECIALIZADO",
        "rango": (0.74, 0.83),
        "metodo": "ESTIMADO",
        "notas": "Distribuidor regional. Sin catalogo online",
    },
    "precio_farmadepot": {
        "nombre": "FARMADEPOT",
        "tipo": "ESPECIALIZADO",
        "rango": (0.72, 0.81),
        "metodo": "ESTIMADO",
        "notas": "Distribuidor tipo depot/almacen. Sin API publica",
    },
    "precio_efra": {
        "nombre": "EFRA",
        "tipo": "ESPECIALIZADO",
        "rango": (0.75, 0.85),
        "metodo": "ESTIMADO",
        "notas": "Distribuidor regional. Sin sitio web con precios",
    },
}

# Ajustes por categoria de producto
AJUSTE_CATEGORIA = {
    "QUIMIOTERAPIA": 0.92,       # Oncologicos: margen mas estrecho
    "INMUNOTERAPIA": 0.90,       # Biologicos: margen estrecho
    "TERAPIA DIRIGIDA": 0.91,
    "ANESTESICOS": 0.95,
    "SOLUCIONES IV": 0.88,       # Alto volumen, bajo margen
    "VASOPRESORES": 0.93,
    "SEDANTES UCI": 0.94,
    "ELECTROLITOS IV": 0.87,
    "HORMONOTERAPIA": 0.92,
    "SOPORTE ONCOLOGICO": 0.93,
    "ANTIBIOTICOS IV": 0.94,
    "ANALGESICOS HOSPITALARIOS": 0.95,
    "RELAJANTES MUSCULARES": 0.95,
    "MEDICAMENTOS": 1.00,        # Sin ajuste
    "HIGIENE": 1.05,             # Margen mayor en higiene
}


def main():
    print("=" * 70)
    print("  AGREGAR PRECIOS MAYORISTAS - 13 DISTRIBUIDORES")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Verificar columnas existentes
    c.execute("PRAGMA table_info(productos)")
    columnas_existentes = [col[1] for col in c.fetchall()]

    # Agregar columnas nuevas
    columnas_nuevas = 0
    for col in DISTRIBUIDORES:
        if col not in columnas_existentes:
            c.execute(f"ALTER TABLE productos ADD COLUMN {col} REAL DEFAULT 0")
            columnas_nuevas += 1
            print(f"    + Columna '{col}' agregada")
        else:
            print(f"    = Columna '{col}' ya existe")
    conn.commit()

    if columnas_nuevas > 0:
        print(f"\n    {columnas_nuevas} columnas nuevas creadas")
    else:
        print(f"\n    Todas las columnas ya existian, se actualizaran los precios")

    # Obtener todos los productos
    c.execute("""SELECT id, nombre, categoria, precio_venta, precio_similares,
                        precio_costo FROM productos""")
    productos = c.fetchall()
    total = len(productos)
    print(f"\n    Procesando {total} productos...")

    actualizados = 0
    sin_precio_ref = 0

    for prod_id, nombre, categoria, precio_venta, precio_sim, precio_costo in productos:
        # Usar precio_similares como referencia, o precio_venta si no hay
        precio_ref = precio_sim or precio_venta or 0
        if not precio_ref or precio_ref <= 0:
            sin_precio_ref += 1
            continue

        # Obtener factor de ajuste por categoria
        cat = (categoria or "MEDICAMENTOS").upper()
        ajuste_cat = AJUSTE_CATEGORIA.get(cat, 1.0)

        # Calcular precio para cada distribuidor
        valores = {}
        for col, info in DISTRIBUIDORES.items():
            lo, hi = info["rango"]
            # Precio mayorista = precio_retail * factor_mayorista * ajuste_categoria
            factor = random.uniform(lo, hi) * ajuste_cat
            precio_may = round(float(precio_ref) * factor, 2)
            # Asegurar que el precio mayorista sea al menos el precio_costo
            if precio_costo and precio_costo > 0:
                precio_may = max(precio_may, round(float(precio_costo) * 1.02, 2))
            valores[col] = precio_may

        # Actualizar BD
        set_clause = ", ".join(f"{col} = ?" for col in valores)
        vals = list(valores.values()) + [prod_id]
        c.execute(f"UPDATE productos SET {set_clause} WHERE id = ?", vals)
        actualizados += 1

        if actualizados % 10000 == 0:
            print(f"      ... {actualizados}/{total} productos")
            conn.commit()

    conn.commit()

    # ================================================================
    # REPORTE DE METODOS
    # ================================================================
    print(f"\n{'=' * 70}")
    print(f"  REPORTE DE METODOS POR DISTRIBUIDOR")
    print(f"{'=' * 70}")
    print(f"  {'Distribuidor':<25} {'Tipo':<15} {'Metodo':<12} {'Rango %'}")
    print(f"  {'-'*70}")

    for col, info in DISTRIBUIDORES.items():
        lo_pct = int(info["rango"][0] * 100)
        hi_pct = int(info["rango"][1] * 100)
        print(f"  {info['nombre']:<25} {info['tipo']:<15} {info['metodo']:<12} {lo_pct}-{hi_pct}% del retail")

    print(f"\n  NOTAS POR DISTRIBUIDOR:")
    for col, info in DISTRIBUIDORES.items():
        print(f"    {info['nombre']}: {info['notas']}")

    # ================================================================
    # RESUMEN
    # ================================================================
    c.execute("SELECT COUNT(*) FROM productos")
    total_bd = c.fetchone()[0]

    # Verificar precios promedio por distribuidor
    print(f"\n{'=' * 70}")
    print(f"  RESUMEN DE PRECIOS MAYORISTAS")
    print(f"{'=' * 70}")
    print(f"  Productos actualizados: {actualizados}")
    print(f"  Sin precio referencia:  {sin_precio_ref}")
    print(f"  Total en BD:            {total_bd}")

    print(f"\n  {'Distribuidor':<25} {'Promedio':>10} {'Min':>10} {'Max':>10}")
    print(f"  {'-'*60}")

    for col, info in DISTRIBUIDORES.items():
        c.execute(f"SELECT AVG({col}), MIN({col}), MAX({col}) FROM productos WHERE {col} > 0")
        avg_p, min_p, max_p = c.fetchone()
        if avg_p:
            print(f"  {info['nombre']:<25} ${avg_p:>9.2f} ${min_p:>9.2f} ${max_p:>9.2f}")

    # Comparativa: precio retail vs mayorista promedio
    print(f"\n  COMPARATIVA RETAIL vs MAYORISTA:")
    c.execute("SELECT AVG(precio_similares) FROM productos WHERE precio_similares > 0")
    avg_retail = c.fetchone()[0] or 0
    c.execute("SELECT AVG(precio_nadro) FROM productos WHERE precio_nadro > 0")
    avg_nadro = c.fetchone()[0] or 0
    if avg_retail > 0 and avg_nadro > 0:
        ahorro = ((avg_retail - avg_nadro) / avg_retail) * 100
        print(f"    Precio retail promedio (Similares): ${avg_retail:.2f}")
        print(f"    Precio mayorista promedio (NADRO):  ${avg_nadro:.2f}")
        print(f"    Ahorro promedio mayorista:          {ahorro:.1f}%")

    conn.close()

    print(f"\n{'=' * 70}")
    print(f"  13 COLUMNAS DE PRECIOS MAYORISTAS INTEGRADAS")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
