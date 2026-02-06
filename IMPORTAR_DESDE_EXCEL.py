"""
IMPORTAR_DESDE_EXCEL.py
========================
Importa CATALOGO_COMPLETO_COFEPRIS.xlsx a farmacia.db
Mantiene tablas existentes (repartidores, entregas, etc.)
"""

import sqlite3
import os
import sys
import time

try:
    import openpyxl
except ImportError:
    print("Instalando openpyxl...")
    os.system("pip install openpyxl")
    import openpyxl

# ============================================================
# CONFIGURACION
# ============================================================
EXCEL_FILE = os.path.join(os.path.dirname(__file__), "CATALOGO_COMPLETO_COFEPRIS.xlsx")
DB_FILE = os.path.join(os.path.dirname(__file__), "farmacia.db")

print("=" * 70)
print("  IMPORTADOR DE CATALOGO COFEPRIS A FARMACIA.DB")
print("=" * 70)
print()
print(f"  Excel: {os.path.basename(EXCEL_FILE)}")
print(f"  BD:    {os.path.basename(DB_FILE)}")
print()

# ============================================================
# 1. VERIFICAR QUE EXISTE EL EXCEL
# ============================================================
if not os.path.exists(EXCEL_FILE):
    print(f"ERROR: No se encontro {EXCEL_FILE}")
    sys.exit(1)

# ============================================================
# 2. CONECTAR A LA BD
# ============================================================
db_exists = os.path.exists(DB_FILE)
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# ============================================================
# 3. CREAR/MANTENER TODAS LAS TABLAS
# ============================================================
print("Verificando estructura de tablas...")

c.execute('''CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE,
    nombre TEXT,
    categoria TEXT,
    laboratorio TEXT,
    precio_costo REAL,
    precio_venta REAL,
    aplica_iva INTEGER,
    stock INTEGER,
    lote TEXT,
    caducidad TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    telefono TEXT,
    email TEXT,
    direccion TEXT,
    colonia TEXT,
    puntos_lealtad INTEGER,
    direccion_completa TEXT,
    referencia TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS empleados (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    usuario TEXT UNIQUE,
    password TEXT,
    nivel TEXT,
    activo INTEGER
)''')

c.execute('''CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folio TEXT UNIQUE,
    fecha TEXT,
    hora TEXT,
    vendedor_id INTEGER,
    cliente_id INTEGER,
    subtotal REAL,
    iva REAL,
    total REAL,
    tipo_pago TEXT,
    monto_efectivo REAL,
    monto_tarjeta REAL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS detalle_ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER,
    producto_id INTEGER,
    cantidad INTEGER,
    precio_unitario REAL,
    subtotal REAL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    contacto TEXT,
    telefono TEXT,
    email TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS repartidores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    telefono TEXT,
    num_moto TEXT,
    activo INTEGER DEFAULT 1
)''')

c.execute('''CREATE TABLE IF NOT EXISTS entregas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER,
    cliente_id INTEGER,
    repartidor_id INTEGER,
    num_moto TEXT,
    direccion TEXT,
    referencia TEXT,
    telefono_cliente TEXT,
    estado TEXT DEFAULT 'PENDIENTE',
    hora_salida TEXT,
    hora_llegada TEXT,
    metodo_pago_entrega TEXT,
    monto_cobrar REAL,
    cambio_llevar REAL DEFAULT 0,
    notas TEXT,
    fecha TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS cortes_caja (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    usuario_id INTEGER,
    total_ventas REAL,
    num_ventas INTEGER,
    efectivo REAL,
    tarjeta REAL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS inventario_movimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    tipo TEXT,
    producto_id INTEGER,
    cantidad INTEGER,
    usuario_id INTEGER,
    notas TEXT
)''')

conn.commit()
print("  Tablas verificadas OK")

# ============================================================
# 4. VERIFICAR DATOS BASE (empleados, clientes, repartidores)
# ============================================================
c.execute("SELECT COUNT(*) FROM empleados")
if c.fetchone()[0] == 0:
    print("  Insertando empleados base...")
    c.execute("INSERT INTO empleados VALUES (1,'ADMIN','admin','admin123','ADMINISTRADOR',1)")
    c.execute("INSERT INTO empleados VALUES (2,'SUPER ROOT','super','root123','ADMINISTRADOR',1)")
    c.execute("INSERT INTO empleados VALUES (3,'Juan Perez','jperez','pass123','VENDEDOR',1)")

c.execute("SELECT COUNT(*) FROM clientes")
if c.fetchone()[0] == 0:
    print("  Insertando clientes base...")
    c.execute("INSERT INTO clientes VALUES (1,'PUBLICO GENERAL','','','','',0,'','')")
    c.execute("INSERT INTO clientes VALUES (2,'Juan Gomez','7751234567','juan@email.com','Calle Principal 123','Centro',0,'Calle Principal 123, Col. Centro','Frente al parque')")
    c.execute("INSERT INTO clientes VALUES (3,'Maria Lopez','7759876543','maria@email.com','Av Juarez 456','Norte',0,'Av Juarez 456, Col. Norte','A lado de la tienda azul')")

c.execute("SELECT COUNT(*) FROM repartidores")
if c.fetchone()[0] == 0:
    print("  Insertando repartidores base...")
    c.execute("INSERT INTO repartidores (id,nombre,telefono,num_moto,activo) VALUES (1,'Carlos Ramirez','7751111111','M-01',1)")
    c.execute("INSERT INTO repartidores (id,nombre,telefono,num_moto,activo) VALUES (2,'Luis Martinez','7752222222','M-02',1)")
    c.execute("INSERT INTO repartidores (id,nombre,telefono,num_moto,activo) VALUES (3,'Pedro Sanchez','7753333333','M-03',1)")

c.execute("SELECT COUNT(*) FROM proveedores")
if c.fetchone()[0] == 0:
    print("  Insertando proveedores base...")
    c.execute("INSERT INTO proveedores VALUES (1,'DISTRIBUIDORA MEDICA SA','Lic. Roberto Gomez','5512345678','ventas@distmedica.com')")
    c.execute("INSERT INTO proveedores VALUES (2,'FARMACEUTICA DEL CENTRO','Ing. Carmen Ruiz','5587654321','contacto@farmcentro.com')")

conn.commit()

# ============================================================
# 5. LIMPIAR TABLA PRODUCTOS (reemplazar con datos nuevos)
# ============================================================
c.execute("SELECT COUNT(*) FROM productos")
productos_antes = c.fetchone()[0]
print(f"\n  Productos existentes: {productos_antes:,}")
print("  Limpiando tabla productos para importacion fresca...")
c.execute("DELETE FROM productos")
c.execute("DELETE FROM sqlite_sequence WHERE name='productos'")
conn.commit()

# ============================================================
# 6. LEER EXCEL E IMPORTAR
# ============================================================
print(f"\nLeyendo {os.path.basename(EXCEL_FILE)}...")
t0 = time.time()

wb = openpyxl.load_workbook(EXCEL_FILE, read_only=True, data_only=True)
ws = wb['Catalogo Completo']

# Header en fila 4 (indice 3 desde 0)
# Columnas: Codigo, Nombre Comercial, Principio Activo, Presentacion,
#           Laboratorio, Categoria, Stock, Precio Costo, Precio Venta, ...

insertados = 0
errores = 0
duplicados = 0
sin_codigo = 0
categorias = {}
laboratorios = {}
batch = []
BATCH_SIZE = 5000

print(f"Importando productos...\n")

for i, row in enumerate(ws.iter_rows(min_row=5, values_only=True)):
    # Saltar filas vacias
    if not row or not row[0]:
        sin_codigo += 1
        continue

    codigo = str(row[0]).strip()
    nombre = str(row[1]).strip() if row[1] else ""
    # principio_activo = row[2]  # No hay columna en tabla productos
    # presentacion = row[3]      # Ya incluida en nombre
    laboratorio = str(row[4]).strip() if row[4] else "SIN LAB"
    categoria = str(row[5]).strip() if row[5] else "GENERAL"
    stock = int(row[6]) if row[6] and str(row[6]).replace('-','').replace('.','').isdigit() else 0
    precio_costo = float(row[7]) if row[7] else 0.0
    precio_venta = float(row[8]) if row[8] else 0.0

    # Si no hay precio venta, calcular con margen 40%
    if precio_venta <= 0 and precio_costo > 0:
        precio_venta = round(precio_costo * 1.4, 2)

    # Medicamentos aplican IVA=0 en Mexico, otros si
    aplica_iva = 0 if "MEDICAMENTO" in categoria.upper() or "ANALGESICO" in categoria.upper() or "ANTIBIOTICO" in categoria.upper() else 1

    # Lote y caducidad no estan en el Excel, dejar vacio
    lote = ""
    caducidad = ""

    # Stock no negativo
    if stock < 0:
        stock = 0

    batch.append((codigo, nombre, categoria, laboratorio, precio_costo, precio_venta, aplica_iva, stock, lote, caducidad))

    # Contar categorias y labs
    categorias[categoria] = categorias.get(categoria, 0) + 1
    laboratorios[laboratorio] = laboratorios.get(laboratorio, 0) + 1

    # Insertar en lotes
    if len(batch) >= BATCH_SIZE:
        try:
            c.executemany("""INSERT OR IGNORE INTO productos
                (codigo, nombre, categoria, laboratorio, precio_costo, precio_venta, aplica_iva, stock, lote, caducidad)
                VALUES (?,?,?,?,?,?,?,?,?,?)""", batch)
            insertados += c.rowcount
            duplicados += len(batch) - c.rowcount
        except Exception as e:
            errores += len(batch)
            print(f"  Error en lote: {e}")
        conn.commit()
        batch = []
        total_proc = insertados + duplicados + errores
        print(f"  Procesados: {total_proc:,} | Insertados: {insertados:,} | Dup: {duplicados:,}", end="\r")

# Insertar ultimo lote
if batch:
    try:
        c.executemany("""INSERT OR IGNORE INTO productos
            (codigo, nombre, categoria, laboratorio, precio_costo, precio_venta, aplica_iva, stock, lote, caducidad)
            VALUES (?,?,?,?,?,?,?,?,?,?)""", batch)
        insertados += c.rowcount
        duplicados += len(batch) - c.rowcount
    except Exception as e:
        errores += len(batch)
        print(f"  Error en lote final: {e}")
    conn.commit()

wb.close()
t1 = time.time()

# ============================================================
# 7. VERIFICAR RESULTADO
# ============================================================
c.execute("SELECT COUNT(*) FROM productos")
total_db = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM productos WHERE precio_venta > 0")
con_precio = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM productos WHERE stock > 0")
con_stock = c.fetchone()[0]

c.execute("SELECT MIN(precio_venta), MAX(precio_venta), AVG(precio_venta) FROM productos WHERE precio_venta > 0")
pmin, pmax, pavg = c.fetchone()

conn.close()

# ============================================================
# 8. REPORTE FINAL
# ============================================================
print(" " * 80)
print()
print("=" * 70)
print("  IMPORTACION COMPLETADA")
print("=" * 70)
print()
print(f"  Tiempo:            {t1-t0:.1f} segundos")
print(f"  Productos leidos:  {insertados + duplicados + sin_codigo:,}")
print(f"  Insertados en BD:  {insertados:,}")
print(f"  Duplicados:        {duplicados:,}")
print(f"  Sin codigo:        {sin_codigo:,}")
print(f"  Errores:           {errores:,}")
print()
print(f"  TOTAL EN farmacia.db: {total_db:,} productos")
print(f"  Con precio:           {con_precio:,}")
print(f"  Con stock:            {con_stock:,}")
print()
if pmin is not None:
    print(f"  Precio minimo:  ${pmin:,.2f}")
    print(f"  Precio maximo:  ${pmax:,.2f}")
    print(f"  Precio promedio: ${pavg:,.2f}")
print()
print(f"  Categorias: {len(categorias)}")
for cat, cnt in sorted(categorias.items(), key=lambda x: -x[1])[:15]:
    print(f"    {cat}: {cnt:,}")
if len(categorias) > 15:
    print(f"    ... y {len(categorias)-15} mas")
print()
print(f"  Laboratorios: {len(laboratorios)}")
for lab, cnt in sorted(laboratorios.items(), key=lambda x: -x[1])[:10]:
    print(f"    {lab}: {cnt:,}")
if len(laboratorios) > 10:
    print(f"    ... y {len(laboratorios)-10} mas")
print()
print("  Tablas conservadas:")
print("    - empleados (admin/admin123, super/root123, jperez/pass123)")
print("    - clientes (3 registros)")
print("    - repartidores (3 registros)")
print("    - proveedores (2 registros)")
print("    - ventas, detalle_ventas, entregas, cortes_caja")
print()
print("  Ejecuta: python SISTEMA.py")
print("=" * 70)
