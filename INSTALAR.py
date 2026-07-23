import sqlite3
import os
from datetime import datetime
import random

print("="*70)
print("  INSTALANDO FARMACIAS MADRID")
print("="*70)

conn = sqlite3.connect('farmacia.db')
c = conn.cursor()

# TABLAS
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
    caducidad TEXT,
    imagen TEXT,
    precio_oferta REAL DEFAULT 0,
    codigo_barras TEXT
)''')

# Imagenes reales disponibles en imagenes/productos (nombre_marca.png -> archivo existente)
_img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagenes", "productos")
_imagenes_disponibles = set(os.listdir(_img_dir)) if os.path.exists(_img_dir) else set()

_placeholder_categoria = {
    "MEDICAMENTOS": "imagenes/productos/_cat_medicamento.png",
    "HIGIENE": "imagenes/productos/_cat_abarrotes.png",
}

def imagen_para(nombre_comercial, categoria):
    """Regresa la ruta relativa de imagen para una marca, o el placeholder de categoria."""
    archivo = nombre_comercial.lower().replace("&", "").replace(" ", "") + ".png"
    if archivo in _imagenes_disponibles:
        return f"imagenes/productos/{archivo}"
    return _placeholder_categoria.get(categoria, "imagenes/productos/_placeholder.png")

c.execute('''CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    telefono TEXT,
    email TEXT,
    direccion TEXT,
    colonia TEXT,
    puntos_lealtad INTEGER,
    direccion_completa TEXT,
    referencia TEXT,
    foto TEXT
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
    monto_tarjeta REAL,
    es_domicilio INTEGER DEFAULT 0
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

c.execute('''CREATE TABLE IF NOT EXISTS traspasos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folio TEXT UNIQUE,
    fecha TEXT,
    hora TEXT,
    sucursal_origen TEXT,
    sucursal_destino TEXT,
    motivo TEXT,
    estado TEXT DEFAULT 'PENDIENTE',
    usuario_solicita INTEGER,
    usuario_confirma INTEGER,
    usuario_completa INTEGER,
    fecha_confirmacion TEXT,
    fecha_completado TEXT,
    notas TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS detalle_traspasos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    traspaso_id INTEGER,
    producto_id INTEGER,
    codigo_producto TEXT,
    nombre_producto TEXT,
    cantidad INTEGER,
    stock_origen_antes INTEGER,
    stock_destino_antes INTEGER,
    FOREIGN KEY (traspaso_id) REFERENCES traspasos(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS sucursales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE,
    direccion TEXT,
    telefono TEXT,
    email TEXT,
    rfc TEXT,
    logo_path TEXT,
    ciudad TEXT,
    estado TEXT,
    cp TEXT,
    activa INTEGER DEFAULT 1,
    impresora_nombre TEXT DEFAULT '',
    impresora_ancho INTEGER DEFAULT 80,
    copias_ticket INTEGER DEFAULT 1,
    auto_imprimir INTEGER DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS config_sistema (
    clave TEXT PRIMARY KEY,
    valor TEXT
)''')

# Insertar sucursales iniciales
sucursales_data = [
    ("Tulancingo 1 (Matriz)", "Av. 21 de Marzo #100, Centro", "7751234001",
     "matriz@farmaciasmadrid.com", "FMA250101AAA", "", "Tulancingo", "Hidalgo", "43600"),
    ("Tulancingo 2", "Blvd. Luis Donaldo Colosio #250, Norte", "7751234002",
     "norte@farmaciasmadrid.com", "FMA250101AAA", "", "Tulancingo", "Hidalgo", "43610"),
    ("Tulancingo 3", "Calle Reforma #80, Sur", "7751234003",
     "sur@farmaciasmadrid.com", "FMA250101AAA", "", "Tulancingo", "Hidalgo", "43620"),
    ("Tulancingo 4", "Av. Alvaro Obregon #340, Oriente", "7751234004",
     "oriente@farmaciasmadrid.com", "FMA250101AAA", "", "Tulancingo", "Hidalgo", "43630"),
    ("Tulancingo 5", "Calle Hidalgo #55, Poniente", "7751234005",
     "poniente@farmaciasmadrid.com", "FMA250101AAA", "", "Tulancingo", "Hidalgo", "43640"),
]
for s in sucursales_data:
    try:
        c.execute("""INSERT INTO sucursales (nombre,direccion,telefono,email,rfc,logo_path,ciudad,estado,cp)
                     VALUES (?,?,?,?,?,?,?,?,?)""", s)
    except:
        pass

# ===== TABLAS MONEDERO SATURNOS =====
c.execute('''CREATE TABLE IF NOT EXISTS monederos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER UNIQUE,
    saldo_saturnos REAL DEFAULT 0,
    total_acumulado REAL DEFAULT 0,
    total_gastado REAL DEFAULT 0,
    activo INTEGER DEFAULT 1,
    fecha_alta TEXT,
    codigo_tarjeta TEXT UNIQUE,
    codigo_barras_path TEXT,
    tarjeta_impresa INTEGER DEFAULT 0,
    fecha_emision TEXT,
    estado_tarjeta TEXT DEFAULT 'ACTIVA',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS movimientos_saturnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    tipo TEXT,
    cantidad REAL,
    saldo_anterior REAL,
    saldo_nuevo REAL,
    concepto TEXT,
    venta_id INTEGER,
    usuario TEXT,
    fecha TEXT,
    hora TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS configuracion_saturnos (
    id INTEGER PRIMARY KEY,
    porcentaje_generico REAL DEFAULT 10.0,
    porcentaje_patente REAL DEFAULT 8.0,
    tasa_conversion REAL DEFAULT 1.0,
    minimo_acumular REAL DEFAULT 50.0,
    minimo_redimir REAL DEFAULT 100.0,
    dias_expiracion INTEGER DEFAULT 365,
    activo INTEGER DEFAULT 1
)''')

try:
    c.execute("INSERT INTO configuracion_saturnos (id,porcentaje_generico,porcentaje_patente,tasa_conversion,minimo_acumular,minimo_redimir,dias_expiracion,activo) VALUES (1,10.0,8.0,1.0,50.0,100.0,365,1)")
except:
    pass

# Monederos para clientes existentes
for cid in [2, 3]:
    try:
        c.execute("INSERT INTO monederos (cliente_id,saldo_saturnos,total_acumulado,total_gastado,activo,fecha_alta) VALUES (?,0,0,0,1,?)", (cid, datetime.now().strftime("%Y-%m-%d")))
    except:
        pass

# ===== TABLAS SISTEMA DE CRÉDITOS =====
c.execute('''CREATE TABLE IF NOT EXISTS creditos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folio TEXT UNIQUE,
    cliente_id INTEGER,
    tipo TEXT,
    monto_aprobado REAL,
    monto_usado REAL DEFAULT 0,
    monto_disponible REAL,
    tasa_interes REAL DEFAULT 0,
    plazo_dias INTEGER,
    fecha_aprobacion TEXT,
    fecha_vencimiento TEXT,
    estado TEXT DEFAULT 'PENDIENTE',
    documentos_completos INTEGER DEFAULT 0,
    aprobado_por TEXT,
    observaciones TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS documentos_credito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credito_id INTEGER,
    cliente_id INTEGER,
    tipo_documento TEXT,
    ruta_archivo TEXT,
    nombre_archivo TEXT,
    fecha_subida TEXT,
    verificado INTEGER DEFAULT 0,
    verificado_por TEXT,
    FOREIGN KEY (credito_id) REFERENCES creditos(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS pagos_credito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credito_id INTEGER,
    folio_pago TEXT,
    monto REAL,
    tipo_pago TEXT,
    fecha TEXT,
    hora TEXT,
    usuario TEXT,
    observaciones TEXT,
    FOREIGN KEY (credito_id) REFERENCES creditos(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS config_creditos (
    id INTEGER PRIMARY KEY,
    monto_max_persona REAL DEFAULT 5000.0,
    monto_max_clinica REAL DEFAULT 50000.0,
    plazo_persona_dias INTEGER DEFAULT 30,
    plazo_clinica_dias INTEGER DEFAULT 60,
    tasa_interes_persona REAL DEFAULT 0.0,
    tasa_interes_clinica REAL DEFAULT 0.0,
    requiere_aval INTEGER DEFAULT 0
)''')

try:
    c.execute("INSERT INTO config_creditos (id,monto_max_persona,monto_max_clinica,plazo_persona_dias,plazo_clinica_dias,tasa_interes_persona,tasa_interes_clinica,requiere_aval) VALUES (1,5000.0,50000.0,30,60,0.0,0.0,0)")
except:
    pass

# ===== TABLAS OFERTAS Y PROMOCIONES =====
c.execute('''CREATE TABLE IF NOT EXISTS ofertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folio TEXT UNIQUE,
    nombre TEXT,
    descripcion TEXT,
    tipo TEXT,
    descuento_porcentaje REAL DEFAULT 0,
    descuento_monto REAL DEFAULT 0,
    bonus_saturnos_extra REAL DEFAULT 15.0,
    aplica_a TEXT,
    productos_ids TEXT,
    categorias TEXT,
    laboratorios TEXT,
    excluir_controlados INTEGER DEFAULT 0,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    dias_semana TEXT DEFAULT 'TODOS',
    hora_inicio TEXT,
    hora_fin TEXT,
    limite_por_cliente INTEGER DEFAULT 0,
    limite_total INTEGER DEFAULT 0,
    unidades_vendidas INTEGER DEFAULT 0,
    activa INTEGER DEFAULT 1,
    destacada INTEGER DEFAULT 0,
    color_banner TEXT DEFAULT '#FF5722',
    creado_por TEXT,
    fecha_creacion TEXT,
    modificado_por TEXT,
    fecha_modificacion TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS ofertas_aplicadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER,
    oferta_id INTEGER,
    producto_codigo TEXT,
    cantidad INTEGER,
    precio_normal REAL,
    precio_oferta REAL,
    descuento_aplicado REAL,
    saturnos_extra REAL,
    fecha TEXT,
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
    FOREIGN KEY (oferta_id) REFERENCES ofertas(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS ofertas_banner (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    oferta_id INTEGER,
    imagen_path TEXT,
    orden INTEGER DEFAULT 0,
    activo INTEGER DEFAULT 1,
    FOREIGN KEY (oferta_id) REFERENCES ofertas(id)
)''')

# ===== TABLAS ROLES Y PERMISOS =====
c.execute('''CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE,
    descripcion TEXT,
    activo INTEGER DEFAULT 1,
    fecha_creacion TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS permisos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rol_id INTEGER,
    modulo TEXT,
    puede_ver INTEGER DEFAULT 0,
    puede_crear INTEGER DEFAULT 0,
    puede_editar INTEGER DEFAULT 0,
    puede_eliminar INTEGER DEFAULT 0,
    FOREIGN KEY (rol_id) REFERENCES roles(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    usuario_nombre TEXT,
    accion TEXT,
    modulo TEXT,
    datos TEXT,
    ip TEXT,
    fecha TEXT,
    hora TEXT
)''')

# Insertar roles por defecto
roles_default = [
    ("ADMINISTRADOR", "Acceso total al sistema"),
    ("GERENTE", "Acceso a reportes, inventario, finanzas, configuracion"),
    ("CAJERO", "Acceso a ventas, clientes, corte de caja"),
    ("REPARTIDOR", "Acceso solo a entregas asignadas"),
]
for nombre_rol, desc_rol in roles_default:
    try:
        c.execute("INSERT INTO roles (nombre, descripcion, fecha_creacion) VALUES (?,?,?)",
                  (nombre_rol, desc_rol, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    except:
        pass

# Permisos por defecto para cada rol
modulos = ["ventas", "inventario", "clientes", "compras", "finanzas", "reportes",
           "usuarios", "caja", "alertas", "saturnos", "creditos", "traspasos",
           "ofertas", "configuracion", "domicilio", "auditoria", "dashboard"]

permisos_rol = {
    "ADMINISTRADOR": {m: (1,1,1,1) for m in modulos},
    "GERENTE": {
        "ventas": (1,1,1,0), "inventario": (1,1,1,0), "clientes": (1,1,1,0),
        "compras": (1,1,0,0), "finanzas": (1,0,0,0), "reportes": (1,0,0,0),
        "usuarios": (0,0,0,0), "caja": (1,1,0,0), "alertas": (1,0,0,0),
        "saturnos": (1,1,1,0), "creditos": (1,1,0,0), "traspasos": (1,1,1,0),
        "ofertas": (1,1,1,0), "configuracion": (1,0,0,0), "domicilio": (1,1,1,0),
        "auditoria": (1,0,0,0), "dashboard": (1,0,0,0),
    },
    "CAJERO": {
        "ventas": (1,1,0,0), "inventario": (1,0,0,0), "clientes": (1,1,0,0),
        "compras": (0,0,0,0), "finanzas": (0,0,0,0), "reportes": (0,0,0,0),
        "usuarios": (0,0,0,0), "caja": (1,1,0,0), "alertas": (1,0,0,0),
        "saturnos": (1,1,0,0), "creditos": (0,0,0,0), "traspasos": (0,0,0,0),
        "ofertas": (1,0,0,0), "configuracion": (0,0,0,0), "domicilio": (1,1,0,0),
        "auditoria": (0,0,0,0), "dashboard": (1,0,0,0),
    },
    "REPARTIDOR": {
        "ventas": (0,0,0,0), "inventario": (0,0,0,0), "clientes": (0,0,0,0),
        "compras": (0,0,0,0), "finanzas": (0,0,0,0), "reportes": (0,0,0,0),
        "usuarios": (0,0,0,0), "caja": (0,0,0,0), "alertas": (0,0,0,0),
        "saturnos": (0,0,0,0), "creditos": (0,0,0,0), "traspasos": (0,0,0,0),
        "ofertas": (0,0,0,0), "configuracion": (0,0,0,0), "domicilio": (1,0,1,0),
        "auditoria": (0,0,0,0), "dashboard": (0,0,0,0),
    },
}

for nombre_rol, perms in permisos_rol.items():
    try:
        c.execute("SELECT id FROM roles WHERE nombre=?", (nombre_rol,))
        row = c.fetchone()
        if row:
            rid = row[0]
            for modulo, (ver, crear, editar, eliminar) in perms.items():
                try:
                    c.execute("INSERT INTO permisos (rol_id, modulo, puede_ver, puede_crear, puede_editar, puede_eliminar) VALUES (?,?,?,?,?,?)",
                              (rid, modulo, ver, crear, editar, eliminar))
                except:
                    pass
    except:
        pass

# ALTER TABLE empleados - agregar columnas rol_id y ultimo_acceso
for col in ["rol_id INTEGER DEFAULT 1", "ultimo_acceso TEXT"]:
    try:
        c.execute(f"ALTER TABLE empleados ADD COLUMN {col}")
    except:
        pass

# Asignar rol ADMINISTRADOR (id=1) a empleados existentes de nivel ADMINISTRADOR
try:
    c.execute("UPDATE empleados SET rol_id=1 WHERE nivel='ADMINISTRADOR'")
    c.execute("UPDATE empleados SET rol_id=3 WHERE nivel='VENDEDOR'")
except:
    pass

# Config por defecto
for clave, valor in [("sucursal_actual", "1"), ("ultimo_folio", "")]:
    try:
        c.execute("INSERT INTO config_sistema (clave,valor) VALUES (?,?)", (clave, valor))
    except:
        pass

print()
print("Generando 45,000 productos (ESPERA 2-3 MINUTOS)...")
print()

# MEDICAMENTOS CON NOMBRES COMERCIALES
medicamentos = {
    "PARACETAMOL": ["TEMPRA", "TYLENOL", "PANADOL", "MEJORAL"],
    "IBUPROFENO": ["ADVIL", "MOTRIN", "ACTRON", "IBUPROX"],
    "ASPIRINA": ["ASPIRINA BAYER", "CAFIASPIRINA"],
    "AMOXICILINA": ["AMOXIL", "TRIMOX"],
    "CIPROFLOXACINO": ["CIPRO", "CIPROXINA"],
    "METFORMINA": ["GLUCOPHAGE", "DABEX"],
    "LOSARTAN": ["COZAAR", "LORTAAN"],
    "ATORVASTATINA": ["LIPITOR", "ZARATOR"],
    "OMEPRAZOL": ["PRILOSEC", "LOSEC"],
    "RANITIDINA": ["ZANTAC", "RANISEN"],
    "CAPTOPRIL": ["CAPOTEN", "CAPOTENA"],
    "ENALAPRIL": ["VASOTEC", "RENITEC"],
    "METOPROLOL": ["LOPRESSOR", "SELOKEN"],
    "FUROSEMIDA": ["LASIX", "SEGURIL"],
    "HIDROCLOROTIAZIDA": ["MICROZIDE"],
    "CLONAZEPAM": ["RIVOTRIL", "KLONOPIN"],
    "DIAZEPAM": ["VALIUM", "ALBORAL"],
    "ALPRAZOLAM": ["XANAX", "TAFIL"],
    "FLUOXETINA": ["PROZAC", "SARAFEM"],
    "SERTRALINA": ["ZOLOFT", "LUSTRAL"],
    "LORATADINA": ["CLARITYNE", "LORATADINA"],
    "CETIRIZINA": ["ZYRTEC", "VIRLIX"],
    "DESLORATADINA": ["AERIUS", "CLARINEX"],
    "SALBUTAMOL": ["VENTOLIN", "PROVENTIL"],
    "BROMHEXINA": ["BISOLVON"],
    "AMBROXOL": ["MUCOSOLVAN", "AMBROXOL"],
    "DEXTROMETORFANO": ["ROBITUSSIN"],
    "NAPROXENO": ["ALEVE", "FLANAX"],
    "DICLOFENACO": ["VOLTAREN", "CATAFLAM"],
    "KETOROLACO": ["TORADOL", "DOLAC"]
}

labs = ["BAYER", "PFIZER", "NOVARTIS", "ROCHE", "GSK", "GENERICO", "PISA", "SOPHIA"]

tipos = {
    "TAB": ["TABLETAS", "TABLETAS RECUBIERTAS", "TABLETAS MASTICABLES"],
    "CAP": ["CAPSULAS", "CAPSULAS BLANDAS"],
    "JAR": ["JARABE", "SUSPENSION ORAL"],
    "INY": ["SOLUCION INYECTABLE", "AMPOLLETAS"]
}

concentraciones = ["50MG", "100MG", "250MG", "500MG", "1G", "5MG", "10MG", "20MG"]

productos = []
print("Generando 40,000 medicamentos...")
for i in range(40000):
    formula = random.choice(list(medicamentos.keys()))
    nombre_comercial = random.choice(medicamentos[formula])
    lab = random.choice(labs)
    
    tipo = random.choice(list(tipos.keys()))
    pres = random.choice(tipos[tipo])
    
    conc = random.choice(concentraciones)
    cant = random.choice([10, 20, 30, 60])
    
    # NOMBRE COMERCIAL PRIMERO, LUEGO FORMULA
    if tipo == "INY":
        nombre = f"{nombre_comercial} ({formula}) {conc} {pres} CAJA {random.choice([1,3,5])} AMP - {lab}"
    elif tipo == "JAR":
        nombre = f"{nombre_comercial} ({formula}) {conc}/5ML {pres} FRASCO {random.choice([60,100,120])}ML - {lab}"
    else:
        nombre = f"{nombre_comercial} ({formula}) {conc} {pres} CAJA {cant} PIEZAS - {lab}"
    
    codigo = f"MED{i+1:06d}"
    precio = round(random.uniform(15, 500), 2)
    img = imagen_para(nombre_comercial, "MEDICAMENTOS")
    cbarras = f"750{i+1:010d}"
    
    productos.append((
        codigo, nombre, "MEDICAMENTOS", lab,
        precio * 0.6, precio, 1,
        random.randint(10, 200),
        f"L{random.randint(1000,9999)}", "2026-12-31",
        img, 0, cbarras
    ))
    
    if (i+1) % 5000 == 0:
        print(f"  Medicamentos: {i+1:,} / 40,000")

higiene = {
    "SHAMPOO": ["200ML", "400ML", "750ML"],
    "JABON": ["BARRA 100G", "LIQUIDO 250ML"],
    "PASTA DENTAL": ["75ML", "100ML"],
    "DESODORANTE": ["ROLL-ON 50ML", "AEROSOL 150ML"],
    "ALCOHOL GEL": ["60ML", "250ML", "500ML"]
}

marcas = ["COLGATE", "PALMOLIVE", "P&G", "JOHNSON", "NIVEA"]

print("Generando 5,000 productos de higiene...")
for i in range(5000):
    prod = random.choice(list(higiene.keys()))
    marca = random.choice(marcas)
    tam = random.choice(higiene[prod])
    
    nombre = f"{marca} {prod} {tam}"
    codigo = f"HIG{i+1:05d}"
    precio = round(random.uniform(20, 300), 2)
    img = imagen_para(marca, "HIGIENE")
    cbarras = f"751{i+1:010d}"
    
    productos.append((
        codigo, nombre, "HIGIENE", marca,
        precio * 0.65, precio, 1,
        random.randint(20, 150),
        f"L{random.randint(1000,9999)}", "2026-12-31",
        img, 0, cbarras
    ))
    
    if (i+1) % 1000 == 0:
        print(f"  Higiene: {i+1:,} / 5,000")

c.executemany("INSERT INTO productos (codigo,nombre,categoria,laboratorio,precio_costo,precio_venta,aplica_iva,stock,lote,caducidad,imagen,precio_oferta,codigo_barras) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", productos)

print()
print("Creando usuarios...")
c.execute("INSERT INTO empleados (id,nombre,usuario,password,nivel,activo,rol_id) VALUES (1,'ADMIN','admin','admin123','ADMINISTRADOR',1,1)")
c.execute("INSERT INTO empleados (id,nombre,usuario,password,nivel,activo,rol_id) VALUES (2,'SUPER ROOT','super','root123','ADMINISTRADOR',1,1)")
c.execute("INSERT INTO empleados (id,nombre,usuario,password,nivel,activo,rol_id) VALUES (3,'Juan Perez','jperez','pass123','VENDEDOR',1,3)")

print("Creando clientes...")
c.execute("INSERT INTO clientes VALUES (1,'PUBLICO GENERAL','','','','',0,'','','')")
c.execute("INSERT INTO clientes VALUES (2,'Juan Gomez','7751234567','juan@email.com','Calle Principal 123','Centro',0,'Calle Principal 123, Col. Centro','Frente al parque','')")
c.execute("INSERT INTO clientes VALUES (3,'Maria Lopez','7759876543','maria@email.com','Av Juarez 456','Norte',0,'Av Juarez 456, Col. Norte','A lado de la tienda azul','')")

print("Creando repartidores...")
c.execute("INSERT INTO repartidores (id, nombre, telefono, num_moto, activo) VALUES (1,'Carlos Ramirez','7751111111','M-01',1)")
c.execute("INSERT INTO repartidores (id, nombre, telefono, num_moto, activo) VALUES (2,'Luis Martinez','7752222222','M-02',1)")
c.execute("INSERT INTO repartidores (id, nombre, telefono, num_moto, activo) VALUES (3,'Pedro Sanchez','7753333333','M-03',1)")

print("Creando proveedores...")
c.execute("INSERT INTO proveedores VALUES (1,'DISTRIBUIDORA MEDICA SA','Lic. Roberto Gomez','5512345678','ventas@distmedica.com')")
c.execute("INSERT INTO proveedores VALUES (2,'FARMACEUTICA DEL CENTRO','Ing. Carmen Ruiz','5587654321','contacto@farmcentro.com')")

# ===== TABLAS CARGO-GO (PAQUETERIA) =====
print()
print("Creando tablas CARGO-GO...")

c.execute('''CREATE TABLE IF NOT EXISTS zonas_cdmx (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE,
    nombre TEXT,
    delegacion TEXT,
    colonias_principales TEXT,
    cp_inicio INTEGER,
    cp_fin INTEGER,
    color_mapa TEXT DEFAULT '#2196F3',
    tarifa_base REAL DEFAULT 150.0,
    activa INTEGER DEFAULT 1
)''')

zonas_data = [
    ('NORTE_1', 'Zona Norte 1', 'Gustavo A. Madero', 7000, 7999, 150),
    ('NORTE_2', 'Zona Norte 2', 'Azcapotzalco', 2000, 2999, 150),
    ('NORTE_3', 'Zona Norte 3 (EdoMex)', 'Ecatepec', 55000, 55999, 180),
    ('CENTRO', 'Zona Centro', 'Cuauhtemoc', 6000, 6999, 150),
    ('PONIENTE_1', 'Zona Poniente 1', 'Miguel Hidalgo', 11000, 11999, 150),
    ('PONIENTE_2', 'Zona Poniente 2', 'Alvaro Obregon', 1000, 1999, 150),
    ('PONIENTE_3', 'Zona Poniente 3 (EdoMex)', 'Huixquilucan', 52760, 52799, 200),
    ('SUR_1', 'Zona Sur 1', 'Benito Juarez', 3000, 3999, 150),
    ('SUR_2', 'Zona Sur 2', 'Coyoacan', 4000, 4999, 150),
    ('SUR_3', 'Zona Sur 3', 'Tlalpan', 14000, 14999, 180),
]
for z in zonas_data:
    try:
        c.execute("INSERT INTO zonas_cdmx (codigo,nombre,delegacion,cp_inicio,cp_fin,tarifa_base) VALUES (?,?,?,?,?,?)", z)
    except:
        pass

c.execute('''CREATE TABLE IF NOT EXISTS repartidores_cdmx (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE,
    nombre TEXT,
    apellidos TEXT,
    telefono TEXT,
    whatsapp TEXT,
    zona_principal_id INTEGER,
    zonas_secundarias TEXT,
    capacidad_diaria INTEGER DEFAULT 5,
    entregas_hoy INTEGER DEFAULT 0,
    calificacion_promedio REAL DEFAULT 5.0,
    total_entregas INTEGER DEFAULT 0,
    activo INTEGER DEFAULT 1,
    disponible INTEGER DEFAULT 1,
    ultimo_cp INTEGER,
    ultima_actualizacion TEXT,
    FOREIGN KEY (zona_principal_id) REFERENCES zonas_cdmx(id)
)''')

reps_data = [
    ('REP-CDMX-001', 'Repartidor', 'Norte', '55-1234-5678', 1, 5),
    ('REP-CDMX-002', 'Repartidor', 'Centro-Sur', '55-2345-6789', 4, 5),
    ('REP-CDMX-003', 'Repartidor', 'Poniente', '55-3456-7890', 5, 5),
]
for r in reps_data:
    try:
        c.execute("INSERT INTO repartidores_cdmx (codigo,nombre,apellidos,telefono,zona_principal_id,capacidad_diaria) VALUES (?,?,?,?,?,?)", r)
    except:
        pass

c.execute('''CREATE TABLE IF NOT EXISTS envios_cargo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folio TEXT UNIQUE,
    tipo_servicio TEXT DEFAULT 'PAQUETERIA',
    tipo_envio TEXT DEFAULT 'EXPRESS_6H',
    origen_nombre TEXT,
    origen_telefono TEXT,
    origen_direccion TEXT,
    origen_cp INTEGER DEFAULT 43600,
    origen_ciudad TEXT DEFAULT 'Tulancingo',
    destino_nombre TEXT,
    destino_telefono TEXT,
    destino_direccion TEXT,
    destino_referencias TEXT,
    destino_cp INTEGER,
    destino_ciudad TEXT DEFAULT 'CDMX',
    destino_delegacion TEXT,
    zona_cdmx_id INTEGER,
    tipo_paquete TEXT,
    contenido TEXT,
    peso_kg REAL,
    valor_declarado REAL DEFAULT 0,
    requiere_seguro INTEGER DEFAULT 0,
    costo_seguro REAL DEFAULT 0,
    fragil INTEGER DEFAULT 0,
    tarifa_base REAL,
    cargo_peso REAL DEFAULT 0,
    subtotal REAL,
    iva REAL,
    total REAL,
    repartidor_id INTEGER,
    estado TEXT DEFAULT 'RECIBIDO',
    orden_entrega INTEGER,
    fecha_registro TEXT,
    hora_registro TEXT,
    fecha_salida_tulancingo TEXT,
    hora_salida_tulancingo TEXT,
    fecha_llegada_cdmx TEXT,
    hora_llegada_cdmx TEXT,
    fecha_entrega TEXT,
    hora_entrega TEXT,
    entregado_a TEXT,
    foto_evidencia TEXT,
    observaciones_entrega TEXT,
    calificacion INTEGER,
    usuario_registro TEXT,
    sucursal_id INTEGER,
    metodo_pago TEXT DEFAULT 'EFECTIVO',
    pagado INTEGER DEFAULT 0,
    codigo_barras_path TEXT,
    qr_rastreo TEXT,
    guia_impresa INTEGER DEFAULT 0,
    FOREIGN KEY (zona_cdmx_id) REFERENCES zonas_cdmx(id),
    FOREIGN KEY (repartidor_id) REFERENCES repartidores_cdmx(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS estados_envio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    envio_id INTEGER,
    estado_anterior TEXT,
    estado_nuevo TEXT,
    fecha TEXT,
    hora TEXT,
    ubicacion TEXT,
    notas TEXT,
    usuario TEXT,
    FOREIGN KEY (envio_id) REFERENCES envios_cargo(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS rutas_diarias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    repartidor_id INTEGER,
    zona_id INTEGER,
    total_envios INTEGER DEFAULT 0,
    envios_entregados INTEGER DEFAULT 0,
    hora_inicio TEXT,
    hora_fin TEXT,
    estado TEXT DEFAULT 'PROGRAMADA',
    FOREIGN KEY (repartidor_id) REFERENCES repartidores_cdmx(id),
    FOREIGN KEY (zona_id) REFERENCES zonas_cdmx(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS compras_cdmx (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    envio_id INTEGER,
    tipo_compra TEXT,
    lugar TEXT,
    lista_productos TEXT,
    presupuesto_cliente REAL,
    costo_real REAL,
    comision_servicio REAL,
    comision_porcentaje REAL DEFAULT 15.0,
    total_cobrar_cliente REAL,
    fotos_compra TEXT,
    notas_comprador TEXT,
    FOREIGN KEY (envio_id) REFERENCES envios_cargo(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS tarifas_cargo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_servicio TEXT,
    peso_desde_kg REAL,
    peso_hasta_kg REAL,
    tarifa_base REAL,
    cargo_adicional_kg REAL,
    activa INTEGER DEFAULT 1
)''')

tarifas_data = [
    ('EXPRESS_6H', 0, 1, 150, 20),
    ('EXPRESS_6H', 1, 5, 180, 25),
    ('EXPRESS_6H', 5, 10, 250, 30),
    ('ESTANDAR_24H', 0, 1, 100, 15),
    ('ESTANDAR_24H', 1, 5, 130, 20),
    ('ESTANDAR_24H', 5, 10, 180, 25),
]
for t in tarifas_data:
    try:
        c.execute("INSERT INTO tarifas_cargo (tipo_servicio,peso_desde_kg,peso_hasta_kg,tarifa_base,cargo_adicional_kg) VALUES (?,?,?,?,?)", t)
    except:
        pass

print("  Tablas CARGO-GO creadas OK")

conn.commit()
conn.close()

print()
print("="*70)
print("INSTALACION COMPLETA")
print("="*70)
print()
print("45,000 productos creados:")
print("  - 40,000 MEDICAMENTOS (con nombres comerciales)")
print("  - 5,000 HIGIENE")
print()
print("Sistema CARGO-GO paqueteria instalado:")
print("  - 10 zonas CDMX configuradas")
print("  - 3 repartidores registrados")
print("  - 6 tarifas configuradas")
print()
print("Usuario: admin")
print("Password: admin123")
print()
print("Ejecuta: python SISTEMA.py")
print("="*70)
