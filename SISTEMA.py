import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageColor
import os
import time
import re
import winsound
import tempfile

# ===== CONSTANTES DE DISENO =====
AZUL_FARMACIA = "#1565C0"
AZUL_OSCURO   = "#0D47A1"
AZUL_CLARO    = "#E3F2FD"
VERDE         = "#00C853"
ROJO          = "#D32F2F"
BLANCO        = "#FFFFFF"
GRIS_FONDO    = "#F5F7FA"
GRIS_TEXTO    = "#37474F"
OSCURO        = "#1A2332"
TEAL          = "#00897B"

# COLORES POS MODERNO VIBRANTE
SIDEBAR_BG      = "#0D47A1"
HEADER_BG       = "#0D47A1"
HEADER_BTN_BG   = "#1565C0"
HEADER_BTN_HV   = "#1E88E5"
ACCENT_GREEN    = "#00C853"

# Colores vibrantes por boton (estilo POS moderno)
CLR_VENTAS      = "#2196F3"   # Azul brillante
CLR_VENTAS_HV   = "#42A5F5"
CLR_DOMICILIO   = "#00BFA5"   # Verde esmeralda
CLR_DOMICILIO_HV= "#26D0B0"
CLR_INVENTARIO  = "#00BCD4"   # Cyan
CLR_INVENTARIO_HV="#26C6DA"
CLR_CLIENTES    = "#607D8B"   # Gris oscuro
CLR_CLIENTES_HV = "#78909C"
CLR_COMPRAS     = "#FF9800"   # Naranja
CLR_COMPRAS_HV  = "#FFB74D"
CLR_FINANZAS    = "#9C27B0"   # Morado
CLR_FINANZAS_HV = "#BA68C8"
CLR_CAJA        = "#FFC107"   # Dorado
CLR_CAJA_HV     = "#FFD54F"
CLR_ALERTAS     = "#F44336"   # Rojo
CLR_ALERTAS_HV  = "#EF5350"
CLR_USUARIOS    = "#546E7A"   # Gris azulado
CLR_USUARIOS_HV = "#78909C"
CLR_CONFIG      = "#757575"   # Gris
CLR_CONFIG_HV   = "#9E9E9E"
CLR_TRASPASOS   = "#4CAF50"   # Verde
CLR_TRASPASOS_HV= "#66BB6A"
CLR_SATURNOS    = "#FFC107"   # Dorado/Amarillo
CLR_SATURNOS_HV = "#FFD54F"
CLR_CREDITOS    = "#2E7D32"   # Verde oscuro
CLR_CREDITOS_HV = "#43A047"
CLR_OFERTAS     = "#FF5722"   # Naranja brillante
CLR_OFERTAS_HV  = "#FF7043"
CLR_REPORTES    = "#00838F"   # Teal oscuro
CLR_REPORTES_HV = "#00ACC1"

FUENTE_TITULO    = ("Segoe UI", 16, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 12, "bold")
FUENTE_NORMAL    = ("Segoe UI", 10)
FUENTE_BOTON     = ("Segoe UI", 10)
FUENTE_BOTON_ICO = ("Segoe UI", 16)
FUENTE_TOTAL     = ("Segoe UI", 36, "bold")

# CONEXION BD
import os
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# ASEGURAR TABLAS Y COLUMNAS NUEVAS (compatibilidad con BD existentes)
def _ensure_tables():
    c.execute("""CREATE TABLE IF NOT EXISTS repartidores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT, telefono TEXT, num_moto TEXT, activo INTEGER DEFAULT 1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS entregas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER, cliente_id INTEGER, repartidor_id INTEGER,
        num_moto TEXT, direccion TEXT, referencia TEXT, telefono_cliente TEXT,
        estado TEXT DEFAULT 'PENDIENTE', hora_salida TEXT, hora_llegada TEXT,
        metodo_pago_entrega TEXT, monto_cobrar REAL, cambio_llevar REAL DEFAULT 0,
        notas TEXT, fecha TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS traspasos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT UNIQUE, fecha TEXT, hora TEXT,
        sucursal_origen TEXT, sucursal_destino TEXT, motivo TEXT,
        estado TEXT DEFAULT 'PENDIENTE',
        usuario_solicita INTEGER, usuario_confirma INTEGER, usuario_completa INTEGER,
        fecha_confirmacion TEXT, fecha_completado TEXT, notas TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS detalle_traspasos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        traspaso_id INTEGER, producto_id INTEGER, codigo_producto TEXT,
        nombre_producto TEXT, cantidad INTEGER,
        stock_origen_antes INTEGER, stock_destino_antes INTEGER,
        FOREIGN KEY (traspaso_id) REFERENCES traspasos(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS sucursales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE, direccion TEXT, telefono TEXT, email TEXT, rfc TEXT,
        logo_path TEXT, ciudad TEXT, estado TEXT, cp TEXT, activa INTEGER DEFAULT 1,
        impresora_nombre TEXT DEFAULT '', impresora_ancho INTEGER DEFAULT 80,
        copias_ticket INTEGER DEFAULT 1, auto_imprimir INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS config_sistema (
        clave TEXT PRIMARY KEY, valor TEXT)""")
    # Insertar sucursales si no existen
    c.execute("SELECT COUNT(*) FROM sucursales")
    if c.fetchone()[0] == 0:
        for s in [
            ("Tulancingo 1 (Matriz)","Av. 21 de Marzo #100, Centro","7751234001","matriz@farmaciasmadrid.com","FMA250101AAA","","Tulancingo","Hidalgo","43600"),
            ("Tulancingo 2","Blvd. Luis Donaldo Colosio #250, Norte","7751234002","norte@farmaciasmadrid.com","FMA250101AAA","","Tulancingo","Hidalgo","43610"),
            ("Tulancingo 3","Calle Reforma #80, Sur","7751234003","sur@farmaciasmadrid.com","FMA250101AAA","","Tulancingo","Hidalgo","43620"),
            ("Tulancingo 4","Av. Alvaro Obregon #340, Oriente","7751234004","oriente@farmaciasmadrid.com","FMA250101AAA","","Tulancingo","Hidalgo","43630"),
            ("Tulancingo 5","Calle Hidalgo #55, Poniente","7751234005","poniente@farmaciasmadrid.com","FMA250101AAA","","Tulancingo","Hidalgo","43640"),
        ]:
            try:
                c.execute("INSERT INTO sucursales (nombre,direccion,telefono,email,rfc,logo_path,ciudad,estado,cp) VALUES (?,?,?,?,?,?,?,?,?)", s)
            except: pass
    # Config defaults
    for clave, valor in [("sucursal_actual","1"),("ultimo_folio","")]:
        try:
            c.execute("INSERT INTO config_sistema (clave,valor) VALUES (?,?)", (clave,valor))
        except: pass
    # --- Tablas Monedero Saturnos ---
    c.execute("""CREATE TABLE IF NOT EXISTS monederos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER UNIQUE,
        saldo_saturnos REAL DEFAULT 0, total_acumulado REAL DEFAULT 0,
        total_gastado REAL DEFAULT 0, activo INTEGER DEFAULT 1, fecha_alta TEXT,
        codigo_tarjeta TEXT UNIQUE, codigo_barras_path TEXT,
        tarjeta_impresa INTEGER DEFAULT 0, fecha_emision TEXT,
        estado_tarjeta TEXT DEFAULT 'ACTIVA',
        FOREIGN KEY (cliente_id) REFERENCES clientes(id))""")
    for col in ["codigo_tarjeta TEXT", "codigo_barras_path TEXT", "tarjeta_impresa INTEGER DEFAULT 0",
                "fecha_emision TEXT", "estado_tarjeta TEXT DEFAULT 'ACTIVA'"]:
        try:
            c.execute(f"ALTER TABLE monederos ADD COLUMN {col}")
        except: pass
    c.execute("""CREATE TABLE IF NOT EXISTS movimientos_saturnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER, tipo TEXT,
        cantidad REAL, saldo_anterior REAL, saldo_nuevo REAL, concepto TEXT,
        venta_id INTEGER, usuario TEXT, fecha TEXT, hora TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS configuracion_saturnos (
        id INTEGER PRIMARY KEY, porcentaje_generico REAL DEFAULT 10.0,
        porcentaje_patente REAL DEFAULT 8.0, tasa_conversion REAL DEFAULT 1.0,
        minimo_acumular REAL DEFAULT 50.0, minimo_redimir REAL DEFAULT 100.0,
        dias_expiracion INTEGER DEFAULT 365, activo INTEGER DEFAULT 1)""")
    try:
        c.execute("INSERT INTO configuracion_saturnos (id,porcentaje_generico,porcentaje_patente,tasa_conversion,minimo_acumular,minimo_redimir,dias_expiracion,activo) VALUES (1,10.0,8.0,1.0,50.0,100.0,365,1)")
    except: pass
    # --- Tablas Sistema Créditos ---
    c.execute("""CREATE TABLE IF NOT EXISTS creditos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, folio TEXT UNIQUE, cliente_id INTEGER,
        tipo TEXT, monto_aprobado REAL, monto_usado REAL DEFAULT 0,
        monto_disponible REAL, tasa_interes REAL DEFAULT 0, plazo_dias INTEGER,
        fecha_aprobacion TEXT, fecha_vencimiento TEXT, estado TEXT DEFAULT 'PENDIENTE',
        documentos_completos INTEGER DEFAULT 0, aprobado_por TEXT, observaciones TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS documentos_credito (
        id INTEGER PRIMARY KEY AUTOINCREMENT, credito_id INTEGER, cliente_id INTEGER,
        tipo_documento TEXT, ruta_archivo TEXT, nombre_archivo TEXT, fecha_subida TEXT,
        verificado INTEGER DEFAULT 0, verificado_por TEXT,
        FOREIGN KEY (credito_id) REFERENCES creditos(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS pagos_credito (
        id INTEGER PRIMARY KEY AUTOINCREMENT, credito_id INTEGER, folio_pago TEXT,
        monto REAL, tipo_pago TEXT, fecha TEXT, hora TEXT, usuario TEXT, observaciones TEXT,
        FOREIGN KEY (credito_id) REFERENCES creditos(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS config_creditos (
        id INTEGER PRIMARY KEY, monto_max_persona REAL DEFAULT 5000.0,
        monto_max_clinica REAL DEFAULT 50000.0, plazo_persona_dias INTEGER DEFAULT 30,
        plazo_clinica_dias INTEGER DEFAULT 60, tasa_interes_persona REAL DEFAULT 0.0,
        tasa_interes_clinica REAL DEFAULT 0.0, requiere_aval INTEGER DEFAULT 0)""")
    try:
        c.execute("INSERT INTO config_creditos (id,monto_max_persona,monto_max_clinica,plazo_persona_dias,plazo_clinica_dias) VALUES (1,5000.0,50000.0,30,60)")
    except: pass
    # --- Tablas Ofertas y Promociones ---
    c.execute("""CREATE TABLE IF NOT EXISTS ofertas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, folio TEXT UNIQUE, nombre TEXT,
        descripcion TEXT, tipo TEXT, descuento_porcentaje REAL DEFAULT 0,
        descuento_monto REAL DEFAULT 0, bonus_saturnos_extra REAL DEFAULT 15.0,
        aplica_a TEXT, productos_ids TEXT, categorias TEXT, laboratorios TEXT,
        excluir_controlados INTEGER DEFAULT 0, fecha_inicio TEXT, fecha_fin TEXT,
        dias_semana TEXT DEFAULT 'TODOS', hora_inicio TEXT, hora_fin TEXT,
        limite_por_cliente INTEGER DEFAULT 0, limite_total INTEGER DEFAULT 0,
        unidades_vendidas INTEGER DEFAULT 0, activa INTEGER DEFAULT 1,
        destacada INTEGER DEFAULT 0, color_banner TEXT DEFAULT '#FF5722',
        creado_por TEXT, fecha_creacion TEXT, modificado_por TEXT, fecha_modificacion TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS ofertas_aplicadas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, venta_id INTEGER, oferta_id INTEGER,
        producto_codigo TEXT, cantidad INTEGER, precio_normal REAL, precio_oferta REAL,
        descuento_aplicado REAL, saturnos_extra REAL, fecha TEXT,
        FOREIGN KEY (venta_id) REFERENCES ventas(id),
        FOREIGN KEY (oferta_id) REFERENCES ofertas(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS ofertas_banner (
        id INTEGER PRIMARY KEY AUTOINCREMENT, oferta_id INTEGER,
        imagen_path TEXT, orden INTEGER DEFAULT 0, activo INTEGER DEFAULT 1,
        FOREIGN KEY (oferta_id) REFERENCES ofertas(id))""")
    # Agregar columnas si no existen
    for col, tabla in [("monto_efectivo REAL", "ventas"), ("monto_tarjeta REAL", "ventas"),
                       ("direccion_completa TEXT", "clientes"), ("referencia TEXT", "clientes")]:
        try:
            c.execute(f"ALTER TABLE {tabla} ADD COLUMN {col}")
        except Exception:
            pass
    # --- Tablas Roles, Permisos, Auditoria ---
    c.execute("""CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE,
        descripcion TEXT, activo INTEGER DEFAULT 1, fecha_creacion TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS permisos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, rol_id INTEGER, modulo TEXT,
        puede_ver INTEGER DEFAULT 0, puede_crear INTEGER DEFAULT 0,
        puede_editar INTEGER DEFAULT 0, puede_eliminar INTEGER DEFAULT 0,
        FOREIGN KEY (rol_id) REFERENCES roles(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER,
        usuario_nombre TEXT, accion TEXT, modulo TEXT, datos TEXT,
        ip TEXT, fecha TEXT, hora TEXT)""")
    for col in ["rol_id INTEGER DEFAULT 1", "ultimo_acceso TEXT"]:
        try:
            c.execute(f"ALTER TABLE empleados ADD COLUMN {col}")
        except: pass
    # --- Tablas CARGO-GO (Paqueteria) ---
    c.execute("""CREATE TABLE IF NOT EXISTS zonas_cdmx (
        id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE, nombre TEXT,
        delegacion TEXT, colonias_principales TEXT, cp_inicio INTEGER, cp_fin INTEGER,
        color_mapa TEXT DEFAULT '#2196F3', tarifa_base REAL DEFAULT 150.0, activa INTEGER DEFAULT 1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS repartidores_cdmx (
        id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE, nombre TEXT, apellidos TEXT,
        telefono TEXT, whatsapp TEXT, zona_principal_id INTEGER, zonas_secundarias TEXT,
        capacidad_diaria INTEGER DEFAULT 5, entregas_hoy INTEGER DEFAULT 0,
        calificacion_promedio REAL DEFAULT 5.0, total_entregas INTEGER DEFAULT 0,
        activo INTEGER DEFAULT 1, disponible INTEGER DEFAULT 1, ultimo_cp INTEGER,
        ultima_actualizacion TEXT,
        FOREIGN KEY (zona_principal_id) REFERENCES zonas_cdmx(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS envios_cargo (
        id INTEGER PRIMARY KEY AUTOINCREMENT, folio TEXT UNIQUE,
        tipo_servicio TEXT DEFAULT 'PAQUETERIA', tipo_envio TEXT DEFAULT 'EXPRESS_6H',
        origen_nombre TEXT, origen_telefono TEXT, origen_direccion TEXT,
        origen_cp INTEGER DEFAULT 43600, origen_ciudad TEXT DEFAULT 'Tulancingo',
        destino_nombre TEXT, destino_telefono TEXT, destino_direccion TEXT,
        destino_referencias TEXT, destino_cp INTEGER, destino_ciudad TEXT DEFAULT 'CDMX',
        destino_delegacion TEXT, zona_cdmx_id INTEGER,
        tipo_paquete TEXT, contenido TEXT, peso_kg REAL,
        valor_declarado REAL DEFAULT 0, requiere_seguro INTEGER DEFAULT 0,
        costo_seguro REAL DEFAULT 0, fragil INTEGER DEFAULT 0,
        tarifa_base REAL, cargo_peso REAL DEFAULT 0, subtotal REAL, iva REAL, total REAL,
        repartidor_id INTEGER, estado TEXT DEFAULT 'RECIBIDO', orden_entrega INTEGER,
        fecha_registro TEXT, hora_registro TEXT,
        fecha_salida_tulancingo TEXT, hora_salida_tulancingo TEXT,
        fecha_llegada_cdmx TEXT, hora_llegada_cdmx TEXT,
        fecha_entrega TEXT, hora_entrega TEXT,
        entregado_a TEXT, foto_evidencia TEXT, observaciones_entrega TEXT, calificacion INTEGER,
        usuario_registro TEXT, sucursal_id INTEGER, metodo_pago TEXT DEFAULT 'EFECTIVO',
        pagado INTEGER DEFAULT 0, codigo_barras_path TEXT, qr_rastreo TEXT, guia_impresa INTEGER DEFAULT 0,
        FOREIGN KEY (zona_cdmx_id) REFERENCES zonas_cdmx(id),
        FOREIGN KEY (repartidor_id) REFERENCES repartidores_cdmx(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS estados_envio (
        id INTEGER PRIMARY KEY AUTOINCREMENT, envio_id INTEGER, estado_anterior TEXT,
        estado_nuevo TEXT, fecha TEXT, hora TEXT, ubicacion TEXT, notas TEXT, usuario TEXT,
        FOREIGN KEY (envio_id) REFERENCES envios_cargo(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS rutas_diarias (
        id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, repartidor_id INTEGER, zona_id INTEGER,
        total_envios INTEGER DEFAULT 0, envios_entregados INTEGER DEFAULT 0,
        hora_inicio TEXT, hora_fin TEXT, estado TEXT DEFAULT 'PROGRAMADA',
        FOREIGN KEY (repartidor_id) REFERENCES repartidores_cdmx(id),
        FOREIGN KEY (zona_id) REFERENCES zonas_cdmx(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS compras_cdmx (
        id INTEGER PRIMARY KEY AUTOINCREMENT, envio_id INTEGER, tipo_compra TEXT, lugar TEXT,
        lista_productos TEXT, presupuesto_cliente REAL, costo_real REAL,
        comision_servicio REAL, comision_porcentaje REAL DEFAULT 15.0,
        total_cobrar_cliente REAL, fotos_compra TEXT, notas_comprador TEXT,
        FOREIGN KEY (envio_id) REFERENCES envios_cargo(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS tarifas_cargo (
        id INTEGER PRIMARY KEY AUTOINCREMENT, tipo_servicio TEXT, peso_desde_kg REAL,
        peso_hasta_kg REAL, tarifa_base REAL, cargo_adicional_kg REAL, activa INTEGER DEFAULT 1)""")
    # Seed zonas if empty
    c.execute("SELECT COUNT(*) FROM zonas_cdmx")
    if c.fetchone()[0] == 0:
        for z in [('NORTE_1','Zona Norte 1','Gustavo A. Madero',7000,7999,150),
                  ('NORTE_2','Zona Norte 2','Azcapotzalco',2000,2999,150),
                  ('NORTE_3','Zona Norte 3 (EdoMex)','Ecatepec',55000,55999,180),
                  ('CENTRO','Zona Centro','Cuauhtemoc',6000,6999,150),
                  ('PONIENTE_1','Zona Poniente 1','Miguel Hidalgo',11000,11999,150),
                  ('PONIENTE_2','Zona Poniente 2','Alvaro Obregon',1000,1999,150),
                  ('PONIENTE_3','Zona Poniente 3 (EdoMex)','Huixquilucan',52760,52799,200),
                  ('SUR_1','Zona Sur 1','Benito Juarez',3000,3999,150),
                  ('SUR_2','Zona Sur 2','Coyoacan',4000,4999,150),
                  ('SUR_3','Zona Sur 3','Tlalpan',14000,14999,180)]:
            try: c.execute("INSERT INTO zonas_cdmx (codigo,nombre,delegacion,cp_inicio,cp_fin,tarifa_base) VALUES (?,?,?,?,?,?)", z)
            except: pass
    c.execute("SELECT COUNT(*) FROM repartidores_cdmx")
    if c.fetchone()[0] == 0:
        for r in [('REP-CDMX-001','Repartidor','Norte','55-1234-5678',1,5),
                  ('REP-CDMX-002','Repartidor','Centro-Sur','55-2345-6789',4,5),
                  ('REP-CDMX-003','Repartidor','Poniente','55-3456-7890',5,5)]:
            try: c.execute("INSERT INTO repartidores_cdmx (codigo,nombre,apellidos,telefono,zona_principal_id,capacidad_diaria) VALUES (?,?,?,?,?,?)", r)
            except: pass
    c.execute("SELECT COUNT(*) FROM tarifas_cargo")
    if c.fetchone()[0] == 0:
        for t in [('EXPRESS_6H',0,1,150,20),('EXPRESS_6H',1,5,180,25),('EXPRESS_6H',5,10,250,30),
                  ('ESTANDAR_24H',0,1,100,15),('ESTANDAR_24H',1,5,130,20),('ESTANDAR_24H',5,10,180,25)]:
            try: c.execute("INSERT INTO tarifas_cargo (tipo_servicio,peso_desde_kg,peso_hasta_kg,tarifa_base,cargo_adicional_kg) VALUES (?,?,?,?,?)", t)
            except: pass
    conn.commit()

_ensure_tables()

# ===== FUNCION DE AUDITORIA GLOBAL =====
def registrar_auditoria(accion, modulo, datos=""):
    """Registra una accion en la tabla de auditoria."""
    try:
        ahora = datetime.now()
        c.execute("INSERT INTO auditoria (usuario_id, usuario_nombre, accion, modulo, datos, ip, fecha, hora) VALUES (?,?,?,?,?,?,?,?)",
                  (usuario_id, usuario_actual, accion, modulo, str(datos)[:500], "local",
                   ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S")))
        conn.commit()
    except Exception:
        pass

# VARIABLES GLOBALES
usuario_actual = ""
nivel_actual = ""
usuario_id = 0
logo_header = None
logo_ventas = None
sucursal_id = 1
sucursal_actual = None  # dict con info de sucursal
ultimo_folio_venta = ""
historial_escaner = []  # Últimos 10 códigos escaneados

def obtener_sucursal():
    """Obtiene la info completa de la sucursal actual."""
    global sucursal_actual
    try:
        c.execute("SELECT valor FROM config_sistema WHERE clave='sucursal_actual'")
        row = c.fetchone()
        sid = int(row[0]) if row else 1
    except:
        sid = 1
    c.execute("SELECT id,nombre,direccion,telefono,email,rfc,logo_path,ciudad,estado,cp,impresora_nombre,impresora_ancho,copias_ticket,auto_imprimir FROM sucursales WHERE id=?", (sid,))
    row = c.fetchone()
    if row:
        sucursal_actual = {
            "id": row[0], "nombre": row[1], "direccion": row[2], "telefono": row[3],
            "email": row[4], "rfc": row[5], "logo_path": row[6], "ciudad": row[7],
            "estado": row[8], "cp": row[9], "impresora": row[10], "ancho": row[11],
            "copias": row[12], "auto_imprimir": row[13]
        }
    else:
        sucursal_actual = {"id":1,"nombre":"FARMACIAS MADRID","direccion":"","telefono":"",
                           "email":"","rfc":"","logo_path":"","ciudad":"","estado":"","cp":"",
                           "impresora":"","ancho":80,"copias":1,"auto_imprimir":0}
    return sucursal_actual

def beep_ok():
    """Sonido beep exitoso al escanear."""
    try:
        winsound.Beep(1200, 100)
    except: pass

def beep_error():
    """Sonido de error al escanear."""
    try:
        winsound.Beep(400, 300)
    except: pass

def es_codigo_barras(texto):
    """Detecta si el texto es un código de barras válido (EAN-13, UPC, interno)."""
    texto = texto.strip()
    if not texto:
        return False
    # EAN-13: 13 dígitos numéricos
    if re.match(r'^\d{13}$', texto):
        return True
    # UPC-A: 12 dígitos
    if re.match(r'^\d{12}$', texto):
        return True
    # EAN-8: 8 dígitos
    if re.match(r'^\d{8}$', texto):
        return True
    # Código interno: MED/HIG + dígitos
    if re.match(r'^(MED|HIG|PROD)\d+$', texto.upper()):
        return True
    # Alfanumérico corto (posible código interno)
    if re.match(r'^[A-Z0-9]{4,20}$', texto.upper()):
        return True
    return False

def obtener_oferta_producto(codigo_producto, nombre_producto="", categoria="", laboratorio="", cliente_id=0):
    """Busca la mejor oferta activa para un producto. Retorna dict o None."""
    ahora = datetime.now()
    hoy = ahora.strftime("%Y-%m-%d")
    hora_actual = ahora.strftime("%H:%M")
    dia_semana = str(ahora.isoweekday())  # 1=Lun, 7=Dom

    c.execute("""SELECT id, folio, nombre, tipo, descuento_porcentaje, descuento_monto,
                 bonus_saturnos_extra, aplica_a, productos_ids, categorias, laboratorios,
                 excluir_controlados, dias_semana, hora_inicio, hora_fin,
                 limite_por_cliente, limite_total, unidades_vendidas, color_banner
                 FROM ofertas WHERE activa=1 AND fecha_inicio<=? AND fecha_fin>=?
                 ORDER BY descuento_porcentaje DESC, descuento_monto DESC""", (hoy, hoy))
    ofertas = c.fetchall()
    mejor = None
    mejor_descuento = 0

    for of in ofertas:
        oid, folio, nombre_of, tipo, pct, monto, bonus, aplica_a, prod_ids, cats, labs, \
            excl_ctrl, dias, h_ini, h_fin, lim_cli, lim_tot, vendidas, color = of

        # Verificar día de la semana
        if dias and dias != "TODOS":
            if dia_semana not in dias.split(","):
                continue

        # Verificar horario
        if h_ini and h_fin:
            if not (h_ini <= hora_actual <= h_fin):
                continue

        # Verificar límite total
        if lim_tot > 0 and vendidas >= lim_tot:
            continue

        # Verificar límite por cliente
        if lim_cli > 0 and cliente_id > 1:
            c.execute("SELECT COALESCE(SUM(cantidad),0) FROM ofertas_aplicadas WHERE oferta_id=? AND venta_id IN (SELECT id FROM ventas WHERE cliente_id=?)",
                      (oid, cliente_id))
            ya_compradas = c.fetchone()[0]
            if ya_compradas >= lim_cli:
                continue

        # Verificar aplicabilidad
        aplica = False
        if aplica_a == "TODOS":
            aplica = True
        elif aplica_a == "PRODUCTO" and prod_ids:
            if codigo_producto in prod_ids.split(","):
                aplica = True
        elif aplica_a == "CATEGORIA" and cats:
            if categoria and categoria.upper() in [x.strip().upper() for x in cats.split(",")]:
                aplica = True
        elif aplica_a == "LABORATORIO" and labs:
            if laboratorio and laboratorio.upper() in [x.strip().upper() for x in labs.split(",")]:
                aplica = True

        if not aplica:
            continue

        # Calcular descuento efectivo para comparar
        desc_efectivo = pct if tipo == "DESCUENTO_PORCENTAJE" else 0
        if tipo == "2X1":
            desc_efectivo = 50
        elif tipo == "3X2":
            desc_efectivo = 33.33

        if desc_efectivo > mejor_descuento or (desc_efectivo == mejor_descuento and mejor is None):
            mejor_descuento = desc_efectivo
            mejor = {
                "id": oid, "folio": folio, "nombre": nombre_of, "tipo": tipo,
                "descuento_porcentaje": pct, "descuento_monto": monto,
                "bonus_saturnos": bonus, "color": color
            }

    return mejor

def calcular_precio_oferta(precio_normal, oferta, cantidad=1):
    """Calcula el precio con oferta aplicada."""
    if not oferta:
        return precio_normal, 0
    tipo = oferta["tipo"]
    if tipo == "DESCUENTO_PORCENTAJE":
        descuento = precio_normal * (oferta["descuento_porcentaje"] / 100.0)
        return round(precio_normal - descuento, 2), round(descuento, 2)
    elif tipo == "DESCUENTO_MONTO":
        descuento = min(oferta["descuento_monto"], precio_normal)
        return round(precio_normal - descuento, 2), round(descuento, 2)
    elif tipo == "2X1":
        if cantidad >= 2:
            pares = cantidad // 2
            sin_par = cantidad % 2
            total_normal = precio_normal * cantidad
            total_oferta = (pares * precio_normal) + (sin_par * precio_normal)
            descuento = total_normal - total_oferta
            return round(total_oferta / cantidad, 2), round(descuento / cantidad, 2)
        return precio_normal, 0
    elif tipo == "3X2":
        if cantidad >= 3:
            trios = cantidad // 3
            resto = cantidad % 3
            total_normal = precio_normal * cantidad
            total_oferta = (trios * 2 * precio_normal) + (resto * precio_normal)
            descuento = total_normal - total_oferta
            return round(total_oferta / cantidad, 2), round(descuento / cantidad, 2)
        return precio_normal, 0
    return precio_normal, 0

# CARGAR LOGO (busca logo.png o la imagen original)
def cargar_logo(tamano):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "logo.png")
        # Si no existe logo.png, intentar copiar la imagen original
        if not os.path.exists(logo_path):
            orig = r"C:\Users\chule\Pictures\imagen farma\Captura de pantalla 2026-01-27 193608.png"
            if os.path.exists(orig):
                import shutil
                shutil.copy2(orig, logo_path)
        img = Image.open(logo_path)
        img = img.resize((tamano, tamano), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        return None

# GENERAR LOGO PLACEHOLDER SI NO EXISTE logo.png
def generar_logo_placeholder():
    """Crea un logo.png con capsula farmaceutica en fondo azul."""
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    if os.path.exists(logo_path):
        return
    try:
        from PIL import ImageDraw, ImageFont
        size = 200
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Circulo azul de fondo
        draw.ellipse([5, 5, size-5, size-5], fill='#1565C0', outline='#E3F2FD', width=4)
        # Circulo interior oscuro
        draw.ellipse([15, 15, size-15, size-15], fill='#0D47A1')
        cx, cy = size // 2, size // 2 - 10
        # Capsula horizontal
        draw.rounded_rectangle([cx-45, cy-18, cx+45, cy+18], radius=18, fill='white')
        # Mitad izquierda color naranja
        draw.rounded_rectangle([cx-45, cy-18, cx-1, cy+18], radius=18, fill='#FF7043')
        # Linea divisoria central
        draw.line([cx, cy-18, cx, cy+18], fill='#1565C0', width=2)
        # Cruz medica en mitad derecha
        draw.rectangle([cx+12, cy-10, cx+18, cy+10], fill='#1565C0')
        draw.rectangle([cx+5, cy-3, cx+25, cy+3], fill='#1565C0')
        # Texto FM abajo
        try:
            font = ImageFont.truetype("segoeui.ttf", 28)
        except Exception:
            try:
                font = ImageFont.truetype("arial.ttf", 28)
            except Exception:
                font = ImageFont.load_default()
        draw.text((cx, size - 35), "FM", fill='white', font=font, anchor='mm')
        img.save(logo_path, 'PNG')
    except Exception:
        pass

generar_logo_placeholder()

# HOVER EFFECT PARA BOTONES
def hover_bind(widget, color_normal, color_hover, color_active=None):
    """Agrega efecto hover a un boton."""
    if color_active is None:
        color_active = color_hover
    def on_enter(e):
        widget.config(bg=color_hover)
    def on_leave(e):
        widget.config(bg=color_normal)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
    widget.config(activebackground=color_active)

def elegant_hover(widget, bg_normal, bg_hover, fg_normal="white", fg_hover="white", accent_frame=None, accent_color=None):
    """Hover elegante: transicion suave de color."""
    def on_enter(e):
        widget.config(bg=bg_hover, fg=fg_hover)
        if accent_frame and accent_color:
            accent_frame.config(bg=accent_color)
    def on_leave(e):
        widget.config(bg=bg_normal, fg=fg_normal)
        if accent_frame and accent_color:
            accent_frame.config(bg=bg_normal)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

# LIMPIAR AREA PRINCIPAL
def limpiar():
    for widget in main.winfo_children():
        widget.destroy()

# SALIR
def salir():
    if messagebox.askyesno("Cerrar sesión", "¿Cerrar sesión?"):
        root.destroy()
        login.deiconify()

# ===== SPLASH SCREEN =====
class SplashScreen:
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.overrideredirect(True)
        # Centrar en pantalla
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w, h = 520, 380
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.configure(bg=AZUL_OSCURO)

        # Frame principal con borde
        frame = tk.Frame(self.root, bg=AZUL_OSCURO)
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Logo
        self.logo_splash = cargar_logo(90)
        if self.logo_splash:
            tk.Label(frame, image=self.logo_splash, bg=AZUL_OSCURO).pack(pady=(40, 10))
        else:
            tk.Label(frame, text="FM", font=("Segoe UI", 48, "bold"),
                    bg=AZUL_OSCURO, fg="white").pack(pady=(40, 10))

        tk.Label(frame, text="FARMACIAS MADRID", font=("Segoe UI", 28, "bold"),
                bg=AZUL_OSCURO, fg="white").pack(pady=(5, 2))
        tk.Label(frame, text="Sistema Punto de Venta Profesional", font=("Segoe UI", 11),
                bg=AZUL_OSCURO, fg="#90CAF9").pack(pady=(0, 5))
        tk.Label(frame, text="v3.0 - Combo Ultimate Edition", font=("Segoe UI", 9),
                bg=AZUL_OSCURO, fg="#64B5F6").pack(pady=(0, 20))

        # Barra de progreso
        self.progress_frame = tk.Frame(frame, bg="#1A237E", height=8, width=360)
        self.progress_frame.pack(pady=(10, 5))
        self.progress_frame.pack_propagate(False)
        self.progress_bar = tk.Frame(self.progress_frame, bg=ACCENT_GREEN, height=8, width=0)
        self.progress_bar.place(x=0, y=0, height=8)

        self.status_label = tk.Label(frame, text="Iniciando...", font=("Segoe UI", 9),
                                     bg=AZUL_OSCURO, fg="#90CAF9")
        self.status_label.pack(pady=(5, 0))

        tk.Label(frame, text="Tulancingo, Hidalgo", font=("Segoe UI", 8),
                bg=AZUL_OSCURO, fg="#5C6BC0").pack(side=tk.BOTTOM, pady=10)

        self.progress = 0
        self.mensajes = [
            "Conectando base de datos...",
            "Cargando 45,000 productos...",
            "Verificando inventario...",
            "Cargando modulos de venta...",
            "Iniciando sistema de ofertas...",
            "Cargando monedero Saturnos...",
            "Verificando respaldos...",
            "Preparando interfaz...",
            "Listo!"
        ]
        self.msg_idx = 0
        self.animar()

    def animar(self):
        if self.progress < 360:
            self.progress += 8
            self.progress_bar.place(x=0, y=0, width=min(self.progress, 360), height=8)
            idx = min(int(self.progress / 360 * len(self.mensajes)), len(self.mensajes) - 1)
            if idx != self.msg_idx:
                self.msg_idx = idx
                self.status_label.config(text=self.mensajes[idx])
            self.root.after(40, self.animar)
        else:
            self.status_label.config(text="Listo!")
            self.root.after(300, self.terminar)

    def terminar(self):
        self.root.destroy()
        mostrar_login()

# ===== LOGIN PREMIUM =====
def mostrar_login():
    global login, user, pwd
    login = tk.Tk()
    login.title("FARMACIAS MADRID - Inicio de Sesion")
    login.geometry("1000x600")
    login.resizable(False, False)
    login.configure(bg="white")
    # Centrar
    sw = login.winfo_screenwidth()
    sh = login.winfo_screenheight()
    x = (sw - 1000) // 2
    y = (sh - 600) // 2
    login.geometry(f"1000x600+{x}+{y}")

    # Layout dividido: izquierda branding, derecha formulario
    # --- IZQUIERDA: Branding azul ---
    left = tk.Frame(login, bg=AZUL_OSCURO, width=450)
    left.pack(side=tk.LEFT, fill=tk.Y)
    left.pack_propagate(False)

    # Espaciador superior
    tk.Frame(left, bg=AZUL_OSCURO, height=80).pack()

    logo_login_img = cargar_logo(100)
    if logo_login_img:
        lbl_logo = tk.Label(left, image=logo_login_img, bg=AZUL_OSCURO)
        lbl_logo.image = logo_login_img
        lbl_logo.pack(pady=(20, 15))
    else:
        tk.Label(left, text="FM", font=("Segoe UI", 56, "bold"),
                bg=AZUL_OSCURO, fg="white").pack(pady=(20, 15))

    tk.Label(left, text="FARMACIAS", font=("Segoe UI", 32, "bold"),
            bg=AZUL_OSCURO, fg="white").pack(pady=(0, 0))
    tk.Label(left, text="MADRID", font=("Segoe UI", 32, "bold"),
            bg=AZUL_OSCURO, fg=ACCENT_GREEN).pack(pady=(0, 10))

    tk.Frame(left, bg=ACCENT_GREEN, height=3, width=80).pack(pady=10)

    tk.Label(left, text="Punto de Venta Profesional", font=("Segoe UI", 12),
            bg=AZUL_OSCURO, fg="#90CAF9").pack(pady=(5, 2))
    tk.Label(left, text="5 Sucursales - Tulancingo, Hgo.", font=("Segoe UI", 9),
            bg=AZUL_OSCURO, fg="#64B5F6").pack(pady=(0, 5))
    tk.Label(left, text="45,000+ Productos | Saturnos | Creditos", font=("Segoe UI", 8),
            bg=AZUL_OSCURO, fg="#5C6BC0").pack(pady=(0, 0))

    # --- DERECHA: Formulario ---
    right = tk.Frame(login, bg="white")
    right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    tk.Frame(right, bg="white", height=60).pack()

    tk.Label(right, text="Bienvenido", font=("Segoe UI", 28, "bold"),
            bg="white", fg=AZUL_OSCURO).pack(pady=(20, 2))
    tk.Label(right, text="Inicia sesion para continuar", font=("Segoe UI", 11),
            bg="white", fg="#90A4AE").pack(pady=(0, 30))

    form_frame = tk.Frame(right, bg="white")
    form_frame.pack(pady=10)

    # Usuario
    tk.Label(form_frame, text="USUARIO", font=("Segoe UI", 9, "bold"),
            bg="white", fg="#78909C").grid(row=0, column=0, sticky="w", padx=20, pady=(0, 5))
    user = tk.Entry(form_frame, width=30, font=("Segoe UI", 13), relief=tk.FLAT, bd=0,
                    bg="#F5F5F5", highlightthickness=2, highlightcolor=AZUL_FARMACIA,
                    highlightbackground="#E0E0E0")
    user.grid(row=1, column=0, padx=20, pady=(0, 15), ipady=8)
    user.insert(0, "admin")

    # Password
    tk.Label(form_frame, text="CONTRASENA", font=("Segoe UI", 9, "bold"),
            bg="white", fg="#78909C").grid(row=2, column=0, sticky="w", padx=20, pady=(0, 5))
    pwd = tk.Entry(form_frame, show="\u25CF", width=30, font=("Segoe UI", 13), relief=tk.FLAT, bd=0,
                   bg="#F5F5F5", highlightthickness=2, highlightcolor=AZUL_FARMACIA,
                   highlightbackground="#E0E0E0")
    pwd.grid(row=3, column=0, padx=20, pady=(0, 20), ipady=8)
    pwd.insert(0, "admin123")

    # Mensaje de error (oculto)
    error_var = tk.StringVar(value="")
    error_lbl = tk.Label(form_frame, textvariable=error_var, font=("Segoe UI", 9),
                         bg="white", fg=ROJO)
    error_lbl.grid(row=4, column=0, padx=20, pady=(0, 5))

    def entrar():
        import hashlib
        pwd_text = pwd.get()
        pwd_hash = hashlib.sha256(pwd_text.encode()).hexdigest()
        # Soportar password en texto plano (legacy) o SHA256
        c.execute("SELECT nombre, nivel, id FROM empleados WHERE usuario=? AND (password=? OR password=?) AND activo=1",
                 (user.get(), pwd_text, pwd_hash))
        res = c.fetchone()
        if res:
            global usuario_actual, nivel_actual, usuario_id
            usuario_actual = res[0]
            nivel_actual = res[1]
            usuario_id = res[2]
            # Registrar ultimo acceso
            try:
                c.execute("UPDATE empleados SET ultimo_acceso=? WHERE id=?",
                         (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), usuario_id))
                conn.commit()
            except: pass
            registrar_auditoria("LOGIN", "sistema", f"Usuario {usuario_actual} inicio sesion")
            seleccionar_sucursal_login()
        else:
            error_var.set("Usuario o contrasena incorrectos")
            pwd.delete(0, tk.END)

    btn = tk.Button(form_frame, text="INICIAR SESION", command=entrar,
                   bg=AZUL_FARMACIA, fg="white", font=("Segoe UI", 14, "bold"),
                   relief=tk.FLAT, cursor="hand2", bd=0, padx=40, pady=12,
                   activebackground=AZUL_OSCURO, activeforeground="white")
    btn.grid(row=5, column=0, padx=20, pady=(10, 15), sticky="ew")
    hover_bind(btn, AZUL_FARMACIA, "#1E88E5")

    # Enter key
    pwd.bind("<Return>", lambda e: entrar())
    user.bind("<Return>", lambda e: pwd.focus())

    tk.Label(right, text="v3.0 Combo Ultimate | Farmacias Madrid", font=("Segoe UI", 8),
            bg="white", fg="#BDBDBD").pack(side=tk.BOTTOM, pady=15)

    login.mainloop()

def seleccionar_sucursal_login():
    """Dialog para seleccionar sucursal al iniciar sesion."""
    global sucursal_id
    c.execute("SELECT id, nombre FROM sucursales WHERE activa=1")
    sucursales = c.fetchall()
    if not sucursales:
        login.withdraw()
        obtener_sucursal()
        abrir_sistema()
        return
    if len(sucursales) == 1:
        sucursal_id = sucursales[0][0]
        c.execute("INSERT OR REPLACE INTO config_sistema (clave,valor) VALUES ('sucursal_actual',?)", (str(sucursal_id),))
        conn.commit()
        login.withdraw()
        obtener_sucursal()
        abrir_sistema()
        return

    dlg = tk.Toplevel(login)
    dlg.title("Seleccionar Sucursal")
    dlg.geometry("420x380")
    dlg.resizable(False, False)
    dlg.configure(bg="white")
    dlg.grab_set()
    dlg.transient(login)

    tk.Label(dlg, text="SELECCIONA SUCURSAL", font=("Segoe UI", 16, "bold"),
            bg="white", fg=AZUL_FARMACIA).pack(pady=(25,10))
    tk.Label(dlg, text="Elige la sucursal donde trabajaras hoy:",
            font=("Segoe UI", 10), bg="white", fg=GRIS_TEXTO).pack(pady=(0,15))

    sel_var = tk.IntVar(value=sucursales[0][0])
    for sid, nombre in sucursales:
        rb = tk.Radiobutton(dlg, text=f"  {nombre}", variable=sel_var, value=sid,
                           font=("Segoe UI", 12), bg="white", fg=GRIS_TEXTO,
                           activebackground="white", selectcolor=AZUL_CLARO,
                           indicatoron=True, padx=20, pady=6, anchor="w")
        rb.pack(fill=tk.X, padx=30)

    def confirmar_sucursal():
        global sucursal_id
        sucursal_id = sel_var.get()
        c.execute("INSERT OR REPLACE INTO config_sistema (clave,valor) VALUES ('sucursal_actual',?)", (str(sucursal_id),))
        conn.commit()
        dlg.destroy()
        login.withdraw()
        obtener_sucursal()
        abrir_sistema()

    tk.Button(dlg, text="ENTRAR", command=confirmar_sucursal,
             bg=AZUL_FARMACIA, fg="white", font=("Segoe UI", 14, "bold"),
             padx=50, pady=10, relief=tk.FLAT, cursor="hand2",
             activebackground=AZUL_OSCURO).pack(pady=25)

# ===== SISTEMA PRINCIPAL =====
def abrir_sistema():
    global root, main, menu_lateral
    
    root = tk.Toplevel()
    root.title("FARMACIAS MADRID - Sistema POS")
    root.state('zoomed')
    root.configure(bg=GRIS_FONDO)

    # ================================================================
    # HEADER - AZUL FARMACIA 60px
    # ================================================================
    header = tk.Frame(root, bg=AZUL_FARMACIA, height=60)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    tk.Frame(root, bg=ACCENT_GREEN, height=3).pack(fill=tk.X)

    # -- LOGO + NOMBRE (pack LEFT, no fixed width, auto-size) --
    logo_container = tk.Frame(header, bg=AZUL_FARMACIA)
    logo_container.pack(side=tk.LEFT, padx=(10, 20), pady=5)

    global logo_header
    logo_header = cargar_logo(40)
    if logo_header:
        tk.Label(logo_container, image=logo_header, bg=AZUL_FARMACIA).pack(side=tk.LEFT, padx=(0, 8))

    tk.Label(logo_container, text="FARMACIAS MADRID", font=("Segoe UI", 16, "bold"),
            bg=AZUL_FARMACIA, fg="white").pack(side=tk.LEFT)
    suc = obtener_sucursal()
    tk.Label(logo_container, text=f"| {suc['nombre']}", font=("Segoe UI", 9),
            bg=AZUL_FARMACIA, fg="#BBDEFB").pack(side=tk.LEFT, padx=(8,0))

    # -- USUARIO + SALIR (pack RIGHT) --
    user_container = tk.Frame(header, bg=AZUL_FARMACIA)
    user_container.pack(side=tk.RIGHT, padx=10, pady=5)

    tk.Label(user_container, text=f"{usuario_actual}", font=("Segoe UI", 9, "bold"),
            bg=AZUL_FARMACIA, fg="#BBDEFB").pack(side=tk.LEFT, padx=(0, 6))
    btn_salir = tk.Button(user_container, text="SALIR", command=salir,
             bg="#B71C1C", fg="white", font=("Segoe UI", 8, "bold"),
             relief=tk.RAISED, padx=6, pady=2, bd=1, cursor="hand2",
             activebackground="#E53935", activeforeground="white")
    btn_salir.pack(side=tk.LEFT)
    elegant_hover(btn_salir, "#B71C1C", "#E53935")

    # -- BOTONES HEADER (centro, todos los modulos, font 9pt) --
    menu_top = tk.Frame(header, bg=AZUL_FARMACIA)
    menu_top.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    botones_top = [
        ("Dashboard",  lambda: ver_dashboard()),
        ("Ventas",     lambda: ver_ventas()),
        ("Domicilio",  lambda: ver_domicilio()),
        ("Inventario", lambda: ver_inventario()),
        ("Compras",    lambda: ver_compras()),
        ("Clientes",   lambda: ver_clientes()),
        ("Finanzas",   lambda: ver_finanzas()),
        ("Reportes",   lambda: ver_reportes()),
        ("Usuarios",   lambda: ver_usuarios()),
        ("Caja",       lambda: ver_corte_caja()),
        ("Alertas",    lambda: ver_alertas_stock()),
        ("Saturnos",   lambda: ver_saturnos()),
        ("Creditos",   lambda: ver_creditos()),
        ("Traspasos",  lambda: ver_traspasos()),
        ("Ofertas",    lambda: ver_ofertas()),
        ("Auditoria",  lambda: ver_auditoria()),
        ("Config",     lambda: ver_configuracion()),
    ]

    for texto, cmd in botones_top:
        btn_top = tk.Button(menu_top, text=texto, command=cmd,
                           bg="#1565C0", fg="white", font=("Segoe UI", 9),
                           relief=tk.FLAT, padx=6, pady=4, cursor="hand2", bd=0,
                           activebackground="#1E88E5", activeforeground="white")
        btn_top.pack(side=tk.LEFT, padx=3, pady=15)
        def make_hv(b):
            b.bind("<Enter>", lambda e: b.config(bg="#1E88E5"))
            b.bind("<Leave>", lambda e: b.config(bg="#1565C0"))
        make_hv(btn_top)

    # ================================================================
    # CONTAINER (sidebar + main)
    # ================================================================
    container = tk.Frame(root, bg=GRIS_FONDO)
    container.pack(fill=tk.BOTH, expand=True)

    # ================================================================
    # SIDEBAR IZQUIERDO - 160px, azul oscuro, botones con colores
    # ================================================================
    menu_lateral = tk.Frame(container, bg=SIDEBAR_BG, width=160)
    menu_lateral.pack(side=tk.LEFT, fill=tk.Y)
    menu_lateral.pack_propagate(False)

    CLR_DASHBOARD    = "#1B5E20"
    CLR_DASHBOARD_HV = "#2E7D32"
    CLR_AUDITORIA    = "#4E342E"
    CLR_AUDITORIA_HV = "#6D4C41"
    CLR_CARGO        = "#001A4D"
    CLR_CARGO_HV     = "#0D47A1"

    botones_comunes = [
        ("\u25C9", "DASHBOARD", lambda: ver_dashboard(),   CLR_DASHBOARD, CLR_DASHBOARD_HV),
        ("\u25B6", "VENTAS",     lambda: ver_ventas(),     CLR_VENTAS,     CLR_VENTAS_HV),
        ("\u25CF", "DOMICILIO",  lambda: ver_domicilio(),  CLR_DOMICILIO,  CLR_DOMICILIO_HV),
        ("\u25A0", "INVENTARIO", lambda: ver_inventario(), CLR_INVENTARIO, CLR_INVENTARIO_HV),
        ("\u2605", "OFERTAS",    lambda: ver_ofertas(),     CLR_OFERTAS,    CLR_OFERTAS_HV),
        ("\u25B2", "CLIENTES",   lambda: ver_clientes(),   CLR_CLIENTES,   CLR_CLIENTES_HV),
        ("💳", "ABONOS",    lambda: ver_abonos_credito(), "#1565C0",    "#1976D2"),
        ("\u20B4", "SATURNOS",   lambda: ver_saturnos(),   CLR_SATURNOS,   CLR_SATURNOS_HV),
        ("\u2708", "CARGO-GO",   lambda: ver_cargo_go(),   CLR_CARGO,      CLR_CARGO_HV),
    ]

    botones_admin = [
        ("\u25C6", "COMPRAS",  lambda: ver_compras(),       CLR_COMPRAS,  CLR_COMPRAS_HV),
        ("\u2666", "FINANZAS", lambda: ver_finanzas(),      CLR_FINANZAS, CLR_FINANZAS_HV),
        ("\u2261", "REPORTES", lambda: ver_reportes(),      CLR_REPORTES, CLR_REPORTES_HV),
        ("\u2663", "CREDITOS", lambda: ver_creditos(),      CLR_CREDITOS, CLR_CREDITOS_HV),
        ("\u25A0", "CAJA",     lambda: ver_corte_caja(),    CLR_CAJA,     CLR_CAJA_HV),
        ("\u25B2", "ALERTAS",  lambda: ver_alertas_stock(), CLR_ALERTAS,  CLR_ALERTAS_HV),
        ("\u25CF", "USUARIOS", lambda: ver_usuarios(),      CLR_USUARIOS, CLR_USUARIOS_HV),
        ("\u21C4", "TRASPASOS",lambda: ver_traspasos(),     CLR_TRASPASOS,CLR_TRASPASOS_HV),
        ("\u270E", "AUDITORIA",lambda: ver_auditoria(),     CLR_AUDITORIA,CLR_AUDITORIA_HV),
        ("\u2699", "CONFIG",   lambda: ver_configuracion(), CLR_CONFIG,   CLR_CONFIG_HV),
    ]

    if nivel_actual == "ADMINISTRADOR":
        botones_lateral = botones_comunes + botones_admin
    else:
        botones_lateral = botones_comunes

    # Botones compactos - 10 en espacio de 8
    sidebar_btns = []
    for simbolo, texto, cmd, btn_color, btn_hover in botones_lateral:
        btn = tk.Button(menu_lateral, text=f" {simbolo}  {texto}", command=cmd,
                       bg=btn_color, fg="white",
                       font=("Segoe UI", 12, "bold"),
                       padx=8, pady=10, relief=tk.RAISED, cursor="hand2",
                       anchor="w", bd=2,
                       activebackground=btn_hover, activeforeground="white")
        btn.pack(fill=tk.X, padx=3, pady=1)
        sidebar_btns.append(btn)

        def make_hover(b, normal, hover):
            def enter(e): b.config(bg=hover, relief=tk.GROOVE)
            def leave(e): b.config(bg=normal, relief=tk.RAISED)
            b.bind("<Enter>", enter)
            b.bind("<Leave>", leave)
        make_hover(btn, btn_color, btn_hover)

    # ================================================================
    # AREA PRINCIPAL - contenido dinamico
    # ================================================================
    main = tk.Frame(container, bg=GRIS_FONDO)
    main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    ver_dashboard()

# ===== DASHBOARD EJECUTIVO =====
def ver_dashboard():
    limpiar()
    registrar_auditoria("VER", "dashboard", "Acceso al dashboard")

    # Header
    hdr = tk.Frame(main, bg="#1B5E20", height=42)
    hdr.pack(fill=tk.X)
    hdr.pack_propagate(False)
    tk.Label(hdr, text="\u25C9 DASHBOARD EJECUTIVO", font=("Segoe UI", 13, "bold"),
            bg="#1B5E20", fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    # Fecha/hora
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    tk.Label(hdr, text=now_str, font=("Segoe UI", 10),
            bg="#1B5E20", fg="#A5D6A7").pack(side=tk.RIGHT, padx=12)

    # Scroll area
    canvas_dash = tk.Canvas(main, bg=GRIS_FONDO, highlightthickness=0)
    scrollbar = ttk.Scrollbar(main, orient="vertical", command=canvas_dash.yview)
    scroll_frame = tk.Frame(canvas_dash, bg=GRIS_FONDO)

    scroll_frame.bind("<Configure>", lambda e: canvas_dash.configure(scrollregion=canvas_dash.bbox("all")))
    canvas_dash.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas_dash.configure(yscrollcommand=scrollbar.set)
    canvas_dash.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    def _on_mousewheel(e):
        try:
            if canvas_dash.winfo_exists():
                canvas_dash.yview_scroll(int(-1*(e.delta/120)), "units")
        except Exception:
            pass
    canvas_dash.bind_all("<MouseWheel>", _on_mousewheel)

    # --- KPIs ---
    hoy = datetime.now().strftime("%Y-%m-%d")
    mes_actual = datetime.now().strftime("%Y-%m")

    # Ventas hoy
    c.execute("SELECT COALESCE(SUM(total),0), COUNT(*) FROM ventas WHERE fecha=?", (hoy,))
    ventas_hoy, tickets_hoy = c.fetchone()

    # Saturnos otorgados hoy
    c.execute("SELECT COALESCE(SUM(cantidad),0) FROM movimientos_saturnos WHERE tipo='ACUMULACION' AND fecha=?", (hoy,))
    saturnos_hoy = c.fetchone()[0]

    # Clientes atendidos hoy
    c.execute("SELECT COUNT(DISTINCT cliente_id) FROM ventas WHERE fecha=? AND cliente_id>1", (hoy,))
    clientes_hoy = c.fetchone()[0]

    # Ventas mes
    c.execute("SELECT COALESCE(SUM(total),0), COUNT(*) FROM ventas WHERE fecha LIKE ?", (mes_actual + "%",))
    ventas_mes, tickets_mes = c.fetchone()

    # Entregas pendientes
    c.execute("SELECT COUNT(*) FROM entregas WHERE estado='PENDIENTE'")
    entregas_pend = c.fetchone()[0]

    kpi_frame = tk.Frame(scroll_frame, bg=GRIS_FONDO)
    kpi_frame.pack(fill=tk.X, padx=15, pady=(15, 5))

    kpis = [
        ("VENTAS HOY", f"${ventas_hoy:,.2f}", "#2196F3", "\u25B6"),
        ("TICKETS HOY", f"{tickets_hoy}", "#00BCD4", "\u25A0"),
        ("SATURNOS HOY", f"{saturnos_hoy:,.0f}", "#FFC107", "\u20B4"),
        ("CLIENTES HOY", f"{clientes_hoy}", "#607D8B", "\u25B2"),
        ("VENTAS MES", f"${ventas_mes:,.2f}", "#4CAF50", "\u2605"),
        ("ENTREGAS PEND.", f"{entregas_pend}", "#FF5722", "\u25CF"),
    ]

    for i, (titulo, valor, color, icono) in enumerate(kpis):
        card = tk.Frame(kpi_frame, bg="white", relief=tk.FLAT, bd=0)
        card.grid(row=0, column=i, padx=6, pady=5, sticky="nsew")
        kpi_frame.columnconfigure(i, weight=1)

        # Barra de color superior
        tk.Frame(card, bg=color, height=4).pack(fill=tk.X)
        tk.Label(card, text=icono, font=("Segoe UI", 20), bg="white", fg=color).pack(pady=(10, 2))
        tk.Label(card, text=valor, font=("Segoe UI", 18, "bold"), bg="white", fg="#212121").pack(pady=(0, 2))
        tk.Label(card, text=titulo, font=("Segoe UI", 8, "bold"), bg="white", fg="#9E9E9E").pack(pady=(0, 10))

    # --- META MENSUAL ---
    meta_frame = tk.Frame(scroll_frame, bg="white")
    meta_frame.pack(fill=tk.X, padx=15, pady=5)
    tk.Frame(meta_frame, bg="#4CAF50", height=3).pack(fill=tk.X)

    meta_mensual = 500000.0  # Meta por defecto
    progreso = min(ventas_mes / meta_mensual * 100, 100) if meta_mensual > 0 else 0

    meta_inner = tk.Frame(meta_frame, bg="white")
    meta_inner.pack(fill=tk.X, padx=15, pady=10)
    tk.Label(meta_inner, text="META MENSUAL", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#333").pack(anchor="w")
    tk.Label(meta_inner, text=f"${ventas_mes:,.2f} / ${meta_mensual:,.2f}  ({progreso:.1f}%)",
            font=("Segoe UI", 10), bg="white", fg="#666").pack(anchor="w", pady=(2,5))

    bar_bg = tk.Frame(meta_inner, bg="#E0E0E0", height=20)
    bar_bg.pack(fill=tk.X, pady=2)
    bar_bg.pack_propagate(False)
    bar_color = "#4CAF50" if progreso >= 80 else "#FFC107" if progreso >= 50 else "#F44336"
    bar_fill = tk.Frame(bar_bg, bg=bar_color, height=20)
    bar_fill.place(x=0, y=0, relwidth=progreso/100, relheight=1.0)
    tk.Label(bar_bg, text=f"{progreso:.0f}%", font=("Segoe UI", 9, "bold"),
            bg=bar_color, fg="white").place(relx=0.01, rely=0.1)

    # --- GRAFICAS CON CANVAS ---
    graficas_frame = tk.Frame(scroll_frame, bg=GRIS_FONDO)
    graficas_frame.pack(fill=tk.X, padx=15, pady=5)

    # Grafica 1: Ventas por hora (ultimas 12 horas)
    graf1 = tk.Frame(graficas_frame, bg="white")
    graf1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    graficas_frame.columnconfigure(0, weight=1)
    graficas_frame.columnconfigure(1, weight=1)

    tk.Label(graf1, text="VENTAS POR HORA (HOY)", font=("Segoe UI", 10, "bold"),
            bg="white", fg="#333").pack(anchor="w", padx=10, pady=(10,5))

    canvas_g1 = tk.Canvas(graf1, width=450, height=180, bg="white", highlightthickness=0)
    canvas_g1.pack(padx=10, pady=5)

    # Obtener ventas por hora
    ventas_hora = {}
    for h in range(24):
        hora_str = f"{h:02d}"
        c.execute("SELECT COALESCE(SUM(total),0) FROM ventas WHERE fecha=? AND hora LIKE ?",
                  (hoy, hora_str + ":%"))
        ventas_hora[h] = c.fetchone()[0]

    max_venta_h = max(ventas_hora.values()) if any(ventas_hora.values()) else 1
    bar_w = 16
    x_offset = 30
    for h in range(24):
        val = ventas_hora[h]
        bar_h = int((val / max_venta_h) * 140) if max_venta_h > 0 else 0
        x = x_offset + h * (bar_w + 2)
        color = "#2196F3" if val > 0 else "#E0E0E0"
        canvas_g1.create_rectangle(x, 160 - bar_h, x + bar_w, 160, fill=color, outline="")
        if h % 4 == 0:
            canvas_g1.create_text(x + bar_w//2, 172, text=f"{h:02d}", font=("Segoe UI", 7), fill="#999")

    # Grafica 2: Top 5 productos del dia
    graf2 = tk.Frame(graficas_frame, bg="white")
    graf2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

    tk.Label(graf2, text="TOP 5 PRODUCTOS (HOY)", font=("Segoe UI", 10, "bold"),
            bg="white", fg="#333").pack(anchor="w", padx=10, pady=(10,5))

    c.execute("""SELECT p.nombre, SUM(dv.cantidad) as cant, SUM(dv.subtotal) as total
                 FROM detalle_ventas dv
                 JOIN ventas v ON dv.venta_id=v.id
                 JOIN productos p ON dv.producto_id=p.id
                 WHERE v.fecha=?
                 GROUP BY dv.producto_id ORDER BY cant DESC LIMIT 5""", (hoy,))
    top_prods = c.fetchall()

    canvas_g2 = tk.Canvas(graf2, width=450, height=180, bg="white", highlightthickness=0)
    canvas_g2.pack(padx=10, pady=5)

    if top_prods:
        max_cant = max(r[1] for r in top_prods) if top_prods else 1
        colores_bar = ["#2196F3", "#00BCD4", "#4CAF50", "#FF9800", "#9C27B0"]
        for i, (nombre, cant, total) in enumerate(top_prods):
            y = 10 + i * 34
            bar_w_prod = int((cant / max_cant) * 250)
            color = colores_bar[i % len(colores_bar)]
            canvas_g2.create_rectangle(150, y, 150 + bar_w_prod, y + 22, fill=color, outline="")
            canvas_g2.create_text(145, y + 11, text=nombre[:20], font=("Segoe UI", 7), fill="#333", anchor="e")
            canvas_g2.create_text(155 + bar_w_prod, y + 11, text=f"{cant}u", font=("Segoe UI", 7, "bold"),
                                  fill="#333", anchor="w")
    else:
        canvas_g2.create_text(225, 90, text="Sin ventas hoy", font=("Segoe UI", 11), fill="#BDBDBD")

    # --- ALERTAS CRITICAS ---
    alertas_frame = tk.Frame(scroll_frame, bg="white")
    alertas_frame.pack(fill=tk.X, padx=15, pady=5)
    tk.Frame(alertas_frame, bg="#F44336", height=3).pack(fill=tk.X)

    tk.Label(alertas_frame, text="ALERTAS CRITICAS", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#D32F2F").pack(anchor="w", padx=15, pady=(10, 5))

    # Stock bajo (< 5 unidades)
    c.execute("SELECT COUNT(*) FROM productos WHERE stock < 5 AND stock >= 0")
    stock_bajo = c.fetchone()[0]

    # Productos por caducar (30 dias)
    fecha_limite = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM productos WHERE caducidad <= ? AND caducidad >= ?", (fecha_limite, hoy))
    por_caducar = c.fetchone()[0]

    # Creditos vencidos
    c.execute("SELECT COUNT(*) FROM creditos WHERE estado='ACTIVO' AND fecha_vencimiento < ?", (hoy,))
    creditos_vencidos = c.fetchone()[0]

    alertas_inner = tk.Frame(alertas_frame, bg="white")
    alertas_inner.pack(fill=tk.X, padx=15, pady=(0, 10))

    alertas_list = []
    if stock_bajo > 0:
        alertas_list.append((f"{stock_bajo} productos con stock critico (<5 unidades)", "#F44336"))
    if por_caducar > 0:
        alertas_list.append((f"{por_caducar} productos por caducar en 30 dias", "#FF9800"))
    if creditos_vencidos > 0:
        alertas_list.append((f"{creditos_vencidos} creditos vencidos", "#F44336"))
    if entregas_pend > 0:
        alertas_list.append((f"{entregas_pend} entregas pendientes por asignar", "#2196F3"))

    if alertas_list:
        for texto_alerta, color_alerta in alertas_list:
            row_a = tk.Frame(alertas_inner, bg="white")
            row_a.pack(fill=tk.X, pady=2)
            tk.Label(row_a, text="\u26A0", font=("Segoe UI", 10), bg="white", fg=color_alerta).pack(side=tk.LEFT, padx=(0,8))
            tk.Label(row_a, text=texto_alerta, font=("Segoe UI", 9), bg="white", fg="#555").pack(side=tk.LEFT)
    else:
        tk.Label(alertas_inner, text="Sin alertas criticas", font=("Segoe UI", 9),
                bg="white", fg="#4CAF50").pack(anchor="w")

    # --- OFERTAS ACTIVAS ---
    ofertas_frame_d = tk.Frame(scroll_frame, bg="white")
    ofertas_frame_d.pack(fill=tk.X, padx=15, pady=5)
    tk.Frame(ofertas_frame_d, bg="#FF5722", height=3).pack(fill=tk.X)

    tk.Label(ofertas_frame_d, text="OFERTAS ACTIVAS", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#E64A19").pack(anchor="w", padx=15, pady=(10, 5))

    c.execute("""SELECT nombre, tipo, descuento_porcentaje, fecha_fin, color_banner
                 FROM ofertas WHERE activa=1 AND fecha_inicio<=? AND fecha_fin>=?
                 ORDER BY destacada DESC LIMIT 5""", (hoy, hoy))
    ofertas_activas = c.fetchall()

    of_inner = tk.Frame(ofertas_frame_d, bg="white")
    of_inner.pack(fill=tk.X, padx=15, pady=(0, 10))

    if ofertas_activas:
        for nombre_of, tipo_of, pct_of, fin_of, color_of in ofertas_activas:
            row_of = tk.Frame(of_inner, bg=color_of or "#FF5722")
            row_of.pack(fill=tk.X, pady=2, ipady=4)
            desc_txt = f"-{pct_of:.0f}%" if tipo_of == "DESCUENTO_PORCENTAJE" else tipo_of
            tk.Label(row_of, text=f"  {nombre_of}  {desc_txt}  (hasta {fin_of})",
                    font=("Segoe UI", 9, "bold"), bg=color_of or "#FF5722", fg="white").pack(side=tk.LEFT, padx=5)
    else:
        tk.Label(of_inner, text="No hay ofertas activas", font=("Segoe UI", 9),
                bg="white", fg="#999").pack(anchor="w")

    # --- ACCESOS RAPIDOS ---
    accesos_frame = tk.Frame(scroll_frame, bg="white")
    accesos_frame.pack(fill=tk.X, padx=15, pady=(5, 15))
    tk.Frame(accesos_frame, bg=AZUL_FARMACIA, height=3).pack(fill=tk.X)

    tk.Label(accesos_frame, text="ACCESOS RAPIDOS", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#333").pack(anchor="w", padx=15, pady=(10, 8))

    acc_inner = tk.Frame(accesos_frame, bg="white")
    acc_inner.pack(fill=tk.X, padx=15, pady=(0, 10))

    accesos = [
        ("NUEVA VENTA", "#2196F3", lambda: ver_ventas()),
        ("INVENTARIO", "#00BCD4", lambda: ver_inventario()),
        ("CORTE CAJA", "#FFC107", lambda: ver_corte_caja()),
        ("OFERTAS", "#FF5722", lambda: ver_ofertas()),
        ("REPORTES", "#9C27B0", lambda: ver_reportes()),
        ("ALERTAS", "#F44336", lambda: ver_alertas_stock()),
    ]
    for i, (txt_acc, clr_acc, cmd_acc) in enumerate(accesos):
        btn_acc = tk.Button(acc_inner, text=txt_acc, command=cmd_acc,
                           bg=clr_acc, fg="white", font=("Segoe UI", 10, "bold"),
                           relief=tk.FLAT, padx=20, pady=8, cursor="hand2",
                           activebackground=clr_acc)
        btn_acc.grid(row=0, column=i, padx=5, pady=5)
        hover_bind(btn_acc, clr_acc, "#333")

    # --- AUTO-REFRESH cada 30 segundos ---
    def auto_refresh():
        try:
            if main.winfo_exists():
                # Check if dashboard is still showing
                children = main.winfo_children()
                if children and hasattr(children[0], 'cget'):
                    try:
                        bg = children[0].cget('bg')
                        if bg == "#1B5E20":  # Dashboard header color
                            ver_dashboard()
                    except:
                        pass
        except:
            pass

    main.after(30000, auto_refresh)

# ===== MODULO AUDITORIA =====
def ver_auditoria():
    limpiar()
    registrar_auditoria("VER", "auditoria", "Acceso al modulo de auditoria")

    hdr = tk.Frame(main, bg="#4E342E", height=42)
    hdr.pack(fill=tk.X)
    hdr.pack_propagate(False)
    tk.Label(hdr, text="\u270E AUDITORIA DEL SISTEMA", font=("Segoe UI", 13, "bold"),
            bg="#4E342E", fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    # Filtros
    filtros = tk.Frame(main, bg="white")
    filtros.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(filtros, text="Desde:", font=("Segoe UI", 9), bg="white").pack(side=tk.LEFT, padx=(10,5))
    desde_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    tk.Entry(filtros, textvariable=desde_var, width=12, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=2)

    tk.Label(filtros, text="Hasta:", font=("Segoe UI", 9), bg="white").pack(side=tk.LEFT, padx=(10,5))
    hasta_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    tk.Entry(filtros, textvariable=hasta_var, width=12, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=2)

    tk.Label(filtros, text="Modulo:", font=("Segoe UI", 9), bg="white").pack(side=tk.LEFT, padx=(10,5))
    modulo_var = tk.StringVar(value="TODOS")
    modulos_combo = ttk.Combobox(filtros, textvariable=modulo_var, width=15, state="readonly",
                                  values=["TODOS", "ventas", "inventario", "clientes", "configuracion",
                                          "sistema", "dashboard", "auditoria", "ofertas", "saturnos",
                                          "creditos", "traspasos", "finanzas", "reportes"])
    modulos_combo.pack(side=tk.LEFT, padx=2)

    tk.Label(filtros, text="Usuario:", font=("Segoe UI", 9), bg="white").pack(side=tk.LEFT, padx=(10,5))
    usuario_var = tk.StringVar(value="TODOS")
    tk.Entry(filtros, textvariable=usuario_var, width=15, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=2)

    # Tabla
    cols_aud = ("ID", "Fecha", "Hora", "Usuario", "Accion", "Modulo", "Datos")
    tree_frame = tk.Frame(main, bg="white")
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    tree_aud = ttk.Treeview(tree_frame, columns=cols_aud, show="headings", height=25)
    for col_name in cols_aud:
        ancho = 60 if col_name == "ID" else 85 if col_name in ("Fecha","Hora") else 120 if col_name in ("Usuario","Accion","Modulo") else 300
        tree_aud.heading(col_name, text=col_name)
        tree_aud.column(col_name, width=ancho, anchor="center" if col_name != "Datos" else "w")

    scroll_aud = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_aud.yview)
    tree_aud.configure(yscrollcommand=scroll_aud.set)
    tree_aud.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll_aud.pack(side=tk.RIGHT, fill=tk.Y)

    def buscar_auditoria():
        for item in tree_aud.get_children():
            tree_aud.delete(item)

        query = "SELECT id, fecha, hora, usuario_nombre, accion, modulo, datos FROM auditoria WHERE 1=1"
        params = []

        if desde_var.get():
            query += " AND fecha >= ?"
            params.append(desde_var.get())
        if hasta_var.get():
            query += " AND fecha <= ?"
            params.append(hasta_var.get())
        if modulo_var.get() != "TODOS":
            query += " AND modulo = ?"
            params.append(modulo_var.get())
        if usuario_var.get() != "TODOS" and usuario_var.get():
            query += " AND usuario_nombre LIKE ?"
            params.append(f"%{usuario_var.get()}%")

        query += " ORDER BY id DESC LIMIT 500"
        c.execute(query, params)
        for row in c.fetchall():
            tree_aud.insert("", "end", values=row)

    btn_buscar = tk.Button(filtros, text="BUSCAR", command=buscar_auditoria,
                           bg="#4E342E", fg="white", font=("Segoe UI", 9, "bold"),
                           relief=tk.FLAT, padx=15, pady=3, cursor="hand2")
    btn_buscar.pack(side=tk.LEFT, padx=10)
    hover_bind(btn_buscar, "#4E342E", "#6D4C41")

    # Boton exportar
    def exportar_auditoria():
        items = tree_aud.get_children()
        if not items:
            messagebox.showinfo("Info", "No hay datos para exportar")
            return
        ruta = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")],
                                            initialfile=f"auditoria_{datetime.now().strftime('%Y%m%d')}.csv")
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("ID,Fecha,Hora,Usuario,Accion,Modulo,Datos\n")
                for item in items:
                    vals = tree_aud.item(item, "values")
                    f.write(",".join(str(v) for v in vals) + "\n")
            messagebox.showinfo("Exportado", f"Auditoria exportada a:\n{ruta}")

    btn_export = tk.Button(filtros, text="EXPORTAR CSV", command=exportar_auditoria,
                           bg="#607D8B", fg="white", font=("Segoe UI", 9, "bold"),
                           relief=tk.FLAT, padx=10, pady=3, cursor="hand2")
    btn_export.pack(side=tk.LEFT, padx=5)

    # Cargar datos iniciales
    buscar_auditoria()

# ===== MODULO VENTAS CON LECTOR DE CODIGOS =====
def ver_ventas():
    limpiar()

    # Diccionario para callbacks (referencia adelantada)
    callbacks = {"bienvenida": None, "producto_info": None}

    # ============================================================
    # HEADER PROFESIONAL CON RELOJ, CAJERO Y FOLIO
    # ============================================================
    header_ventas = tk.Frame(main, bg=AZUL_FARMACIA, height=50)
    header_ventas.pack(fill=tk.X)
    header_ventas.pack_propagate(False)

    tk.Label(header_ventas, text="🛒 PUNTO DE VENTA", font=("Segoe UI", 14, "bold"),
            bg=AZUL_FARMACIA, fg="white").pack(side=tk.LEFT, padx=12, pady=12)

    # === RELOJ EN TIEMPO REAL ===
    reloj_frame = tk.Frame(header_ventas, bg=AZUL_FARMACIA)
    reloj_frame.pack(side=tk.RIGHT, padx=15)

    reloj_label = tk.Label(reloj_frame, text="", font=("Segoe UI", 16, "bold"),
                          bg=AZUL_FARMACIA, fg="#FFEB3B")
    reloj_label.pack()
    fecha_label = tk.Label(reloj_frame, text="", font=("Segoe UI", 8),
                          bg=AZUL_FARMACIA, fg="#B3E5FC")
    fecha_label.pack()

    def actualizar_reloj():
        ahora = datetime.now()
        reloj_label.config(text=ahora.strftime("%H:%M:%S"))
        fecha_label.config(text=ahora.strftime("%A %d/%m/%Y").title())
        try:
            header_ventas.after(1000, actualizar_reloj)
        except:
            pass

    actualizar_reloj()

    # === INFO CAJERO Y TURNO ===
    cajero_frame = tk.Frame(header_ventas, bg="#0D47A1", relief=tk.FLAT)
    cajero_frame.pack(side=tk.RIGHT, padx=10, pady=8)

    hora_actual = datetime.now().hour
    turno = "MATUTINO" if 6 <= hora_actual < 14 else "VESPERTINO" if 14 <= hora_actual < 22 else "NOCTURNO"

    tk.Label(cajero_frame, text=f"👤 {usuario_actual}", font=("Segoe UI", 9, "bold"),
            bg="#0D47A1", fg="white", padx=8, pady=2).pack()
    tk.Label(cajero_frame, text=f"Turno: {turno}", font=("Segoe UI", 7),
            bg="#0D47A1", fg="#B3E5FC", padx=8).pack()

    # === PRÓXIMO FOLIO ===
    c.execute("SELECT COUNT(*) FROM ventas WHERE fecha=?", (datetime.now().strftime('%Y-%m-%d'),))
    ventas_hoy = c.fetchone()[0]
    proximo_folio = ventas_hoy + 1

    folio_frame = tk.Frame(header_ventas, bg="#1B5E20", relief=tk.FLAT)
    folio_frame.pack(side=tk.RIGHT, padx=5, pady=8)
    tk.Label(folio_frame, text=f"TICKET #{proximo_folio:04d}", font=("Segoe UI", 10, "bold"),
            bg="#1B5E20", fg="#A5D6A7", padx=10, pady=4).pack()

    # Botón reimprimir último ticket
    def reimprimir_ultimo():
        if not ultimo_folio_venta:
            messagebox.showinfo("Info", "No hay ticket previo para reimprimir")
            return
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta = os.path.join(base_dir, f"ticket_{ultimo_folio_venta}.txt")
        if os.path.exists(ruta):
            try:
                os.startfile(ruta, "print")
                messagebox.showinfo("Reimprimir", f"Ticket {ultimo_folio_venta} enviado a imprimir")
            except:
                messagebox.showinfo("Info", f"Ticket guardado en: {ruta}")
        else:
            messagebox.showinfo("Info", "Archivo de ticket no encontrado")

    btn_reimp = tk.Button(header_ventas, text="🖨️ REIMPRIMIR", command=reimprimir_ultimo,
                          bg="#0D47A1", fg="white", font=("Segoe UI", 8, "bold"),
                          relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
    btn_reimp.pack(side=tk.RIGHT, padx=5, pady=10)
    hover_bind(btn_reimp, "#0D47A1", "#1E88E5")
    
    # BANNER DE OFERTAS ACTIVAS
    hoy_of = datetime.now().strftime("%Y-%m-%d")
    c.execute("""SELECT nombre, tipo, descuento_porcentaje, descuento_monto, bonus_saturnos_extra, color_banner
                 FROM ofertas WHERE activa=1 AND destacada=1 AND fecha_inicio<=? AND fecha_fin>=?
                 ORDER BY id DESC LIMIT 5""", (hoy_of, hoy_of))
    ofertas_banner = c.fetchall()
    if ofertas_banner:
        banner_frame = tk.Frame(main, bg="#FF5722", height=36)
        banner_frame.pack(fill=tk.X)
        banner_frame.pack_propagate(False)
        tk.Label(banner_frame, text="\u2605", font=("Segoe UI", 12), bg="#FF5722", fg="white").pack(side=tk.LEFT, padx=5)
        ofertas_textos = []
        for of in ofertas_banner:
            nombre, tipo, pct, monto, bonus, color = of
            if tipo in ("DESCUENTO_PORCENTAJE",):
                desc_txt = f"-{pct:.0f}%"
            elif tipo == "2X1":
                desc_txt = "2x1"
            elif tipo == "3X2":
                desc_txt = "3x2"
            elif tipo == "DESCUENTO_MONTO":
                desc_txt = f"${monto:.0f} OFF"
            else:
                desc_txt = tipo
            ofertas_textos.append(f"{nombre} {desc_txt} +{bonus:.0f}%\u20B4")
        banner_text_var = tk.StringVar(value="  OFERTAS HOY:  " + "  |  ".join(ofertas_textos))
        banner_lbl = tk.Label(banner_frame, textvariable=banner_text_var, font=("Segoe UI", 9, "bold"),
                              bg="#FF5722", fg="white")
        banner_lbl.pack(side=tk.LEFT, padx=5)

        # Auto-carrusel cada 5 segundos
        banner_idx = [0]
        def rotar_banner():
            if len(ofertas_textos) > 1:
                banner_idx[0] = (banner_idx[0] + 1) % len(ofertas_textos)
                banner_text_var.set(f"  \u2605 OFERTA:  {ofertas_textos[banner_idx[0]]}")
            try:
                banner_frame.after(5000, rotar_banner)
            except:
                pass
        if len(ofertas_textos) > 1:
            banner_frame.after(5000, rotar_banner)

    # ============================================================
    # BARRA DE TECLAS RÁPIDAS Y ACCIONES
    # ============================================================
    shortcuts_bar = tk.Frame(main, bg="#263238", height=35)
    shortcuts_bar.pack(fill=tk.X)
    shortcuts_bar.pack_propagate(False)

    # Ventas pausadas (almacenamiento temporal)
    ventas_pausadas = []

    # === TECLAS RÁPIDAS ===
    shortcuts_left = tk.Frame(shortcuts_bar, bg="#263238")
    shortcuts_left.pack(side=tk.LEFT, padx=10, pady=5)

    tk.Label(shortcuts_left, text="⌨️ ATAJOS:", font=("Segoe UI", 8, "bold"),
            bg="#263238", fg="#90A4AE").pack(side=tk.LEFT, padx=5)

    atajos_info = [
        ("F2", "Buscar", "#42A5F5"),
        ("F5", "Efectivo", "#4CAF50"),
        ("F8", "Pausar", "#FF9800"),
        ("F12", "Cobrar", "#F44336"),
        ("ESC", "Cancelar", "#9E9E9E"),
    ]

    for tecla, accion, color in atajos_info:
        frame_atajo = tk.Frame(shortcuts_left, bg="#37474F", relief=tk.RAISED, bd=1)
        frame_atajo.pack(side=tk.LEFT, padx=2)
        tk.Label(frame_atajo, text=tecla, font=("Consolas", 8, "bold"),
                bg="#37474F", fg=color, padx=4, pady=1).pack(side=tk.LEFT)
        tk.Label(frame_atajo, text=accion, font=("Segoe UI", 7),
                bg="#37474F", fg="#B0BEC5", padx=3, pady=1).pack(side=tk.LEFT)

    # === BOTONES DE ACCIÓN RÁPIDA ===
    shortcuts_right = tk.Frame(shortcuts_bar, bg="#263238")
    shortcuts_right.pack(side=tk.RIGHT, padx=10, pady=5)

    def pausar_venta():
        """Pausa la venta actual y la guarda temporalmente."""
        if not carrito_items:
            messagebox.showinfo("Info", "No hay productos en el carrito para pausar")
            return
        venta_pausada = {
            "cliente": cliente_var.get(),
            "items": list(carrito_items),
            "hora": datetime.now().strftime("%H:%M"),
            "total": sum(float(item[5]) for item in carrito_items)
        }
        ventas_pausadas.append(venta_pausada)
        # Limpiar carrito
        carrito_items.clear()
        ofertas_carrito.clear()
        actualizar_carrito()
        efectivo_var.set("")
        tarjeta_var.set("")
        vale_var.set("")
        # Actualizar botón
        btn_recuperar.config(text=f"📋 RECUPERAR ({len(ventas_pausadas)})")
        messagebox.showinfo("Venta Pausada", f"Venta guardada temporalmente.\nVentas pausadas: {len(ventas_pausadas)}")

    def recuperar_venta():
        """Recupera la última venta pausada."""
        if not ventas_pausadas:
            messagebox.showinfo("Info", "No hay ventas pausadas")
            return
        if carrito_items:
            if not messagebox.askyesno("Confirmar", "Hay productos en el carrito actual.\n¿Desea reemplazarlos con la venta pausada?"):
                return
        # Recuperar última venta pausada
        venta = ventas_pausadas.pop()
        cliente_var.set(venta["cliente"])
        carrito_items.clear()
        carrito_items.extend(venta["items"])
        actualizar_carrito()
        # Actualizar botón
        if ventas_pausadas:
            btn_recuperar.config(text=f"📋 RECUPERAR ({len(ventas_pausadas)})")
        else:
            btn_recuperar.config(text="📋 RECUPERAR")
        messagebox.showinfo("Venta Recuperada", f"Venta de {venta['cliente']} recuperada.\nTotal: ${venta['total']:,.2f}")

    def ver_ultimas_ventas():
        """Muestra mini historial de últimas ventas del día."""
        win = tk.Toplevel(main)
        win.title("📊 Últimas Ventas del Día")
        win.geometry("600x400")
        win.configure(bg="#1A2332")

        tk.Label(win, text="📊 ÚLTIMAS VENTAS DEL DÍA", font=("Segoe UI", 14, "bold"),
                bg="#1A2332", fg="#4FC3F7").pack(pady=10)

        hoy = datetime.now().strftime('%Y-%m-%d')
        c.execute("""SELECT folio, hora, total, tipo_pago, cl.nombre
                     FROM ventas v LEFT JOIN clientes cl ON v.cliente_id=cl.id
                     WHERE v.fecha=? ORDER BY v.id DESC LIMIT 15""", (hoy,))
        ventas = c.fetchall()

        tree_frame = tk.Frame(win, bg="#1A2332")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = ("FOLIO", "HORA", "CLIENTE", "TOTAL", "PAGO")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.column("CLIENTE", width=150)

        for v in ventas:
            tree.insert("", "end", values=(v[0], v[1], v[4] or "PUBLICO GENERAL", f"${v[2]:,.2f}", v[3]))

        tree.pack(fill=tk.BOTH, expand=True)

        # Totales del día
        c.execute("SELECT COUNT(*), SUM(total), SUM(monto_efectivo), SUM(monto_tarjeta) FROM ventas WHERE fecha=?", (hoy,))
        totales = c.fetchone()
        total_ventas = totales[0] or 0
        total_monto = totales[1] or 0
        total_efec = totales[2] or 0
        total_tarj = totales[3] or 0

        totales_frame = tk.Frame(win, bg="#0D1B2A")
        totales_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(totales_frame, text=f"🛒 Ventas: {total_ventas}  |  💰 Total: ${total_monto:,.2f}  |  💵 Efectivo: ${total_efec:,.2f}  |  💳 Tarjeta: ${total_tarj:,.2f}",
                font=("Segoe UI", 10, "bold"), bg="#0D1B2A", fg="#A5D6A7").pack(pady=8)

    def hacer_corte_caja():
        """Ventana para realizar corte de caja."""
        win = tk.Toplevel(main)
        win.title("💰 CORTE DE CAJA")
        win.geometry("500x600")
        win.configure(bg="#1A2332")

        tk.Label(win, text="💰 CORTE DE CAJA", font=("Segoe UI", 16, "bold"),
                bg="#1A2332", fg="#4FC3F7").pack(pady=15)

        hoy = datetime.now().strftime('%Y-%m-%d')

        # Obtener datos del día
        c.execute("""SELECT COUNT(*), COALESCE(SUM(total),0), COALESCE(SUM(monto_efectivo),0), COALESCE(SUM(monto_tarjeta),0)
                     FROM ventas WHERE fecha=?""", (hoy,))
        datos = c.fetchone()
        num_ventas, total_ventas, total_efec, total_tarj = datos

        # Frame de resumen
        resumen_frame = tk.Frame(win, bg="#0D1B2A", relief=tk.RIDGE, bd=2)
        resumen_frame.pack(fill=tk.X, padx=20, pady=10)

        datos_resumen = [
            ("📅 Fecha:", datetime.now().strftime('%d/%m/%Y')),
            ("👤 Cajero:", usuario_actual),
            ("🛒 Total Ventas:", f"{num_ventas}"),
            ("💰 Venta Total:", f"${total_ventas:,.2f}"),
            ("💵 Efectivo:", f"${total_efec:,.2f}"),
            ("💳 Tarjeta:", f"${total_tarj:,.2f}"),
        ]

        for label, valor in datos_resumen:
            row = tk.Frame(resumen_frame, bg="#0D1B2A")
            row.pack(fill=tk.X, padx=15, pady=3)
            tk.Label(row, text=label, font=("Segoe UI", 10), bg="#0D1B2A", fg="#90A4AE").pack(side=tk.LEFT)
            tk.Label(row, text=valor, font=("Segoe UI", 10, "bold"), bg="#0D1B2A", fg="white").pack(side=tk.RIGHT)

        # Separador
        tk.Frame(win, bg="#37474F", height=2).pack(fill=tk.X, padx=20, pady=10)

        # Conteo de efectivo
        tk.Label(win, text="💵 CONTEO DE EFECTIVO EN CAJA", font=("Segoe UI", 12, "bold"),
                bg="#1A2332", fg="#FFC107").pack(pady=5)

        conteo_frame = tk.Frame(win, bg="#263238", relief=tk.RIDGE, bd=1)
        conteo_frame.pack(fill=tk.X, padx=20, pady=5)

        denominaciones = [
            ("$1000", 1000), ("$500", 500), ("$200", 200), ("$100", 100),
            ("$50", 50), ("$20", 20), ("$10", 10), ("$5", 5), ("$1", 1), ("$0.50", 0.5)
        ]

        conteo_vars = {}
        for i, (den, val) in enumerate(denominaciones):
            row = tk.Frame(conteo_frame, bg="#263238")
            row.pack(fill=tk.X, padx=10, pady=2)
            tk.Label(row, text=den, font=("Segoe UI", 9), bg="#263238", fg="white", width=8).pack(side=tk.LEFT)
            tk.Label(row, text="x", font=("Segoe UI", 9), bg="#263238", fg="#90A4AE").pack(side=tk.LEFT, padx=5)
            var = tk.StringVar(value="0")
            conteo_vars[val] = var
            tk.Entry(row, textvariable=var, font=("Segoe UI", 9), width=5, bg="#37474F", fg="white",
                    insertbackground="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

        # Total contado
        total_contado_var = tk.StringVar(value="$0.00")
        total_frame = tk.Frame(win, bg="#1B5E20")
        total_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(total_frame, text="TOTAL CONTADO:", font=("Segoe UI", 12, "bold"),
                bg="#1B5E20", fg="white").pack(side=tk.LEFT, padx=15, pady=8)
        tk.Label(total_frame, textvariable=total_contado_var, font=("Segoe UI", 14, "bold"),
                bg="#1B5E20", fg="#A5D6A7").pack(side=tk.RIGHT, padx=15, pady=8)

        def calcular_conteo(*args):
            total = 0
            for val, var in conteo_vars.items():
                try:
                    cant = int(var.get() or 0)
                    total += val * cant
                except:
                    pass
            total_contado_var.set(f"${total:,.2f}")

        for var in conteo_vars.values():
            var.trace_add("write", calcular_conteo)

        # Diferencia
        diferencia_var = tk.StringVar(value="$0.00")
        dif_frame = tk.Frame(win, bg="#1A2332")
        dif_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(dif_frame, text="Diferencia (Contado - Esperado):", font=("Segoe UI", 9),
                bg="#1A2332", fg="#90A4AE").pack(side=tk.LEFT)
        tk.Label(dif_frame, textvariable=diferencia_var, font=("Segoe UI", 10, "bold"),
                bg="#1A2332", fg="#FFC107").pack(side=tk.RIGHT)

        def actualizar_diferencia(*args):
            try:
                contado = float(total_contado_var.get().replace("$", "").replace(",", ""))
                dif = contado - total_efec
                color = "#4CAF50" if abs(dif) < 1 else "#F44336" if dif < 0 else "#FF9800"
                diferencia_var.set(f"${dif:,.2f}")
            except:
                pass

        total_contado_var.trace_add("write", actualizar_diferencia)

        # Botón guardar corte
        def guardar_corte():
            try:
                contado = float(total_contado_var.get().replace("$", "").replace(",", ""))
            except:
                contado = 0
            diferencia = contado - total_efec

            # Guardar en BD (crear tabla si no existe)
            try:
                c.execute("""CREATE TABLE IF NOT EXISTS cortes_caja (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT, hora TEXT, cajero TEXT, num_ventas INTEGER,
                    total_ventas REAL, efectivo_esperado REAL, efectivo_contado REAL,
                    diferencia REAL, tarjeta REAL, observaciones TEXT)""")
                c.execute("""INSERT INTO cortes_caja (fecha, hora, cajero, num_ventas, total_ventas,
                            efectivo_esperado, efectivo_contado, diferencia, tarjeta, observaciones)
                            VALUES (?,?,?,?,?,?,?,?,?,?)""",
                         (hoy, datetime.now().strftime('%H:%M:%S'), usuario_actual, num_ventas,
                          total_ventas, total_efec, contado, diferencia, total_tarj, ""))
                conn.commit()
                messagebox.showinfo("Corte Guardado", f"Corte de caja guardado correctamente.\nDiferencia: ${diferencia:,.2f}")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar corte: {e}")

        tk.Button(win, text="💾 GUARDAR CORTE", command=guardar_corte,
                 bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"),
                 relief=tk.RAISED, padx=20, pady=10, cursor="hand2").pack(pady=15)

    def ver_devoluciones():
        """Ventana para registrar devoluciones."""
        win = tk.Toplevel(main)
        win.title("↩️ DEVOLUCIONES")
        win.geometry("700x500")
        win.configure(bg="#1A2332")

        tk.Label(win, text="↩️ REGISTRAR DEVOLUCIÓN", font=("Segoe UI", 14, "bold"),
                bg="#1A2332", fg="#4FC3F7").pack(pady=10)

        # Buscar folio
        buscar_frame = tk.Frame(win, bg="#1A2332")
        buscar_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(buscar_frame, text="Folio de venta:", font=("Segoe UI", 10),
                bg="#1A2332", fg="white").pack(side=tk.LEFT, padx=5)
        folio_dev_var = tk.StringVar()
        tk.Entry(buscar_frame, textvariable=folio_dev_var, font=("Segoe UI", 11), width=25,
                bg="#263238", fg="white", insertbackground="white").pack(side=tk.LEFT, padx=5)

        productos_venta = []
        tree_dev = None

        def buscar_venta():
            nonlocal productos_venta, tree_dev
            folio = folio_dev_var.get().strip()
            if not folio:
                return

            c.execute("""SELECT v.id, v.fecha, v.total, cl.nombre FROM ventas v
                         LEFT JOIN clientes cl ON v.cliente_id=cl.id WHERE v.folio=?""", (folio,))
            venta = c.fetchone()
            if not venta:
                messagebox.showwarning("No encontrado", f"No se encontró la venta {folio}")
                return

            venta_id, fecha, total, cliente = venta
            info_venta_lbl.config(text=f"Venta: {folio} | Fecha: {fecha} | Cliente: {cliente or 'PUBLICO GENERAL'} | Total: ${total:,.2f}")

            # Obtener productos
            c.execute("""SELECT p.codigo, p.nombre, dv.cantidad, dv.precio_unitario, dv.subtotal
                         FROM detalle_ventas dv JOIN productos p ON dv.producto_id=p.id
                         WHERE dv.venta_id=?""", (venta_id,))
            productos_venta = c.fetchall()

            # Mostrar en tree
            for item in tree_dev.get_children():
                tree_dev.delete(item)
            for prod in productos_venta:
                tree_dev.insert("", "end", values=prod)

        tk.Button(buscar_frame, text="🔍 BUSCAR", command=buscar_venta,
                 bg="#1976D2", fg="white", font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, padx=10, cursor="hand2").pack(side=tk.LEFT, padx=10)

        # Info de la venta
        info_venta_lbl = tk.Label(win, text="", font=("Segoe UI", 10),
                                  bg="#1A2332", fg="#A5D6A7")
        info_venta_lbl.pack(pady=5)

        # Tabla de productos
        tree_frame = tk.Frame(win, bg="#1A2332")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        cols = ("CÓDIGO", "PRODUCTO", "CANT", "PRECIO", "SUBTOTAL")
        tree_dev = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)
        for col in cols:
            tree_dev.heading(col, text=col)
        tree_dev.column("CÓDIGO", width=100)
        tree_dev.column("PRODUCTO", width=250)
        tree_dev.column("CANT", width=60)
        tree_dev.column("PRECIO", width=80)
        tree_dev.column("SUBTOTAL", width=80)
        tree_dev.pack(fill=tk.BOTH, expand=True)

        # Motivo y acción
        motivo_frame = tk.Frame(win, bg="#1A2332")
        motivo_frame.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(motivo_frame, text="Motivo:", font=("Segoe UI", 9),
                bg="#1A2332", fg="white").pack(side=tk.LEFT, padx=5)
        motivo_var = tk.StringVar(value="DEFECTUOSO")
        ttk.Combobox(motivo_frame, textvariable=motivo_var, width=20,
                    values=["DEFECTUOSO", "CADUCADO", "ERROR CAJERO", "CAMBIO PRODUCTO", "OTRO"],
                    state="readonly").pack(side=tk.LEFT, padx=5)

        def procesar_devolucion():
            sel = tree_dev.selection()
            if not sel:
                messagebox.showwarning("Seleccionar", "Selecciona un producto a devolver")
                return
            # Aquí iría la lógica de devolución
            messagebox.showinfo("Devolución", "Funcionalidad de devolución en desarrollo.\nContacte al administrador.")

        tk.Button(win, text="↩️ PROCESAR DEVOLUCIÓN", command=procesar_devolucion,
                 bg="#F44336", fg="white", font=("Segoe UI", 11, "bold"),
                 relief=tk.RAISED, padx=15, pady=8, cursor="hand2").pack(pady=15)

    # Botones de acción
    btn_pausar = tk.Button(shortcuts_right, text="⏸️ PAUSAR", command=pausar_venta,
                          bg="#FF9800", fg="white", font=("Segoe UI", 8, "bold"),
                          relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
    btn_pausar.pack(side=tk.LEFT, padx=2)

    btn_recuperar = tk.Button(shortcuts_right, text="📋 RECUPERAR", command=recuperar_venta,
                             bg="#2196F3", fg="white", font=("Segoe UI", 8, "bold"),
                             relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
    btn_recuperar.pack(side=tk.LEFT, padx=2)

    btn_historial = tk.Button(shortcuts_right, text="📊 ÚLTIMAS VENTAS", command=ver_ultimas_ventas,
                             bg="#673AB7", fg="white", font=("Segoe UI", 8, "bold"),
                             relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
    btn_historial.pack(side=tk.LEFT, padx=2)

    btn_corte = tk.Button(shortcuts_right, text="💰 CORTE CAJA", command=hacer_corte_caja,
                         bg="#4CAF50", fg="white", font=("Segoe UI", 8, "bold"),
                         relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
    btn_corte.pack(side=tk.LEFT, padx=2)

    btn_devol = tk.Button(shortcuts_right, text="↩️ DEVOLUCIÓN", command=ver_devoluciones,
                         bg="#F44336", fg="white", font=("Segoe UI", 8, "bold"),
                         relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
    btn_devol.pack(side=tk.LEFT, padx=2)

    content = tk.Frame(main, bg="#F5F5F5")
    content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # PANEL IZQUIERDO
    left_panel = tk.Frame(content, bg="white", relief=tk.RIDGE, bd=2)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Ofertas aplicadas al carrito (tracking interno)
    ofertas_carrito = {}  # codigo_producto -> oferta dict

    # FOLIO Y VENDEDOR
    info_frame = tk.Frame(left_panel, bg="white")
    info_frame.pack(fill=tk.X, padx=10, pady=10)
    
    folio = f"V{datetime.now().strftime('%Y%m%d%H%M%S')}"
    tk.Label(info_frame, text=f"Folio: {folio}", font=("Arial", 10, "bold"),
            bg="white").pack(side=tk.LEFT, padx=10)
    tk.Label(info_frame, text=f"Vendedor: {usuario_actual}", font=("Arial", 10),
            bg="white").pack(side=tk.LEFT, padx=10)

    # ===== PANEL INFO PRODUCTO ESCANEADO (AZUL) =====
    info_prod_frame = tk.Frame(left_panel, bg="#E3F2FD", relief=tk.RIDGE, bd=2)
    info_prod_frame.pack(fill=tk.X, padx=10, pady=5)

    prod_nombre_lbl = tk.Label(info_prod_frame, text="Escanea un producto...",
                               font=("Segoe UI", 10, "bold"), bg="#E3F2FD", fg="#1565C0", anchor="w")
    prod_nombre_lbl.pack(fill=tk.X, padx=10, pady=(8, 2))

    precios_frame = tk.Frame(info_prod_frame, bg="#E3F2FD")
    precios_frame.pack(fill=tk.X, padx=10, pady=5)

    col_izq = tk.Frame(precios_frame, bg="#E3F2FD")
    col_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    precio_normal_lbl = tk.Label(col_izq, text="Normal: $0.00", font=("Segoe UI", 9),
                                 bg="#E3F2FD", fg="#666", anchor="w")
    precio_normal_lbl.pack(anchor="w")

    precio_oferta_lbl = tk.Label(col_izq, text="Oferta (35%): $0.00", font=("Segoe UI", 11, "bold"),
                                 bg="#E3F2FD", fg="#2E7D32", anchor="w")
    precio_oferta_lbl.pack(anchor="w")

    saturnos_gana_lbl = tk.Label(col_izq, text="⭐ Ganas: 0 Saturnos", font=("Segoe UI", 9, "bold"),
                                 bg="#E3F2FD", fg="#F57F17", anchor="w")
    saturnos_gana_lbl.pack(anchor="w")

    col_der = tk.Frame(precios_frame, bg="#E3F2FD")
    col_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    credito_precio_lbl = tk.Label(col_der, text="A crédito: $0.00", font=("Segoe UI", 9),
                                  bg="#E3F2FD", fg="#1565C0", anchor="w")
    credito_precio_lbl.pack(anchor="w")

    credito_pagos_lbl = tk.Label(col_der, text="4 pagos de: $0.00", font=("Segoe UI", 10, "bold"),
                                 bg="#E3F2FD", fg="#1976D2", anchor="w")
    credito_pagos_lbl.pack(anchor="w")

    stock_lbl = tk.Label(col_der, text="Stock: 0", font=("Segoe UI", 9),
                         bg="#E3F2FD", fg="#666", anchor="w")
    stock_lbl.pack(anchor="w")

    # CLIENTE
    cliente_frame = tk.Frame(left_panel, bg="white")
    cliente_frame.pack(fill=tk.X, padx=10, pady=5)
    
    tk.Label(cliente_frame, text="Cliente:", font=("Arial", 9, "bold"),
            bg="white").pack(side=tk.LEFT, padx=5)
    
    cliente_var = tk.StringVar(value="PUBLICO GENERAL")
    cliente_combo = ttk.Combobox(cliente_frame, textvariable=cliente_var,
                                width=35, state="readonly")
    c.execute("SELECT nombre FROM clientes")
    cliente_combo['values'] = [row[0] for row in c.fetchall()]
    cliente_combo.pack(side=tk.LEFT, padx=5)
    
    # ESCANEAR TARJETA SATURNOS
    tarjeta_frame = tk.Frame(left_panel, bg="#FFF8E1")
    tarjeta_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
    tk.Label(tarjeta_frame, text="\u20B4 Tarjeta Saturnos:", font=("Arial", 9, "bold"),
            bg="#FFF8E1", fg="#F57F17").pack(side=tk.LEFT, padx=5)
    tarjeta_sat_entry = tk.Entry(tarjeta_frame, width=25, font=("Arial", 9))
    tarjeta_sat_entry.pack(side=tk.LEFT, padx=5)
    tarjeta_sat_info = tk.Label(tarjeta_frame, text="", font=("Arial", 8), bg="#FFF8E1", fg="#4CAF50")
    tarjeta_sat_info.pack(side=tk.LEFT, padx=5)

    def escanear_tarjeta(event=None):
        """Busca cliente por código de tarjeta Saturnos (SAT-...)."""
        codigo = tarjeta_sat_entry.get().strip().upper()
        if not codigo:
            return
        c.execute("""SELECT cl.nombre, m.saldo_saturnos, m.estado_tarjeta, m.codigo_tarjeta
                     FROM monederos m JOIN clientes cl ON m.cliente_id=cl.id
                     WHERE m.codigo_tarjeta=?""", (codigo,))
        row = c.fetchone()
        if not row:
            tarjeta_sat_info.config(text="Tarjeta no encontrada", fg="#D32F2F")
            beep_error()
            return
        nombre, saldo, estado, tarjeta_cod = row
        if estado == "BLOQUEADA":
            tarjeta_sat_info.config(text=f"BLOQUEADA - {nombre}", fg="#D32F2F")
            beep_error()
            return
        if estado == "ANULADA":
            tarjeta_sat_info.config(text=f"ANULADA - {nombre}", fg="#D32F2F")
            beep_error()
            return
        # Seleccionar cliente automáticamente
        cliente_var.set(nombre)
        tarjeta_sat_info.config(text=f"{nombre} | Saldo: {saldo:,.0f} \u20B4", fg="#4CAF50")
        # Mostrar bienvenida en panel COBRO (si el callback está disponible)
        if callbacks.get("bienvenida"):
            callbacks["bienvenida"](nombre, tarjeta_cod, saldo)
        beep_ok()
        # Mover foco al campo de productos
        search_entry.focus()

    tarjeta_sat_entry.bind("<Return>", escanear_tarjeta)
    tk.Button(tarjeta_frame, text="BUSCAR", command=escanear_tarjeta,
             bg="#FFC107", fg="#333", font=("Arial", 8, "bold"),
             relief=tk.FLAT, padx=8, pady=2, cursor="hand2").pack(side=tk.LEFT, padx=3)

    # BUSCAR PRODUCTO / CÓDIGO DE BARRAS / ESCÁNER
    search_frame = tk.Frame(left_panel, bg="white")
    search_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(search_frame, text="🔍 Código o nombre:", font=("Arial", 9, "bold"),
            bg="white").pack(side=tk.LEFT, padx=5)

    search_entry = tk.Entry(search_frame, width=40, font=("Arial", 9))
    search_entry.pack(side=tk.LEFT, padx=5)
    search_entry.focus()

    # Indicador de escáner
    scanner_label = tk.Label(search_frame, text="", font=("Arial", 8), bg="white", fg="#4CAF50")
    scanner_label.pack(side=tk.LEFT, padx=5)

    # Detección de escáner: entrada rápida (< 80ms entre teclas)
    scanner_state = {"last_key_time": 0, "buffer": "", "rapid_count": 0}

    def on_key_press(event):
        """Detecta entrada rápida de escáner vs escritura manual."""
        now = time.time()
        char = event.char
        if not char or char in ('\r', '\n'):
            return
        elapsed = now - scanner_state["last_key_time"]
        scanner_state["last_key_time"] = now
        if elapsed < 0.08:  # menos de 80ms = escáner
            scanner_state["rapid_count"] += 1
        else:
            scanner_state["rapid_count"] = 0

    search_entry.bind("<KeyPress>", on_key_press)

    # Mensaje de error visible
    error_frame = tk.Frame(left_panel, bg="white")
    error_frame.pack(fill=tk.X, padx=10)
    error_label = tk.Label(error_frame, text="", font=("Segoe UI", 9, "bold"),
                          bg="white", fg="#D32F2F")
    error_label.pack(side=tk.LEFT, padx=5)

    def limpiar_error():
        error_label.config(text="")
    def mostrar_error(msg):
        error_label.config(text=msg)
        left_panel.after(4000, limpiar_error)
    def mostrar_ok(msg):
        scanner_label.config(text=msg, fg="#4CAF50")
        left_panel.after(3000, lambda: scanner_label.config(text=""))

    # Notificación de oferta
    oferta_notif = tk.Frame(left_panel, bg="#FFF3E0")
    oferta_notif_label = tk.Label(oferta_notif, text="", font=("Segoe UI", 9, "bold"),
                                   bg="#FFF3E0", fg="#E65100", wraplength=700, justify="left")
    oferta_notif_label.pack(padx=10, pady=4, anchor="w")

    def mostrar_oferta_notif(msg):
        oferta_notif_label.config(text=msg)
        oferta_notif.pack(fill=tk.X, padx=10, pady=(0, 2), before=carrito_header_lbl)
        left_panel.after(6000, lambda: oferta_notif.pack_forget())

    # CARRITO
    carrito_header_lbl = tk.Label(left_panel, text="🛒 Carrito de compra", font=("Arial", 10, "bold"),
            bg="white")
    carrito_header_lbl.pack(pady=10)

    tree_frame = tk.Frame(left_panel, bg="white")
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    cols = ("CÓDIGO", "DESCRIPCIÓN", "PRECIO", "OFERTA", "CANT", "SUBTOTAL")
    tree_carrito = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12)

    for col in cols:
        tree_carrito.heading(col, text=col)
    
    tree_carrito.column("CÓDIGO", width=90)
    tree_carrito.column("DESCRIPCIÓN", width=240)
    tree_carrito.column("PRECIO", width=70)
    tree_carrito.column("OFERTA", width=80)
    tree_carrito.column("CANT", width=50)
    tree_carrito.column("SUBTOTAL", width=80)
    
    scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_carrito.yview)
    tree_carrito.configure(yscrollcommand=scroll.set)
    
    tree_carrito.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    carrito_items = []
    
    def agregar_por_codigo(codigo, desde_scanner=False):
        """Agrega producto al carrito directamente por código, aplicando ofertas."""
        c.execute("SELECT codigo, nombre, precio_venta, stock, categoria, laboratorio, imagen FROM productos WHERE codigo=?", (codigo,))
        producto = c.fetchone()

        if producto:
            precio_normal = float(producto[2])
            cat = producto[4] or ""
            lab = producto[5] or ""
            img_path = producto[6] or ""

            # Mostrar producto escaneado en panel azul y COBRO
            if callbacks.get("producto_info"):
                callbacks["producto_info"](producto[0], producto[1], precio_normal, producto[3], img_path)
            # Llenar campos de pago automáticamente
            if callbacks.get("llenar_campos"):
                callbacks["llenar_campos"]()

            # Obtener precio_oferta (con 35% descuento base) de la BD
            c.execute("SELECT precio_oferta FROM productos WHERE codigo=?", (producto[0],))
            oferta_row = c.fetchone()
            precio_base_oferta = oferta_row[0] if oferta_row and oferta_row[0] else precio_normal * 0.65

            # Buscar oferta especial adicional para este producto
            c.execute("SELECT id FROM clientes WHERE nombre=?", (cliente_var.get(),))
            cl_row = c.fetchone()
            cli_id = cl_row[0] if cl_row else 0
            oferta = obtener_oferta_producto(producto[0], producto[1], cat, lab, cli_id)

            # SIEMPRE usar precio con 35% descuento como base
            precio_final = precio_base_oferta
            oferta_txt = "-35%"
            if oferta:
                precio_final, descuento = calcular_precio_oferta(precio_normal, oferta)
                ofertas_carrito[producto[0]] = oferta
                if oferta["tipo"] == "DESCUENTO_PORCENTAJE":
                    oferta_txt = f"-{oferta['descuento_porcentaje']:.0f}%"
                elif oferta["tipo"] == "DESCUENTO_MONTO":
                    oferta_txt = f"${oferta['descuento_monto']:.0f}OFF"
                elif oferta["tipo"] == "2X1":
                    oferta_txt = "2x1"
                elif oferta["tipo"] == "3X2":
                    oferta_txt = "3x2"
                else:
                    oferta_txt = oferta["tipo"][:8]
                # Notificación visual
                ahorro = precio_normal - precio_final
                mostrar_oferta_notif(
                    f"\u2605 OFERTA: {oferta['nombre']} | {producto[1][:30]} "
                    f"| Normal: ${precio_normal:,.2f} -> Oferta: ${precio_final:,.2f} "
                    f"| Ahorras: ${ahorro:,.2f} | +{oferta['bonus_saturnos']:.0f}% Saturnos extra")

            # Verificar si ya existe en carrito
            existe = False
            for idx, item in enumerate(carrito_items):
                if item[0] == producto[0]:
                    nueva_cant = item[3] + 1
                    # Recalcular para 2x1/3x2
                    if oferta and oferta["tipo"] in ("2X1", "3X2"):
                        p_of, _ = calcular_precio_oferta(precio_normal, oferta, nueva_cant)
                        carrito_items[idx] = (producto[0], producto[1], precio_normal,
                                            oferta_txt, nueva_cant, round(p_of * nueva_cant, 2))
                    else:
                        carrito_items[idx] = (producto[0], producto[1], precio_normal,
                                            oferta_txt, nueva_cant, round(precio_final * nueva_cant, 2))
                    existe = True
                    break

            if not existe:
                carrito_items.append((producto[0], producto[1], precio_normal, oferta_txt, 1, precio_final))

            actualizar_carrito()
            search_entry.delete(0, tk.END)

            # Feedback de escáner
            beep_ok()
            mostrar_ok(f"OK: {producto[1][:30]}")
            limpiar_error()

            # Historial de escáner
            historial_escaner.insert(0, {"codigo": codigo, "nombre": producto[1], "hora": datetime.now().strftime("%H:%M:%S")})
            if len(historial_escaner) > 10:
                historial_escaner.pop()

            return True

        if desde_scanner:
            beep_error()
            mostrar_error(f"CODIGO NO ENCONTRADO: {codigo}")
        return False

    def buscar_o_agregar(event=None):
        """Si es código exacto, agrega. Si no, busca. Detecta escáner automáticamente."""
        busqueda = search_entry.get().strip().upper()

        if not busqueda:
            return

        # Detectar tarjeta Saturnos escaneada en campo de productos
        if busqueda.startswith("SAT-"):
            tarjeta_sat_entry.delete(0, tk.END)
            tarjeta_sat_entry.insert(0, busqueda)
            escanear_tarjeta()
            search_entry.delete(0, tk.END)
            return

        # Detectar si viene del escáner (entrada rápida)
        es_scanner = scanner_state["rapid_count"] >= 3

        # Validar formato de código de barras
        if es_codigo_barras(busqueda) or es_scanner:
            if agregar_por_codigo(busqueda, desde_scanner=True):
                scanner_state["rapid_count"] = 0
                return
            # Si es escáner y no encontró, no abrir búsqueda
            if es_scanner:
                scanner_state["rapid_count"] = 0
                return

        # Intentar por código exacto
        if agregar_por_codigo(busqueda):
            return

        # Si no es código, buscar normalmente
        buscar()
    
    def buscar():
        busqueda = search_entry.get()
        if len(busqueda) < 2:
            return

        resultado_win = tk.Toplevel(main)
        resultado_win.title("Resultados de búsqueda")
        resultado_win.geometry("1200x600")
        resultado_win.configure(bg="#F5F7FA")

        # Frame principal con scroll
        main_frame = tk.Frame(resultado_win, bg="#F5F7FA")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas con scroll para productos con imagen
        canvas = tk.Canvas(main_frame, bg="#F5F7FA", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#F5F7FA")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        c.execute("SELECT codigo, nombre, precio_venta, stock, imagen FROM productos WHERE nombre LIKE ? LIMIT 50",
                 (f"%{busqueda}%",))

        productos_busq = c.fetchall()
        img_refs = []  # Mantener referencias a las imagenes
        producto_seleccionado = [None]

        for idx, row in enumerate(productos_busq):
            codigo, nombre, precio, stock, img_path = row

            # Frame para cada producto
            prod_frame = tk.Frame(scrollable_frame, bg="white", relief="raised", bd=1)
            prod_frame.pack(fill=tk.X, padx=5, pady=3)

            # Cargar imagen
            img_label = tk.Label(prod_frame, bg="white", width=60, height=60)
            img_label.pack(side=tk.LEFT, padx=5, pady=5)

            base_dir = os.path.dirname(os.path.abspath(__file__))
            img_loaded = False

            if img_path:
                img_full_path = os.path.join(base_dir, img_path)
                if os.path.exists(img_full_path):
                    try:
                        img = Image.open(img_full_path)
                        img = img.resize((55, 55), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        img_label.configure(image=photo, width=55, height=55)
                        img_refs.append(photo)
                        img_loaded = True
                    except:
                        pass

            # Si no se cargó imagen, usar placeholder genérico
            if not img_loaded:
                placeholder_path = os.path.join(base_dir, "imagenes", "productos", "_placeholder.png")
                if os.path.exists(placeholder_path):
                    try:
                        img = Image.open(placeholder_path)
                        img = img.resize((55, 55), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        img_label.configure(image=photo, width=55, height=55)
                        img_refs.append(photo)
                    except:
                        img_label.configure(text="📦", font=("Arial", 18), width=6, height=3)
                else:
                    img_label.configure(text="📦", font=("Arial", 18), width=6, height=3)

            # Info del producto
            info_frame = tk.Frame(prod_frame, bg="white")
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

            tk.Label(info_frame, text=nombre[:60], font=("Segoe UI", 10, "bold"),
                    bg="white", anchor="w").pack(anchor="w")
            tk.Label(info_frame, text=f"Código: {codigo}", font=("Segoe UI", 9),
                    bg="white", fg="#666", anchor="w").pack(anchor="w")

            # Calcular saturnos que se ganan
            c.execute("SELECT porcentaje_generico, porcentaje_patente FROM configuracion_saturnos WHERE id=1")
            sat_row = c.fetchone()
            pct_gen = sat_row[0] if sat_row else 10.0
            pct_pat = sat_row[1] if sat_row else 8.0

            # Determinar si es genérico
            c.execute("SELECT laboratorio FROM productos WHERE codigo=?", (codigo,))
            lab_row = c.fetchone()
            lab = lab_row[0] if lab_row else ""
            es_generico = "GENERICO" in (lab or "").upper() or "GENÉRICO" in nombre.upper()
            pct_sat = pct_gen if es_generico else pct_pat
            saturnos = round(precio * pct_sat / 100, 2)

            tk.Label(info_frame, text=f"⭐ +{saturnos:.0f} Saturnos ({pct_sat:.0f}%)", font=("Segoe UI", 9, "bold"),
                    bg="white", fg="#F57F17", anchor="w").pack(anchor="w")

            # Precio y stock
            precio_frame = tk.Frame(prod_frame, bg="white")
            precio_frame.pack(side=tk.RIGHT, padx=10)

            tk.Label(precio_frame, text=f"${precio:,.2f}", font=("Segoe UI", 14, "bold"),
                    bg="white", fg="#27AE60").pack()
            stock_color = "#27AE60" if stock > 5 else "#F44336" if stock <= 0 else "#FF9800"
            tk.Label(precio_frame, text=f"Stock: {stock}", font=("Segoe UI", 9),
                    bg="white", fg=stock_color).pack()

            # Boton agregar
            def hacer_agregar(cod=codigo):
                producto_seleccionado[0] = cod
                resultado_win.destroy()
                agregar_por_codigo(cod)

            btn_add = tk.Button(prod_frame, text="+ AGREGAR", command=hacer_agregar,
                              bg="#27AE60", fg="white", font=("Segoe UI", 9, "bold"),
                              padx=10, pady=5, cursor="hand2")
            btn_add.pack(side=tk.RIGHT, padx=5)

        # Al cerrar, limpiar bind del mouse
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            resultado_win.destroy()
        resultado_win.protocol("WM_DELETE_WINDOW", on_close)
    
    def actualizar_carrito():
        for item in tree_carrito.get_children():
            tree_carrito.delete(item)

        total = 0.0
        total_ahorro = 0.0
        for item in carrito_items:
            # item = (codigo, nombre, precio_normal, oferta_txt, cant, subtotal)
            codigo = item[0]
            cant = int(item[4])
            precio_normal = float(item[2])

            # SIEMPRE usar precio_oferta de la BD (35% descuento)
            c.execute("SELECT precio_oferta FROM productos WHERE codigo=?", (codigo,))
            of_row = c.fetchone()
            precio_oferta = of_row[0] if of_row and of_row[0] else precio_normal * 0.65
            subtotal_oferta = precio_oferta * cant

            # Actualizar el item con el precio correcto
            tree_carrito.insert("", "end", values=(codigo, item[1], precio_normal, "-35%", cant, f"{subtotal_oferta:.2f}"))
            total += subtotal_oferta

            # Calcular ahorro
            precio_normal_total = precio_normal * cant
            ahorro_item = precio_normal_total - subtotal_oferta
            if ahorro_item > 0:
                total_ahorro += ahorro_item

        # TOTAL A COBRAR = mismo que EFECTIVO
        total_label.config(text=f"${total:,.2f}")
        ahorro_txt = f"  |  Ahorro: ${total_ahorro:,.2f}" if total_ahorro > 0 else ""
        productos_label.config(text=f"{len(carrito_items)} productos{ahorro_txt}")

        # LLENAR TODAS LAS CASILLAS CON INFO
        efectivo_var.set(f"{total:.2f}")  # Precio con 35% desc
        tarjeta_var.set(f"{total:.2f}")   # Mismo precio
        vale_var.set(f"{total:.2f}")      # Mismo precio
        descuento_pct_var.set("35")       # Descuento aplicado
        # Calcular saturnos del carrito
        total_saturnos = 0
        for item in carrito_items:
            codigo = item[0]
            cant = int(item[4])
            c.execute("SELECT precio_oferta, laboratorio FROM productos WHERE codigo=?", (codigo,))
            row = c.fetchone()
            if row:
                precio_of = row[0] if row[0] else float(item[2]) * 0.65
                lab = row[1] or ""
                es_gen = "GENERICO" in lab.upper()
                pct = 10.0 if es_gen else 8.0
                total_saturnos += precio_of * pct / 100 * cant
        saturnos_var.set(f"{total_saturnos:.0f}")
        # Crédito = 25% desc (más caro, +15.4% sobre precio oferta)
        total_credito = total * 1.154
        credito_var.set(f"{total_credito:.2f}")
        abono_credito_var.set(f"{total_credito / 4:.2f}")

        # Actualizar calculo de cobro en tiempo real
        try:
            actualizar_cobro()
        except Exception:
            pass
    
    def mas_uno():
        sel = tree_carrito.selection()
        if sel:
            idx = tree_carrito.index(sel[0])
            item = carrito_items[idx]
            precio = float(item[2])
            nueva_cant = item[4] + 1
            oferta = ofertas_carrito.get(item[0])
            if oferta and oferta["tipo"] in ("2X1", "3X2"):
                p_of, _ = calcular_precio_oferta(precio, oferta, nueva_cant)
                carrito_items[idx] = (item[0], item[1], precio, item[3], nueva_cant, round(p_of * nueva_cant, 2))
            elif oferta:
                p_of, _ = calcular_precio_oferta(precio, oferta)
                carrito_items[idx] = (item[0], item[1], precio, item[3], nueva_cant, round(p_of * nueva_cant, 2))
            else:
                carrito_items[idx] = (item[0], item[1], precio, item[3], nueva_cant, round(precio * nueva_cant, 2))
            actualizar_carrito()

    def menos_uno():
        sel = tree_carrito.selection()
        if sel:
            idx = tree_carrito.index(sel[0])
            item = carrito_items[idx]
            precio = float(item[2])
            if item[4] > 1:
                nueva_cant = item[4] - 1
                oferta = ofertas_carrito.get(item[0])
                if oferta and oferta["tipo"] in ("2X1", "3X2"):
                    p_of, _ = calcular_precio_oferta(precio, oferta, nueva_cant)
                    carrito_items[idx] = (item[0], item[1], precio, item[3], nueva_cant, round(p_of * nueva_cant, 2))
                elif oferta:
                    p_of, _ = calcular_precio_oferta(precio, oferta)
                    carrito_items[idx] = (item[0], item[1], precio, item[3], nueva_cant, round(p_of * nueva_cant, 2))
                else:
                    carrito_items[idx] = (item[0], item[1], precio, item[3], nueva_cant, round(precio * nueva_cant, 2))
            else:
                carrito_items.pop(idx)
                if item[0] in ofertas_carrito:
                    del ofertas_carrito[item[0]]
            actualizar_carrito()
    
    def eliminar():
        sel = tree_carrito.selection()
        if sel:
            idx = tree_carrito.index(sel[0])
            carrito_items.pop(idx)
            actualizar_carrito()
    
    # BOTONES CARRITO
    btn_frame = tk.Frame(left_panel, bg="white")
    btn_frame.pack(pady=10)
    
    tk.Button(btn_frame, text="+ 1", command=mas_uno,
             bg="#27AE60", fg="white", font=("Arial", 10, "bold"),
             padx=18, pady=10).pack(side=tk.LEFT, padx=3)
    
    tk.Button(btn_frame, text="- 1", command=menos_uno,
             bg="#F39C12", fg="white", font=("Arial", 10, "bold"),
             padx=18, pady=10).pack(side=tk.LEFT, padx=3)
    
    tk.Button(btn_frame, text="🗑️ Eliminar", command=eliminar,
             bg="#E74C3C", fg="white", font=("Arial", 10, "bold"),
             padx=18, pady=10).pack(side=tk.LEFT, padx=3)

    # ============================================================
    # BOTÓN ABONAR A CRÉDITO - Visible en el punto de venta
    # ============================================================
    btn_abono_frame = tk.Frame(left_panel, bg="white")
    btn_abono_frame.pack(pady=5, fill=tk.X, padx=10)

    tk.Button(btn_abono_frame, text="💳 ABONAR A CRÉDITO",
             command=lambda: ver_abonos_credito(),
             bg="#1565C0", fg="white", font=("Arial", 12, "bold"),
             padx=20, pady=12, cursor="hand2",
             activebackground="#1976D2", activeforeground="white",
             relief=tk.RAISED, bd=2).pack(fill=tk.X)

    tk.Label(btn_abono_frame, text="¿El cliente tiene crédito pendiente? Puede abonar aquí",
            font=("Arial", 8), bg="white", fg="#666").pack(pady=2)

    # ============================================================
    # MÓDULO PRODUCTO RÁPIDO - Agregar productos sin buscar
    # ============================================================
    prod_rapido_frame = tk.Frame(left_panel, bg="#E8F5E9", relief=tk.RIDGE, bd=1)
    prod_rapido_frame.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(prod_rapido_frame, text="⚡ PRODUCTO RÁPIDO", font=("Segoe UI", 10, "bold"),
            bg="#E8F5E9", fg="#2E7D32").pack(pady=(8,5))

    # Frame para entrada rápida
    entrada_rapida = tk.Frame(prod_rapido_frame, bg="#E8F5E9")
    entrada_rapida.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(entrada_rapida, text="Código/Nombre:", font=("Segoe UI", 9),
            bg="#E8F5E9").pack(side=tk.LEFT, padx=3)
    codigo_rapido_var = tk.StringVar()
    entry_codigo_rapido = tk.Entry(entrada_rapida, textvariable=codigo_rapido_var,
                                   width=20, font=("Segoe UI", 10))
    entry_codigo_rapido.pack(side=tk.LEFT, padx=3)

    tk.Label(entrada_rapida, text="Cant:", font=("Segoe UI", 9),
            bg="#E8F5E9").pack(side=tk.LEFT, padx=3)
    cant_rapido_var = tk.StringVar(value="1")
    tk.Spinbox(entrada_rapida, textvariable=cant_rapido_var, from_=1, to=99,
              width=4, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=3)

    # Label para mostrar resultado de búsqueda
    resultado_rapido_label = tk.Label(prod_rapido_frame, text="", font=("Segoe UI", 8),
                                      bg="#E8F5E9", fg="#1B5E20")
    resultado_rapido_label.pack(fill=tk.X, padx=10)

    def agregar_rapido():
        busqueda = codigo_rapido_var.get().strip().upper()
        if not busqueda:
            return
        cant = int(cant_rapido_var.get() or 1)

        # Primero buscar por código exacto
        c.execute("SELECT codigo, nombre, precio_venta, precio_oferta, stock FROM productos WHERE codigo=?", (busqueda,))
        producto = c.fetchone()

        # Si no encuentra por código, buscar por código de barras
        if not producto:
            c.execute("SELECT codigo, nombre, precio_venta, precio_oferta, stock FROM productos WHERE codigo_barras=?", (busqueda,))
            producto = c.fetchone()

        # Si no encuentra, buscar por nombre (primera coincidencia)
        if not producto:
            c.execute("SELECT codigo, nombre, precio_venta, precio_oferta, stock FROM productos WHERE nombre LIKE ? LIMIT 1", (f"%{busqueda}%",))
            producto = c.fetchone()

        if producto:
            codigo, nombre, precio, precio_of, stock = producto
            precio_mostrar = precio_of if precio_of else precio * 0.65

            # Mostrar qué producto se encontró
            resultado_rapido_label.config(
                text=f"✓ {nombre[:40]} | ${precio_mostrar:,.2f} | Stock: {stock}",
                fg="#1B5E20"
            )

            # Agregar la cantidad indicada
            for _ in range(cant):
                agregar_por_codigo(codigo)

            codigo_rapido_var.set("")
            cant_rapido_var.set("1")

            # Limpiar mensaje después de 3 segundos
            prod_rapido_frame.after(3000, lambda: resultado_rapido_label.config(text=""))
        else:
            # No encontrado
            resultado_rapido_label.config(
                text=f"✗ No encontrado: {busqueda}",
                fg="#D32F2F"
            )
            beep_error()
            prod_rapido_frame.after(3000, lambda: resultado_rapido_label.config(text=""))

    tk.Button(entrada_rapida, text="➕ AGREGAR", command=agregar_rapido,
             bg="#4CAF50", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=10, cursor="hand2").pack(side=tk.LEFT, padx=5)

    entry_codigo_rapido.bind("<Return>", lambda e: agregar_rapido())

    # Separador
    tk.Frame(prod_rapido_frame, bg="#C8E6C9", height=1).pack(fill=tk.X, padx=10, pady=5)

    # Botones de productos más vendidos
    tk.Label(prod_rapido_frame, text="Productos Frecuentes:", font=("Segoe UI", 8, "bold"),
            bg="#E8F5E9", fg="#1B5E20").pack(anchor="w", padx=10)

    btns_frecuentes = tk.Frame(prod_rapido_frame, bg="#E8F5E9")
    btns_frecuentes.pack(fill=tk.X, padx=10, pady=5)

    # Obtener productos más vendidos con precio
    productos_frecuentes = []
    try:
        c.execute("""SELECT p.codigo, p.nombre, p.precio_oferta, p.precio_venta, COUNT(dv.id) as ventas
                     FROM detalle_ventas dv
                     JOIN productos p ON dv.producto_id = p.id
                     GROUP BY p.id ORDER BY ventas DESC LIMIT 8""")
        productos_frecuentes = c.fetchall()
    except:
        pass

    # Si no hay historial, usar algunos productos comunes
    if not productos_frecuentes:
        c.execute("""SELECT codigo, nombre, precio_oferta, precio_venta FROM productos
                     WHERE nombre LIKE '%TEMPRA%' OR nombre LIKE '%PARACETAMOL%'
                     OR nombre LIKE '%ASPIRINA%' OR nombre LIKE '%IBUPROFENO%'
                     OR nombre LIKE '%OMEPRAZOL%' OR nombre LIKE '%RANITIDINA%'
                     LIMIT 8""")
        productos_frecuentes = [(r[0], r[1], r[2], r[3], 0) for r in c.fetchall()]

    def crear_btn_frecuente(codigo, nombre, precio_of, precio_normal):
        nombre_corto = nombre[:15] + ".." if len(nombre) > 15 else nombre
        precio = precio_of if precio_of else (precio_normal * 0.65 if precio_normal else 0)
        texto = f"{nombre_corto}\n${precio:,.0f}"
        btn = tk.Button(btns_frecuentes, text=texto,
                       command=lambda c=codigo: agregar_por_codigo(c),
                       bg="#81C784", fg="white", font=("Segoe UI", 7, "bold"),
                       relief=tk.FLAT, padx=2, pady=2, cursor="hand2",
                       wraplength=80, justify="center")
        return btn

    # Crear grid de botones 4x2
    for i, prod in enumerate(productos_frecuentes[:8]):
        codigo, nombre = prod[0], prod[1]
        precio_of = prod[2] if len(prod) > 2 else None
        precio_normal = prod[3] if len(prod) > 3 else None
        btn = crear_btn_frecuente(codigo, nombre, precio_of, precio_normal)
        row = i // 4
        col = i % 4
        btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")

    # Configurar columnas para que se expandan
    for i in range(4):
        btns_frecuentes.grid_columnconfigure(i, weight=1)

    # Botón para agregar producto personalizado (sin código)
    tk.Frame(prod_rapido_frame, bg="#C8E6C9", height=1).pack(fill=tk.X, padx=10, pady=5)

    custom_frame = tk.Frame(prod_rapido_frame, bg="#E8F5E9")
    custom_frame.pack(fill=tk.X, padx=10, pady=(0,8))

    def agregar_producto_custom():
        """Ventana para agregar producto que no existe en catálogo."""
        win = tk.Toplevel(main)
        win.title("➕ Agregar Producto Personalizado")
        win.geometry("500x450")
        win.configure(bg="white")
        win.transient(main)
        win.grab_set()

        tk.Label(win, text="➕ PRODUCTO PERSONALIZADO", font=("Segoe UI", 14, "bold"),
                bg="white", fg="#1565C0").pack(pady=15)

        tk.Label(win, text="Para productos que no están en el catálogo",
                font=("Segoe UI", 9), bg="white", fg="#666").pack()

        form = tk.Frame(win, bg="white")
        form.pack(pady=20, padx=30)

        # Variables
        codigo_custom = tk.StringVar(value=f"PERS{datetime.now().strftime('%H%M%S')}")
        nombre_custom = tk.StringVar()
        precio_normal_custom = tk.StringVar()
        precio_oferta_custom = tk.StringVar()
        cant_custom = tk.StringVar(value="1")

        campos = [
            ("Código:", codigo_custom, 0),
            ("Descripción:", nombre_custom, 1),
            ("Precio Normal $:", precio_normal_custom, 2),
            ("Precio Oferta $:", precio_oferta_custom, 3),
            ("Cantidad:", cant_custom, 4),
        ]

        for label, var, row in campos:
            tk.Label(form, text=label, font=("Segoe UI", 10, "bold"),
                    bg="white").grid(row=row, column=0, sticky="e", padx=5, pady=8)
            width = 35 if row == 1 else 15
            tk.Entry(form, textvariable=var, width=width, font=("Segoe UI", 10)
                    ).grid(row=row, column=1, sticky="w", padx=5, pady=8)

        # Auto calcular precio oferta (35% desc)
        def calcular_oferta(*args):
            try:
                precio_n = float(precio_normal_custom.get() or 0)
                if precio_n > 0 and not precio_oferta_custom.get():
                    precio_oferta_custom.set(f"{precio_n * 0.65:.2f}")
            except:
                pass

        precio_normal_custom.trace_add("write", calcular_oferta)

        # Vista previa
        preview_frame = tk.Frame(win, bg="#E3F2FD", relief=tk.RIDGE, bd=1)
        preview_frame.pack(fill=tk.X, padx=30, pady=10)

        tk.Label(preview_frame, text="Vista previa en carrito:", font=("Segoe UI", 9, "bold"),
                bg="#E3F2FD", fg="#1565C0").pack(anchor="w", padx=10, pady=5)

        preview_label = tk.Label(preview_frame, text="", font=("Courier New", 9),
                                bg="#E3F2FD", fg="#333", anchor="w", justify="left")
        preview_label.pack(fill=tk.X, padx=10, pady=5)

        def actualizar_preview(*args):
            try:
                codigo = codigo_custom.get() or "---"
                nombre = nombre_custom.get() or "Sin descripción"
                precio_n = float(precio_normal_custom.get() or 0)
                precio_of = float(precio_oferta_custom.get() or precio_n * 0.65)
                cant = int(cant_custom.get() or 1)
                subtotal = precio_of * cant
                descuento = round((1 - precio_of/precio_n) * 100) if precio_n > 0 else 0

                texto = f"CÓDIGO: {codigo}\n"
                texto += f"NOMBRE: {nombre[:40]}\n"
                texto += f"PRECIO: ${precio_n:,.2f}  |  OFERTA: ${precio_of:,.2f} (-{descuento}%)\n"
                texto += f"CANTIDAD: {cant}  |  SUBTOTAL: ${subtotal:,.2f}"
                preview_label.config(text=texto)
            except:
                pass

        for var in [codigo_custom, nombre_custom, precio_normal_custom, precio_oferta_custom, cant_custom]:
            var.trace_add("write", actualizar_preview)

        def confirmar_custom():
            codigo = codigo_custom.get().strip().upper() or f"PERS{datetime.now().strftime('%H%M%S')}"
            nombre = nombre_custom.get().strip()
            try:
                precio_normal = float(precio_normal_custom.get() or 0)
                precio_oferta = float(precio_oferta_custom.get() or precio_normal * 0.65)
                cant = int(cant_custom.get() or 1)
            except:
                messagebox.showwarning("Error", "Precio o cantidad inválidos")
                return

            if not nombre or precio_normal <= 0:
                messagebox.showwarning("Datos incompletos", "Ingresa descripción y precio")
                return

            # Calcular descuento
            descuento = round((1 - precio_oferta/precio_normal) * 100) if precio_normal > 0 else 35
            oferta_txt = f"-{descuento}%"

            # Agregar al carrito con formato correcto
            # formato: (codigo, nombre, precio_normal, oferta_txt, cantidad, subtotal)
            for _ in range(cant):
                # Verificar si ya existe en carrito
                existe = False
                for idx, item in enumerate(carrito_items):
                    if item[0] == codigo:
                        nueva_cant = item[4] + 1
                        nuevo_subtotal = precio_oferta * nueva_cant
                        carrito_items[idx] = (codigo, nombre, precio_normal, oferta_txt, nueva_cant, nuevo_subtotal)
                        existe = True
                        break
                if not existe:
                    carrito_items.append((codigo, nombre, precio_normal, oferta_txt, 1, precio_oferta))

            actualizar_carrito()
            win.destroy()
            messagebox.showinfo("Agregado", f"{nombre} agregado al carrito")

        tk.Button(win, text="✓ AGREGAR AL CARRITO", command=confirmar_custom,
                 bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"),
                 relief=tk.FLAT, padx=20, pady=10, cursor="hand2").pack(pady=20)

    tk.Button(custom_frame, text="📝 PRODUCTO SIN CÓDIGO", command=agregar_producto_custom,
             bg="#FF9800", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=12, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)

    def refrescar_frecuentes():
        """Actualiza los botones de productos frecuentes con precio."""
        for widget in btns_frecuentes.winfo_children():
            widget.destroy()
        try:
            c.execute("""SELECT p.codigo, p.nombre, p.precio_oferta, p.precio_venta, COUNT(dv.id) as ventas
                         FROM detalle_ventas dv
                         JOIN productos p ON dv.producto_id = p.id
                         GROUP BY p.id ORDER BY ventas DESC LIMIT 8""")
            prods = c.fetchall()
            for i, prod in enumerate(prods[:8]):
                codigo, nombre = prod[0], prod[1]
                precio_of = prod[2] if len(prod) > 2 else None
                precio_normal = prod[3] if len(prod) > 3 else None
                btn = crear_btn_frecuente(codigo, nombre, precio_of, precio_normal)
                row = i // 4
                col = i % 4
                btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
        except:
            pass

    tk.Button(custom_frame, text="🔄 ACTUALIZAR", command=refrescar_frecuentes,
             bg="#2196F3", fg="white", font=("Segoe UI", 8),
             relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.RIGHT, padx=5)

    search_entry.bind("<Return>", buscar_o_agregar)
    
    tk.Button(search_frame, text="BUSCAR", command=buscar,
             bg="#4A90E2", fg="white", font=("Arial", 9, "bold"),
             padx=15, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)
    
    # ============================================================
    # PANEL DERECHO - MODULO DE COBRO PROFESIONAL (estilo TPVMultiNet)
    # ============================================================
    right_panel_container = tk.Frame(content, bg="#1A2332", width=320, relief=tk.FLAT, bd=0)
    right_panel_container.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)
    right_panel_container.pack_propagate(False)

    # --- Encabezado del panel (fijo arriba) ---
    header_cobro = tk.Frame(right_panel_container, bg="#0D1B2A", height=50)
    header_cobro.pack(fill=tk.X)
    header_cobro.pack_propagate(False)
    tk.Label(header_cobro, text="COBRO", font=("Segoe UI", 14, "bold"),
            bg="#0D1B2A", fg="#4FC3F7").pack(pady=12)

    # === BOTÓN COBRAR ARRIBA (fijo) ===
    btn_cobrar_frame = tk.Frame(right_panel_container, bg="#D32F2F")
    btn_cobrar_frame.pack(fill=tk.X, padx=8, pady=5)

    # === CANVAS SCROLLABLE para el resto del contenido ===
    cobro_canvas = tk.Canvas(right_panel_container, bg="#1A2332", highlightthickness=0)
    cobro_scrollbar = ttk.Scrollbar(right_panel_container, orient="vertical", command=cobro_canvas.yview)
    right_panel = tk.Frame(cobro_canvas, bg="#1A2332")

    right_panel.bind("<Configure>", lambda e: cobro_canvas.configure(scrollregion=cobro_canvas.bbox("all")))
    cobro_canvas.create_window((0, 0), window=right_panel, anchor="nw", width=304)
    cobro_canvas.configure(yscrollcommand=cobro_scrollbar.set)

    cobro_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    cobro_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Scroll con rueda del mouse
    def _on_cobro_mousewheel(event):
        cobro_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    cobro_canvas.bind_all("<MouseWheel>", _on_cobro_mousewheel)

    # ===== SECCIÓN INFO CLIENTE (cuando escanea tarjeta) =====
    cliente_info_cobro = tk.Frame(right_panel, bg="#1B5E20")
    cliente_bienvenida_lbl = tk.Label(cliente_info_cobro, text="", font=("Segoe UI", 10, "bold"),
                                       bg="#1B5E20", fg="#C8E6C9")
    cliente_bienvenida_lbl.pack(pady=4)
    cliente_tarjeta_lbl = tk.Label(cliente_info_cobro, text="", font=("Segoe UI", 8),
                                    bg="#1B5E20", fg="#A5D6A7")
    cliente_tarjeta_lbl.pack(pady=(0, 4))

    def mostrar_bienvenida_cliente(nombre, tarjeta_codigo, saldo_sat):
        """Muestra mensaje de bienvenida cuando se escanea tarjeta Saturnos."""
        cliente_bienvenida_lbl.config(text=f"¡Qué gusto verte, {nombre}!")
        cliente_tarjeta_lbl.config(text=f"Tarjeta: {tarjeta_codigo} | Saldo: {saldo_sat:,.0f} ₴")
        cliente_info_cobro.pack(fill=tk.X, after=header_cobro)

    # Registrar callback para poder llamar desde escanear_tarjeta
    callbacks["bienvenida"] = mostrar_bienvenida_cliente

    def mostrar_producto_escaneado(codigo, nombre, precio, stock, img_path):
        """Muestra info del producto en panel azul y llena campos de pago."""
        # Obtener precio_oferta de la base de datos
        c.execute("SELECT precio_venta, precio_oferta FROM productos WHERE codigo=?", (codigo,))
        precios_row = c.fetchone()
        precio_normal = precios_row[0] if precios_row else precio
        precio_oferta = precios_row[1] if precios_row else precio * 0.65

        # Calcular saturnos
        c.execute("SELECT porcentaje_generico, porcentaje_patente FROM configuracion_saturnos WHERE id=1")
        sat_row = c.fetchone()
        pct_gen = sat_row[0] if sat_row else 10.0
        pct_pat = sat_row[1] if sat_row else 8.0
        c.execute("SELECT laboratorio FROM productos WHERE codigo=?", (codigo,))
        lab_row = c.fetchone()
        lab = lab_row[0] if lab_row else ""
        es_generico = "GENERICO" in (lab or "").upper() or "GENÉRICO" in nombre.upper()
        pct_sat = pct_gen if es_generico else pct_pat
        saturnos = round(precio_oferta * pct_sat / 100, 2)

        # Precio a crédito (25% desc = 75% del normal)
        precio_credito = precio_normal * 0.75
        pago_quincenal = precio_credito / 4

        # === Actualizar PANEL AZUL (izquierdo) ===
        prod_nombre_lbl.config(text=f"✓ {nombre[:55]}")
        precio_normal_lbl.config(text=f"Normal: ${precio_normal:,.2f}")
        precio_oferta_lbl.config(text=f"Oferta (35%): ${precio_oferta:,.2f}")
        saturnos_gana_lbl.config(text=f"⭐ Ganas: {saturnos:.0f} Saturnos ({pct_sat:.0f}%)")
        credito_precio_lbl.config(text=f"A crédito (25%): ${precio_credito:,.2f}")
        credito_pagos_lbl.config(text=f"4 pagos de: ${pago_quincenal:,.2f}")
        stock_color = "#2E7D32" if stock > 5 else "#F44336" if stock <= 0 else "#FF9800"
        stock_lbl.config(text=f"Stock: {stock}", fg=stock_color)

        # === LLENAR CAMPOS DE PAGO AUTOMÁTICAMENTE ===
        # Guardar info para usar en campos (se llena después de que existen las vars)
        callbacks["ultimo_producto"] = {
            "precio_oferta": precio_oferta,
            "saturnos": saturnos,
            "precio_credito": precio_credito,
            "pago_quincenal": pago_quincenal
        }

    # Registrar callback para mostrar info de producto
    callbacks["producto_info"] = mostrar_producto_escaneado

    # --- Total a cobrar (compacto) ---
    total_section = tk.Frame(right_panel, bg="#1A2332")
    total_section.pack(fill=tk.X, padx=8, pady=(5, 2))

    tk.Label(total_section, text="TOTAL A COBRAR", font=("Segoe UI", 8, "bold"),
            bg="#1A2332", fg="#78909C").pack()

    total_label = tk.Label(total_section, text="$0.00", font=("Segoe UI", 28, "bold"),
                          bg="#1A2332", fg="#00E676")
    total_label.pack()

    productos_label = tk.Label(total_section, text="0 productos", font=("Segoe UI", 8),
                              bg="#1A2332", fg="#546E7A")
    productos_label.pack()

    # --- Separador ---
    tk.Frame(right_panel, bg="#2C3E50", height=1).pack(fill=tk.X, padx=8)

    # --- Campos de pago (compactos) ---
    pago_frame = tk.Frame(right_panel, bg="#1A2332")
    pago_frame.pack(fill=tk.X, padx=8, pady=3)

    # Variables de pago
    efectivo_var = tk.StringVar(value="")
    tarjeta_var = tk.StringVar(value="")
    vale_var = tk.StringVar(value="")

    def crear_campo_pago(parent, icono, label_text, variable, color_icono, row):
        """Crea un campo de pago compacto."""
        frame = tk.Frame(parent, bg="#1A2332")
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=2)
        parent.grid_columnconfigure(1, weight=1)

        lbl_frame = tk.Frame(frame, bg="#1A2332")
        lbl_frame.pack(fill=tk.X)

        tk.Label(lbl_frame, text=icono, font=("Segoe UI", 9),
                bg="#1A2332", fg=color_icono).pack(side=tk.LEFT)
        tk.Label(lbl_frame, text=label_text, font=("Segoe UI", 8, "bold"),
                bg="#1A2332", fg="#B0BEC5").pack(side=tk.LEFT, padx=2)

        entry = tk.Entry(frame, textvariable=variable, font=("Segoe UI", 12, "bold"),
                        bg="#263238", fg="#FFFFFF", insertbackground="#FFFFFF",
                        relief=tk.FLAT, bd=0, justify="right")
        entry.pack(fill=tk.X, ipady=3)

        # Borde inferior del entry
        tk.Frame(frame, bg=color_icono, height=1).pack(fill=tk.X)
        return entry

    entry_efectivo = crear_campo_pago(pago_frame, "$", "EFECTIVO", efectivo_var, "#4CAF50", 0)
    entry_tarjeta = crear_campo_pago(pago_frame, "T", "TARJETA", tarjeta_var, "#42A5F5", 1)
    entry_vale = crear_campo_pago(pago_frame, "V", "VALE", vale_var, "#FFA726", 2)

    # --- DESCUENTO (compacto, sin slider) ---
    descuento_pct_var = tk.StringVar(value="35")

    desc_frame = tk.Frame(pago_frame, bg="#1A2332")
    desc_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=2)

    tk.Label(desc_frame, text="% DESC:", font=("Segoe UI", 8, "bold"),
            bg="#1A2332", fg="#FF5722").pack(side=tk.LEFT)

    desc_entry = tk.Entry(desc_frame, textvariable=descuento_pct_var, font=("Segoe UI", 10, "bold"),
                         bg="#263238", fg="#FF5722", insertbackground="#FF5722",
                         relief=tk.FLAT, bd=0, justify="center", width=5)
    desc_entry.pack(side=tk.LEFT, padx=3, ipady=2)

    # Label que muestra el descuento calculado
    descuento_monto_label = tk.Label(desc_frame, text="(35% aplicado)", font=("Segoe UI", 7),
                                     bg="#1A2332", fg="#FF5722")
    descuento_monto_label.pack(side=tk.LEFT, padx=5)

    # --- SATURNOS y CRÉDITO (compactos) ---
    saturnos_var = tk.StringVar(value="")
    credito_var = tk.StringVar(value="")
    abono_credito_var = tk.StringVar(value="")
    entry_saturnos = crear_campo_pago(pago_frame, "₴", "SATURNOS", saturnos_var, "#FFC107", 4)
    entry_credito = crear_campo_pago(pago_frame, "C", "CRÉDITO", credito_var, "#2E7D32", 5)
    entry_abono = crear_campo_pago(pago_frame, "A", "ABONO", abono_credito_var, "#1976D2", 6)

    # === FUNCIÓN PARA LLENAR CAMPOS DE PAGO AUTOMÁTICAMENTE ===
    def llenar_campos_pago():
        """Llena los campos de pago con info del último producto escaneado."""
        if "ultimo_producto" not in callbacks:
            return
        info = callbacks["ultimo_producto"]

        # Calcular total del carrito con precios oferta
        total_carrito = sum(float(item[5]) for item in carrito_items) if carrito_items else info['precio_oferta']

        # EFECTIVO = total del carrito con descuento
        efectivo_var.set(f"{total_carrito:.2f}")
        # TARJETA = mismo precio
        tarjeta_var.set(f"{total_carrito:.2f}")
        # VALE = mismo precio
        vale_var.set(f"{total_carrito:.2f}")
        # DESCUENTO = 35%
        descuento_pct_var.set("35")
        # SATURNOS = lo que gana del último producto
        saturnos_var.set(f"{info['saturnos']:.0f}")
        # CRÉDITO = precio a crédito (total * 0.75/0.65 para ajustar)
        total_credito = total_carrito * 1.154  # De 35% desc a 25% desc
        credito_var.set(f"{total_credito:.2f}")
        # ABONO = 4 pagos quincenales
        pago_quincenal = total_credito / 4
        abono_credito_var.set(f"{pago_quincenal:.2f}")

        # ACTUALIZAR TOTAL A PAGAR (mismo que efectivo)
        total_label.config(text=f"${total_carrito:,.2f}")

    # Registrar callback
    callbacks["llenar_campos"] = llenar_campos_pago

    # Info Saturnos del cliente
    saldo_sat_frame = tk.Frame(right_panel, bg="#1A2332")
    saldo_sat_frame.pack(fill=tk.X, padx=12)
    saldo_sat_label = tk.Label(saldo_sat_frame, text="", font=("Segoe UI", 8),
                               bg="#1A2332", fg="#FFC107")
    saldo_sat_label.pack(anchor="w")
    credito_info_label = tk.Label(saldo_sat_frame, text="", font=("Segoe UI", 8),
                                  bg="#1A2332", fg="#66BB6A")
    credito_info_label.pack(anchor="w")

    acumular_sat_var = tk.IntVar(value=1)
    tk.Checkbutton(saldo_sat_frame, text="Acumular Saturnos", variable=acumular_sat_var,
                  font=("Segoe UI", 7), bg="#1A2332", fg="#FFC107", selectcolor="#263238",
                  activebackground="#1A2332", activeforeground="#FFC107"
                  ).pack(anchor="w")

    def actualizar_info_cliente(*args):
        """Muestra saldo Saturnos y crédito disponible del cliente seleccionado."""
        nombre_cl = cliente_var.get()
        c.execute("SELECT id FROM clientes WHERE nombre=?", (nombre_cl,))
        row = c.fetchone()
        if not row:
            saldo_sat_label.config(text="")
            credito_info_label.config(text="")
            return
        cid = row[0]
        # Saturnos
        c.execute("SELECT saldo_saturnos FROM monederos WHERE cliente_id=? AND activo=1", (cid,))
        m = c.fetchone()
        if m:
            saldo_sat_label.config(text=f"\u20B4 Saldo Saturnos: {m[0]:,.0f}")
        else:
            saldo_sat_label.config(text="\u20B4 Sin monedero")
        # Crédito
        c.execute("SELECT monto_disponible FROM creditos WHERE cliente_id=? AND estado='ACTIVO'", (cid,))
        cr = c.fetchone()
        if cr:
            credito_info_label.config(text=f"Crédito disponible: ${cr[0]:,.2f}")
        else:
            credito_info_label.config(text="")

    cliente_var.trace_add("write", actualizar_info_cliente)
    # Trigger inicial
    try: actualizar_info_cliente()
    except: pass

    # --- Info de pago/cambio (compacto) ---
    tk.Frame(right_panel, bg="#2C3E50", height=1).pack(fill=tk.X, padx=8, pady=2)

    info_frame = tk.Frame(right_panel, bg="#1A2332")
    info_frame.pack(fill=tk.X, padx=8, pady=2)

    suma_label = tk.Label(info_frame, text="Suma: $0.00",
                         font=("Segoe UI", 8), bg="#1A2332", fg="#78909C")
    suma_label.pack(anchor="w")

    falta_label = tk.Label(info_frame, text="",
                          font=("Segoe UI", 9, "bold"), bg="#1A2332", fg="#EF5350")
    falta_label.pack(anchor="w")

    cambio_frame = tk.Frame(info_frame, bg="#1B5E20")
    cambio_label = tk.Label(cambio_frame, text="CAMBIO: $0.00",
                           font=("Segoe UI", 12, "bold"), bg="#1B5E20", fg="#A5D6A7")
    cambio_label.pack(pady=3, padx=8)

    def _parse_monto(var):
        """Obtiene float de un StringVar de forma segura."""
        val = var.get().strip().replace(",", "").replace("$", "")
        if not val:
            return 0.0
        try:
            return float(val)
        except ValueError:
            return 0.0

    def actualizar_cobro(*args):
        """Recalcula suma de pagos, faltante y cambio en tiempo real, aplicando descuento."""
        # Calcular subtotal usando precio_oferta de la BD (35% descuento)
        subtotal = 0.0
        for item in carrito_items:
            codigo = item[0]
            cant = int(item[4])
            precio_normal = float(item[2])
            c.execute("SELECT precio_oferta FROM productos WHERE codigo=?", (codigo,))
            of_row = c.fetchone()
            precio_oferta = of_row[0] if of_row and of_row[0] else precio_normal * 0.65
            subtotal += precio_oferta * cant

        # Verificar si hay pago a crédito
        cred = _parse_monto(credito_var)
        usa_credito = cred > 0

        # A crédito: descuento baja de 35% a 25% (precio sube ~15%)
        # Calcular ajuste por crédito
        if usa_credito:
            # Si se paga a crédito, el subtotal sube 15.4% (de 65% a 75% del precio normal)
            subtotal_ajustado = subtotal * 1.154  # 75/65 = 1.154
            credito_info_label.config(text=f"⚠️ A crédito +15.4% = ${subtotal_ajustado:,.2f}", fg="#FF9800")
        else:
            subtotal_ajustado = subtotal
            # Restaurar info crédito normal
            try:
                nombre_cl = cliente_var.get()
                c.execute("SELECT id FROM clientes WHERE nombre=?", (nombre_cl,))
                row = c.fetchone()
                if row:
                    c.execute("SELECT monto_disponible FROM creditos WHERE cliente_id=? AND estado='ACTIVO'", (row[0],))
                    cr = c.fetchone()
                    if cr:
                        credito_info_label.config(text=f"Crédito disponible: ${cr[0]:,.2f}", fg="#66BB6A")
            except:
                pass

        # El 35% ya está aplicado en precio_oferta, mostrar info
        try:
            desc_pct = float(descuento_pct_var.get() or 0)
        except:
            desc_pct = 0

        # NO aplicar descuento adicional, el subtotal YA tiene el 35%
        total = subtotal_ajustado

        # Mostrar que el 35% ya está aplicado
        descuento_monto_label.config(text=f"Descuento base: {desc_pct:.0f}% aplicado")

        efec = _parse_monto(efectivo_var)
        tarj = _parse_monto(tarjeta_var)
        val = _parse_monto(vale_var)
        sat = _parse_monto(saturnos_var)

        # Si efectivo, tarjeta y vale tienen el mismo valor, es info (solo contar uno)
        if efec > 0 and efec == tarj == val:
            suma = efec  # Solo contar efectivo como pago
        else:
            suma = efec + tarj + val + sat + cred

        suma_label.config(text=f"Suma pagos: ${suma:,.2f}")

        if suma < total and total > 0:
            faltante = total - suma
            falta_label.config(text=f"Falta: ${faltante:,.2f}", fg="#EF5350")
            cambio_frame.pack_forget()
        elif suma >= total and total > 0:
            # Cambio solo sobre efectivo
            excedente_total = suma - total
            cambio_efectivo = min(efec, efec - (total - tarj - val)) if efec > 0 else 0
            cambio_efectivo = max(excedente_total, 0)
            falta_label.config(text="PAGO COMPLETO", fg="#66BB6A")
            cambio_label.config(text=f"CAMBIO: ${cambio_efectivo:,.2f}")
            cambio_frame.pack(fill=tk.X, pady=(4, 0))
        else:
            falta_label.config(text="")
            cambio_frame.pack_forget()

    efectivo_var.trace_add("write", actualizar_cobro)
    tarjeta_var.trace_add("write", actualizar_cobro)
    vale_var.trace_add("write", actualizar_cobro)
    saturnos_var.trace_add("write", actualizar_cobro)
    credito_var.trace_add("write", actualizar_cobro)
    descuento_pct_var.trace_add("write", actualizar_cobro)

    # --- Botones rapidos de efectivo (compacto) ---
    rapidos_frame = tk.Frame(right_panel, bg="#1A2332")
    rapidos_frame.pack(fill=tk.X, padx=8, pady=2)

    btns_rapidos = tk.Frame(rapidos_frame, bg="#1A2332")
    btns_rapidos.pack(fill=tk.X)

    def pago_rapido_exacto():
        # Calcular total con precio_oferta (35% desc)
        total = 0.0
        for item in carrito_items:
            codigo = item[0]
            cant = int(item[4])
            precio_normal = float(item[2])
            c.execute("SELECT precio_oferta FROM productos WHERE codigo=?", (codigo,))
            of_row = c.fetchone()
            precio_oferta = of_row[0] if of_row and of_row[0] else precio_normal * 0.65
            total += precio_oferta * cant
        efectivo_var.set(f"{total:.2f}")
        tarjeta_var.set("")
        vale_var.set("")

    def pago_rapido_tarjeta():
        # Calcular total con precio_oferta (35% desc)
        total = 0.0
        for item in carrito_items:
            codigo = item[0]
            cant = int(item[4])
            precio_normal = float(item[2])
            c.execute("SELECT precio_oferta FROM productos WHERE codigo=?", (codigo,))
            of_row = c.fetchone()
            precio_oferta = of_row[0] if of_row and of_row[0] else precio_normal * 0.65
            total += precio_oferta * cant
        tarjeta_var.set(f"{total:.2f}")
        efectivo_var.set("")
        vale_var.set("")

    for texto, cmd, color in [
        ("EXACTO", pago_rapido_exacto, "#37474F"),
        ("TARJETA", pago_rapido_tarjeta, "#1565C0"),
        ("$50", lambda: efectivo_var.set("50.00"), "#37474F"),
        ("$100", lambda: efectivo_var.set("100.00"), "#37474F"),
        ("$200", lambda: efectivo_var.set("200.00"), "#37474F"),
        ("$500", lambda: efectivo_var.set("500.00"), "#37474F"),
    ]:
        tk.Button(btns_rapidos, text=texto, command=cmd,
                 bg=color, fg="white", font=("Segoe UI", 8, "bold"),
                 relief=tk.FLAT, padx=6, pady=3,
                 cursor="hand2", activebackground="#455A64"
                 ).pack(side=tk.LEFT, padx=1, expand=True, fill=tk.X)

    # --- Separador ---
    tk.Frame(right_panel, bg="#2C3E50", height=1).pack(fill=tk.X, padx=12, pady=8)

    # --- Boton COBRAR ---
    def cobrar():
        if not carrito_items:
            messagebox.showwarning("Carrito vacio", "Agrega productos al carrito")
            return

        # Calcular total con precio_oferta (35% desc)
        total = 0.0
        for item in carrito_items:
            codigo = item[0]
            cant = int(item[4])
            precio_normal = float(item[2])
            c.execute("SELECT precio_oferta FROM productos WHERE codigo=?", (codigo,))
            of_row = c.fetchone()
            precio_oferta = of_row[0] if of_row and of_row[0] else precio_normal * 0.65
            total += precio_oferta * cant

        efec = _parse_monto(efectivo_var)
        tarj = _parse_monto(tarjeta_var)
        val = _parse_monto(vale_var)
        sat = _parse_monto(saturnos_var)
        cred = _parse_monto(credito_var)

        # Si efectivo, tarjeta y vale tienen el mismo valor (info automática), solo contar efectivo
        if efec > 0 and abs(efec - tarj) < 0.01 and abs(efec - val) < 0.01:
            tarj = 0.0
            val = 0.0
            tarjeta_var.set("")
            vale_var.set("")

        # Los campos SATURNOS y CREDITO son informativos, no para pagar
        # Si el usuario no modificó manualmente, limpiarlos
        sat = 0.0  # No usar saturnos automáticamente
        cred = 0.0  # No usar crédito automáticamente
        saturnos_var.set("")
        credito_var.set("")

        # Obtener cliente
        c.execute("SELECT id FROM clientes WHERE nombre=?", (cliente_var.get(),))
        row_cl = c.fetchone()
        cliente_id = row_cl[0] if row_cl else 1

        # Validar Saturnos
        saturnos_usados = 0.0
        if sat > 0:
            c.execute("SELECT saldo_saturnos FROM monederos WHERE cliente_id=? AND activo=1", (cliente_id,))
            m = c.fetchone()
            if not m:
                messagebox.showwarning("Saturnos", "Este cliente no tiene monedero Saturnos activo")
                return
            c.execute("SELECT minimo_redimir, tasa_conversion FROM configuracion_saturnos WHERE id=1")
            cfg_s = c.fetchone()
            min_red = cfg_s[0] if cfg_s else 100
            tasa = cfg_s[1] if cfg_s else 1.0
            if m[0] < min_red:
                messagebox.showwarning("Saturnos", f"Mínimo para redimir: {min_red:,.0f} Saturnos\nSaldo actual: {m[0]:,.0f}")
                return
            if sat > m[0]:
                messagebox.showwarning("Saturnos", f"Saldo insuficiente.\nDisponible: {m[0]:,.0f} Saturnos")
                return
            saturnos_usados = sat
            sat_pesos = sat * tasa  # Conversión a pesos
        else:
            sat_pesos = 0.0

        # Validar Crédito
        credito_usado = 0.0
        credito_id_activo = None
        if cred > 0:
            c.execute("SELECT id, monto_disponible FROM creditos WHERE cliente_id=? AND estado='ACTIVO'", (cliente_id,))
            cr = c.fetchone()
            if not cr:
                messagebox.showwarning("Crédito", "Este cliente no tiene crédito activo")
                return
            if cred > cr[1]:
                messagebox.showwarning("Crédito", f"Crédito disponible: ${cr[1]:,.2f}\nSolicitado: ${cred:,.2f}")
                return
            credito_usado = cred
            credito_id_activo = cr[0]

        suma = efec + tarj + val + sat_pesos + credito_usado

        if suma < total:
            faltante = total - suma
            messagebox.showwarning("Pago insuficiente",
                                   f"Faltan ${faltante:,.2f} para completar el pago.\n\n"
                                   f"Total: ${total:,.2f}\n"
                                   f"Efectivo: ${efec:,.2f}\n"
                                   f"Tarjeta: ${tarj:,.2f}\n"
                                   f"Vale: ${val:,.2f}\n"
                                   f"Saturnos: {saturnos_usados:,.0f} (=${sat_pesos:,.2f})\n"
                                   f"Crédito: ${credito_usado:,.2f}\n"
                                   f"Suma: ${suma:,.2f}")
            return

        cambio = max(suma - total, 0)

        # Determinar tipo de pago
        metodos = []
        if efec > 0: metodos.append("EFECTIVO")
        if tarj > 0: metodos.append("TARJETA")
        if val > 0: metodos.append("VALE")
        if saturnos_usados > 0: metodos.append("SATURNOS")
        if credito_usado > 0: metodos.append("CREDITO")
        tipo_pago = "+".join(metodos) if metodos else "EFECTIVO"

        # GUARDAR VENTA
        folio_actual = f"V{datetime.now().strftime('%Y%m%d%H%M%S')}"
        fecha = datetime.now().strftime('%Y-%m-%d')
        hora = datetime.now().strftime('%H:%M:%S')

        c.execute("""INSERT INTO ventas (folio, fecha, hora, vendedor_id, cliente_id,
                    subtotal, iva, total, tipo_pago, monto_efectivo, monto_tarjeta)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                 (folio_actual, fecha, hora, usuario_id, cliente_id,
                  total, 0, total, tipo_pago, efec, tarj))

        venta_id = c.lastrowid

        # item = (codigo, nombre, precio_normal, oferta_txt, cant, subtotal)
        total_descuento_ofertas = 0.0
        total_bonus_saturnos = 0.0
        for item in carrito_items:
            c.execute("SELECT id FROM productos WHERE codigo=?", (item[0],))
            producto_id = c.fetchone()[0]
            cant = int(item[4])
            precio_unit = float(item[5]) / cant if cant > 0 else float(item[2])
            c.execute("""INSERT INTO detalle_ventas (venta_id, producto_id, cantidad,
                        precio_unitario, subtotal) VALUES (?,?,?,?,?)""",
                     (venta_id, producto_id, cant, precio_unit, float(item[5])))
            c.execute("UPDATE productos SET stock = stock - ? WHERE id = ?",
                     (cant, producto_id))

            # Registrar oferta aplicada
            oferta = ofertas_carrito.get(item[0])
            if oferta:
                precio_normal = float(item[2])
                descuento_item = (precio_normal * cant) - float(item[5])
                bonus_sat = round(float(item[5]) * (oferta["bonus_saturnos"] / 100.0), 2)
                total_descuento_ofertas += descuento_item
                total_bonus_saturnos += bonus_sat
                c.execute("""INSERT INTO ofertas_aplicadas (venta_id,oferta_id,producto_codigo,cantidad,
                            precio_normal,precio_oferta,descuento_aplicado,saturnos_extra,fecha)
                            VALUES (?,?,?,?,?,?,?,?,?)""",
                          (venta_id, oferta["id"], item[0], cant, precio_normal,
                           precio_unit, descuento_item, bonus_sat, fecha))
                # Incrementar unidades vendidas en la oferta
                c.execute("UPDATE ofertas SET unidades_vendidas=unidades_vendidas+? WHERE id=?",
                          (cant, oferta["id"]))

        # --- PROCESAR SATURNOS ---
        saturnos_ganados = 0.0
        if saturnos_usados > 0:
            # Redimir saturnos
            c.execute("SELECT saldo_saturnos FROM monederos WHERE cliente_id=?", (cliente_id,))
            saldo_ant = c.fetchone()[0]
            nuevo_saldo = saldo_ant - saturnos_usados
            c.execute("UPDATE monederos SET saldo_saturnos=?, total_gastado=total_gastado+? WHERE cliente_id=?",
                      (nuevo_saldo, saturnos_usados, cliente_id))
            c.execute("""INSERT INTO movimientos_saturnos (cliente_id,tipo,cantidad,saldo_anterior,saldo_nuevo,concepto,venta_id,usuario,fecha,hora)
                        VALUES (?,?,?,?,?,?,?,?,?,?)""",
                      (cliente_id, "REDIMIR", -saturnos_usados, saldo_ant, nuevo_saldo,
                       f"Pago venta {folio_actual}", venta_id, usuario_actual, fecha, hora))

        # Acumular saturnos (si checkbox activado y cliente no es PUBLICO GENERAL)
        if acumular_sat_var.get() and cliente_id > 1:
            c.execute("SELECT porcentaje_generico, porcentaje_patente, minimo_acumular, activo FROM configuracion_saturnos WHERE id=1")
            cfg_sat = c.fetchone()
            if cfg_sat and cfg_sat[3] == 1 and total >= cfg_sat[2]:
                pct = cfg_sat[0] / 100.0  # Usar genérico por defecto
                saturnos_ganados = round(total * pct, 2) + round(total_bonus_saturnos, 2)
                # Asegurar que exista monedero
                c.execute("SELECT saldo_saturnos FROM monederos WHERE cliente_id=?", (cliente_id,))
                m_row = c.fetchone()
                if m_row:
                    saldo_ant = m_row[0]
                    nuevo_saldo = saldo_ant + saturnos_ganados
                    c.execute("UPDATE monederos SET saldo_saturnos=?, total_acumulado=total_acumulado+? WHERE cliente_id=?",
                              (nuevo_saldo, saturnos_ganados, cliente_id))
                else:
                    nuevo_saldo = saturnos_ganados
                    saldo_ant = 0
                    c.execute("INSERT INTO monederos (cliente_id,saldo_saturnos,total_acumulado,total_gastado,activo,fecha_alta) VALUES (?,?,?,0,1,?)",
                              (cliente_id, saturnos_ganados, saturnos_ganados, fecha))
                c.execute("""INSERT INTO movimientos_saturnos (cliente_id,tipo,cantidad,saldo_anterior,saldo_nuevo,concepto,venta_id,usuario,fecha,hora)
                            VALUES (?,?,?,?,?,?,?,?,?,?)""",
                          (cliente_id, "ACUMULACION", saturnos_ganados, saldo_ant, nuevo_saldo,
                           f"Compra {folio_actual}", venta_id, usuario_actual, fecha, hora))

        # --- PROCESAR CRÉDITO ---
        if credito_usado > 0 and credito_id_activo:
            c.execute("UPDATE creditos SET monto_usado=monto_usado+?, monto_disponible=monto_disponible-? WHERE id=?",
                      (credito_usado, credito_usado, credito_id_activo))
            c.execute("""INSERT INTO pagos_credito (credito_id,folio_pago,monto,tipo_pago,fecha,hora,usuario,observaciones)
                        VALUES (?,?,?,?,?,?,?,?)""",
                      (credito_id_activo, folio_actual, credito_usado, "CARGO_VENTA", fecha, hora, usuario_actual,
                       f"Cargo por venta {folio_actual}"))

        conn.commit()

        registrar_auditoria("VENTA", "ventas", f"Folio: {folio_actual}, Total: ${total:,.2f}, Pago: {tipo_pago}")

        # Pasar info de pago mixto al ticket
        pago_info = {"efectivo": efec, "tarjeta": tarj, "vale": val,
                     "cambio": cambio, "tipo": tipo_pago,
                     "saturnos_usados": saturnos_usados, "saturnos_pesos": sat_pesos,
                     "credito_usado": credito_usado,
                     "saturnos_ganados": saturnos_ganados,
                     "descuento_ofertas": total_descuento_ofertas,
                     "bonus_saturnos_ofertas": total_bonus_saturnos,
                     "ofertas_carrito": dict(ofertas_carrito)}
        # Saldo actual saturnos para ticket
        if cliente_id > 1:
            c.execute("SELECT saldo_saturnos FROM monederos WHERE cliente_id=?", (cliente_id,))
            mr = c.fetchone()
            pago_info["saldo_saturnos"] = mr[0] if mr else 0
        else:
            pago_info["saldo_saturnos"] = 0

        mostrar_ticket(folio_actual, fecha, hora, cliente_var.get(),
                       tipo_pago, list(carrito_items), total, pago_info)

        # Mostrar ganancia Saturnos
        if saturnos_ganados > 0:
            messagebox.showinfo("Saturnos", f"Ganaste +{saturnos_ganados:,.0f} Saturnos!")

        # Limpiar todo
        carrito_items.clear()
        ofertas_carrito.clear()
        actualizar_carrito()
        efectivo_var.set("")
        tarjeta_var.set("")
        vale_var.set("")
        saturnos_var.set("")
        credito_var.set("")
        actualizar_info_cliente()

    def cancelar():
        if carrito_items and messagebox.askyesno("Cancelar", "Cancelar venta actual?"):
            carrito_items.clear()
            ofertas_carrito.clear()
            actualizar_carrito()
            efectivo_var.set("")
            tarjeta_var.set("")
            vale_var.set("")
            saturnos_var.set("")
            credito_var.set("")

    # === BOTÓN COBRAR EN EL FRAME DE ARRIBA ===
    btn_cobrar = tk.Button(btn_cobrar_frame, text="💰 COBRAR", command=cobrar,
             bg="#D32F2F", fg="white", font=("Segoe UI", 16, "bold"),
             relief=tk.RAISED, bd=2, padx=10, pady=12, cursor="hand2",
             activebackground="#F44336", activeforeground="white")
    btn_cobrar.pack(fill=tk.X, padx=2, pady=2)

    # Botón cancelar junto al cobrar
    btn_cancelar = tk.Button(btn_cobrar_frame, text="✖ CANCELAR", command=cancelar,
             bg="#424242", fg="white", font=("Segoe UI", 8),
             relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
    btn_cancelar.pack(fill=tk.X, padx=2, pady=2)

    # Focus en efectivo al presionar F5
    def _focus_efectivo(e=None):
        entry_efectivo.focus_set()
        entry_efectivo.select_range(0, tk.END)

    def _atajo_cobrar(e=None):
        cobrar()

    def _atajo_pausar(e=None):
        pausar_venta()

    right_panel_container.winfo_toplevel().bind("<F5>", _focus_efectivo)
    right_panel_container.winfo_toplevel().bind("<F12>", _atajo_cobrar)
    right_panel_container.winfo_toplevel().bind("<F8>", _atajo_pausar)

# ===== TICKET PROFESIONAL CON LOGO =====
def generar_texto_ticket(folio, fecha, hora, cliente, tipo_pago, items, total, pago_info=None):
    suc = obtener_sucursal()
    ancho = suc.get("ancho", 80)
    # Ajustar columnas según ancho de impresora
    if ancho <= 58:
        w = 32
    else:
        w = 44

    linea = "=" * w
    linea2 = "-" * w

    # Calcular IVA desglosado (16%)
    subtotal_sin_iva = total / 1.16
    iva = total - subtotal_sin_iva

    ticket = f"""{linea}
{"FARMACIAS MADRID":^{w}}
{suc['nombre']:^{w}}
{linea}
{suc['direccion'][:w]:^{w}}
{(suc['ciudad']+', '+suc['estado']+' C.P.'+suc['cp'])[:w]:^{w}}
{"Tel: "+suc['telefono']:^{w}}
{"RFC: "+suc['rfc']:^{w}}
{suc['email'][:w]:^{w}}
{linea2}
 Folio:    {folio}
 Fecha:    {fecha}    Hora: {hora}
 Vendedor: {usuario_actual}
 Cliente:  {cliente}
{linea2}
"""
    # items = (codigo, nombre, precio_normal, oferta_txt, cant, subtotal)
    ofertas_dict = pago_info.get("ofertas_carrito", {}) if pago_info else {}
    if ancho <= 58:
        ticket += f" {'CANT':>4} {'PRODUCTO':<16} {'SUBT':>8}\n"
        ticket += f"{linea2}\n"
        for item in items:
            nombre = item[1][:16].ljust(16)
            cant = str(item[4]).rjust(4)
            subtotal = f"${float(item[5]):,.2f}".rjust(8)
            ticket += f" {cant} {nombre} {subtotal}\n"
            ticket += f"      ${float(item[2]):,.2f} c/u\n"
            if item[3]:
                ticket += f"      OFERTA {item[3]}\n"
    else:
        ticket += f" {'CANT':>4} {'PRODUCTO':<22} {'P.UNIT':>8} {'SUBT':>8}\n"
        ticket += f"{linea2}\n"
        for item in items:
            nombre = item[1][:22].ljust(22)
            cant = str(item[4]).rjust(4)
            precio = f"${float(item[2]):,.2f}".rjust(8)
            subtotal = f"${float(item[5]):,.2f}".rjust(8)
            ticket += f" {cant} {nombre} {precio} {subtotal}\n"
            if item[3]:
                of_data = ofertas_dict.get(item[0])
                of_name = of_data["nombre"][:20] if of_data else ""
                ticket += f"      \u2605 {item[3]} {of_name}\n"

    # Descuento de ofertas
    desc_ofertas = pago_info.get("descuento_ofertas", 0) if pago_info else 0
    total_sin_desc = total + desc_ofertas

    ticket += f"{linea2}\n"
    if desc_ofertas > 0:
        ticket += f" Precio normal: {"${:>10,.2f}".format(total_sin_desc):>{w-16}}\n"
        ticket += f" Desc ofertas:  {"-${:>9,.2f}".format(desc_ofertas):>{w-16}}\n"
    ticket += f" SUBTOTAL:{"${:>10,.2f}".format(subtotal_sin_iva):>{w-10}}\n"
    ticket += f" IVA 16%: {"${:>10,.2f}".format(iva):>{w-10}}\n"
    ticket += f" TOTAL:   {"${:>10,.2f}".format(total):>{w-10}}\n"
    if desc_ofertas > 0:
        ticket += f" AHORRASTE: {"${:>8,.2f}".format(desc_ofertas):>{w-12}}\n"
    ticket += f"{linea}\n"
    # Desglose de pago
    if pago_info:
        if pago_info.get("efectivo", 0) > 0:
            ticket += f" Efectivo:{"${:>10,.2f}".format(pago_info['efectivo']):>{w-10}}\n"
        if pago_info.get("tarjeta", 0) > 0:
            ticket += f" Tarjeta: {"${:>10,.2f}".format(pago_info['tarjeta']):>{w-10}}\n"
        if pago_info.get("vale", 0) > 0:
            ticket += f" Vale:    {"${:>10,.2f}".format(pago_info['vale']):>{w-10}}\n"
        if pago_info.get("cambio", 0) > 0:
            ticket += f" CAMBIO:  {"${:>10,.2f}".format(pago_info['cambio']):>{w-10}}\n"
    else:
        ticket += f" Forma de pago: {tipo_pago}\n"

    # Saturnos y Crédito
    if pago_info:
        if pago_info.get("saturnos_usados", 0) > 0:
            ticket += f" Saturnos usados:{"${:>10,.2f}".format(pago_info['saturnos_pesos']):>{w-18}}\n"
            ticket += f"   ({pago_info['saturnos_usados']:,.0f} Saturnos)\n"
        if pago_info.get("credito_usado", 0) > 0:
            ticket += f" Crédito:  {"${:>10,.2f}".format(pago_info['credito_usado']):>{w-10}}\n"

    # Sección Programa Saturnos
    if pago_info and (pago_info.get("saturnos_ganados", 0) > 0 or pago_info.get("saturnos_usados", 0) > 0):
        ticket += f"{linea2}\n"
        ticket += f"{"PROGRAMA SATURNOS":^{w}}\n"
        if pago_info.get("saturnos_ganados", 0) > 0:
            bonus_of = pago_info.get("bonus_saturnos_ofertas", 0)
            base_sat = pago_info["saturnos_ganados"] - bonus_of
            ticket += f" Ganaste:       +{pago_info['saturnos_ganados']:,.0f} S\n"
            if bonus_of > 0:
                ticket += f"   (Base: {base_sat:,.0f} + Bonus oferta: {bonus_of:,.0f})\n"
        if pago_info.get("saturnos_usados", 0) > 0:
            ticket += f" Usaste:        -{pago_info['saturnos_usados']:,.0f} S\n"
        saldo = pago_info.get("saldo_saturnos", 0)
        ticket += f" Saldo actual:   {saldo:,.0f} S\n"
        ticket += f"{linea2}\n"

    ticket += f"""{linea}

{"Gracias por su compra":^{w}}
{"Vuelva pronto a Farmacias Madrid":^{w}}

{linea}
"""
    return ticket

def generar_ticket_imagen(folio, fecha, hora, cliente, tipo_pago, items, total, pago_info=None):
    """Genera imagen del ticket con logo de cápsula para impresión profesional."""
    suc = obtener_sucursal()
    ancho_mm = suc.get("ancho", 80)
    ancho_px = 576 if ancho_mm >= 80 else 384  # 80mm=576px, 58mm=384px

    # Calcular IVA
    subtotal_sin_iva = total / 1.16
    iva = total - subtotal_sin_iva

    # Cargar fuentes
    try:
        font_titulo = ImageFont.truetype("segoeui.ttf", 20)
        font_sub = ImageFont.truetype("segoeui.ttf", 14)
        font_normal = ImageFont.truetype("segoeui.ttf", 12)
        font_bold = ImageFont.truetype("segoeuib.ttf", 12)
        font_total = ImageFont.truetype("segoeuib.ttf", 18)
        font_small = ImageFont.truetype("segoeui.ttf", 10)
    except:
        font_titulo = ImageFont.load_default()
        font_sub = font_normal = font_bold = font_total = font_small = font_titulo

    # Pre-calcular altura
    n_items = len(items)
    altura = 320 + (n_items * 22) + 250  # header + items + footer

    img = Image.new('RGB', (ancho_px, altura), 'white')
    draw = ImageDraw.Draw(img)
    y = 10

    # LOGO - cápsula centrada (80x80)
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = suc.get("logo_path","") or os.path.join(base_dir, "logo.png")
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).resize((80, 80), Image.Resampling.LANCZOS)
            img.paste(logo, ((ancho_px - 80) // 2, y))
            y += 85
    except:
        y += 10

    # Nombre farmacia
    draw.text((ancho_px // 2, y), "FARMACIAS MADRID", fill='black', font=font_titulo, anchor='mt')
    y += 24
    draw.text((ancho_px // 2, y), suc['nombre'], fill='#333', font=font_sub, anchor='mt')
    y += 18

    # Dirección, RFC, teléfono, email
    for txt in [suc['direccion'], f"{suc['ciudad']}, {suc['estado']} C.P.{suc['cp']}",
                f"Tel: {suc['telefono']}", f"RFC: {suc['rfc']}", suc['email']]:
        if txt:
            draw.text((ancho_px // 2, y), txt, fill='#555', font=font_small, anchor='mt')
            y += 14

    # Línea separadora
    y += 5
    draw.line([(10, y), (ancho_px - 10, y)], fill='black', width=2)
    y += 8

    # Fecha, hora, folio, vendedor, cliente
    for label, val in [("Folio:", folio), ("Fecha:", f"{fecha}  Hora: {hora}"),
                       ("Vendedor:", usuario_actual), ("Cliente:", cliente)]:
        draw.text((15, y), label, fill='black', font=font_bold)
        draw.text((100, y), val, fill='#333', font=font_normal)
        y += 16

    # Línea separadora
    y += 4
    draw.line([(10, y), (ancho_px - 10, y)], fill='gray', width=1)
    y += 6

    # Encabezado tabla
    draw.text((15, y), "CANT", fill='black', font=font_bold)
    draw.text((55, y), "PRODUCTO", fill='black', font=font_bold)
    draw.text((ancho_px - 150, y), "PRECIO", fill='black', font=font_bold)
    draw.text((ancho_px - 70, y), "SUBT.", fill='black', font=font_bold)
    y += 16
    draw.line([(10, y), (ancho_px - 10, y)], fill='gray', width=1)
    y += 4

    # Productos (item = codigo, nombre, precio_normal, oferta_txt, cant, subtotal)
    for item in items:
        draw.text((20, y), str(item[4]), fill='black', font=font_normal)
        draw.text((55, y), item[1][:28], fill='black', font=font_normal)
        draw.text((ancho_px - 150, y), f"${float(item[2]):,.2f}", fill='black', font=font_normal)
        draw.text((ancho_px - 70, y), f"${float(item[5]):,.2f}", fill='black', font=font_normal)
        y += 18
        if item[3]:
            draw.text((55, y), f"\u2605 {item[3]}", fill='#FF5722', font=font_small)
            y += 14
        y += 2

    # Totales
    y += 4
    draw.line([(10, y), (ancho_px - 10, y)], fill='black', width=2)
    y += 8
    desc_ofertas = pago_info.get("descuento_ofertas", 0) if pago_info else 0
    if desc_ofertas > 0:
        draw.text((ancho_px - 200, y), "Desc ofertas:", fill='#D32F2F', font=font_bold)
        draw.text((ancho_px - 80, y), f"-${desc_ofertas:,.2f}", fill='#D32F2F', font=font_bold)
        y += 18
    draw.text((ancho_px - 200, y), "SUBTOTAL:", fill='black', font=font_bold)
    draw.text((ancho_px - 80, y), f"${subtotal_sin_iva:,.2f}", fill='black', font=font_bold)
    y += 18
    draw.text((ancho_px - 200, y), "IVA 16%:", fill='black', font=font_bold)
    draw.text((ancho_px - 80, y), f"${iva:,.2f}", fill='black', font=font_bold)
    y += 20
    draw.line([(ancho_px - 210, y), (ancho_px - 10, y)], fill='black', width=1)
    y += 4
    draw.text((ancho_px - 200, y), "TOTAL:", fill='black', font=font_total)
    draw.text((ancho_px - 90, y), f"${total:,.2f}", fill='black', font=font_total)
    y += 28

    # Forma de pago
    draw.line([(10, y), (ancho_px - 10, y)], fill='gray', width=1)
    y += 6
    if pago_info:
        for label, key in [("Efectivo:", "efectivo"), ("Tarjeta:", "tarjeta"), ("Vale:", "vale"), ("CAMBIO:", "cambio")]:
            if pago_info.get(key, 0) > 0:
                draw.text((15, y), label, fill='black', font=font_bold)
                draw.text((120, y), f"${pago_info[key]:,.2f}", fill='black', font=font_normal)
                y += 16
    else:
        draw.text((15, y), f"Forma de pago: {tipo_pago}", fill='black', font=font_normal)
        y += 16

    # Pie del ticket
    y += 10
    draw.line([(10, y), (ancho_px - 10, y)], fill='black', width=2)
    y += 12
    draw.text((ancho_px // 2, y), "Gracias por su compra", fill='black', font=font_sub, anchor='mt')
    y += 18
    draw.text((ancho_px // 2, y), "Vuelva pronto a Farmacias Madrid", fill='#555', font=font_small, anchor='mt')
    y += 20

    # QR opcional del folio
    try:
        import qrcode
        qr = qrcode.make(folio, box_size=3, border=1)
        qr = qr.resize((80, 80))
        img.paste(qr, ((ancho_px - 80) // 2, y))
        y += 85
    except ImportError:
        pass

    # Recortar imagen al tamaño real
    img = img.crop((0, 0, ancho_px, y + 10))
    return img

def imprimir_ticket_archivo(texto_ticket, folio):
    """Imprime ticket a archivo y lo envía a impresora."""
    suc = obtener_sucursal()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base_dir, f"ticket_{folio}.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto_ticket)

    copias = suc.get("copias", 1)
    impresora = suc.get("impresora", "")

    for _ in range(copias):
        try:
            if impresora:
                # Enviar directo a impresora nombrada
                os.system(f'copy /b "{ruta}" "{impresora}"')
            else:
                os.startfile(ruta, "print")
        except Exception:
            pass
    return ruta

def mostrar_ticket(folio, fecha, hora, cliente, tipo_pago, items, total, pago_info=None):
    global ultimo_folio_venta
    ultimo_folio_venta = folio

    ticket_win = tk.Toplevel()
    ticket_win.title(f"Ticket Profesional - {folio}")
    ticket_win.geometry("560x780")
    ticket_win.resizable(False, False)
    ticket_win.configure(bg="white")

    # Header
    hdr = tk.Frame(ticket_win, bg="#4CAF50", height=40)
    hdr.pack(fill=tk.X)
    hdr.pack_propagate(False)
    tk.Label(hdr, text=f"TICKET DE VENTA - {folio}", font=("Segoe UI", 12, "bold"),
            bg="#4CAF50", fg="white").pack(pady=8)

    texto_ticket = generar_texto_ticket(folio, fecha, hora, cliente, tipo_pago, items, total, pago_info)

    # Vista previa del ticket
    preview = tk.Frame(ticket_win, bg="white")
    preview.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    # Mostrar imagen del ticket si PIL disponible
    ticket_img = None
    try:
        ticket_img = generar_ticket_imagen(folio, fecha, hora, cliente, tipo_pago, items, total, pago_info)
        # Escalar para vista previa
        ratio = min(520 / ticket_img.width, 600 / ticket_img.height)
        preview_size = (int(ticket_img.width * ratio), int(ticket_img.height * ratio))
        preview_img = ticket_img.resize(preview_size, Image.Resampling.LANCZOS)
        tk_preview = ImageTk.PhotoImage(preview_img)

        canvas = tk.Canvas(preview, width=preview_size[0], height=preview_size[1],
                          bg="#FFFFF0", relief=tk.SOLID, bd=1)
        canvas.pack(pady=5)
        canvas.create_image(preview_size[0]//2, preview_size[1]//2, image=tk_preview)
        canvas._img_ref = tk_preview  # Mantener referencia
    except Exception:
        # Fallback a texto
        text_widget = tk.Text(preview, font=("Courier New", 9), wrap=tk.NONE,
                              bg="#FFFFF0", relief=tk.SOLID, bd=1, height=28)
        text_widget.insert("1.0", texto_ticket)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)

    # Resumen de pago mixto
    if pago_info and ("+" in pago_info.get("tipo", "")):
        mix_frame = tk.Frame(ticket_win, bg="#E3F2FD", relief=tk.RIDGE, bd=1)
        mix_frame.pack(fill=tk.X, padx=15, pady=3)
        tk.Label(mix_frame, text="PAGO MIXTO", font=("Segoe UI", 10, "bold"),
                bg="#E3F2FD", fg="#1565C0").pack(pady=(4,0))
        desglose = ""
        if pago_info["efectivo"] > 0: desglose += f"  Efectivo: ${pago_info['efectivo']:,.2f}"
        if pago_info["tarjeta"] > 0: desglose += f"  Tarjeta: ${pago_info['tarjeta']:,.2f}"
        if pago_info["vale"] > 0: desglose += f"  Vale: ${pago_info['vale']:,.2f}"
        if pago_info["cambio"] > 0: desglose += f"  Cambio: ${pago_info['cambio']:,.2f}"
        tk.Label(mix_frame, text=desglose, font=("Segoe UI", 9),
                bg="#E3F2FD", fg="#37474F").pack(pady=(0,4))

    # Botones
    btn_frame = tk.Frame(ticket_win, bg="white")
    btn_frame.pack(pady=8)

    def imprimir_texto():
        ruta = imprimir_ticket_archivo(texto_ticket, folio)
        messagebox.showinfo("Imprimir", f"Ticket enviado a imprimir.\nGuardado en: {ruta}")

    def imprimir_imagen():
        if ticket_img:
            try:
                tmp = os.path.join(tempfile.gettempdir(), f"ticket_{folio}.png")
                ticket_img.save(tmp, "PNG")
                os.startfile(tmp, "print")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo imprimir imagen: {e}")
        else:
            imprimir_texto()

    # === FUNCIÓN ENVIAR POR WHATSAPP ===
    def enviar_whatsapp():
        # Pedir número de teléfono
        tel_win = tk.Toplevel(ticket_win)
        tel_win.title("Enviar por WhatsApp")
        tel_win.geometry("350x200")
        tel_win.configure(bg="white")
        tel_win.transient(ticket_win)
        tel_win.grab_set()

        tk.Label(tel_win, text="📱 ENVIAR TICKET POR WHATSAPP",
                font=("Segoe UI", 12, "bold"), bg="white", fg="#25D366").pack(pady=15)

        tk.Label(tel_win, text="Número de teléfono (con código de país):",
                font=("Segoe UI", 10), bg="white").pack(pady=5)
        tk.Label(tel_win, text="Ejemplo: 52 para México + número",
                font=("Segoe UI", 8), bg="white", fg="gray").pack()

        # Obtener teléfono del cliente si existe
        tel_cliente = ""
        c.execute("SELECT telefono FROM clientes WHERE nombre=?", (cliente,))
        tel_row = c.fetchone()
        if tel_row and tel_row[0]:
            tel_cliente = "52" + tel_row[0].replace(" ", "").replace("-", "")

        tel_entry = tk.Entry(tel_win, font=("Segoe UI", 14), width=20, justify="center")
        tel_entry.pack(pady=10)
        tel_entry.insert(0, tel_cliente if tel_cliente else "527753200224")
        tel_entry.focus()

        def enviar():
            telefono = tel_entry.get().strip().replace(" ", "").replace("-", "").replace("+", "")
            if len(telefono) < 10:
                messagebox.showwarning("Error", "Ingresa un número válido")
                return

            # Obtener info completa del cliente
            c.execute("""SELECT nombre, telefono, direccion, email, rfc
                        FROM clientes WHERE nombre=?""", (cliente,))
            cl_info = c.fetchone()
            cl_nombre = cl_info[0] if cl_info else cliente
            cl_tel = cl_info[1] if cl_info and cl_info[1] else "N/A"
            cl_dir = cl_info[2] if cl_info and cl_info[2] else "N/A"

            # Obtener saldo Saturnos
            c.execute("""SELECT m.saldo_saturnos FROM monederos m
                        JOIN clientes cl ON m.cliente_id=cl.id
                        WHERE cl.nombre=?""", (cliente,))
            sat_row = c.fetchone()
            saldo_sat = sat_row[0] if sat_row else 0

            # Obtener crédito disponible
            c.execute("""SELECT cr.monto_disponible FROM creditos cr
                        JOIN clientes cl ON cr.cliente_id=cl.id
                        WHERE cl.nombre=? AND cr.estado='ACTIVO'""", (cliente,))
            cred_row = c.fetchone()
            credito_disp = cred_row[0] if cred_row else 0

            # Crear mensaje para WhatsApp
            suc = obtener_sucursal()
            mensaje = f"""🧾 *TICKET DE COMPRA*
━━━━━━━━━━━━━━━━━━━━
🏪 *{suc.get('nombre', 'FARMACIAS MADRID')}*
📍 {suc.get('direccion', '')}
📞 {suc.get('telefono', '')}
━━━━━━━━━━━━━━━━━━━━
📋 *Folio:* {folio}
📅 *Fecha:* {fecha}
🕐 *Hora:* {hora}
━━━━━━━━━━━━━━━━━━━━
👤 *CLIENTE:*
• Nombre: {cl_nombre}
• Tel: {cl_tel}
• Dir: {cl_dir}
⭐ Saturnos: {saldo_sat:,.0f}
💳 Crédito: ${credito_disp:,.2f}
━━━━━━━━━━━━━━━━━━━━
🛒 *PRODUCTOS:*
"""
            for item in items:
                nombre = item[1][:30]
                cant = item[4]
                subtotal = float(item[5])
                mensaje += f"• {nombre} x{cant} = ${subtotal:,.2f}\n"

            mensaje += f"""━━━━━━━━━━━━━━━━━━
💰 *TOTAL: ${total:,.2f}*
💳 Pago: {tipo_pago}
"""
            if pago_info and pago_info.get("cambio", 0) > 0:
                mensaje += f"💵 Cambio: ${pago_info['cambio']:,.2f}\n"

            mensaje += f"""━━━━━━━━━━━━━━━━━━
¡Gracias por su compra! 🙏
*{suc.get('nombre', 'FARMACIAS MADRID')}*"""

            # Abrir WhatsApp Web con el mensaje
            import urllib.parse
            mensaje_encoded = urllib.parse.quote(mensaje)
            url = f"https://wa.me/{telefono}?text={mensaje_encoded}"

            import webbrowser
            webbrowser.open(url)

            tel_win.destroy()
            messagebox.showinfo("WhatsApp", f"Se abrió WhatsApp para enviar al número {telefono}")

        tk.Button(tel_win, text="📤 ENVIAR", command=enviar,
                 bg="#25D366", fg="white", font=("Segoe UI", 12, "bold"),
                 padx=20, pady=8, cursor="hand2", relief=tk.FLAT).pack(pady=15)

    # Botón WhatsApp grande y verde
    tk.Button(btn_frame, text="📱 WHATSAPP", command=enviar_whatsapp,
             bg="#25D366", fg="white", font=("Segoe UI", 10, "bold"),
             padx=14, pady=6, cursor="hand2", relief=tk.FLAT).pack(side=tk.LEFT, padx=4)

    tk.Button(btn_frame, text="🖨️ IMPRIMIR", command=imprimir_texto,
             bg="#1565C0", fg="white", font=("Segoe UI", 10, "bold"),
             padx=14, pady=6, cursor="hand2", relief=tk.FLAT).pack(side=tk.LEFT, padx=4)

    tk.Button(btn_frame, text="CERRAR", command=ticket_win.destroy,
             bg="#757575", fg="white", font=("Segoe UI", 10, "bold"),
             padx=14, pady=6, cursor="hand2", relief=tk.FLAT).pack(side=tk.LEFT, padx=4)

    # Auto-imprimir si está configurado
    suc = obtener_sucursal()
    if suc.get("auto_imprimir", 0):
        ticket_win.after(500, imprimir_texto)

# ===== MÓDULO COMPRAS =====
def ver_compras():
    limpiar()
    
    header_mod = tk.Frame(main, bg=AZUL_FARMACIA, height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="🛍️ COMPRAS A PROVEEDORES", font=("Segoe UI", 13, "bold"),
            bg=AZUL_FARMACIA, fg="white").pack(side=tk.LEFT, padx=12, pady=10)
    
    content = tk.Frame(main, bg="white")
    content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    tk.Label(content, text="REGISTRO DE COMPRAS", font=("Arial", 14, "bold"),
            bg="white").pack(pady=15)
    
    form = tk.Frame(content, bg="white")
    form.pack(pady=10)
    
    tk.Label(form, text="Folio:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=0, sticky="e", padx=10, pady=8)
    folio_var = tk.StringVar(value=f"C{datetime.now().strftime('%Y%m%d%H%M%S')}")
    tk.Entry(form, textvariable=folio_var, width=30, state="readonly").grid(row=0, column=1, padx=10, pady=8)
    
    tk.Label(form, text="Proveedor:", font=("Arial", 10, "bold"), bg="white").grid(row=1, column=0, sticky="e", padx=10, pady=8)
    prov_var = tk.StringVar()
    prov_combo = ttk.Combobox(form, textvariable=prov_var, width=28, state="readonly")
    c.execute("SELECT nombre FROM proveedores")
    prov_combo['values'] = [row[0] for row in c.fetchall()]
    if prov_combo['values']:
        prov_combo.current(0)
    prov_combo.grid(row=1, column=1, padx=10, pady=8)
    
    tk.Label(form, text="Producto (código):", font=("Arial", 10, "bold"), bg="white").grid(row=2, column=0, sticky="e", padx=10, pady=8)
    prod_frame = tk.Frame(form, bg="white")
    prod_frame.grid(row=2, column=1, padx=10, pady=8, sticky="w")
    
    prod_entry = tk.Entry(prod_frame, width=20)
    prod_entry.pack(side=tk.LEFT, padx=5)
    
    prod_nombre_var = tk.StringVar(value="")
    tk.Label(prod_frame, textvariable=prod_nombre_var, font=("Arial", 9),
            bg="white", fg="#27AE60").pack(side=tk.LEFT, padx=5)
    
    def buscar_producto(event=None):
        codigo = prod_entry.get().strip().upper()
        if not codigo:
            return
        
        c.execute("SELECT nombre FROM productos WHERE codigo=?", (codigo,))
        producto = c.fetchone()
        
        if producto:
            prod_nombre_var.set(f"✓ {producto[0][:50]}")
        else:
            prod_nombre_var.set("✗ No encontrado")
    
    prod_entry.bind("<Return>", buscar_producto)
    tk.Button(prod_frame, text="🔍", command=buscar_producto,
             bg="#4A90E2", fg="white", font=("Arial", 8, "bold"),
             padx=5, pady=2).pack(side=tk.LEFT, padx=2)
    
    tk.Label(form, text="Cantidad:", font=("Arial", 10, "bold"), bg="white").grid(row=3, column=0, sticky="e", padx=10, pady=8)
    cant_spin = tk.Spinbox(form, from_=1, to=10000, width=28)
    cant_spin.grid(row=3, column=1, padx=10, pady=8)
    
    tk.Label(form, text="Precio compra:", font=("Arial", 10, "bold"), bg="white").grid(row=4, column=0, sticky="e", padx=10, pady=8)
    precio_entry = tk.Entry(form, width=30)
    precio_entry.grid(row=4, column=1, padx=10, pady=8)
    
    tk.Label(form, text="Total:", font=("Arial", 10, "bold"), bg="white").grid(row=5, column=0, sticky="e", padx=10, pady=8)
    total_var = tk.StringVar(value="$0.00")
    tk.Label(form, textvariable=total_var, font=("Arial", 12, "bold"),
            bg="white", fg="#27AE60").grid(row=5, column=1, sticky="w", padx=10, pady=8)
    
    def calcular_total(event=None):
        try:
            cant = int(cant_spin.get())
            precio = float(precio_entry.get())
            total = cant * precio
            total_var.set(f"${total:,.2f}")
        except:
            total_var.set("$0.00")
    
    cant_spin.bind("<KeyRelease>", calcular_total)
    precio_entry.bind("<KeyRelease>", calcular_total)
    
    def registrar():
        if not prov_var.get() or not prod_entry.get():
            messagebox.showwarning("Incompleto", "Completa todos los campos")
            return
        
        c.execute("SELECT id, nombre FROM productos WHERE codigo=?", (prod_entry.get().upper(),))
        producto = c.fetchone()
        
        if not producto:
            messagebox.showerror("Error", "Producto no encontrado")
            return
        
        try:
            cant = int(cant_spin.get())
            precio = float(precio_entry.get())
            total = cant * precio
            
            c.execute("UPDATE productos SET stock = stock + ? WHERE codigo = ?",
                     (cant, prod_entry.get().upper()))
            
            conn.commit()
            
            messagebox.showinfo("Registrado",
                              f"✅ Compra {folio_var.get()} registrada\n\n"
                              f"Proveedor: {prov_var.get()}\n"
                              f"Producto: {producto[1][:50]}\n"
                              f"Cantidad: {cant}\n"
                              f"Total: ${total:,.2f}\n\n"
                              f"Stock actualizado")
            
            prod_entry.delete(0, tk.END)
            prod_nombre_var.set("")
            cant_spin.delete(0, tk.END)
            cant_spin.insert(0, "1")
            precio_entry.delete(0, tk.END)
            total_var.set("$0.00")
            folio_var.set(f"C{datetime.now().strftime('%Y%m%d%H%M%S')}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar compra: {str(e)}")
    
    tk.Button(content, text="✅ REGISTRAR COMPRA", command=registrar,
             bg="#27AE60", fg="white", font=("Arial", 12, "bold"),
             padx=30, pady=12).pack(pady=30)

# ===== MÓDULO INVENTARIO =====
def ver_inventario():
    limpiar()

    header_mod = tk.Frame(main, bg=AZUL_FARMACIA, height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="📋 INVENTARIO - CON IMÁGENES", font=("Segoe UI", 13, "bold"),
            bg=AZUL_FARMACIA, fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    content = tk.Frame(main, bg="#F5F7FA")
    content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    search_frame = tk.Frame(content, bg="#F5F7FA")
    search_frame.pack(fill=tk.X, pady=10)

    tk.Label(search_frame, text="🔍 Buscar:", font=("Arial", 10, "bold"),
            bg="#F5F7FA").pack(side=tk.LEFT, padx=5)

    search_entry = tk.Entry(search_frame, width=40, font=("Arial", 10))
    search_entry.pack(side=tk.LEFT, padx=5)

    tk.Label(search_frame, text="Categoría:", font=("Arial", 10, "bold"),
            bg="#F5F7FA").pack(side=tk.LEFT, padx=15)

    cat_var = tk.StringVar(value="TODAS")
    cat_combo = ttk.Combobox(search_frame, textvariable=cat_var, width=20,
                            values=["TODAS", "MEDICAMENTOS", "HIGIENE", "ESPECIALIDAD"], state="readonly")
    cat_combo.pack(side=tk.LEFT, padx=5)

    # Botones de acciones
    btn_frame = tk.Frame(content, bg="#F5F7FA")
    btn_frame.pack(fill=tk.X, pady=5)

    def importar_excel():
        """Importar productos desde archivo Excel."""
        from tkinter import filedialog
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Error", "Necesitas instalar pandas: pip install pandas openpyxl")
            return

        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not archivo:
            return

        try:
            if archivo.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)

            # Normalizar nombres de columnas
            df.columns = [col.upper().strip() for col in df.columns]

            # Mapear columnas comunes
            col_map = {
                'CODIGO': ['CODIGO', 'CODE', 'SKU', 'ID'],
                'NOMBRE': ['NOMBRE', 'NAME', 'DESCRIPCION', 'PRODUCTO'],
                'PRECIO': ['PRECIO', 'PRECIO_VENTA', 'PRICE', 'PVP'],
                'PRECIO_OFERTA': ['PRECIO_OFERTA', 'OFERTA', 'DESCUENTO'],
                'STOCK': ['STOCK', 'CANTIDAD', 'EXISTENCIA', 'QTY'],
                'CATEGORIA': ['CATEGORIA', 'CATEGORY', 'TIPO'],
            }

            for target, options in col_map.items():
                for opt in options:
                    if opt in df.columns and target not in df.columns:
                        df = df.rename(columns={opt: target})
                        break

            importados = 0
            actualizados = 0

            for _, row in df.iterrows():
                codigo = str(row.get('CODIGO', '')).strip()
                nombre = str(row.get('NOMBRE', '')).strip()
                if not codigo or not nombre:
                    continue

                precio = float(row.get('PRECIO', 0) or 0)
                precio_oferta = float(row.get('PRECIO_OFERTA', 0) or 0)
                # Descuento base 35%, máximo 90%
                if precio_oferta <= 0:
                    precio_oferta = precio * 0.65  # 35% descuento base
                # Validar rango: mínimo 65% del precio (35% desc), máximo 10% (90% desc)
                precio_oferta = max(precio * 0.10, min(precio_oferta, precio * 0.65))
                stock = int(row.get('STOCK', 50) or 50)
                categoria = str(row.get('CATEGORIA', 'MEDICAMENTOS')).strip().upper()

                # Verificar si existe
                c.execute("SELECT id FROM productos WHERE codigo=?", (codigo,))
                existe = c.fetchone()

                if existe:
                    c.execute("""UPDATE productos SET nombre=?, precio_venta=?, precio_oferta=?, stock=?, categoria=?
                                WHERE codigo=?""", (nombre, precio, precio_oferta, stock, categoria, codigo))
                    actualizados += 1
                else:
                    c.execute("""INSERT INTO productos (codigo, nombre, precio_venta, precio_oferta, stock, categoria, precio_costo)
                                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                             (codigo, nombre, precio, precio_oferta, stock, categoria, precio * 0.55))
                    importados += 1

            conn.commit()
            messagebox.showinfo("Importación completa",
                f"Nuevos: {importados}\nActualizados: {actualizados}")
            buscar()  # Refrescar lista

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar: {str(e)}")

    def exportar_excel():
        """Exportar productos a Excel."""
        from tkinter import filedialog
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Error", "Necesitas instalar pandas: pip install pandas openpyxl")
            return

        archivo = filedialog.asksaveasfilename(
            title="Guardar como Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )
        if not archivo:
            return

        try:
            c.execute("""SELECT codigo, nombre, categoria, laboratorio, stock,
                        precio_costo, precio_venta, precio_oferta FROM productos""")
            datos = c.fetchall()
            df = pd.DataFrame(datos, columns=['CODIGO', 'NOMBRE', 'CATEGORIA', 'LABORATORIO',
                                              'STOCK', 'PRECIO_COSTO', 'PRECIO_VENTA', 'PRECIO_OFERTA'])
            if archivo.endswith('.csv'):
                df.to_csv(archivo, index=False)
            else:
                df.to_excel(archivo, index=False)
            messagebox.showinfo("Exportación completa", f"Archivo guardado: {archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    tk.Button(btn_frame, text="📥 IMPORTAR EXCEL", command=importar_excel,
             bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), padx=15, pady=5).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="📤 EXPORTAR EXCEL", command=exportar_excel,
             bg="#2196F3", fg="white", font=("Arial", 9, "bold"), padx=15, pady=5).pack(side=tk.LEFT, padx=5)

    # Toggle vista: Lista / Tarjetas
    vista_var = tk.StringVar(value="LISTA")
    tk.Label(btn_frame, text="Vista:", font=("Arial", 10, "bold"),
            bg="#F5F7FA").pack(side=tk.LEFT, padx=15)
    ttk.Radiobutton(btn_frame, text="Lista", variable=vista_var, value="LISTA").pack(side=tk.LEFT)
    ttk.Radiobutton(btn_frame, text="Tarjetas", variable=vista_var, value="TARJETAS").pack(side=tk.LEFT)

    # Frame contenedor para ambas vistas
    container = tk.Frame(content, bg="#F5F7FA")
    container.pack(fill=tk.BOTH, expand=True, pady=10)

    # Vista Lista (Treeview tradicional)
    tree_frame = tk.Frame(container, bg="white")

    cols = ("CÓDIGO", "NOMBRE", "CATEGORÍA", "P.NORMAL", "P.OFERTA", "STOCK")
    tree_inv = ttk.Treeview(tree_frame, columns=cols, show="headings", height=22)

    for col in cols:
        tree_inv.heading(col, text=col)

    tree_inv.column("CÓDIGO", width=90)
    tree_inv.column("NOMBRE", width=450)
    tree_inv.column("CATEGORÍA", width=100)
    tree_inv.column("P.NORMAL", width=90)
    tree_inv.column("P.OFERTA", width=90)
    tree_inv.column("PRECIO", width=100)
    tree_inv.column("STOCK", width=80)

    scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_inv.yview)
    tree_inv.configure(yscrollcommand=scroll.set)

    # Vista Tarjetas (con imagenes)
    cards_frame = tk.Frame(container, bg="#F5F7FA")
    canvas_cards = tk.Canvas(cards_frame, bg="#F5F7FA", highlightthickness=0)
    scrollbar_cards = ttk.Scrollbar(cards_frame, orient="vertical", command=canvas_cards.yview)
    scrollable_cards = tk.Frame(canvas_cards, bg="#F5F7FA")

    scrollable_cards.bind("<Configure>", lambda e: canvas_cards.configure(scrollregion=canvas_cards.bbox("all")))
    canvas_cards.create_window((0, 0), window=scrollable_cards, anchor="nw")
    canvas_cards.configure(yscrollcommand=scrollbar_cards.set)

    img_refs_inv = []  # Referencias de imagenes

    def mostrar_vista():
        if vista_var.get() == "LISTA":
            cards_frame.pack_forget()
            tree_frame.pack(fill=tk.BOTH, expand=True)
            tree_inv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scroll.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            tree_frame.pack_forget()
            cards_frame.pack(fill=tk.BOTH, expand=True)
            canvas_cards.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar_cards.pack(side=tk.RIGHT, fill=tk.Y)

    vista_var.trace("w", lambda *args: mostrar_vista())
    mostrar_vista()  # Inicial

    tree_inv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # Función para editar producto (doble click)
    def editar_producto(event=None):
        sel = tree_inv.selection()
        if not sel:
            return
        item = tree_inv.item(sel[0])
        codigo = item['values'][0]

        c.execute("SELECT codigo, nombre, precio_venta, precio_oferta, stock, categoria FROM productos WHERE codigo=?", (codigo,))
        prod = c.fetchone()
        if not prod:
            return

        # Ventana de edición
        edit_win = tk.Toplevel(main)
        edit_win.title(f"Editar: {prod[1][:40]}")
        edit_win.geometry("450x350")
        edit_win.configure(bg="#F5F7FA")
        edit_win.transient(main)
        edit_win.grab_set()

        tk.Label(edit_win, text="EDITAR PRODUCTO", font=("Segoe UI", 14, "bold"),
                bg="#F5F7FA", fg="#1565C0").pack(pady=10)

        # Nombre (solo lectura)
        tk.Label(edit_win, text=prod[1][:60], font=("Segoe UI", 10),
                bg="#F5F7FA", fg="#333", wraplength=400).pack(pady=5)

        # Frame para campos
        campos = tk.Frame(edit_win, bg="#F5F7FA")
        campos.pack(pady=10, padx=20, fill=tk.X)

        # Precio normal
        tk.Label(campos, text="Precio Normal:", font=("Arial", 10, "bold"),
                bg="#F5F7FA").grid(row=0, column=0, sticky="w", pady=5)
        precio_var = tk.StringVar(value=f"{prod[2]:.2f}")
        tk.Entry(campos, textvariable=precio_var, font=("Arial", 11), width=15).grid(row=0, column=1, pady=5, padx=10)

        # Precio oferta con slider de descuento
        tk.Label(campos, text="Precio Oferta:", font=("Arial", 10, "bold"),
                bg="#F5F7FA").grid(row=1, column=0, sticky="w", pady=5)
        oferta_var = tk.StringVar(value=f"{prod[3]:.2f}")
        oferta_entry = tk.Entry(campos, textvariable=oferta_var, font=("Arial", 11), width=15)
        oferta_entry.grid(row=1, column=1, pady=5, padx=10)

        # Slider de descuento (35% - 90%)
        tk.Label(campos, text="Descuento:", font=("Arial", 10, "bold"),
                bg="#F5F7FA").grid(row=2, column=0, sticky="w", pady=5)

        desc_frame = tk.Frame(campos, bg="#F5F7FA")
        desc_frame.grid(row=2, column=1, pady=5, padx=10, sticky="w")

        desc_pct = round((1 - prod[3]/prod[2]) * 100) if prod[2] > 0 else 35
        desc_var = tk.IntVar(value=max(35, min(desc_pct, 90)))

        def actualizar_oferta(*args):
            try:
                precio = float(precio_var.get())
                desc = desc_var.get()
                nueva_oferta = round(precio * (1 - desc/100), 2)
                oferta_var.set(f"{nueva_oferta:.2f}")
            except:
                pass

        desc_scale = tk.Scale(desc_frame, from_=35, to=90, orient=tk.HORIZONTAL,
                             variable=desc_var, bg="#F5F7FA", length=150,
                             command=actualizar_oferta)
        desc_scale.pack(side=tk.LEFT)
        tk.Label(desc_frame, text="%", font=("Arial", 10), bg="#F5F7FA").pack(side=tk.LEFT)

        # Stock
        tk.Label(campos, text="Stock:", font=("Arial", 10, "bold"),
                bg="#F5F7FA").grid(row=3, column=0, sticky="w", pady=5)
        stock_var = tk.StringVar(value=str(prod[4]))
        tk.Entry(campos, textvariable=stock_var, font=("Arial", 11), width=15).grid(row=3, column=1, pady=5, padx=10)

        def guardar_cambios():
            try:
                nuevo_precio = float(precio_var.get())
                nueva_oferta = float(oferta_var.get())
                nuevo_stock = int(stock_var.get())

                # Validar descuento (35%-90%)
                nueva_oferta = max(nuevo_precio * 0.10, min(nueva_oferta, nuevo_precio * 0.65))

                c.execute("""UPDATE productos SET precio_venta=?, precio_oferta=?, stock=?
                            WHERE codigo=?""", (nuevo_precio, nueva_oferta, nuevo_stock, codigo))
                conn.commit()
                messagebox.showinfo("Guardado", "Producto actualizado correctamente")
                edit_win.destroy()
                buscar()  # Refrescar lista
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        # Botones
        btn_frame = tk.Frame(edit_win, bg="#F5F7FA")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="💾 GUARDAR", command=guardar_cambios,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=20, pady=8).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="CANCELAR", command=edit_win.destroy,
                 bg="#9E9E9E", fg="white", font=("Arial", 10, "bold"), padx=20, pady=8).pack(side=tk.LEFT, padx=10)

    tree_inv.bind("<Double-1>", editar_producto)

    # Obtener config de saturnos
    c.execute("SELECT porcentaje_generico, porcentaje_patente FROM configuracion_saturnos WHERE id=1")
    sat_cfg = c.fetchone()
    sat_generico = sat_cfg[0] if sat_cfg else 10.0
    sat_patente = sat_cfg[1] if sat_cfg else 8.0

    def buscar(event=None):
        # Limpiar lista
        for item in tree_inv.get_children():
            tree_inv.delete(item)

        # Limpiar tarjetas
        for widget in scrollable_cards.winfo_children():
            widget.destroy()
        img_refs_inv.clear()

        busqueda = search_entry.get()
        categoria = cat_var.get()

        if categoria == "TODAS":
            c.execute("SELECT codigo, nombre, categoria, precio_venta, precio_oferta, stock, imagen, laboratorio FROM productos WHERE nombre LIKE ? LIMIT 100",
                     (f"%{busqueda}%",))
        else:
            c.execute("SELECT codigo, nombre, categoria, precio_venta, precio_oferta, stock, imagen, laboratorio FROM productos WHERE categoria=? AND nombre LIKE ? LIMIT 100",
                     (categoria, f"%{busqueda}%"))

        productos_inv = c.fetchall()

        for row in productos_inv:
            codigo, nombre, cat, precio, precio_oferta, stock, img_path, lab = row
            precio_oferta = precio_oferta or precio * 0.65

            # Vista Lista - mostrar ambos precios
            tree_inv.insert("", "end", values=(codigo, nombre, cat, f"${precio:,.2f}", f"${precio_oferta:,.2f}", stock))

            # Vista Tarjetas
            card = tk.Frame(scrollable_cards, bg="white", relief="raised", bd=1)
            card.pack(fill=tk.X, padx=5, pady=3)

            # Imagen
            img_label = tk.Label(card, bg="white", width=60, height=60)
            img_label.pack(side=tk.LEFT, padx=8, pady=8)

            base_dir = os.path.dirname(os.path.abspath(__file__))
            img_loaded = False

            if img_path:
                img_full = os.path.join(base_dir, img_path)
                if os.path.exists(img_full):
                    try:
                        img = Image.open(img_full)
                        img = img.resize((55, 55), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        img_label.configure(image=photo, width=55, height=55)
                        img_refs_inv.append(photo)
                        img_loaded = True
                    except:
                        pass

            # Si no se cargó imagen, usar placeholder
            if not img_loaded:
                placeholder_path = os.path.join(base_dir, "imagenes", "productos", "_placeholder.png")
                if os.path.exists(placeholder_path):
                    try:
                        img = Image.open(placeholder_path)
                        img = img.resize((55, 55), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        img_label.configure(image=photo, width=55, height=55)
                        img_refs_inv.append(photo)
                    except:
                        img_label.configure(text="📦", font=("Arial", 18), width=6, height=3)
                else:
                    img_label.configure(text="📦", font=("Arial", 18), width=6, height=3)

            # Info
            info = tk.Frame(card, bg="white")
            info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)

            tk.Label(info, text=nombre[:55], font=("Segoe UI", 10, "bold"),
                    bg="white", anchor="w").pack(anchor="w")
            tk.Label(info, text=f"Código: {codigo}  |  {cat}  |  {lab or ''}", font=("Segoe UI", 8),
                    bg="white", fg="#666", anchor="w").pack(anchor="w")

            # Calcular saturnos
            es_generico = "GENERICO" in (lab or "").upper() or "GENÉRICO" in nombre.upper()
            pct_sat = sat_generico if es_generico else sat_patente
            saturnos = round(precio * pct_sat / 100, 2)

            tk.Label(info, text=f"⭐ +{saturnos:.0f} Saturnos ({pct_sat:.0f}%)", font=("Segoe UI", 8, "bold"),
                    bg="white", fg="#F57F17", anchor="w").pack(anchor="w")

            # Precio y stock
            right = tk.Frame(card, bg="white")
            right.pack(side=tk.RIGHT, padx=10)

            tk.Label(right, text=f"${precio:,.2f}", font=("Segoe UI", 14, "bold"),
                    bg="white", fg="#27AE60").pack()
            stock_color = "#27AE60" if stock > 5 else "#F44336" if stock <= 0 else "#FF9800"
            tk.Label(right, text=f"Stock: {stock}", font=("Segoe UI", 9),
                    bg="white", fg=stock_color).pack()

    search_entry.bind("<KeyRelease>", buscar)
    cat_combo.bind("<<ComboboxSelected>>", buscar)

    # Scroll con rueda
    def _scroll_cards(event):
        canvas_cards.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas_cards.bind_all("<MouseWheel>", _scroll_cards)

    buscar()

# ===== MÓDULO ABONO A CRÉDITO =====
def ver_abonos_credito():
    limpiar()

    header_mod = tk.Frame(main, bg="#1565C0", height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="💳 ABONOS A CRÉDITO", font=("Segoe UI", 13, "bold"),
            bg="#1565C0", fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    content = tk.Frame(main, bg="#F5F5F5")
    content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # Panel izquierdo - Buscar cliente
    left_panel = tk.Frame(content, bg="white", relief=tk.RIDGE, bd=2)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    tk.Label(left_panel, text="🔍 BUSCAR CLIENTE", font=("Segoe UI", 12, "bold"),
            bg="white", fg="#1565C0").pack(pady=10)

    search_frame = tk.Frame(left_panel, bg="white")
    search_frame.pack(fill=tk.X, padx=15)

    tk.Label(search_frame, text="Nombre o Teléfono:", bg="white").pack(anchor="w")
    search_entry = tk.Entry(search_frame, font=("Segoe UI", 12), width=30)
    search_entry.pack(fill=tk.X, pady=5)

    # Info del cliente seleccionado
    info_frame = tk.Frame(left_panel, bg="#E3F2FD", relief=tk.RIDGE, bd=1)
    info_frame.pack(fill=tk.X, padx=15, pady=10)

    cliente_info_lbl = tk.Label(info_frame, text="Selecciona un cliente...",
                                font=("Segoe UI", 10), bg="#E3F2FD", fg="#1565C0",
                                justify="left", anchor="w")
    cliente_info_lbl.pack(fill=tk.X, padx=10, pady=10)

    cliente_seleccionado = {"id": None, "nombre": "", "credito_id": None, "disponible": 0, "usado": 0}

    # Lista de clientes
    tree_clientes = ttk.Treeview(left_panel, columns=("nombre", "telefono", "credito"),
                                  show="headings", height=8)
    tree_clientes.heading("nombre", text="Cliente")
    tree_clientes.heading("telefono", text="Teléfono")
    tree_clientes.heading("credito", text="Crédito Disp.")
    tree_clientes.column("nombre", width=150)
    tree_clientes.column("telefono", width=100)
    tree_clientes.column("credito", width=100)
    tree_clientes.pack(fill=tk.X, padx=15, pady=5)

    def buscar_clientes(*args):
        for item in tree_clientes.get_children():
            tree_clientes.delete(item)
        termino = search_entry.get().strip()
        if len(termino) < 2:
            return
        c.execute("""SELECT cl.id, cl.nombre, cl.telefono,
                    COALESCE(cr.monto_disponible, 0) as credito
                    FROM clientes cl
                    LEFT JOIN creditos cr ON cl.id=cr.cliente_id AND cr.estado='ACTIVO'
                    WHERE cl.nombre LIKE ? OR cl.telefono LIKE ?
                    LIMIT 20""", (f"%{termino}%", f"%{termino}%"))
        for row in c.fetchall():
            tree_clientes.insert("", "end", values=(row[1], row[2] or "N/A", f"${row[3]:,.2f}"))

    search_entry.bind("<KeyRelease>", buscar_clientes)

    def seleccionar_cliente(event):
        sel = tree_clientes.selection()
        if not sel:
            return
        valores = tree_clientes.item(sel[0], "values")
        nombre = valores[0]

        c.execute("""SELECT cl.id, cl.nombre, cl.telefono, cl.direccion,
                    cr.id, cr.monto_limite, cr.monto_usado, cr.monto_disponible
                    FROM clientes cl
                    LEFT JOIN creditos cr ON cl.id=cr.cliente_id AND cr.estado='ACTIVO'
                    WHERE cl.nombre=?""", (nombre,))
        row = c.fetchone()
        if row:
            cliente_seleccionado["id"] = row[0]
            cliente_seleccionado["nombre"] = row[1]
            cliente_seleccionado["credito_id"] = row[4]
            cliente_seleccionado["limite"] = row[5] or 0
            cliente_seleccionado["usado"] = row[6] or 0
            cliente_seleccionado["disponible"] = row[7] or 0

            # Obtener saldo saturnos
            c.execute("SELECT saldo_saturnos FROM monederos WHERE cliente_id=?", (row[0],))
            sat = c.fetchone()
            saldo_sat = sat[0] if sat else 0

            info_txt = f"""👤 {row[1]}
📞 {row[2] or 'N/A'}
📍 {row[3] or 'N/A'}
━━━━━━━━━━━━━━━━━━
💳 Límite de Crédito: ${cliente_seleccionado['limite']:,.2f}
🔴 Crédito Usado: ${cliente_seleccionado['usado']:,.2f}
🟢 Crédito Disponible: ${cliente_seleccionado['disponible']:,.2f}
⭐ Saturnos: {saldo_sat:,.0f}"""
            cliente_info_lbl.config(text=info_txt)
            cargar_historial()

    tree_clientes.bind("<<TreeviewSelect>>", seleccionar_cliente)

    # Panel derecho - Historial y Abono
    right_panel = tk.Frame(content, bg="white", relief=tk.RIDGE, bd=2, width=450)
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
    right_panel.pack_propagate(False)

    tk.Label(right_panel, text="📜 HISTORIAL DE PAGOS", font=("Segoe UI", 12, "bold"),
            bg="white", fg="#1565C0").pack(pady=10)

    # Historial de abonos
    tree_historial = ttk.Treeview(right_panel, columns=("fecha", "monto", "tipo", "folio"),
                                   show="headings", height=10)
    tree_historial.heading("fecha", text="Fecha")
    tree_historial.heading("monto", text="Monto")
    tree_historial.heading("tipo", text="Tipo")
    tree_historial.heading("folio", text="Folio")
    tree_historial.column("fecha", width=100)
    tree_historial.column("monto", width=100)
    tree_historial.column("tipo", width=100)
    tree_historial.column("folio", width=120)
    tree_historial.pack(fill=tk.X, padx=15, pady=5)

    scroll_hist = ttk.Scrollbar(right_panel, orient="vertical", command=tree_historial.yview)
    tree_historial.configure(yscrollcommand=scroll_hist.set)

    def cargar_historial():
        for item in tree_historial.get_children():
            tree_historial.delete(item)
        if not cliente_seleccionado["credito_id"]:
            return
        c.execute("""SELECT fecha, monto, tipo_pago, folio_pago
                    FROM pagos_credito WHERE credito_id=?
                    ORDER BY fecha DESC, hora DESC LIMIT 50""",
                  (cliente_seleccionado["credito_id"],))
        for row in c.fetchall():
            tipo_txt = "ABONO" if row[2] == "ABONO" else "CARGO" if "CARGO" in row[2] else row[2]
            monto_txt = f"+${row[1]:,.2f}" if row[2] == "ABONO" else f"-${row[1]:,.2f}"
            tree_historial.insert("", "end", values=(row[0], monto_txt, tipo_txt, row[3]))

    # Frame para hacer abono
    abono_frame = tk.Frame(right_panel, bg="#E8F5E9", relief=tk.RIDGE, bd=2)
    abono_frame.pack(fill=tk.X, padx=15, pady=15)

    tk.Label(abono_frame, text="💵 REALIZAR ABONO", font=("Segoe UI", 11, "bold"),
            bg="#E8F5E9", fg="#2E7D32").pack(pady=10)

    monto_frame = tk.Frame(abono_frame, bg="#E8F5E9")
    monto_frame.pack(fill=tk.X, padx=20)

    tk.Label(monto_frame, text="Monto a abonar:", font=("Segoe UI", 10),
            bg="#E8F5E9").pack(side=tk.LEFT)
    monto_entry = tk.Entry(monto_frame, font=("Segoe UI", 14, "bold"), width=15, justify="center")
    monto_entry.pack(side=tk.LEFT, padx=10)

    tipo_pago_var = tk.StringVar(value="EFECTIVO")
    tipo_frame = tk.Frame(abono_frame, bg="#E8F5E9")
    tipo_frame.pack(fill=tk.X, padx=20, pady=10)

    for tipo in ["EFECTIVO", "TARJETA", "TRANSFERENCIA"]:
        tk.Radiobutton(tipo_frame, text=tipo, variable=tipo_pago_var, value=tipo,
                      bg="#E8F5E9", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=10)

    def realizar_abono():
        if not cliente_seleccionado["credito_id"]:
            messagebox.showwarning("Error", "Selecciona un cliente con crédito activo")
            return
        try:
            monto = float(monto_entry.get().replace(",", "").replace("$", ""))
        except:
            messagebox.showwarning("Error", "Ingresa un monto válido")
            return
        if monto <= 0:
            messagebox.showwarning("Error", "El monto debe ser mayor a 0")
            return

        # Confirmar
        if not messagebox.askyesno("Confirmar Abono",
                f"¿Registrar abono de ${monto:,.2f} para {cliente_seleccionado['nombre']}?\n\n"
                f"Forma de pago: {tipo_pago_var.get()}"):
            return

        # Registrar abono
        folio = f"AB{datetime.now().strftime('%Y%m%d%H%M%S')}"
        fecha = datetime.now().strftime('%Y-%m-%d')
        hora = datetime.now().strftime('%H:%M:%S')

        c.execute("""INSERT INTO pagos_credito (credito_id, folio_pago, monto, tipo_pago, fecha, hora, usuario, observaciones)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                  (cliente_seleccionado["credito_id"], folio, monto, "ABONO",
                   fecha, hora, usuario_actual, f"Abono en {tipo_pago_var.get()}"))

        # Actualizar crédito
        c.execute("""UPDATE creditos SET monto_usado = monto_usado - ?,
                    monto_disponible = monto_disponible + ? WHERE id = ?""",
                  (monto, monto, cliente_seleccionado["credito_id"]))
        conn.commit()

        messagebox.showinfo("Abono Exitoso",
            f"✅ Abono registrado\n\n"
            f"Folio: {folio}\n"
            f"Monto: ${monto:,.2f}\n"
            f"Cliente: {cliente_seleccionado['nombre']}\n"
            f"Nuevo disponible: ${cliente_seleccionado['disponible'] + monto:,.2f}")

        # Refrescar
        monto_entry.delete(0, tk.END)
        seleccionar_cliente(None)
        cargar_historial()

        # Preguntar si enviar por WhatsApp
        if messagebox.askyesno("WhatsApp", "¿Enviar comprobante por WhatsApp?"):
            enviar_comprobante_whatsapp(folio, monto, cliente_seleccionado["nombre"],
                                        cliente_seleccionado["disponible"] + monto)

    def enviar_comprobante_whatsapp(folio, monto, nombre, nuevo_disp):
        c.execute("SELECT telefono FROM clientes WHERE nombre=?", (nombre,))
        tel_row = c.fetchone()
        telefono = "52" + (tel_row[0] or "7753200224").replace(" ", "").replace("-", "") if tel_row else "527753200224"

        suc = obtener_sucursal()
        mensaje = f"""💳 *COMPROBANTE DE ABONO*
━━━━━━━━━━━━━━━━━━━━
🏪 *{suc.get('nombre', 'FARMACIAS MADRID')}*
━━━━━━━━━━━━━━━━━━━━
📋 Folio: *{folio}*
📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━━━
👤 *Cliente:* {nombre}
💵 *Abono:* ${monto:,.2f}
🟢 *Nuevo Disponible:* ${nuevo_disp:,.2f}
━━━━━━━━━━━━━━━━━━━━
¡Gracias por su pago! 🙏
*{suc.get('nombre', 'FARMACIAS MADRID')}*"""

        import urllib.parse
        import webbrowser
        mensaje_encoded = urllib.parse.quote(mensaje)
        url = f"https://wa.me/{telefono}?text={mensaje_encoded}"
        webbrowser.open(url)

    tk.Button(abono_frame, text="💰 REGISTRAR ABONO", command=realizar_abono,
             bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"),
             padx=20, pady=10, cursor="hand2", relief=tk.FLAT).pack(pady=15)

    # Botones rápidos de monto
    rapidos_frame = tk.Frame(abono_frame, bg="#E8F5E9")
    rapidos_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

    for monto_rap in [100, 200, 500, 1000]:
        tk.Button(rapidos_frame, text=f"${monto_rap}",
                 command=lambda m=monto_rap: monto_entry.delete(0, tk.END) or monto_entry.insert(0, str(m)),
                 bg="#81C784", fg="white", font=("Segoe UI", 9, "bold"),
                 padx=10, cursor="hand2").pack(side=tk.LEFT, padx=3)

# ===== MÓDULO CLIENTES =====
def ver_clientes():
    limpiar()
    
    header_mod = tk.Frame(main, bg=AZUL_FARMACIA, height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="👥 CLIENTES", font=("Segoe UI", 13, "bold"),
            bg=AZUL_FARMACIA, fg="white").pack(side=tk.LEFT, padx=12, pady=10)
    
    content = tk.Frame(main, bg="white")
    content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    btn_frame = tk.Frame(content, bg="white")
    btn_frame.pack(fill=tk.X, pady=10)
    
    def nuevo_cliente():
        win = tk.Toplevel(main)
        win.title("Nuevo Cliente")
        win.geometry("500x400")
        win.resizable(False, False)
        
        tk.Label(win, text="NUEVO CLIENTE", font=("Arial", 14, "bold")).pack(pady=20)
        
        form = tk.Frame(win)
        form.pack(pady=10)
        
        tk.Label(form, text="Nombre:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="e", padx=10, pady=8)
        nombre_entry = tk.Entry(form, width=30)
        nombre_entry.grid(row=0, column=1, padx=10, pady=8)
        
        tk.Label(form, text="Teléfono:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="e", padx=10, pady=8)
        tel_entry = tk.Entry(form, width=30)
        tel_entry.grid(row=1, column=1, padx=10, pady=8)
        
        tk.Label(form, text="Email:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="e", padx=10, pady=8)
        email_entry = tk.Entry(form, width=30)
        email_entry.grid(row=2, column=1, padx=10, pady=8)
        
        tk.Label(form, text="Dirección:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="e", padx=10, pady=8)
        dir_entry = tk.Entry(form, width=30)
        dir_entry.grid(row=3, column=1, padx=10, pady=8)
        
        tk.Label(form, text="Colonia:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="e", padx=10, pady=8)
        col_entry = tk.Entry(form, width=30)
        col_entry.grid(row=4, column=1, padx=10, pady=8)

        emitir_tarj_var = tk.IntVar(value=1)
        tk.Checkbutton(form, text="Emitir tarjeta Saturnos al registrar",
                      variable=emitir_tarj_var, font=("Arial", 9, "bold"),
                      fg="#F57F17", selectcolor="white"
                      ).grid(row=5, column=0, columnspan=2, pady=8)

        def guardar():
            if not nombre_entry.get():
                messagebox.showwarning("Incompleto", "El nombre es obligatorio")
                return

            c.execute("SELECT MAX(id) FROM clientes")
            max_id = c.fetchone()[0] or 0
            nuevo_id = max_id + 1

            c.execute("INSERT INTO clientes (id, nombre, telefono, email, direccion, colonia, puntos_lealtad) VALUES (?,?,?,?,?,?,?)",
                     (nuevo_id, nombre_entry.get(), tel_entry.get(), email_entry.get(),
                      dir_entry.get(), col_entry.get(), 0))

            # Crear monedero Saturnos y emitir tarjeta si se seleccionó
            if emitir_tarj_var.get():
                ahora = datetime.now()
                codigo = generar_codigo_tarjeta()
                barcode_path = os.path.join(_ensure_tarjetas_dirs(), "tarjetas", "codigos", f"{codigo}.png")
                c.execute("""INSERT INTO monederos (cliente_id,saldo_saturnos,total_acumulado,total_gastado,activo,fecha_alta,
                            codigo_tarjeta,codigo_barras_path,tarjeta_impresa,fecha_emision,estado_tarjeta)
                            VALUES (?,0,0,0,1,?,?,?,0,?,'ACTIVA')""",
                          (nuevo_id, ahora.strftime("%Y-%m-%d"), codigo, barcode_path, ahora.strftime("%Y-%m-%d")))
                conn.commit()
                # Generar imagen de tarjeta
                try:
                    ruta_f, ruta_r = generar_tarjeta_imagen(nuevo_id, codigo)
                    if ruta_f:
                        messagebox.showinfo("Tarjeta Saturnos",
                            f"Cliente {nombre_entry.get()} creado.\nTarjeta emitida: {codigo}\nImagen: {ruta_f}")
                except Exception:
                    messagebox.showinfo("Guardado", f"Cliente {nombre_entry.get()} creado.\nTarjeta: {codigo}")
            else:
                conn.commit()
                messagebox.showinfo("Guardado", f"Cliente {nombre_entry.get()} creado")

            win.destroy()
            ver_clientes()
        
        tk.Button(win, text="💾 GUARDAR", command=guardar,
                 bg="#27AE60", fg="white", font=("Arial", 12, "bold"),
                 padx=30, pady=10).pack(pady=20)
    
    tk.Button(btn_frame, text="➕ NUEVO CLIENTE", command=nuevo_cliente,
             bg="#27AE60", fg="white", font=("Arial", 11, "bold"),
             padx=20, pady=10).pack(side=tk.LEFT, padx=10)
    
    tree_frame = tk.Frame(content, bg="white")
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    cols = ("ID", "NOMBRE", "TELÉFONO", "DIRECCIÓN")
    tree_cli = ttk.Treeview(tree_frame, columns=cols, show="headings", height=25)
    
    for col in cols:
        tree_cli.heading(col, text=col)
    
    tree_cli.column("ID", width=60)
    tree_cli.column("NOMBRE", width=250)
    tree_cli.column("TELÉFONO", width=120)
    tree_cli.column("DIRECCIÓN", width=300)
    
    scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_cli.yview)
    tree_cli.configure(yscrollcommand=scroll.set)
    
    tree_cli.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    c.execute("SELECT id, nombre, telefono, direccion FROM clientes")
    for row in c.fetchall():
        tree_cli.insert("", "end", values=row)

# ===== MÓDULO USUARIOS =====
def ver_usuarios():
    limpiar()
    
    header_mod = tk.Frame(main, bg=AZUL_FARMACIA, height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="👤 USUARIOS", font=("Segoe UI", 13, "bold"),
            bg=AZUL_FARMACIA, fg="white").pack(side=tk.LEFT, padx=12, pady=10)
    
    content = tk.Frame(main, bg="white")
    content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    btn_frame = tk.Frame(content, bg="white")
    btn_frame.pack(fill=tk.X, pady=10)
    
    def nuevo_usuario():
        import hashlib
        win = tk.Toplevel(main)
        win.title("Nuevo Usuario")
        win.geometry("500x500")
        win.resizable(False, False)
        win.configure(bg="white")
        win.grab_set()

        tk.Label(win, text="NUEVO USUARIO", font=("Segoe UI", 14, "bold"),
                bg="white", fg=AZUL_FARMACIA).pack(pady=20)

        form = tk.Frame(win, bg="white")
        form.pack(pady=10)

        tk.Label(form, text="Nombre completo:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=0, column=0, sticky="e", padx=10, pady=8)
        nombre_entry = tk.Entry(form, width=30, font=("Segoe UI", 10))
        nombre_entry.grid(row=0, column=1, padx=10, pady=8)

        tk.Label(form, text="Usuario:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=1, column=0, sticky="e", padx=10, pady=8)
        usuario_entry = tk.Entry(form, width=30, font=("Segoe UI", 10))
        usuario_entry.grid(row=1, column=1, padx=10, pady=8)

        tk.Label(form, text="Password:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=2, column=0, sticky="e", padx=10, pady=8)
        pass_entry = tk.Entry(form, show="*", width=30, font=("Segoe UI", 10))
        pass_entry.grid(row=2, column=1, padx=10, pady=8)

        tk.Label(form, text="Rol:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=3, column=0, sticky="ne", padx=10, pady=8)
        rol_frame = tk.Frame(form, bg="white")
        rol_frame.grid(row=3, column=1, sticky="w", padx=10, pady=8)
        rol_var = tk.StringVar(value="CAJERO")
        for rol_n, rol_d in [("ADMINISTRADOR","Acceso total"),("GERENTE","Gestion"),("CAJERO","Solo ventas"),("REPARTIDOR","Solo entregas")]:
            tk.Radiobutton(rol_frame, text=f"{rol_n} ({rol_d})", variable=rol_var, value=rol_n,
                          font=("Segoe UI", 9), bg="white", activebackground="white").pack(anchor="w")

        tk.Label(form, text="Activo:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=4, column=0, sticky="e", padx=10, pady=8)
        activo_var = tk.IntVar(value=1)
        tk.Checkbutton(form, variable=activo_var, bg="white").grid(row=4, column=1, sticky="w", padx=10, pady=8)

        def guardar():
            if not nombre_entry.get().strip() or not usuario_entry.get().strip() or not pass_entry.get().strip():
                messagebox.showwarning("Incompleto", "Todos los campos son obligatorios")
                return

            usr = usuario_entry.get().strip()
            c.execute("SELECT id FROM empleados WHERE usuario=?", (usr,))
            if c.fetchone():
                messagebox.showerror("Error", f"El usuario '{usr}' ya existe")
                return

            pwd_hash = hashlib.sha256(pass_entry.get().strip().encode()).hexdigest()
            rol = rol_var.get()
            nivel_map = {"ADMINISTRADOR": "ADMINISTRADOR", "GERENTE": "ADMINISTRADOR",
                         "CAJERO": "CAJERO", "REPARTIDOR": "REPARTIDOR"}
            c.execute("SELECT id FROM roles WHERE nombre=?", (rol,))
            rol_row = c.fetchone()
            rol_id = rol_row[0] if rol_row else 3

            try:
                c.execute("INSERT INTO empleados (nombre, usuario, password, nivel, activo, rol_id) VALUES (?,?,?,?,?,?)",
                         (nombre_entry.get().strip(), usr, pwd_hash,
                          nivel_map.get(rol, "CAJERO"), activo_var.get(), rol_id))
                conn.commit()
                registrar_auditoria("CREAR_USUARIO", "usuarios", f"Usuario: {usr}, Rol: {rol}")
                messagebox.showinfo("Guardado", f"Usuario '{usr}' creado con rol {rol}")
                win.destroy()
                ver_usuarios()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear el usuario:\n{e}")

        tk.Button(win, text="GUARDAR", command=guardar,
                 bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"),
                 relief=tk.FLAT, padx=30, pady=10, cursor="hand2").pack(pady=20)
    
    def editar_usuario_standalone():
        import hashlib
        sel = tree_users.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un usuario para editar")
            return
        vals = tree_users.item(sel[0])["values"]
        uid = vals[0]

        win = tk.Toplevel(main)
        win.title(f"Editar Usuario - {vals[2]}")
        win.geometry("400x400")
        win.configure(bg="white")
        win.grab_set()

        tk.Label(win, text=f"EDITAR: {vals[1]}", font=("Segoe UI", 14, "bold"),
                bg="white", fg=AZUL_FARMACIA).pack(pady=(15, 10))

        form_e = tk.Frame(win, bg="white")
        form_e.pack(padx=20, fill=tk.X)

        tk.Label(form_e, text="Nueva contrasena (dejar vacio para no cambiar):",
                font=("Segoe UI", 9), bg="white").pack(anchor="w")
        new_pass = tk.StringVar()
        tk.Entry(form_e, textvariable=new_pass, width=35, font=("Segoe UI", 10), show="*").pack(fill=tk.X, ipady=3, pady=(0,10))

        tk.Label(form_e, text="Rol:", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w")
        rol_var_e = tk.StringVar(value=vals[3])
        for rol_n in ["ADMINISTRADOR", "GERENTE", "CAJERO", "REPARTIDOR"]:
            tk.Radiobutton(form_e, text=rol_n, variable=rol_var_e, value=rol_n,
                          font=("Segoe UI", 9), bg="white").pack(anchor="w")

        activo_var_e = tk.BooleanVar(value=vals[4] == "SI")
        tk.Checkbutton(form_e, text="Usuario activo", variable=activo_var_e,
                      font=("Segoe UI", 9), bg="white").pack(anchor="w", pady=5)

        def guardar_edicion():
            rol = rol_var_e.get()
            activo = 1 if activo_var_e.get() else 0
            nivel_map = {"ADMINISTRADOR": "ADMINISTRADOR", "GERENTE": "ADMINISTRADOR",
                         "CAJERO": "CAJERO", "REPARTIDOR": "REPARTIDOR"}
            c.execute("SELECT id FROM roles WHERE nombre=?", (rol,))
            rol_row = c.fetchone()
            rol_id = rol_row[0] if rol_row else 3

            if new_pass.get().strip():
                pwd_hash = hashlib.sha256(new_pass.get().strip().encode()).hexdigest()
                c.execute("UPDATE empleados SET password=?, nivel=?, rol_id=?, activo=? WHERE id=?",
                          (pwd_hash, nivel_map.get(rol, "CAJERO"), rol_id, activo, uid))
            else:
                c.execute("UPDATE empleados SET nivel=?, rol_id=?, activo=? WHERE id=?",
                          (nivel_map.get(rol, "CAJERO"), rol_id, activo, uid))
            conn.commit()
            registrar_auditoria("EDITAR_USUARIO", "usuarios", f"Usuario ID: {uid}, Rol: {rol}")
            win.destroy()
            cargar_lista_usuarios()
            messagebox.showinfo("Guardado", "Usuario actualizado")

        tk.Button(win, text="GUARDAR", command=guardar_edicion,
                 bg="#1565C0", fg="white", font=("Segoe UI", 11, "bold"),
                 relief=tk.FLAT, padx=25, pady=8, cursor="hand2").pack(pady=10)

    def desactivar_usuario_standalone():
        sel = tree_users.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un usuario")
            return
        vals = tree_users.item(sel[0])["values"]
        if vals[0] == usuario_id:
            messagebox.showwarning("Aviso", "No puedes desactivar tu propio usuario")
            return
        if not messagebox.askyesno("Confirmar", f"Desactivar usuario '{vals[2]}'?"):
            return
        c.execute("UPDATE empleados SET activo=0 WHERE id=?", (vals[0],))
        conn.commit()
        registrar_auditoria("DESACTIVAR_USUARIO", "usuarios", f"Usuario: {vals[2]}")
        cargar_lista_usuarios()

    tk.Button(btn_frame, text="+ NUEVO USUARIO", command=nuevo_usuario,
             bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"),
             relief=tk.FLAT, padx=20, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)

    tk.Button(btn_frame, text="EDITAR", command=editar_usuario_standalone,
             bg="#1565C0", fg="white", font=("Segoe UI", 11, "bold"),
             relief=tk.FLAT, padx=20, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)

    tk.Button(btn_frame, text="DESACTIVAR", command=desactivar_usuario_standalone,
             bg="#D32F2F", fg="white", font=("Segoe UI", 11, "bold"),
             relief=tk.FLAT, padx=20, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)

    tree_frame = tk.Frame(content, bg="white")
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    cols = ("ID", "NOMBRE", "USUARIO", "ROL", "ACTIVO", "ULTIMO ACCESO")
    tree_users = ttk.Treeview(tree_frame, columns=cols, show="headings", height=25)

    for col in cols:
        tree_users.heading(col, text=col)

    tree_users.column("ID", width=50)
    tree_users.column("NOMBRE", width=200)
    tree_users.column("USUARIO", width=130)
    tree_users.column("ROL", width=140)
    tree_users.column("ACTIVO", width=70)
    tree_users.column("ULTIMO ACCESO", width=160)

    scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_users.yview)
    tree_users.configure(yscrollcommand=scroll.set)

    tree_users.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def cargar_lista_usuarios():
        for item in tree_users.get_children():
            tree_users.delete(item)
        c.execute("""SELECT e.id, e.nombre, e.usuario,
                     COALESCE(r.nombre, e.nivel) as rol,
                     e.activo, COALESCE(e.ultimo_acceso, '')
                     FROM empleados e LEFT JOIN roles r ON e.rol_id=r.id
                     ORDER BY e.id""")
        for row in c.fetchall():
            activo_txt = "SI" if row[4] == 1 else "NO"
            tree_users.insert("", "end", values=(row[0], row[1], row[2], row[3], activo_txt, row[5]))

    cargar_lista_usuarios()

# ===== MÓDULOS PLACEHOLDER =====
def ver_finanzas():
    limpiar()

    header_mod = tk.Frame(main, bg=AZUL_FARMACIA, height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="💰 FINANZAS Y REPORTES", font=("Segoe UI", 13, "bold"),
            bg=AZUL_FARMACIA, fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    content = tk.Frame(main, bg="white")
    content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # TABS
    tab_frame = tk.Frame(content, bg="white")
    tab_frame.pack(fill=tk.X, pady=5)

    display_frame = tk.Frame(content, bg="white")
    display_frame.pack(fill=tk.BOTH, expand=True)

    def limpiar_display():
        for w in display_frame.winfo_children():
            w.destroy()

    # --- VENTAS DEL DIA ---
    def ventas_dia():
        limpiar_display()
        hoy = datetime.now().strftime('%Y-%m-%d')

        tk.Label(display_frame, text=f"VENTAS DEL DIA - {hoy}", font=("Arial", 13, "bold"),
                bg="white").pack(pady=10)

        c.execute("""SELECT v.folio, v.hora, e.nombre, v.total, v.tipo_pago,
                            v.monto_efectivo, v.monto_tarjeta
                     FROM ventas v LEFT JOIN empleados e ON v.vendedor_id=e.id
                     WHERE v.fecha=? ORDER BY v.hora DESC""", (hoy,))
        rows = c.fetchall()

        tree_f = tk.Frame(display_frame, bg="white")
        tree_f.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = ("FOLIO", "HORA", "VENDEDOR", "TOTAL", "PAGO")
        tree = ttk.Treeview(tree_f, columns=cols, show="headings", height=18)
        for col in cols:
            tree.heading(col, text=col)
        tree.column("FOLIO", width=180)
        tree.column("HORA", width=100)
        tree.column("VENDEDOR", width=200)
        tree.column("TOTAL", width=120)
        tree.column("PAGO", width=100)

        scroll = ttk.Scrollbar(tree_f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        total_dia = 0.0
        efectivo = 0.0
        tarjeta = 0.0
        for row in rows:
            tree.insert("", "end", values=(row[0], row[1], row[2] or "", f"${float(row[3]):,.2f}", row[4]))
            total_dia += float(row[3])
            # Soporte pago mixto: usar montos individuales si existen
            if len(row) > 5 and row[5] is not None:
                efectivo += float(row[5] or 0)
                tarjeta += float(row[6] or 0) if len(row) > 6 else 0
            elif row[4] == "EFECTIVO":
                efectivo += float(row[3])
            elif row[4] == "TARJETA":
                tarjeta += float(row[3])
            else:
                # Pago mixto sin columnas detalladas - asignar a efectivo
                efectivo += float(row[3])

        resumen = tk.Frame(display_frame, bg="#F0F8FF", relief=tk.RIDGE, bd=1)
        resumen.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(resumen, text=f"Total del dia: ${total_dia:,.2f}  |  Ventas: {len(rows)}  |  "
                 f"Efectivo: ${efectivo:,.2f}  |  Tarjeta: ${tarjeta:,.2f}",
                 font=("Arial", 11, "bold"), bg="#F0F8FF", fg="#2C3E50").pack(pady=8)

    # --- VENTAS DEL MES ---
    def ventas_mes():
        limpiar_display()
        mes_actual = datetime.now().strftime('%Y-%m')

        tk.Label(display_frame, text=f"VENTAS DEL MES - {mes_actual}", font=("Arial", 13, "bold"),
                bg="white").pack(pady=10)

        c.execute("""SELECT v.fecha, COUNT(*) as num, SUM(v.total) as total_dia
                     FROM ventas v WHERE v.fecha LIKE ?
                     GROUP BY v.fecha ORDER BY v.fecha DESC""", (f"{mes_actual}%",))
        rows = c.fetchall()

        tree_f = tk.Frame(display_frame, bg="white")
        tree_f.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = ("FECHA", "NUM. VENTAS", "TOTAL")
        tree = ttk.Treeview(tree_f, columns=cols, show="headings", height=18)
        for col in cols:
            tree.heading(col, text=col)
        tree.column("FECHA", width=200)
        tree.column("NUM. VENTAS", width=150)
        tree.column("TOTAL", width=200)

        tree.pack(fill=tk.BOTH, expand=True)

        total_mes = 0.0
        total_ventas = 0
        for row in rows:
            tree.insert("", "end", values=(row[0], row[1], f"${float(row[2]):,.2f}"))
            total_mes += float(row[2])
            total_ventas += row[1]

        resumen = tk.Frame(display_frame, bg="#F0FFF0", relief=tk.RIDGE, bd=1)
        resumen.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(resumen, text=f"Total del mes: ${total_mes:,.2f}  |  Ventas totales: {total_ventas}",
                 font=("Arial", 11, "bold"), bg="#F0FFF0", fg="#2C3E50").pack(pady=8)

    # --- TOP 10 PRODUCTOS ---
    def top_productos():
        limpiar_display()
        tk.Label(display_frame, text="TOP 10 PRODUCTOS MAS VENDIDOS", font=("Arial", 13, "bold"),
                bg="white").pack(pady=10)

        c.execute("""SELECT p.nombre, SUM(dv.cantidad) as total_cant, SUM(dv.subtotal) as total_venta
                     FROM detalle_ventas dv
                     JOIN productos p ON dv.producto_id=p.id
                     GROUP BY dv.producto_id
                     ORDER BY total_cant DESC LIMIT 10""")
        rows = c.fetchall()

        tree_f = tk.Frame(display_frame, bg="white")
        tree_f.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = ("PRODUCTO", "UNIDADES VENDIDAS", "TOTAL VENDIDO")
        tree = ttk.Treeview(tree_f, columns=cols, show="headings", height=12)
        for col in cols:
            tree.heading(col, text=col)
        tree.column("PRODUCTO", width=450)
        tree.column("UNIDADES VENDIDAS", width=150)
        tree.column("TOTAL VENDIDO", width=150)
        tree.pack(fill=tk.BOTH, expand=True)

        for row in rows:
            tree.insert("", "end", values=(row[0][:60], row[1], f"${float(row[2]):,.2f}"))

        if not rows:
            tk.Label(display_frame, text="No hay ventas registradas aun.",
                    font=("Arial", 11), bg="white", fg="#999").pack(pady=20)

        # GRAFICA SIMPLE CON CANVAS
        if rows:
            tk.Label(display_frame, text="Grafica de unidades vendidas", font=("Arial", 10, "bold"),
                    bg="white").pack(pady=5)
            canvas = tk.Canvas(display_frame, bg="white", height=180, relief=tk.RIDGE, bd=1)
            canvas.pack(fill=tk.X, padx=10, pady=5)

            max_val = max(r[1] for r in rows) if rows else 1
            bar_width = 60
            spacing = 10
            x = 30
            for i, row in enumerate(rows):
                bar_h = int((row[1] / max_val) * 140) if max_val > 0 else 0
                y_top = 160 - bar_h
                color = ["#4A90E2", "#27AE60", "#E67E22", "#9B59B6", "#E74C3C",
                         "#3498DB", "#F39C12", "#1ABC9C", "#5D6D7E", "#C0392B"][i % 10]
                canvas.create_rectangle(x, y_top, x + bar_width, 160, fill=color, outline="white")
                canvas.create_text(x + bar_width // 2, y_top - 8, text=str(row[1]),
                                   font=("Arial", 8, "bold"))
                canvas.create_text(x + bar_width // 2, 172, text=f"#{i+1}",
                                   font=("Arial", 7))
                x += bar_width + spacing

    # --- VENTAS POR VENDEDOR ---
    def ventas_vendedor():
        limpiar_display()
        tk.Label(display_frame, text="VENTAS POR VENDEDOR", font=("Arial", 13, "bold"),
                bg="white").pack(pady=10)

        c.execute("""SELECT e.nombre, COUNT(v.id) as num_ventas, SUM(v.total) as total
                     FROM ventas v JOIN empleados e ON v.vendedor_id=e.id
                     GROUP BY v.vendedor_id ORDER BY total DESC""")
        rows = c.fetchall()

        tree_f = tk.Frame(display_frame, bg="white")
        tree_f.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = ("VENDEDOR", "NUM. VENTAS", "TOTAL VENDIDO")
        tree = ttk.Treeview(tree_f, columns=cols, show="headings", height=15)
        for col in cols:
            tree.heading(col, text=col)
        tree.column("VENDEDOR", width=300)
        tree.column("NUM. VENTAS", width=150)
        tree.column("TOTAL VENDIDO", width=200)
        tree.pack(fill=tk.BOTH, expand=True)

        for row in rows:
            tree.insert("", "end", values=(row[0], row[1], f"${float(row[2]):,.2f}"))

        if not rows:
            tk.Label(display_frame, text="No hay ventas registradas aun.",
                    font=("Arial", 11), bg="white", fg="#999").pack(pady=20)

    # --- EXPORTAR REPORTE ---
    def exportar_reporte():
        hoy = datetime.now().strftime('%Y-%m-%d')
        c.execute("""SELECT v.folio, v.fecha, v.hora, e.nombre, v.total, v.tipo_pago
                     FROM ventas v LEFT JOIN empleados e ON v.vendedor_id=e.id
                     ORDER BY v.fecha DESC, v.hora DESC""")
        rows = c.fetchall()

        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"reporte_ventas_{hoy}.csv")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("FOLIO,FECHA,HORA,VENDEDOR,TOTAL,TIPO_PAGO\n")
            for row in rows:
                f.write(f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}\n")

        messagebox.showinfo("Exportado", f"Reporte exportado a:\n{ruta}")

    # BOTONES DE TABS
    tabs = [
        ("Ventas del dia", ventas_dia, "#27AE60"),
        ("Ventas del mes", ventas_mes, "#3498DB"),
        ("Top 10 productos", top_productos, "#E67E22"),
        ("Por vendedor", ventas_vendedor, "#9B59B6"),
        ("Exportar CSV", exportar_reporte, "#5D6D7E"),
    ]

    for texto, cmd, color in tabs:
        tk.Button(tab_frame, text=texto, command=cmd,
                 bg=color, fg="white", font=("Arial", 10, "bold"),
                 padx=15, pady=8, cursor="hand2", relief=tk.FLAT).pack(side=tk.LEFT, padx=3)

    ventas_dia()

def ver_alertas_stock():
    limpiar()

    header_mod = tk.Frame(main, bg=AZUL_FARMACIA, height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="⚠️ ALERTAS DE STOCK", font=("Segoe UI", 13, "bold"),
            bg=AZUL_FARMACIA, fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    content = tk.Frame(main, bg="white")
    content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    tab_frame = tk.Frame(content, bg="white")
    tab_frame.pack(fill=tk.X, pady=5)

    display_frame = tk.Frame(content, bg="white")
    display_frame.pack(fill=tk.BOTH, expand=True)

    def limpiar_display():
        for w in display_frame.winfo_children():
            w.destroy()

    # --- STOCK BAJO ---
    def stock_bajo():
        limpiar_display()
        tk.Label(display_frame, text="PRODUCTOS CON STOCK BAJO (< 10 unidades)",
                font=("Arial", 13, "bold"), bg="white", fg="#E74C3C").pack(pady=10)

        c.execute("""SELECT codigo, nombre, categoria, stock, precio_venta
                     FROM productos WHERE stock < 10 ORDER BY stock ASC LIMIT 200""")
        rows = c.fetchall()

        tree_f = tk.Frame(display_frame, bg="white")
        tree_f.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = ("CODIGO", "PRODUCTO", "CATEGORIA", "STOCK", "PRECIO")
        tree = ttk.Treeview(tree_f, columns=cols, show="headings", height=18)
        for col in cols:
            tree.heading(col, text=col)
        tree.column("CODIGO", width=100)
        tree.column("PRODUCTO", width=450)
        tree.column("CATEGORIA", width=120)
        tree.column("STOCK", width=80)
        tree.column("PRECIO", width=100)

        scroll = ttk.Scrollbar(tree_f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        for row in rows:
            tag = "critico" if row[3] <= 2 else "bajo"
            tree.insert("", "end", values=(row[0], row[1][:60], row[2], row[3],
                        f"${float(row[4]):,.2f}"), tags=(tag,))

        tree.tag_configure("critico", background="#FFCCCC")
        tree.tag_configure("bajo", background="#FFF3CD")

        resumen = tk.Frame(display_frame, bg="#FFF0F0", relief=tk.RIDGE, bd=1)
        resumen.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(resumen, text=f"Total productos con stock bajo: {len(rows)}",
                 font=("Arial", 11, "bold"), bg="#FFF0F0", fg="#E74C3C").pack(pady=8)

    # --- PROXIMOS A CADUCAR ---
    def proximos_caducar():
        limpiar_display()
        tk.Label(display_frame, text="PRODUCTOS PROXIMOS A CADUCAR (< 30 dias)",
                font=("Arial", 13, "bold"), bg="white", fg="#E67E22").pack(pady=10)

        fecha_limite = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        hoy = datetime.now().strftime('%Y-%m-%d')

        c.execute("""SELECT codigo, nombre, categoria, stock, caducidad
                     FROM productos WHERE caducidad != '' AND caducidad IS NOT NULL
                     AND caducidad <= ? AND caducidad >= ?
                     ORDER BY caducidad ASC LIMIT 200""", (fecha_limite, hoy))
        rows = c.fetchall()

        tree_f = tk.Frame(display_frame, bg="white")
        tree_f.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = ("CODIGO", "PRODUCTO", "CATEGORIA", "STOCK", "CADUCIDAD")
        tree = ttk.Treeview(tree_f, columns=cols, show="headings", height=18)
        for col in cols:
            tree.heading(col, text=col)
        tree.column("CODIGO", width=100)
        tree.column("PRODUCTO", width=450)
        tree.column("CATEGORIA", width=120)
        tree.column("STOCK", width=80)
        tree.column("CADUCIDAD", width=120)
        tree.pack(fill=tk.BOTH, expand=True)

        for row in rows:
            tree.insert("", "end", values=row)

        if not rows:
            tk.Label(display_frame, text="No hay productos proximos a caducar.",
                    font=("Arial", 11), bg="white", fg="#999").pack(pady=20)
        else:
            resumen = tk.Frame(display_frame, bg="#FFF8E1", relief=tk.RIDGE, bd=1)
            resumen.pack(fill=tk.X, padx=10, pady=10)
            tk.Label(resumen, text=f"Productos por caducar: {len(rows)}",
                     font=("Arial", 11, "bold"), bg="#FFF8E1", fg="#E67E22").pack(pady=8)

    # --- GENERAR ORDEN DE COMPRA ---
    def generar_orden_compra():
        c.execute("""SELECT codigo, nombre, stock FROM productos
                     WHERE stock < 10 ORDER BY stock ASC LIMIT 50""")
        rows = c.fetchall()

        if not rows:
            messagebox.showinfo("Sin alertas", "No hay productos con stock bajo.")
            return

        orden = "=" * 50 + "\n"
        orden += "   ORDEN DE COMPRA - FARMACIAS MADRID\n"
        orden += f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        orden += "=" * 50 + "\n\n"
        orden += f"{'CODIGO':<12} {'PRODUCTO':<30} {'STOCK':<6} {'PEDIR':<6}\n"
        orden += "-" * 50 + "\n"

        for row in rows:
            cantidad_pedir = max(20 - row[2], 10)
            orden += f"{row[0]:<12} {row[1][:30]:<30} {row[2]:<6} {cantidad_pedir:<6}\n"

        orden += "-" * 50 + "\n"
        orden += f"Total de productos a pedir: {len(rows)}\n"
        orden += "=" * 50 + "\n"

        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           f"orden_compra_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(orden)

        messagebox.showinfo("Orden generada", f"Orden de compra generada:\n{ruta}\n\n{len(rows)} productos incluidos.")

    tabs = [
        ("Stock bajo", stock_bajo, "#E74C3C"),
        ("Por caducar", proximos_caducar, "#E67E22"),
        ("Generar orden de compra", generar_orden_compra, "#27AE60"),
    ]

    for texto, cmd, color in tabs:
        tk.Button(tab_frame, text=texto, command=cmd,
                 bg=color, fg="white", font=("Arial", 10, "bold"),
                 padx=15, pady=8, cursor="hand2", relief=tk.FLAT).pack(side=tk.LEFT, padx=3)

    stock_bajo()

# ===== MODULO CORTE DE CAJA =====
def ver_corte_caja():
    limpiar()

    header_mod = tk.Frame(main, bg=AZUL_FARMACIA, height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="💳 CORTE DE CAJA", font=("Segoe UI", 13, "bold"),
            bg=AZUL_FARMACIA, fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    content = tk.Frame(main, bg="white")
    content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    hoy = datetime.now().strftime('%Y-%m-%d')

    # Verificar si hay un corte abierto hoy
    c.execute("SELECT id, fecha, total_ventas, num_ventas, efectivo, tarjeta FROM cortes_caja WHERE fecha=? AND usuario_id=?",
             (hoy, usuario_id))
    corte_existente = c.fetchone()

    # --- PANEL SUPERIOR: APERTURA ---
    apertura_frame = tk.LabelFrame(content, text="APERTURA DE CAJA", font=("Arial", 11, "bold"),
                                    bg="white", padx=15, pady=10)
    apertura_frame.pack(fill=tk.X, pady=5)

    tk.Label(apertura_frame, text=f"Fecha: {hoy}", font=("Arial", 10),
            bg="white").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    tk.Label(apertura_frame, text=f"Cajero: {usuario_actual}", font=("Arial", 10),
            bg="white").grid(row=0, column=1, sticky="w", padx=10, pady=5)

    tk.Label(apertura_frame, text="Monto inicial en caja:", font=("Arial", 10, "bold"),
            bg="white").grid(row=1, column=0, sticky="e", padx=10, pady=5)
    monto_inicial = tk.Entry(apertura_frame, width=15, font=("Arial", 12))
    monto_inicial.grid(row=1, column=1, sticky="w", padx=10, pady=5)
    monto_inicial.insert(0, "0.00")

    # --- PANEL MEDIO: RESUMEN DE VENTAS DEL DIA ---
    resumen_frame = tk.LabelFrame(content, text="RESUMEN DE VENTAS DEL DIA", font=("Arial", 11, "bold"),
                                   bg="white", padx=15, pady=10)
    resumen_frame.pack(fill=tk.X, pady=5)

    c.execute("""SELECT COUNT(*), COALESCE(SUM(total), 0),
                 COALESCE(SUM(COALESCE(monto_efectivo,
                     CASE WHEN tipo_pago='EFECTIVO' THEN total ELSE 0 END)), 0),
                 COALESCE(SUM(COALESCE(monto_tarjeta,
                     CASE WHEN tipo_pago='TARJETA' THEN total ELSE 0 END)), 0)
                 FROM ventas WHERE fecha=?""", (hoy,))
    stats = c.fetchone()
    num_ventas = stats[0]
    total_ventas = float(stats[1])
    total_efectivo = float(stats[2])
    total_tarjeta = float(stats[3])

    info_labels = [
        ("Numero de ventas:", str(num_ventas)),
        ("Total ventas:", f"${total_ventas:,.2f}"),
        ("Efectivo:", f"${total_efectivo:,.2f}"),
        ("Tarjeta:", f"${total_tarjeta:,.2f}"),
    ]
    for i, (label, value) in enumerate(info_labels):
        tk.Label(resumen_frame, text=label, font=("Arial", 10, "bold"),
                bg="white").grid(row=i, column=0, sticky="e", padx=10, pady=3)
        tk.Label(resumen_frame, text=value, font=("Arial", 10),
                bg="white", fg="#27AE60").grid(row=i, column=1, sticky="w", padx=10, pady=3)

    # --- PANEL INFERIOR: CIERRE ---
    cierre_frame = tk.LabelFrame(content, text="CIERRE DE CAJA", font=("Arial", 11, "bold"),
                                  bg="white", padx=15, pady=10)
    cierre_frame.pack(fill=tk.X, pady=5)

    tk.Label(cierre_frame, text="Efectivo en caja (contado):", font=("Arial", 10, "bold"),
            bg="white").grid(row=0, column=0, sticky="e", padx=10, pady=5)
    efectivo_contado = tk.Entry(cierre_frame, width=15, font=("Arial", 12))
    efectivo_contado.grid(row=0, column=1, sticky="w", padx=10, pady=5)
    efectivo_contado.insert(0, "0.00")

    diferencia_var = tk.StringVar(value="$0.00")
    estado_var = tk.StringVar(value="")

    tk.Label(cierre_frame, text="Diferencia:", font=("Arial", 10, "bold"),
            bg="white").grid(row=1, column=0, sticky="e", padx=10, pady=5)
    dif_label = tk.Label(cierre_frame, textvariable=diferencia_var, font=("Arial", 12, "bold"),
                         bg="white", fg="#2C3E50")
    dif_label.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    estado_label = tk.Label(cierre_frame, textvariable=estado_var, font=("Arial", 10, "bold"),
                            bg="white")
    estado_label.grid(row=2, column=0, columnspan=2, pady=5)

    def calcular_diferencia(event=None):
        try:
            inicio = float(monto_inicial.get())
            contado = float(efectivo_contado.get())
            esperado = inicio + total_efectivo
            dif = contado - esperado
            diferencia_var.set(f"${dif:,.2f}")

            if dif == 0:
                estado_var.set("CUADRE EXACTO")
                estado_label.config(fg="#27AE60")
                dif_label.config(fg="#27AE60")
            elif dif > 0:
                estado_var.set(f"SOBRANTE: ${dif:,.2f}")
                estado_label.config(fg="#3498DB")
                dif_label.config(fg="#3498DB")
            else:
                estado_var.set(f"FALTANTE: ${abs(dif):,.2f}")
                estado_label.config(fg="#E74C3C")
                dif_label.config(fg="#E74C3C")
        except ValueError:
            diferencia_var.set("$0.00")
            estado_var.set("")

    efectivo_contado.bind("<KeyRelease>", calcular_diferencia)
    monto_inicial.bind("<KeyRelease>", calcular_diferencia)

    # BOTONES
    btn_frame = tk.Frame(content, bg="white")
    btn_frame.pack(pady=15)

    def guardar_corte():
        try:
            inicio = float(monto_inicial.get())
            contado = float(efectivo_contado.get())
            esperado = inicio + total_efectivo
            dif = contado - esperado

            c.execute("""INSERT INTO cortes_caja (fecha, usuario_id, total_ventas, num_ventas, efectivo, tarjeta)
                         VALUES (?,?,?,?,?,?)""",
                     (hoy, usuario_id, total_ventas, num_ventas, total_efectivo, total_tarjeta))
            conn.commit()

            messagebox.showinfo("Corte guardado",
                              f"Corte de caja guardado\n\n"
                              f"Fecha: {hoy}\n"
                              f"Ventas: {num_ventas}\n"
                              f"Total: ${total_ventas:,.2f}\n"
                              f"Efectivo: ${total_efectivo:,.2f}\n"
                              f"Tarjeta: ${total_tarjeta:,.2f}\n"
                              f"Diferencia: ${dif:,.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar corte: {str(e)}")

    def imprimir_corte():
        try:
            inicio = float(monto_inicial.get())
            contado = float(efectivo_contado.get())
            esperado = inicio + total_efectivo
            dif = contado - esperado
        except ValueError:
            inicio = 0.0
            contado = 0.0
            esperado = total_efectivo
            dif = 0.0

        linea = "=" * 44
        linea2 = "-" * 44
        texto = f"""
{linea}
       FARMACIAS MADRID
         CORTE DE CAJA
{linea}
 Fecha:          {hoy}
 Cajero:         {usuario_actual}
{linea2}
 Monto inicial:          ${inicio:>10,.2f}
{linea2}
 Num. de ventas:         {num_ventas:>10}
 Total ventas:           ${total_ventas:>10,.2f}
 Efectivo:               ${total_efectivo:>10,.2f}
 Tarjeta:                ${total_tarjeta:>10,.2f}
{linea2}
 Efectivo esperado:      ${esperado:>10,.2f}
 Efectivo contado:       ${contado:>10,.2f}
 Diferencia:             ${dif:>10,.2f}
{linea}
"""
        if dif == 0:
            texto += "  ESTADO: CUADRE EXACTO\n"
        elif dif > 0:
            texto += f"  ESTADO: SOBRANTE ${dif:,.2f}\n"
        else:
            texto += f"  ESTADO: FALTANTE ${abs(dif):,.2f}\n"

        texto += f"{linea}\n"

        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           f"corte_caja_{hoy}_{datetime.now().strftime('%H%M%S')}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto)

        try:
            os.startfile(ruta, "print")
            messagebox.showinfo("Imprimir", f"Corte enviado a imprimir.\nGuardado en: {ruta}")
        except Exception:
            messagebox.showinfo("Corte guardado", f"Corte guardado en:\n{ruta}")

    tk.Button(btn_frame, text="💾 GUARDAR CORTE", command=guardar_corte,
             bg="#27AE60", fg="white", font=("Arial", 12, "bold"),
             padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=5)

    tk.Button(btn_frame, text="🖨️ IMPRIMIR CORTE", command=imprimir_corte,
             bg="#4A90E2", fg="white", font=("Arial", 12, "bold"),
             padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=5)

    # HISTORIAL DE CORTES
    hist_frame = tk.LabelFrame(content, text="HISTORIAL DE CORTES", font=("Arial", 11, "bold"),
                                bg="white", padx=15, pady=10)
    hist_frame.pack(fill=tk.BOTH, expand=True, pady=5)

    cols_h = ("FECHA", "VENTAS", "TOTAL", "EFECTIVO", "TARJETA")
    tree_h = ttk.Treeview(hist_frame, columns=cols_h, show="headings", height=6)
    for col in cols_h:
        tree_h.heading(col, text=col)
    tree_h.column("FECHA", width=150)
    tree_h.column("VENTAS", width=100)
    tree_h.column("TOTAL", width=150)
    tree_h.column("EFECTIVO", width=150)
    tree_h.column("TARJETA", width=150)
    tree_h.pack(fill=tk.BOTH, expand=True)

    c.execute("SELECT fecha, num_ventas, total_ventas, efectivo, tarjeta FROM cortes_caja ORDER BY fecha DESC LIMIT 20")
    for row in c.fetchall():
        tree_h.insert("", "end", values=(row[0], row[1], f"${float(row[2]):,.2f}",
                      f"${float(row[3]):,.2f}", f"${float(row[4]):,.2f}"))

# ===== MODULO SERVICIO A DOMICILIO =====
def ver_domicilio():
    limpiar()

    header_mod = tk.Frame(main, bg="#00897B", height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="🏍️ SERVICIO A DOMICILIO", font=("Arial", 13, "bold"),
            bg="#00897B", fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    tk.Button(header_mod, text="+ NUEVA ENTREGA", command=lambda: nueva_entrega_dialog(),
             bg="#00C853", fg="white", font=("Arial", 10, "bold"),
             padx=15, pady=5, relief=tk.FLAT, cursor="hand2").pack(side=tk.RIGHT, padx=12, pady=8)

    content = tk.Frame(main, bg="white")
    content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    # --- ENTREGAS ACTIVAS ---
    activas_frame = tk.LabelFrame(content, text="ENTREGAS ACTIVAS", font=("Arial", 11, "bold"),
                                   bg="white", padx=10, pady=5)
    activas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

    cols_act = ("ID", "CLIENTE", "DIRECCION", "REPARTIDOR", "MOTO", "ESTADO", "HORA SAL.")
    tree_activas = ttk.Treeview(activas_frame, columns=cols_act, show="headings", height=8)
    for col in cols_act:
        tree_activas.heading(col, text=col)
    tree_activas.column("ID", width=50)
    tree_activas.column("CLIENTE", width=150)
    tree_activas.column("DIRECCION", width=250)
    tree_activas.column("REPARTIDOR", width=130)
    tree_activas.column("MOTO", width=60)
    tree_activas.column("ESTADO", width=100)
    tree_activas.column("HORA SAL.", width=80)

    scroll_act = ttk.Scrollbar(activas_frame, orient="vertical", command=tree_activas.yview)
    tree_activas.configure(yscrollcommand=scroll_act.set)
    tree_activas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll_act.pack(side=tk.RIGHT, fill=tk.Y)

    # Botones de accion para entregas activas
    btn_activas = tk.Frame(content, bg="white")
    btn_activas.pack(fill=tk.X, pady=5)

    def enviar_entrega():
        sel = tree_activas.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona una entrega PENDIENTE")
            return
        vals = tree_activas.item(sel[0])['values']
        eid = vals[0]
        if vals[5] != "PENDIENTE":
            messagebox.showwarning("Estado", "Solo se pueden enviar entregas PENDIENTES")
            return
        hora = datetime.now().strftime('%H:%M:%S')
        c.execute("UPDATE entregas SET estado='EN_CAMINO', hora_salida=? WHERE id=?", (hora, eid))
        conn.commit()
        messagebox.showinfo("Enviado", f"Entrega #{eid} marcada EN CAMINO a las {hora}")
        cargar_activas()

    def marcar_entregado():
        sel = tree_activas.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona una entrega EN CAMINO")
            return
        vals = tree_activas.item(sel[0])['values']
        eid = vals[0]
        if vals[5] != "EN_CAMINO":
            messagebox.showwarning("Estado", "Solo se pueden entregar pedidos EN CAMINO")
            return
        hora = datetime.now().strftime('%H:%M:%S')
        c.execute("UPDATE entregas SET estado='ENTREGADO', hora_llegada=? WHERE id=?", (hora, eid))
        conn.commit()
        messagebox.showinfo("Entregado", f"Entrega #{eid} marcada como ENTREGADO a las {hora}")
        cargar_activas()
        cargar_historial()

    def cancelar_entrega():
        sel = tree_activas.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona una entrega")
            return
        vals = tree_activas.item(sel[0])['values']
        eid = vals[0]
        if vals[5] == "ENTREGADO":
            messagebox.showwarning("Estado", "No se puede cancelar una entrega ya ENTREGADA")
            return
        if not messagebox.askyesno("Cancelar", f"Cancelar entrega #{eid}?\nSe revertira el stock."):
            return
        # Revertir stock: buscar la venta asociada
        c.execute("SELECT venta_id FROM entregas WHERE id=?", (eid,))
        row = c.fetchone()
        if row and row[0]:
            venta_id = row[0]
            c.execute("SELECT producto_id, cantidad FROM detalle_ventas WHERE venta_id=?", (venta_id,))
            for prod_id, cant in c.fetchall():
                c.execute("UPDATE productos SET stock = stock + ? WHERE id=?", (cant, prod_id))
        c.execute("UPDATE entregas SET estado='CANCELADO' WHERE id=?", (eid,))
        conn.commit()
        messagebox.showinfo("Cancelado", f"Entrega #{eid} CANCELADA. Stock revertido.")
        cargar_activas()
        cargar_historial()

    tk.Button(btn_activas, text="📤 ENVIAR", command=enviar_entrega,
             bg="#1565C0", fg="white", font=("Arial", 10, "bold"),
             padx=15, pady=6, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(btn_activas, text="✅ ENTREGADO", command=marcar_entregado,
             bg="#00C853", fg="white", font=("Arial", 10, "bold"),
             padx=15, pady=6, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(btn_activas, text="❌ CANCELAR", command=cancelar_entrega,
             bg="#D32F2F", fg="white", font=("Arial", 10, "bold"),
             padx=15, pady=6, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(btn_activas, text="🔄 ACTUALIZAR", command=lambda: (cargar_activas(), cargar_historial()),
             bg="#546E7A", fg="white", font=("Arial", 10, "bold"),
             padx=15, pady=6, relief=tk.FLAT, cursor="hand2").pack(side=tk.RIGHT, padx=3)

    # --- HISTORIAL DE HOY ---
    hist_frame = tk.LabelFrame(content, text="HISTORIAL DE HOY", font=("Arial", 11, "bold"),
                                bg="white", padx=10, pady=5)
    hist_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    # Filtros historial
    filtro_frame = tk.Frame(hist_frame, bg="white")
    filtro_frame.pack(fill=tk.X, pady=5)

    tk.Label(filtro_frame, text="Fecha:", font=("Arial", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    fecha_filtro = tk.Entry(filtro_frame, width=12, font=("Arial", 9))
    fecha_filtro.pack(side=tk.LEFT, padx=3)
    fecha_filtro.insert(0, datetime.now().strftime('%Y-%m-%d'))

    tk.Label(filtro_frame, text="Repartidor:", font=("Arial", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=(15, 5))
    rep_filtro_var = tk.StringVar(value="TODOS")
    rep_filtro = ttk.Combobox(filtro_frame, textvariable=rep_filtro_var, width=18, state="readonly")
    c.execute("SELECT nombre FROM repartidores WHERE activo=1")
    rep_nombres = ["TODOS"] + [r[0] for r in c.fetchall()]
    rep_filtro['values'] = rep_nombres
    rep_filtro.pack(side=tk.LEFT, padx=3)

    tk.Button(filtro_frame, text="FILTRAR", command=lambda: cargar_historial(),
             bg="#546E7A", fg="white", font=("Arial", 9, "bold"),
             padx=10, pady=3, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=5)

    cols_hist = ("ID", "CLIENTE", "TOTAL", "REPARTIDOR", "MOTO", "ESTADO", "HORA SAL.", "HORA LLEG.")
    tree_hist = ttk.Treeview(hist_frame, columns=cols_hist, show="headings", height=8)
    for col in cols_hist:
        tree_hist.heading(col, text=col)
    tree_hist.column("ID", width=50)
    tree_hist.column("CLIENTE", width=150)
    tree_hist.column("TOTAL", width=90)
    tree_hist.column("REPARTIDOR", width=130)
    tree_hist.column("MOTO", width=60)
    tree_hist.column("ESTADO", width=100)
    tree_hist.column("HORA SAL.", width=80)
    tree_hist.column("HORA LLEG.", width=80)

    scroll_hist = ttk.Scrollbar(hist_frame, orient="vertical", command=tree_hist.yview)
    tree_hist.configure(yscrollcommand=scroll_hist.set)
    tree_hist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll_hist.pack(side=tk.RIGHT, fill=tk.Y)

    # Tags de color para estados
    tree_activas.tag_configure("pendiente", background="#FFF9C4")
    tree_activas.tag_configure("en_camino", background="#B3E5FC")
    tree_hist.tag_configure("entregado", background="#C8E6C9")
    tree_hist.tag_configure("cancelado", background="#FFCDD2")

    def cargar_activas():
        for item in tree_activas.get_children():
            tree_activas.delete(item)
        c.execute("""SELECT e.id, cl.nombre, e.direccion, r.nombre, e.num_moto, e.estado, e.hora_salida
                     FROM entregas e
                     LEFT JOIN clientes cl ON e.cliente_id=cl.id
                     LEFT JOIN repartidores r ON e.repartidor_id=r.id
                     WHERE e.estado IN ('PENDIENTE','EN_CAMINO')
                     ORDER BY e.id DESC""")
        for row in c.fetchall():
            tag = "pendiente" if row[5] == "PENDIENTE" else "en_camino"
            tree_activas.insert("", "end", values=(row[0], row[1] or "", row[2] or "",
                               row[3] or "", row[4] or "", row[5], row[6] or ""), tags=(tag,))

    def cargar_historial():
        for item in tree_hist.get_children():
            tree_hist.delete(item)
        fecha = fecha_filtro.get().strip()
        rep_nombre = rep_filtro_var.get()

        query = """SELECT e.id, cl.nombre, e.monto_cobrar, r.nombre, e.num_moto,
                          e.estado, e.hora_salida, e.hora_llegada
                   FROM entregas e
                   LEFT JOIN clientes cl ON e.cliente_id=cl.id
                   LEFT JOIN repartidores r ON e.repartidor_id=r.id
                   WHERE e.fecha=?"""
        params = [fecha]
        if rep_nombre != "TODOS":
            query += " AND r.nombre=?"
            params.append(rep_nombre)
        query += " ORDER BY e.id DESC"

        c.execute(query, params)
        for row in c.fetchall():
            tag = ""
            if row[5] == "ENTREGADO":
                tag = "entregado"
            elif row[5] == "CANCELADO":
                tag = "cancelado"
            monto = f"${float(row[2]):,.2f}" if row[2] else "$0.00"
            tree_hist.insert("", "end", values=(row[0], row[1] or "", monto,
                            row[3] or "", row[4] or "", row[5], row[6] or "", row[7] or ""), tags=(tag,))

    # --- DIALOG NUEVA ENTREGA ---
    def nueva_entrega_dialog():
        win = tk.Toplevel(main)
        win.title("Nueva Entrega a Domicilio")
        win.geometry("700x750")
        win.resizable(False, False)
        win.configure(bg="white")
        win.grab_set()

        tk.Label(win, text="🏍️ NUEVA ENTREGA A DOMICILIO", font=("Arial", 14, "bold"),
                bg="white", fg="#00897B").pack(pady=12)

        # --- DATOS DEL CLIENTE ---
        cli_frame = tk.LabelFrame(win, text="DATOS DEL CLIENTE", font=("Arial", 10, "bold"),
                                   bg="white", padx=10, pady=8)
        cli_frame.pack(fill=tk.X, padx=15, pady=5)

        tel_frame = tk.Frame(cli_frame, bg="white")
        tel_frame.pack(fill=tk.X, pady=3)
        tk.Label(tel_frame, text="Telefono:", font=("Arial", 9, "bold"), bg="white", width=10, anchor="e").pack(side=tk.LEFT, padx=5)
        tel_entry = tk.Entry(tel_frame, width=20, font=("Arial", 10))
        tel_entry.pack(side=tk.LEFT, padx=5)

        cliente_id_var = tk.IntVar(value=0)
        info_cli = tk.Label(tel_frame, text="", font=("Arial", 8), bg="white", fg="#00897B")
        info_cli.pack(side=tk.LEFT, padx=5)

        nom_frame = tk.Frame(cli_frame, bg="white")
        nom_frame.pack(fill=tk.X, pady=3)
        tk.Label(nom_frame, text="Nombre:", font=("Arial", 9, "bold"), bg="white", width=10, anchor="e").pack(side=tk.LEFT, padx=5)
        nom_entry = tk.Entry(nom_frame, width=40, font=("Arial", 10))
        nom_entry.pack(side=tk.LEFT, padx=5)

        dir_frame = tk.Frame(cli_frame, bg="white")
        dir_frame.pack(fill=tk.X, pady=3)
        tk.Label(dir_frame, text="Direccion:", font=("Arial", 9, "bold"), bg="white", width=10, anchor="e").pack(side=tk.LEFT, padx=5)
        dir_entry = tk.Entry(dir_frame, width=40, font=("Arial", 10))
        dir_entry.pack(side=tk.LEFT, padx=5)

        ref_frame = tk.Frame(cli_frame, bg="white")
        ref_frame.pack(fill=tk.X, pady=3)
        tk.Label(ref_frame, text="Referencia:", font=("Arial", 9, "bold"), bg="white", width=10, anchor="e").pack(side=tk.LEFT, padx=5)
        ref_entry = tk.Entry(ref_frame, width=40, font=("Arial", 10))
        ref_entry.pack(side=tk.LEFT, padx=5)

        def buscar_cliente():
            tel = tel_entry.get().strip()
            if not tel:
                return
            c.execute("SELECT id, nombre, direccion, colonia, direccion_completa, referencia FROM clientes WHERE telefono=?", (tel,))
            cli = c.fetchone()
            if cli:
                cliente_id_var.set(cli[0])
                nom_entry.delete(0, tk.END)
                nom_entry.insert(0, cli[1] or "")
                dir_entry.delete(0, tk.END)
                dir_entry.insert(0, cli[4] or cli[3] or cli[2] or "")
                ref_entry.delete(0, tk.END)
                ref_entry.insert(0, cli[5] or "")
                info_cli.config(text=f"Cliente encontrado: {cli[1]}", fg="#00897B")
            else:
                cliente_id_var.set(0)
                info_cli.config(text="Cliente no encontrado - se creara nuevo", fg="#E67E22")

        tk.Button(tel_frame, text="Buscar", command=buscar_cliente,
                 bg="#00897B", fg="white", font=("Arial", 8, "bold"),
                 padx=8, pady=2, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=3)

        # --- PRODUCTOS DEL PEDIDO ---
        prod_frame = tk.LabelFrame(win, text="PRODUCTOS DEL PEDIDO", font=("Arial", 10, "bold"),
                                    bg="white", padx=10, pady=5)
        prod_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        busq_frame = tk.Frame(prod_frame, bg="white")
        busq_frame.pack(fill=tk.X, pady=3)
        tk.Label(busq_frame, text="Codigo/nombre:", font=("Arial", 9), bg="white").pack(side=tk.LEFT, padx=5)
        prod_entry = tk.Entry(busq_frame, width=30, font=("Arial", 9))
        prod_entry.pack(side=tk.LEFT, padx=5)

        pedido_items = []

        cols_ped = ("COD", "PRODUCTO", "PRECIO", "CANT", "SUBTOTAL")
        tree_ped = ttk.Treeview(prod_frame, columns=cols_ped, show="headings", height=5)
        for col in cols_ped:
            tree_ped.heading(col, text=col)
        tree_ped.column("COD", width=80)
        tree_ped.column("PRODUCTO", width=250)
        tree_ped.column("PRECIO", width=70)
        tree_ped.column("CANT", width=50)
        tree_ped.column("SUBTOTAL", width=70)
        tree_ped.pack(fill=tk.BOTH, expand=True, pady=3)

        total_ped_var = tk.StringVar(value="TOTAL: $0.00")
        tk.Label(prod_frame, textvariable=total_ped_var, font=("Arial", 12, "bold"),
                bg="white", fg="#00897B").pack(anchor="e", padx=10)

        def actualizar_tree_pedido():
            for item in tree_ped.get_children():
                tree_ped.delete(item)
            total = 0.0
            for it in pedido_items:
                tree_ped.insert("", "end", values=it)
                total += float(it[4])
            total_ped_var.set(f"TOTAL: ${total:,.2f}")

        def agregar_producto(event=None):
            busqueda = prod_entry.get().strip().upper()
            if not busqueda:
                return
            # Intentar por codigo exacto
            c.execute("SELECT codigo, nombre, precio_venta, stock FROM productos WHERE codigo=?", (busqueda,))
            producto = c.fetchone()
            if not producto:
                # Buscar por nombre
                c.execute("SELECT codigo, nombre, precio_venta, stock FROM productos WHERE nombre LIKE ? LIMIT 1", (f"%{busqueda}%",))
                producto = c.fetchone()
            if producto:
                precio = float(producto[2])
                # Verificar si ya existe
                existe = False
                for idx, it in enumerate(pedido_items):
                    if it[0] == producto[0]:
                        nueva_cant = it[3] + 1
                        pedido_items[idx] = (it[0], it[1], precio, nueva_cant, precio * nueva_cant)
                        existe = True
                        break
                if not existe:
                    pedido_items.append((producto[0], producto[1][:40], precio, 1, precio))
                actualizar_tree_pedido()
                prod_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("No encontrado", f"Producto '{busqueda}' no encontrado")

        def quitar_producto():
            sel = tree_ped.selection()
            if sel:
                idx = tree_ped.index(sel[0])
                pedido_items.pop(idx)
                actualizar_tree_pedido()

        prod_entry.bind("<Return>", agregar_producto)
        btn_prod = tk.Frame(busq_frame, bg="white")
        btn_prod.pack(side=tk.LEFT, padx=3)
        tk.Button(btn_prod, text="Agregar", command=agregar_producto,
                 bg="#00897B", fg="white", font=("Arial", 8, "bold"),
                 padx=6, pady=2, relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_prod, text="Quitar", command=quitar_producto,
                 bg="#D32F2F", fg="white", font=("Arial", 8, "bold"),
                 padx=6, pady=2, relief=tk.FLAT).pack(side=tk.LEFT, padx=2)

        # --- DATOS DE ENTREGA ---
        ent_frame = tk.LabelFrame(win, text="DATOS DE ENTREGA", font=("Arial", 10, "bold"),
                                   bg="white", padx=10, pady=5)
        ent_frame.pack(fill=tk.X, padx=15, pady=5)

        rep_row = tk.Frame(ent_frame, bg="white")
        rep_row.pack(fill=tk.X, pady=3)
        tk.Label(rep_row, text="Repartidor:", font=("Arial", 9, "bold"), bg="white", width=12, anchor="e").pack(side=tk.LEFT, padx=5)
        rep_var = tk.StringVar()
        rep_combo = ttk.Combobox(rep_row, textvariable=rep_var, width=25, state="readonly")
        c.execute("SELECT id, nombre, num_moto FROM repartidores WHERE activo=1")
        repartidores = c.fetchall()
        rep_combo['values'] = [f"{r[1]} ({r[2]})" for r in repartidores]
        if rep_combo['values']:
            rep_combo.current(0)
        rep_combo.pack(side=tk.LEFT, padx=5)

        moto_var = tk.StringVar(value=repartidores[0][2] if repartidores else "")
        tk.Label(rep_row, text="Moto:", font=("Arial", 9), bg="white").pack(side=tk.LEFT, padx=(10, 5))
        tk.Label(rep_row, textvariable=moto_var, font=("Arial", 9, "bold"), bg="white", fg="#1565C0").pack(side=tk.LEFT)

        def actualizar_moto(event=None):
            idx = rep_combo.current()
            if idx >= 0 and idx < len(repartidores):
                moto_var.set(repartidores[idx][2])
        rep_combo.bind("<<ComboboxSelected>>", actualizar_moto)

        pago_row = tk.Frame(ent_frame, bg="white")
        pago_row.pack(fill=tk.X, pady=3)
        tk.Label(pago_row, text="Metodo pago:", font=("Arial", 9, "bold"), bg="white", width=12, anchor="e").pack(side=tk.LEFT, padx=5)
        metodo_pago_var = tk.StringVar(value="EFECTIVO")
        tk.Radiobutton(pago_row, text="Efectivo", variable=metodo_pago_var, value="EFECTIVO",
                       bg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(pago_row, text="Tarjeta", variable=metodo_pago_var, value="TARJETA",
                       bg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(pago_row, text="Pagado", variable=metodo_pago_var, value="PAGADO",
                       bg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)

        cambio_row = tk.Frame(ent_frame, bg="white")
        cambio_row.pack(fill=tk.X, pady=3)
        tk.Label(cambio_row, text="Monto cliente:", font=("Arial", 9, "bold"), bg="white", width=12, anchor="e").pack(side=tk.LEFT, padx=5)
        monto_cli_entry = tk.Entry(cambio_row, width=12, font=("Arial", 10))
        monto_cli_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(cambio_row, text="Cambio a llevar:", font=("Arial", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=(10, 5))
        cambio_var = tk.StringVar(value="$0.00")
        tk.Label(cambio_row, textvariable=cambio_var, font=("Arial", 10, "bold"), bg="white", fg="#D32F2F").pack(side=tk.LEFT)

        def calcular_cambio(event=None):
            total = sum(float(it[4]) for it in pedido_items) if pedido_items else 0.0
            try:
                monto = float(monto_cli_entry.get())
                cambio = max(monto - total, 0)
                cambio_var.set(f"${cambio:,.2f}")
            except ValueError:
                cambio_var.set("$0.00")
        monto_cli_entry.bind("<KeyRelease>", calcular_cambio)

        notas_row = tk.Frame(ent_frame, bg="white")
        notas_row.pack(fill=tk.X, pady=3)
        tk.Label(notas_row, text="Notas:", font=("Arial", 9, "bold"), bg="white", width=12, anchor="e").pack(side=tk.LEFT, padx=5)
        notas_entry = tk.Entry(notas_row, width=40, font=("Arial", 9))
        notas_entry.pack(side=tk.LEFT, padx=5)

        # --- BOTONES ---
        btn_frame = tk.Frame(win, bg="white")
        btn_frame.pack(fill=tk.X, padx=15, pady=10)

        def registrar_entrega():
            if not pedido_items:
                messagebox.showwarning("Sin productos", "Agrega al menos un producto al pedido")
                return
            if not nom_entry.get().strip():
                messagebox.showwarning("Sin cliente", "Ingresa el nombre del cliente")
                return
            if not dir_entry.get().strip():
                messagebox.showwarning("Sin direccion", "Ingresa la direccion de entrega")
                return

            # Crear o buscar cliente
            cli_id = cliente_id_var.get()
            if cli_id == 0:
                c.execute("SELECT MAX(id) FROM clientes")
                max_id = c.fetchone()[0] or 0
                cli_id = max_id + 1
                c.execute("INSERT INTO clientes VALUES (?,?,?,?,?,?,?,?,?)",
                         (cli_id, nom_entry.get().strip(), tel_entry.get().strip(), "",
                          dir_entry.get().strip(), "", 0, dir_entry.get().strip(), ref_entry.get().strip()))

            # Crear venta
            total = sum(float(it[4]) for it in pedido_items)
            folio_v = f"D{datetime.now().strftime('%Y%m%d%H%M%S')}"
            fecha = datetime.now().strftime('%Y-%m-%d')
            hora = datetime.now().strftime('%H:%M:%S')

            metodo = metodo_pago_var.get()
            efec = total if metodo == "EFECTIVO" else 0.0
            tarj = total if metodo == "TARJETA" else 0.0

            c.execute("""INSERT INTO ventas (folio, fecha, hora, vendedor_id, cliente_id,
                        subtotal, iva, total, tipo_pago, monto_efectivo, monto_tarjeta)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                     (folio_v, fecha, hora, usuario_id, cli_id, total, 0, total, metodo, efec, tarj))
            venta_id = c.lastrowid

            for it in pedido_items:
                c.execute("SELECT id FROM productos WHERE codigo=?", (it[0],))
                pid_row = c.fetchone()
                if pid_row:
                    c.execute("INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
                             (venta_id, pid_row[0], it[3], it[2], it[4]))
                    c.execute("UPDATE productos SET stock = stock - ? WHERE id=?", (it[3], pid_row[0]))

            # Crear entrega
            idx_rep = rep_combo.current()
            rep_id = repartidores[idx_rep][0] if idx_rep >= 0 else None
            moto = moto_var.get()

            try:
                monto_cobrar = float(monto_cli_entry.get()) if monto_cli_entry.get() else total
            except ValueError:
                monto_cobrar = total
            cambio_llevar = max(monto_cobrar - total, 0)

            c.execute("""INSERT INTO entregas (venta_id, cliente_id, repartidor_id, num_moto,
                        direccion, referencia, telefono_cliente, estado, metodo_pago_entrega,
                        monto_cobrar, cambio_llevar, notas, fecha)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                     (venta_id, cli_id, rep_id, moto, dir_entry.get().strip(),
                      ref_entry.get().strip(), tel_entry.get().strip(),
                      "PENDIENTE", metodo, monto_cobrar, cambio_llevar,
                      notas_entry.get().strip(), fecha))

            conn.commit()
            messagebox.showinfo("Registrado",
                              f"Entrega registrada\n\n"
                              f"Folio: {folio_v}\n"
                              f"Cliente: {nom_entry.get()}\n"
                              f"Total: ${total:,.2f}\n"
                              f"Repartidor: {rep_var.get()}\n"
                              f"Cambio a llevar: ${cambio_llevar:,.2f}")
            win.destroy()
            cargar_activas()
            cargar_historial()

        tk.Button(btn_frame, text="REGISTRAR ENTREGA", command=registrar_entrega,
                 bg="#00C853", fg="white", font=("Arial", 12, "bold"),
                 padx=25, pady=10, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="CANCELAR", command=win.destroy,
                 bg="#D32F2F", fg="white", font=("Arial", 12, "bold"),
                 padx=25, pady=10, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=10)

    # Carga inicial
    cargar_activas()
    cargar_historial()


# ===== MÓDULO TRASPASOS ENTRE FARMACIAS =====
def ver_traspasos():
    limpiar()

    SUCURSALES = ["Tulancingo 1", "Tulancingo 2", "Tulancingo 3", "Tulancingo 4", "Tulancingo 5"]

    # HEADER
    header_mod = tk.Frame(main, bg="#4CAF50", height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="\u21C4 TRASPASOS ENTRE FARMACIAS", font=("Segoe UI", 13, "bold"),
            bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    content = tk.Frame(main, bg="#F5F5F5")
    content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- BARRA DE FILTROS Y BOTÓN NUEVO ---
    toolbar = tk.Frame(content, bg="white", relief=tk.RIDGE, bd=1)
    toolbar.pack(fill=tk.X, pady=(0, 8))

    btn_nuevo = tk.Button(toolbar, text="+ NUEVO TRASPASO", command=lambda: dialog_nuevo_traspaso(),
                          bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"),
                          relief=tk.FLAT, padx=16, pady=6, cursor="hand2",
                          activebackground="#66BB6A", activeforeground="white")
    btn_nuevo.pack(side=tk.LEFT, padx=10, pady=8)
    hover_bind(btn_nuevo, "#4CAF50", "#66BB6A")

    tk.Label(toolbar, text="Sucursal:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=(20,4))
    filtro_suc = tk.StringVar(value="TODAS")
    combo_suc = ttk.Combobox(toolbar, textvariable=filtro_suc, width=16,
                             values=["TODAS"] + SUCURSALES, state="readonly")
    combo_suc.pack(side=tk.LEFT, padx=4, pady=8)

    tk.Label(toolbar, text="Desde:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=(16,4))
    fecha_desde = tk.Entry(toolbar, width=12, font=("Segoe UI", 9))
    fecha_desde.pack(side=tk.LEFT, padx=4, pady=8)
    fecha_desde.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))

    tk.Label(toolbar, text="Hasta:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=(10,4))
    fecha_hasta = tk.Entry(toolbar, width=12, font=("Segoe UI", 9))
    fecha_hasta.pack(side=tk.LEFT, padx=4, pady=8)
    fecha_hasta.insert(0, datetime.now().strftime("%Y-%m-%d"))

    btn_filtrar = tk.Button(toolbar, text="FILTRAR", command=lambda: cargar_datos(),
                            bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
                            relief=tk.FLAT, padx=12, pady=4, cursor="hand2",
                            activebackground="#1E88E5")
    btn_filtrar.pack(side=tk.LEFT, padx=10, pady=8)
    hover_bind(btn_filtrar, "#1565C0", "#1E88E5")

    # --- TABLA PENDIENTES ---
    tk.Label(content, text="TRASPASOS PENDIENTES", font=("Segoe UI", 11, "bold"),
            bg="#F5F5F5", fg="#E65100").pack(anchor="w", pady=(6,2))

    frame_pend = tk.Frame(content, bg="white", relief=tk.RIDGE, bd=1)
    frame_pend.pack(fill=tk.X, pady=(0,8))

    cols_pend = ("FOLIO", "FECHA", "ORIGEN", "DESTINO", "MOTIVO", "PRODUCTOS", "ESTADO")
    tree_pend = ttk.Treeview(frame_pend, columns=cols_pend, show="headings", height=6)
    for col in cols_pend:
        tree_pend.heading(col, text=col)
    tree_pend.column("FOLIO", width=160)
    tree_pend.column("FECHA", width=100)
    tree_pend.column("ORIGEN", width=130)
    tree_pend.column("DESTINO", width=130)
    tree_pend.column("MOTIVO", width=110)
    tree_pend.column("PRODUCTOS", width=80)
    tree_pend.column("ESTADO", width=110)
    scroll_pend = ttk.Scrollbar(frame_pend, orient="vertical", command=tree_pend.yview)
    tree_pend.configure(yscrollcommand=scroll_pend.set)
    tree_pend.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll_pend.pack(side=tk.RIGHT, fill=tk.Y)

    # Botones de acción para pendientes
    frame_acciones = tk.Frame(content, bg="#F5F5F5")
    frame_acciones.pack(fill=tk.X, pady=(0,6))

    btn_confirmar = tk.Button(frame_acciones, text="CONFIRMAR TRASPASO",
                              command=lambda: cambiar_estado("CONFIRMADO"),
                              bg="#FF9800", fg="white", font=("Segoe UI", 9, "bold"),
                              relief=tk.FLAT, padx=12, pady=4, cursor="hand2")
    btn_confirmar.pack(side=tk.LEFT, padx=4)
    hover_bind(btn_confirmar, "#FF9800", "#FFB74D")

    btn_completar = tk.Button(frame_acciones, text="COMPLETAR TRASPASO",
                              command=lambda: cambiar_estado("COMPLETADO"),
                              bg="#4CAF50", fg="white", font=("Segoe UI", 9, "bold"),
                              relief=tk.FLAT, padx=12, pady=4, cursor="hand2")
    btn_completar.pack(side=tk.LEFT, padx=4)
    hover_bind(btn_completar, "#4CAF50", "#66BB6A")

    btn_cancelar = tk.Button(frame_acciones, text="CANCELAR",
                             command=lambda: cambiar_estado("CANCELADO"),
                             bg="#D32F2F", fg="white", font=("Segoe UI", 9, "bold"),
                             relief=tk.FLAT, padx=12, pady=4, cursor="hand2")
    btn_cancelar.pack(side=tk.LEFT, padx=4)
    hover_bind(btn_cancelar, "#D32F2F", "#EF5350")

    btn_imprimir = tk.Button(frame_acciones, text="IMPRIMIR ORDEN",
                             command=lambda: imprimir_orden(),
                             bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
                             relief=tk.FLAT, padx=12, pady=4, cursor="hand2")
    btn_imprimir.pack(side=tk.LEFT, padx=4)
    hover_bind(btn_imprimir, "#1565C0", "#1E88E5")

    # --- HISTORIAL ---
    tk.Label(content, text="HISTORIAL DE TRASPASOS", font=("Segoe UI", 11, "bold"),
            bg="#F5F5F5", fg="#1565C0").pack(anchor="w", pady=(6,2))

    frame_hist = tk.Frame(content, bg="white", relief=tk.RIDGE, bd=1)
    frame_hist.pack(fill=tk.BOTH, expand=True, pady=(0,4))

    cols_hist = ("FOLIO", "FECHA", "ORIGEN", "DESTINO", "MOTIVO", "PRODUCTOS", "ESTADO", "CONFIRMÓ", "COMPLETÓ")
    tree_hist = ttk.Treeview(frame_hist, columns=cols_hist, show="headings", height=10)
    for col in cols_hist:
        tree_hist.heading(col, text=col)
    tree_hist.column("FOLIO", width=160)
    tree_hist.column("FECHA", width=90)
    tree_hist.column("ORIGEN", width=110)
    tree_hist.column("DESTINO", width=110)
    tree_hist.column("MOTIVO", width=100)
    tree_hist.column("PRODUCTOS", width=70)
    tree_hist.column("ESTADO", width=100)
    tree_hist.column("CONFIRMÓ", width=90)
    tree_hist.column("COMPLETÓ", width=90)
    scroll_hist = ttk.Scrollbar(frame_hist, orient="vertical", command=tree_hist.yview)
    tree_hist.configure(yscrollcommand=scroll_hist.set)
    tree_hist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll_hist.pack(side=tk.RIGHT, fill=tk.Y)

    # --- FUNCIONES INTERNAS ---
    def cargar_datos():
        for item in tree_pend.get_children():
            tree_pend.delete(item)
        for item in tree_hist.get_children():
            tree_hist.delete(item)

        suc = filtro_suc.get()
        f1 = fecha_desde.get()
        f2 = fecha_hasta.get()

        base_q = """SELECT t.folio, t.fecha, t.sucursal_origen, t.sucursal_destino,
                    t.motivo, (SELECT COUNT(*) FROM detalle_traspasos WHERE traspaso_id=t.id),
                    t.estado"""
        base_from = " FROM traspasos t WHERE t.fecha BETWEEN ? AND ?"
        params = [f1, f2]

        if suc != "TODAS":
            base_from += " AND (t.sucursal_origen=? OR t.sucursal_destino=?)"
            params += [suc, suc]

        # Pendientes y confirmados
        c.execute(base_q + base_from + " AND t.estado IN ('PENDIENTE','CONFIRMADO') ORDER BY t.fecha DESC", params)
        for row in c.fetchall():
            tree_pend.insert("", "end", values=row)

        # Historial (completados y cancelados)
        q_hist = """SELECT t.folio, t.fecha, t.sucursal_origen, t.sucursal_destino,
                    t.motivo, (SELECT COUNT(*) FROM detalle_traspasos WHERE traspaso_id=t.id),
                    t.estado, COALESCE(e1.nombre,''), COALESCE(e2.nombre,'')
                    FROM traspasos t
                    LEFT JOIN empleados e1 ON t.usuario_confirma=e1.id
                    LEFT JOIN empleados e2 ON t.usuario_completa=e2.id
                    WHERE t.fecha BETWEEN ? AND ?"""
        params_h = [f1, f2]
        if suc != "TODAS":
            q_hist += " AND (t.sucursal_origen=? OR t.sucursal_destino=?)"
            params_h += [suc, suc]
        q_hist += " AND t.estado IN ('COMPLETADO','CANCELADO') ORDER BY t.fecha DESC"
        c.execute(q_hist, params_h)
        for row in c.fetchall():
            tree_hist.insert("", "end", values=row)

    def cambiar_estado(nuevo_estado):
        sel = tree_pend.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un traspaso de la tabla de pendientes")
            return
        folio = tree_pend.item(sel[0])["values"][0]
        estado_actual = tree_pend.item(sel[0])["values"][6]

        if nuevo_estado == "CONFIRMADO" and estado_actual != "PENDIENTE":
            messagebox.showwarning("Aviso", "Solo se pueden confirmar traspasos PENDIENTES")
            return
        if nuevo_estado == "COMPLETADO" and estado_actual != "CONFIRMADO":
            messagebox.showwarning("Aviso", "Solo se pueden completar traspasos CONFIRMADOS")
            return

        if not messagebox.askyesno("Confirmar", f"¿Cambiar traspaso {folio} a {nuevo_estado}?"):
            return

        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if nuevo_estado == "CONFIRMADO":
            c.execute("UPDATE traspasos SET estado=?, usuario_confirma=?, fecha_confirmacion=? WHERE folio=?",
                      (nuevo_estado, usuario_id, ahora, folio))

        elif nuevo_estado == "COMPLETADO":
            # Mover stock: restar de origen (simulado), sumar en destino (stock local)
            c.execute("SELECT id FROM traspasos WHERE folio=?", (folio,))
            tid = c.fetchone()[0]
            c.execute("SELECT producto_id, cantidad FROM detalle_traspasos WHERE traspaso_id=?", (tid,))
            for prod_id, cant in c.fetchall():
                # Sumar stock en destino (esta sucursal)
                c.execute("UPDATE productos SET stock = stock + ? WHERE id=?", (cant, prod_id))
                # Registrar movimiento
                c.execute("INSERT INTO inventario_movimientos (fecha,tipo,producto_id,cantidad,usuario_id,notas) VALUES (?,?,?,?,?,?)",
                          (ahora, "TRASPASO_ENTRADA", prod_id, cant, usuario_id, f"Traspaso {folio}"))
            c.execute("UPDATE traspasos SET estado=?, usuario_completa=?, fecha_completado=? WHERE folio=?",
                      (nuevo_estado, usuario_id, ahora, folio))

        elif nuevo_estado == "CANCELADO":
            # Devolver stock si ya fue restado (estado CONFIRMADO con descuento previo)
            c.execute("SELECT id, estado FROM traspasos WHERE folio=?", (folio,))
            row = c.fetchone()
            tid, est = row[0], row[1]
            if est == "CONFIRMADO":
                c.execute("SELECT producto_id, cantidad FROM detalle_traspasos WHERE traspaso_id=?", (tid,))
                for prod_id, cant in c.fetchall():
                    c.execute("UPDATE productos SET stock = stock + ? WHERE id=?", (cant, prod_id))
            c.execute("UPDATE traspasos SET estado=? WHERE folio=?", (nuevo_estado, folio))

        conn.commit()
        cargar_datos()
        messagebox.showinfo("Éxito", f"Traspaso {folio} ahora está {nuevo_estado}")

    def imprimir_orden():
        sel = tree_pend.selection()
        if not sel:
            sel = tree_hist.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un traspaso para imprimir")
            return
        folio = sel[0]
        folio_val = tree_pend.item(folio)["values"][0] if folio in tree_pend.get_children() else tree_hist.item(folio)["values"][0]

        c.execute("SELECT * FROM traspasos WHERE folio=?", (folio_val,))
        traspaso = c.fetchone()
        if not traspaso:
            return
        tid = traspaso[0]

        c.execute("SELECT codigo_producto, nombre_producto, cantidad FROM detalle_traspasos WHERE traspaso_id=?", (tid,))
        detalles = c.fetchall()

        # Generar texto imprimible
        win = tk.Toplevel(main)
        win.title(f"Orden de Traspaso - {folio_val}")
        win.geometry("600x500")
        win.configure(bg="white")

        txt = tk.Text(win, font=("Courier New", 10), wrap=tk.WORD, bg="white")
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        lineas = []
        lineas.append("=" * 50)
        lineas.append("     FARMACIAS MADRID - ORDEN DE TRASPASO")
        lineas.append("=" * 50)
        lineas.append(f"  Folio:    {traspaso[1]}")
        lineas.append(f"  Fecha:    {traspaso[2]}  Hora: {traspaso[3]}")
        lineas.append(f"  Origen:   {traspaso[4]}")
        lineas.append(f"  Destino:  {traspaso[5]}")
        lineas.append(f"  Motivo:   {traspaso[6]}")
        lineas.append(f"  Estado:   {traspaso[7]}")
        lineas.append("-" * 50)
        lineas.append(f"  {'CÓDIGO':<14} {'PRODUCTO':<24} {'CANT':>6}")
        lineas.append("-" * 50)
        for det in detalles:
            lineas.append(f"  {det[0]:<14} {det[1][:24]:<24} {det[2]:>6}")
        lineas.append("-" * 50)
        lineas.append(f"  Total productos: {len(detalles)}")
        lineas.append("")
        lineas.append("  Firma Origen: __________________")
        lineas.append("")
        lineas.append("  Firma Destino: __________________")
        lineas.append("=" * 50)

        txt.insert("1.0", "\n".join(lineas))
        txt.config(state=tk.DISABLED)

        def imprimir_fisico():
            try:
                import tempfile
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
                tmp.write("\n".join(lineas))
                tmp.close()
                os.startfile(tmp.name, "print")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo imprimir: {e}")

        tk.Button(win, text="IMPRIMIR", command=imprimir_fisico,
                  bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"),
                  relief=tk.FLAT, padx=20, pady=6, cursor="hand2").pack(pady=8)

    # --- DIALOG NUEVO TRASPASO ---
    def dialog_nuevo_traspaso():
        dlg = tk.Toplevel(main)
        dlg.title("Nuevo Traspaso entre Farmacias")
        dlg.geometry("750x600")
        dlg.configure(bg="white")
        dlg.grab_set()

        # Header del dialog
        hdr = tk.Frame(dlg, bg="#4CAF50", height=40)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="\u21C4 NUEVO TRASPASO", font=("Segoe UI", 12, "bold"),
                bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=12, pady=8)

        # Folio automático
        now = datetime.now()
        c.execute("SELECT COUNT(*) FROM traspasos WHERE fecha=?", (now.strftime("%Y-%m-%d"),))
        num_hoy = c.fetchone()[0] + 1
        folio_nuevo = f"TRAS-{now.strftime('%Y%m%d')}-{num_hoy:04d}"

        info = tk.Frame(dlg, bg="white")
        info.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(info, text=f"Folio: {folio_nuevo}", font=("Segoe UI", 11, "bold"),
                bg="white", fg="#4CAF50").pack(side=tk.LEFT, padx=10)
        tk.Label(info, text=f"Fecha: {now.strftime('%Y-%m-%d %H:%M')}",
                font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=20)

        # Sucursales
        suc_frame = tk.Frame(dlg, bg="white")
        suc_frame.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(suc_frame, text="Sucursal Origen:", font=("Segoe UI", 10, "bold"),
                bg="white").pack(side=tk.LEFT, padx=5)
        origen_var = tk.StringVar(value=SUCURSALES[0])
        combo_origen = ttk.Combobox(suc_frame, textvariable=origen_var, width=18,
                                    values=SUCURSALES, state="readonly")
        combo_origen.pack(side=tk.LEFT, padx=5)

        tk.Label(suc_frame, text="\u2192", font=("Segoe UI", 14, "bold"),
                bg="white", fg="#4CAF50").pack(side=tk.LEFT, padx=10)

        tk.Label(suc_frame, text="Sucursal Destino:", font=("Segoe UI", 10, "bold"),
                bg="white").pack(side=tk.LEFT, padx=5)
        destino_var = tk.StringVar(value=SUCURSALES[1])
        combo_destino = ttk.Combobox(suc_frame, textvariable=destino_var, width=18,
                                     values=SUCURSALES, state="readonly")
        combo_destino.pack(side=tk.LEFT, padx=5)

        # Motivo
        motivo_frame = tk.Frame(dlg, bg="white")
        motivo_frame.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(motivo_frame, text="Motivo:", font=("Segoe UI", 10, "bold"),
                bg="white").pack(side=tk.LEFT, padx=5)
        motivo_var = tk.StringVar(value="Desabasto")
        combo_motivo = ttk.Combobox(motivo_frame, textvariable=motivo_var, width=20,
                                    values=["Desabasto", "Exceso", "Caducidad", "Otro"], state="readonly")
        combo_motivo.pack(side=tk.LEFT, padx=5)

        tk.Label(motivo_frame, text="Notas:", font=("Segoe UI", 10, "bold"),
                bg="white").pack(side=tk.LEFT, padx=(20,5))
        notas_entry = tk.Entry(motivo_frame, width=30, font=("Segoe UI", 9))
        notas_entry.pack(side=tk.LEFT, padx=5)

        # Buscar producto
        busq_frame = tk.Frame(dlg, bg="white")
        busq_frame.pack(fill=tk.X, padx=15, pady=8)

        tk.Label(busq_frame, text="Buscar producto:", font=("Segoe UI", 10, "bold"),
                bg="white").pack(side=tk.LEFT, padx=5)
        prod_entry = tk.Entry(busq_frame, width=35, font=("Segoe UI", 9))
        prod_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(busq_frame, text="Cantidad:", font=("Segoe UI", 10, "bold"),
                bg="white").pack(side=tk.LEFT, padx=(15,5))
        cant_entry = tk.Entry(busq_frame, width=8, font=("Segoe UI", 9))
        cant_entry.pack(side=tk.LEFT, padx=5)
        cant_entry.insert(0, "1")

        items_traspaso = []

        def agregar_producto():
            busqueda = prod_entry.get().strip()
            if not busqueda:
                return
            try:
                cantidad = int(cant_entry.get())
            except ValueError:
                messagebox.showwarning("Aviso", "Cantidad debe ser un número entero")
                return
            if cantidad <= 0:
                messagebox.showwarning("Aviso", "Cantidad debe ser mayor a 0")
                return

            # Buscar por código exacto o nombre
            c.execute("SELECT id, codigo, nombre, stock FROM productos WHERE codigo=? OR nombre LIKE ? LIMIT 1",
                      (busqueda.upper(), f"%{busqueda}%"))
            prod = c.fetchone()
            if not prod:
                messagebox.showwarning("Aviso", "Producto no encontrado")
                return

            prod_id, codigo, nombre, stock = prod

            # Validar stock
            if cantidad > stock:
                messagebox.showwarning("Stock insuficiente",
                                       f"Stock disponible: {stock}\nSolicitado: {cantidad}")
                return

            # Verificar duplicado
            for i, item in enumerate(items_traspaso):
                if item[0] == prod_id:
                    nueva_cant = item[3] + cantidad
                    if nueva_cant > stock:
                        messagebox.showwarning("Stock insuficiente",
                                               f"Stock disponible: {stock}\nTotal solicitado: {nueva_cant}")
                        return
                    items_traspaso[i] = (prod_id, codigo, nombre, nueva_cant, stock)
                    actualizar_tabla()
                    prod_entry.delete(0, tk.END)
                    cant_entry.delete(0, tk.END)
                    cant_entry.insert(0, "1")
                    prod_entry.focus()
                    return

            items_traspaso.append((prod_id, codigo, nombre, cantidad, stock))
            actualizar_tabla()
            prod_entry.delete(0, tk.END)
            cant_entry.delete(0, tk.END)
            cant_entry.insert(0, "1")
            prod_entry.focus()

        btn_agregar = tk.Button(busq_frame, text="AGREGAR", command=agregar_producto,
                                bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
                                relief=tk.FLAT, padx=10, pady=2, cursor="hand2")
        btn_agregar.pack(side=tk.LEFT, padx=8)
        hover_bind(btn_agregar, "#1565C0", "#1E88E5")

        prod_entry.bind("<Return>", lambda e: agregar_producto())

        # Tabla de productos del traspaso
        tree_dlg_frame = tk.Frame(dlg, bg="white")
        tree_dlg_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        cols_dlg = ("CÓDIGO", "PRODUCTO", "CANTIDAD", "STOCK DISP.")
        tree_dlg = ttk.Treeview(tree_dlg_frame, columns=cols_dlg, show="headings", height=8)
        for col in cols_dlg:
            tree_dlg.heading(col, text=col)
        tree_dlg.column("CÓDIGO", width=120)
        tree_dlg.column("PRODUCTO", width=350)
        tree_dlg.column("CANTIDAD", width=90)
        tree_dlg.column("STOCK DISP.", width=90)
        scroll_dlg = ttk.Scrollbar(tree_dlg_frame, orient="vertical", command=tree_dlg.yview)
        tree_dlg.configure(yscrollcommand=scroll_dlg.set)
        tree_dlg.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_dlg.pack(side=tk.RIGHT, fill=tk.Y)

        def actualizar_tabla():
            for item in tree_dlg.get_children():
                tree_dlg.delete(item)
            for it in items_traspaso:
                tree_dlg.insert("", "end", values=(it[1], it[2], it[3], it[4]))

        def quitar_producto():
            sel = tree_dlg.selection()
            if not sel:
                return
            idx = tree_dlg.index(sel[0])
            items_traspaso.pop(idx)
            actualizar_tabla()

        # Botones inferiores
        bottom = tk.Frame(dlg, bg="white")
        bottom.pack(fill=tk.X, padx=15, pady=10)

        btn_quitar = tk.Button(bottom, text="QUITAR SELECCIONADO", command=quitar_producto,
                               bg="#D32F2F", fg="white", font=("Segoe UI", 9, "bold"),
                               relief=tk.FLAT, padx=10, pady=4, cursor="hand2")
        btn_quitar.pack(side=tk.LEFT, padx=5)
        hover_bind(btn_quitar, "#D32F2F", "#EF5350")

        def guardar_traspaso():
            if origen_var.get() == destino_var.get():
                messagebox.showwarning("Aviso", "Sucursal origen y destino deben ser diferentes")
                return
            if not items_traspaso:
                messagebox.showwarning("Aviso", "Agrega al menos un producto al traspaso")
                return
            if not messagebox.askyesno("Confirmar", f"¿Crear traspaso {folio_nuevo}?\n"
                                       f"{origen_var.get()} \u2192 {destino_var.get()}\n"
                                       f"{len(items_traspaso)} productos"):
                return

            ahora = datetime.now()
            c.execute("""INSERT INTO traspasos
                        (folio, fecha, hora, sucursal_origen, sucursal_destino, motivo, estado, usuario_solicita, notas)
                        VALUES (?,?,?,?,?,?,?,?,?)""",
                      (folio_nuevo, ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S"),
                       origen_var.get(), destino_var.get(), motivo_var.get(),
                       "PENDIENTE", usuario_id, notas_entry.get()))
            tid = c.lastrowid

            for it in items_traspaso:
                prod_id, codigo, nombre, cantidad, stock = it
                # Restar stock en origen al crear
                c.execute("UPDATE productos SET stock = stock - ? WHERE id=?", (cantidad, prod_id))
                c.execute("""INSERT INTO detalle_traspasos
                            (traspaso_id, producto_id, codigo_producto, nombre_producto, cantidad, stock_origen_antes, stock_destino_antes)
                            VALUES (?,?,?,?,?,?,?)""",
                          (tid, prod_id, codigo, nombre, cantidad, stock, 0))
                c.execute("INSERT INTO inventario_movimientos (fecha,tipo,producto_id,cantidad,usuario_id,notas) VALUES (?,?,?,?,?,?)",
                          (ahora.strftime("%Y-%m-%d %H:%M:%S"), "TRASPASO_SALIDA", prod_id, -cantidad, usuario_id, f"Traspaso {folio_nuevo}"))
            conn.commit()
            dlg.destroy()
            cargar_datos()
            messagebox.showinfo("Éxito", f"Traspaso {folio_nuevo} creado correctamente")

        btn_guardar = tk.Button(bottom, text="GUARDAR TRASPASO", command=guardar_traspaso,
                                bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"),
                                relief=tk.FLAT, padx=20, pady=6, cursor="hand2")
        btn_guardar.pack(side=tk.RIGHT, padx=5)
        hover_bind(btn_guardar, "#4CAF50", "#66BB6A")

        btn_cancelar_dlg = tk.Button(bottom, text="CANCELAR", command=dlg.destroy,
                                     bg="#757575", fg="white", font=("Segoe UI", 9, "bold"),
                                     relief=tk.FLAT, padx=12, pady=4, cursor="hand2")
        btn_cancelar_dlg.pack(side=tk.RIGHT, padx=5)
        hover_bind(btn_cancelar_dlg, "#757575", "#9E9E9E")

    # Cargar datos iniciales
    cargar_datos()

# ===== FUNCIONES TARJETAS SATURNOS =====
def _ensure_tarjetas_dirs():
    """Crea carpetas necesarias para tarjetas."""
    base = os.path.dirname(os.path.abspath(__file__))
    for d in ["tarjetas", "tarjetas/codigos", "tarjetas/pdfs", "tarjetas/temp"]:
        os.makedirs(os.path.join(base, d), exist_ok=True)
    return base

def generar_codigo_tarjeta():
    """Genera código único SAT-YYYYMMDD-XXXXX."""
    ahora = datetime.now().strftime("%Y%m%d")
    c.execute("SELECT COUNT(*) FROM monederos WHERE codigo_tarjeta IS NOT NULL")
    num = c.fetchone()[0] + 1
    while True:
        codigo = f"SAT-{ahora}-{num:05d}"
        c.execute("SELECT id FROM monederos WHERE codigo_tarjeta=?", (codigo,))
        if not c.fetchone():
            return codigo
        num += 1

def generar_codigo_barras_img(codigo):
    """Genera imagen de código de barras Code128 GRANDE Y PROFESIONAL."""
    base = _ensure_tarjetas_dirs()
    os.makedirs(os.path.join(base, "tarjetas", "codigos"), exist_ok=True)
    ruta = os.path.join(base, "tarjetas", "codigos", f"{codigo}")
    try:
        import barcode
        from barcode.writer import ImageWriter
        # Configurar opciones para barras más gruesas
        options = {
            'module_width': 0.4,  # Barras más gruesas
            'module_height': 20,  # Barras más altas
            'quiet_zone': 2,
            'font_size': 14,
            'text_distance': 5,
            'write_text': False,  # Sin texto (lo ponemos nosotros)
        }
        code = barcode.get('code128', codigo, writer=ImageWriter())
        ruta_final = code.save(ruta, options=options)
        return ruta_final
    except ImportError:
        # Fallback: generar código de barras GRANDE con PIL
        img = Image.new('RGB', (500, 150), 'white')
        draw = ImageDraw.Draw(img)
        # Barras más gruesas basadas en el código
        x = 20
        bar_height = 120
        for i, ch in enumerate(codigo):
            w = (ord(ch) % 4) + 2  # Barras más gruesas (2-5 pixeles)
            if i % 2 == 0:
                draw.rectangle([x, 10, x + w, bar_height], fill='black')
            x += w + 2
        # Rellenar el resto con patrón
        while x < 480:
            w = ((x * 7) % 4) + 2
            if (x // 10) % 2 == 0:
                draw.rectangle([x, 10, x + w, bar_height], fill='black')
            x += w + 2
        ruta_png = ruta + ".png"
        img.save(ruta_png)
        return ruta_png

def generar_tarjeta_imagen(cliente_id, codigo_tarjeta, nivel="AZUL"):
    """Genera tarjeta Saturnos estilo premium vertical.
    nivel: AZUL, DORADA o NEGRA"""
    base = _ensure_tarjetas_dirs()
    for d in ["tarjetas/azul", "tarjetas/dorada", "tarjetas/negra", "tarjetas/fotos"]:
        os.makedirs(os.path.join(base, d), exist_ok=True)

    c.execute("SELECT nombre, telefono, email, direccion_completa, direccion, colonia FROM clientes WHERE id=?", (cliente_id,))
    cl = c.fetchone()
    if not cl:
        return None, None
    nombre = cl[0]
    telefono = cl[1] or ""
    email = cl[2] or ""
    direccion = cl[3] or cl[4] or ""
    colonia = cl[5] or ""

    c.execute("SELECT saldo_saturnos, fecha_alta FROM monederos WHERE cliente_id=?", (cliente_id,))
    mon = c.fetchone()
    saldo = mon[0] if mon else 0
    fecha_alta = mon[1] if mon else datetime.now().strftime("%Y-%m-%d")

    c.execute("SELECT porcentaje_generico, porcentaje_patente, tasa_conversion FROM configuracion_saturnos WHERE id=1")
    cfg = c.fetchone()
    pct_gen = cfg[0] if cfg else 10
    pct_pat = cfg[1] if cfg else 8

    # Colores por nivel - FRENTE VERTICAL, REVERSO HORIZONTAL
    NIVELES = {
        "AZUL":   {"bg1": "#1E88E5", "bg2": "#1565C0", "text": "white", "accent": "#90CAF9", "badge": "#0D47A1", "icon_border": "#64B5F6"},
        "DORADA": {"bg1": "#FFF8E7", "bg2": "#F5E6C8", "text": "#5D4037", "accent": "#D4A00A", "badge": "#D4A00A", "icon_border": "#FFD700"},
        "NEGRA":  {"bg1": "#1A1A1A", "bg2": "#0D0D0D", "text": "white", "accent": "#FFD700", "badge": "#2D2D2D", "icon_border": "#D4AF37"},
    }
    nv = NIVELES.get(nivel, NIVELES["AZUL"])

    # Fuentes PREMIUM - Elegantes y legibles
    try:
        # Título principal - Grande y elegante
        font_titulo = ImageFont.truetype("georgia.ttf", 30)
        # Subtítulos - MÁS GRANDE y Bold
        font_subtitulo = ImageFont.truetype("segoeuib.ttf", 20)
        # Texto pequeño - MÁS GRANDE para mejor legibilidad
        font_small = ImageFont.truetype("segoeuib.ttf", 15)
        # Código - Monospace elegante
        font_codigo = ImageFont.truetype("consolab.ttf", 14)
        # Badge - Bold compacto
        font_badge = ImageFont.truetype("segoeuib.ttf", 12)
        # Nombre del cliente - Grande y destacado
        font_nombre = ImageFont.truetype("georgia.ttf", 26)
        # Fuente extra para beneficios
        font_beneficios = ImageFont.truetype("segoeuil.ttf", 12)
        # FIRMA ELEGANTE - Para tarjeta negra (Script/Cursiva)
        font_firma_inicial = ImageFont.truetype("georgiab.ttf", 42)  # Inicial grande
        font_firma_resto = ImageFont.truetype("georgiai.ttf", 24)   # Resto en itálica
    except:
        try:
            font_titulo = ImageFont.truetype("arial.ttf", 30)
            font_subtitulo = ImageFont.truetype("arialbd.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 13)
            font_codigo = ImageFont.truetype("cour.ttf", 14)
            font_badge = ImageFont.truetype("arialbd.ttf", 12)
            font_nombre = ImageFont.truetype("arial.ttf", 26)
            font_beneficios = ImageFont.truetype("arial.ttf", 12)
            font_firma_inicial = ImageFont.truetype("arialbd.ttf", 42)
            font_firma_resto = ImageFont.truetype("ariali.ttf", 24)
        except:
            font_titulo = font_subtitulo = font_small = font_codigo = font_badge = font_nombre = font_beneficios = ImageFont.load_default()
            font_firma_inicial = font_firma_resto = ImageFont.load_default()

    # ========== FRENTE VERTICAL (diseño premium por nivel) ==========
    W_f, H_f = 380, 560
    import math

    frontal = Image.new('RGB', (W_f, H_f), nv["bg1"])
    draw = ImageDraw.Draw(frontal)

    # Degradado vertical suave base
    for y in range(H_f):
        factor = y / H_f * 0.3
        r1, g1, b1 = ImageColor.getrgb(nv["bg1"])
        r2, g2, b2 = ImageColor.getrgb(nv["bg2"])
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        draw.line([(0, y), (W_f, y)], fill=(r, g, b))

    # ===== DISEÑO PREMIUM TARJETA NEGRA - Elegante con detalles dorados =====
    if nivel == "NEGRA":
        # Curva superior derecha con brillo DORADO
        for i in range(4):
            offset = i * 6
            for t in range(120):
                angle = t / 120 * math.pi / 2
                x = W_f - 10 + offset + int(200 * math.cos(angle))
                y = -100 + offset + int(220 * math.sin(angle))
                if 0 <= x < W_f and 0 <= y < H_f:
                    intensity = max(0, 1 - t / 120 - i * 0.2)
                    px = frontal.getpixel((x, y))
                    # Color dorado (255, 215, 0) mezclado
                    r = min(255, px[0] + int(200 * intensity))
                    g = min(255, px[1] + int(170 * intensity))
                    b = min(255, px[2] + int(50 * intensity))
                    frontal.putpixel((x, y), (r, g, b))

        # Línea curva dorada brillante superior (más gruesa y definida)
        for t in range(180):
            angle = t / 180 * math.pi / 2.2
            x = W_f + 50 - int(280 * math.cos(angle))
            y = -70 + int(200 * math.sin(angle))
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W_f and 0 <= ny < H_f:
                        dist = abs(dx) + abs(dy)
                        intensity = max(0, (1 - dist / 6) * (1 - t / 200))
                        px = frontal.getpixel((nx, ny))
                        # Dorado brillante
                        r = min(255, px[0] + int(255 * intensity))
                        g = min(255, px[1] + int(200 * intensity))
                        b = min(255, px[2] + int(80 * intensity))
                        frontal.putpixel((nx, ny), (r, g, b))

        # Curva inferior izquierda dorada
        for t in range(150):
            angle = t / 150 * math.pi / 2.2
            x = -80 + int(220 * math.cos(angle))
            y = H_f + 50 - int(200 * math.sin(angle))
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W_f and 0 <= ny < H_f:
                        dist = abs(dx) + abs(dy)
                        intensity = max(0, (1 - dist / 6) * (1 - t / 180))
                        px = frontal.getpixel((nx, ny))
                        r = min(255, px[0] + int(255 * intensity))
                        g = min(255, px[1] + int(190 * intensity))
                        b = min(255, px[2] + int(70 * intensity))
                        frontal.putpixel((nx, ny), (r, g, b))

        # Marco dorado sutil interior
        draw = ImageDraw.Draw(frontal)
        draw.rounded_rectangle([12, 12, W_f - 13, H_f - 13], radius=15, outline="#B8860B", width=1)

        # Detalles dorados en esquinas
        # Esquina superior izquierda
        draw.arc([8, 8, 45, 45], 180, 270, fill="#FFD700", width=2)
        # Esquina superior derecha
        draw.arc([W_f - 45, 8, W_f - 8, 45], 270, 360, fill="#FFD700", width=2)
        # Esquina inferior izquierda
        draw.arc([8, H_f - 45, 45, H_f - 8], 90, 180, fill="#FFD700", width=2)
        # Esquina inferior derecha
        draw.arc([W_f - 45, H_f - 45, W_f - 8, H_f - 8], 0, 90, fill="#FFD700", width=2)

    # ===== DISEÑO SUPER PREMIUM TARJETA AZUL =====
    elif nivel == "AZUL":
        # Curva superior derecha brillante (estilo igual que NEGRA pero en tonos claros)
        for i in range(4):
            offset = i * 6
            for t in range(140):
                angle = t / 140 * math.pi / 2
                x = W_f - 5 + offset + int(220 * math.cos(angle))
                y = -120 + offset + int(240 * math.sin(angle))
                if 0 <= x < W_f and 0 <= y < H_f:
                    intensity = max(0, 1 - t / 140 - i * 0.18)
                    px = frontal.getpixel((x, y))
                    r = min(255, px[0] + int(100 * intensity))
                    g = min(255, px[1] + int(150 * intensity))
                    b = min(255, px[2] + int(180 * intensity))
                    frontal.putpixel((x, y), (r, g, b))

        # Línea curva brillante superior
        for t in range(200):
            angle = t / 200 * math.pi / 2
            x = W_f + 60 - int(320 * math.cos(angle))
            y = -90 + int(230 * math.sin(angle))
            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W_f and 0 <= ny < H_f:
                        dist = abs(dx) + abs(dy)
                        intensity = max(0, (1 - dist / 8) * (1 - t / 220))
                        px = frontal.getpixel((nx, ny))
                        r = min(255, px[0] + int(120 * intensity))
                        g = min(255, px[1] + int(180 * intensity))
                        b = min(255, px[2] + int(220 * intensity))
                        frontal.putpixel((nx, ny), (r, g, b))

        # Curva inferior izquierda
        for t in range(180):
            angle = t / 180 * math.pi / 2
            x = -100 + int(280 * math.cos(angle))
            y = H_f + 70 - int(240 * math.sin(angle))
            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W_f and 0 <= ny < H_f:
                        dist = abs(dx) + abs(dy)
                        intensity = max(0, (1 - dist / 8) * (1 - t / 200))
                        px = frontal.getpixel((nx, ny))
                        r = min(255, px[0] + int(100 * intensity))
                        g = min(255, px[1] + int(160 * intensity))
                        b = min(255, px[2] + int(200 * intensity))
                        frontal.putpixel((nx, ny), (r, g, b))

        draw = ImageDraw.Draw(frontal)

        # Marco interior elegante
        draw.rounded_rectangle([10, 10, W_f - 11, H_f - 11], radius=16, outline="#64B5F6", width=1)

        # Arcos en esquinas
        draw.arc([6, 6, 50, 50], 180, 270, fill="#00BCD4", width=3)
        draw.arc([W_f - 50, 6, W_f - 6, 50], 270, 360, fill="#00BCD4", width=3)
        draw.arc([6, H_f - 50, 50, H_f - 6], 90, 180, fill="#00BCD4", width=3)
        draw.arc([W_f - 50, H_f - 50, W_f - 6, H_f - 6], 0, 90, fill="#00BCD4", width=3)

    # ===== DISEÑO PREMIUM TARJETA DORADA - Curvas doradas elegantes =====
    elif nivel == "DORADA":
        # Fondo crema/beige elegante
        for y in range(H_f):
            for x in range(W_f):
                factor = (x + y) / (W_f + H_f) * 0.15
                r = int(255 - factor * 15)
                g = int(250 - factor * 20)
                b = int(240 - factor * 30)
                frontal.putpixel((x, y), (r, g, b))

        # Curva superior derecha con brillo DORADO
        for i in range(4):
            offset = i * 6
            for t in range(120):
                angle = t / 120 * math.pi / 2
                x = W_f - 10 + offset + int(200 * math.cos(angle))
                y = -100 + offset + int(220 * math.sin(angle))
                if 0 <= x < W_f and 0 <= y < H_f:
                    intensity = max(0, 1 - t / 120 - i * 0.2)
                    px = frontal.getpixel((x, y))
                    r = min(255, px[0] + int(60 * intensity))
                    g = min(255, px[1] + int(40 * intensity))
                    b = max(0, px[2] - int(30 * intensity))
                    frontal.putpixel((x, y), (r, g, b))

        # Línea curva dorada brillante superior
        for t in range(180):
            angle = t / 180 * math.pi / 2.2
            x = W_f + 50 - int(280 * math.cos(angle))
            y = -70 + int(200 * math.sin(angle))
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W_f and 0 <= ny < H_f:
                        dist = abs(dx) + abs(dy)
                        intensity = max(0, (1 - dist / 6) * (1 - t / 200))
                        px = frontal.getpixel((nx, ny))
                        r = min(255, px[0] + int(180 * intensity))
                        g = min(255, px[1] + int(140 * intensity))
                        b = min(255, px[2] + int(50 * intensity))
                        frontal.putpixel((nx, ny), (r, g, b))

        # Curva inferior izquierda dorada
        for t in range(150):
            angle = t / 150 * math.pi / 2.2
            x = -80 + int(220 * math.cos(angle))
            y = H_f + 50 - int(200 * math.sin(angle))
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W_f and 0 <= ny < H_f:
                        dist = abs(dx) + abs(dy)
                        intensity = max(0, (1 - dist / 6) * (1 - t / 180))
                        px = frontal.getpixel((nx, ny))
                        r = min(255, px[0] + int(180 * intensity))
                        g = min(255, px[1] + int(130 * intensity))
                        b = min(255, px[2] + int(40 * intensity))
                        frontal.putpixel((nx, ny), (r, g, b))

        # Marco dorado interior
        draw = ImageDraw.Draw(frontal)
        draw.rounded_rectangle([12, 12, W_f - 13, H_f - 13], radius=15, outline="#D4A00A", width=1)

        # Detalles dorados en esquinas
        draw.arc([8, 8, 45, 45], 180, 270, fill="#FFD700", width=2)
        draw.arc([W_f - 45, 8, W_f - 8, 45], 270, 360, fill="#FFD700", width=2)
        draw.arc([8, H_f - 45, 45, H_f - 8], 90, 180, fill="#FFD700", width=2)
        draw.arc([W_f - 45, H_f - 45, W_f - 8, H_f - 8], 0, 90, fill="#FFD700", width=2)

    # BADGE WhatsApp (arriba derecha) - Muestra el teléfono del cliente
    whats_text = telefono if telefono else "Sin WhatsApp"
    badge_w = max(120, len(whats_text) * 8 + 20)
    badge_h = 28
    badge_x = W_f - badge_w - 12
    # Sombra del badge
    draw.rounded_rectangle([badge_x + 2, 14, badge_x + badge_w + 2, 14 + badge_h], radius=14, fill="#00000033")
    # Para AZUL: fondo blanco, para otros: color del nivel
    badge_bg = "white" if nivel == "AZUL" else nv["badge"]
    badge_text_color = "#1E88E5" if nivel == "AZUL" else ("white" if nivel != "DORADA" else "#5D4037")
    draw.rounded_rectangle([badge_x, 12, badge_x + badge_w, 12 + badge_h], radius=14, fill=badge_bg)
    draw.text((badge_x + badge_w//2, 12 + badge_h//2), f"📱 {whats_text}", fill=badge_text_color, font=font_badge, anchor='mm')

    # LOGO CENTRADO (cuadrado redondeado con DOBLE borde premium)
    icon_size = 150
    icon_x = (W_f - icon_size) // 2
    icon_y = 70

    # Sombra del logo
    draw.rounded_rectangle([icon_x - 2, icon_y + 4, icon_x + icon_size + 2, icon_y + icon_size + 8],
                          radius=28, fill="#00000022")
    # Borde exterior brillante
    draw.rounded_rectangle([icon_x - 6, icon_y - 6, icon_x + icon_size + 6, icon_y + icon_size + 6],
                          radius=28, fill=nv["icon_border"])
    # Fondo blanco del ícono con borde de color
    draw.rounded_rectangle([icon_x - 4, icon_y - 4, icon_x + icon_size + 4, icon_y + icon_size + 4],
                          radius=25, fill=nv["icon_border"])
    draw.rounded_rectangle([icon_x, icon_y, icon_x + icon_size, icon_y + icon_size],
                          radius=22, fill="white")

    # Logo dentro (sin fondo blanco)
    try:
        logo_path = os.path.join(base, "logo.png")
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            # Eliminar fondo blanco del logo
            datas = logo.getdata()
            new_data = []
            for item in datas:
                # Si el pixel es blanco o casi blanco, hacerlo transparente
                if item[0] > 230 and item[1] > 230 and item[2] > 230:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            logo.putdata(new_data)
            logo = logo.resize((icon_size - 20, icon_size - 20), Image.Resampling.LANCZOS)
            temp = Image.new('RGBA', (W_f, H_f), (0, 0, 0, 0))
            temp.paste(logo, (icon_x + 10, icon_y + 10), logo)
            frontal = Image.alpha_composite(frontal.convert('RGBA'), temp).convert('RGB')
            draw = ImageDraw.Draw(frontal)
    except:
        pass

    # "FARMACIAS MADRID" - TÍTULO ELEGANTE GEORGIA
    # Sombra suave para profundidad
    if nivel == "NEGRA" or nivel == "AZUL":
        draw.text((W_f // 2 + 2, 267), "FARMACIAS MADRID", fill="#00000055", font=font_titulo, anchor='mm')
    elif nivel == "DORADA":
        draw.text((W_f // 2 + 1, 266), "FARMACIAS MADRID", fill="#C4960888", font=font_titulo, anchor='mm')
    draw.text((W_f // 2, 265), "FARMACIAS MADRID", fill=nv["text"], font=font_titulo, anchor='mm')

    # Línea decorativa elegante doble
    line_w = 220
    draw.line([(W_f//2 - line_w//2, 300), (W_f//2 + line_w//2, 300)], fill=nv["accent"], width=2)
    draw.line([(W_f//2 - line_w//2 + 30, 307), (W_f//2 + line_w//2 - 30, 307)], fill=nv["accent"], width=1)

    # "MONEDERO SATURNOS ₴" - Subtítulo elegante
    if nivel == "NEGRA" or nivel == "AZUL":
        draw.text((W_f // 2 + 1, 341), "MONEDERO SATURNOS \u20B4", fill="#00000033", font=font_subtitulo, anchor='mm')
    draw.text((W_f // 2, 340), "MONEDERO SATURNOS \u20B4", fill=nv["text"], font=font_subtitulo, anchor='mm')

    # "BENEFICIOS • DESCUENTOS • RECOMPENSAS" - Texto limpio
    draw.text((W_f // 2, 380), "BENEFICIOS  •  DESCUENTOS  •  RECOMPENSAS", fill=nv["accent"], font=font_small, anchor='mm')

    # Línea inferior elegante doble
    draw.line([(W_f//2 - line_w//2 + 30, 412), (W_f//2 + line_w//2 - 30, 412)], fill=nv["accent"], width=1)
    draw.line([(W_f//2 - line_w//2, 418), (W_f//2 + line_w//2, 418)], fill=nv["accent"], width=2)

    # Nombre del cliente - ELEGANTE Y DESTACADO
    # Nombre del cliente - ESTILO FIRMA para NEGRA, normal para otras
    if nivel == "NEGRA" and len(nombre) > 0:
        # Estilo FIRMA elegante: Primera letra GRANDE, resto en itálica
        nombre_formato = nombre.title()[:22]  # Primera mayúscula de cada palabra
        inicial = nombre_formato[0]
        resto = nombre_formato[1:] if len(nombre_formato) > 1 else ""

        # Calcular posición centrada
        bbox_inicial = draw.textbbox((0, 0), inicial, font=font_firma_inicial)
        bbox_resto = draw.textbbox((0, 0), resto, font=font_firma_resto)
        ancho_inicial = bbox_inicial[2] - bbox_inicial[0]
        ancho_resto = bbox_resto[2] - bbox_resto[0]
        ancho_total = ancho_inicial + ancho_resto - 5

        x_inicio = W_f // 2 - ancho_total // 2

        # Sombra dorada sutil
        draw.text((x_inicio + 2, 452), inicial, fill="#D4AF3744", font=font_firma_inicial, anchor='lm')
        # Inicial grande dorada
        draw.text((x_inicio, 450), inicial, fill="#FFD700", font=font_firma_inicial, anchor='lm')
        # Resto del nombre en blanco itálica
        draw.text((x_inicio + ancho_inicial - 5, 458), resto, fill="white", font=font_firma_resto, anchor='lm')
    else:
        # Estilo normal para AZUL y DORADA - Title Case (menos formal)
        nombre_display = nombre.title()[:22]
        if nivel == "AZUL":
            draw.text((W_f // 2 + 2, 462), nombre_display, fill="#00000044", font=font_nombre, anchor='mm')
        draw.text((W_f // 2, 460), nombre_display, fill=nv["text"], font=font_nombre, anchor='mm')

    # Código de tarjeta (abajo) - FONDO BLANCO elegante
    code_y = H_f - 45
    draw.rounded_rectangle([W_f//2 - 105, code_y - 14, W_f//2 + 105, code_y + 16], radius=12, fill="white")
    draw.text((W_f // 2, code_y), codigo_tarjeta, fill="#1A1A1A", font=font_codigo, anchor='mm')

    # Borde elegante DOBLE
    border_color = nv["icon_border"]
    draw.rounded_rectangle([3, 3, W_f-4, H_f-4], radius=20, outline=border_color, width=4)
    draw.rounded_rectangle([8, 8, W_f-9, H_f-9], radius=17, outline="#FFFFFF33", width=1)

    # ========== REVERSO HORIZONTAL - DISEÑO PREMIUM ==========
    W_r, H_r = 700, 440

    # Color de fondo según nivel
    if nivel == "NEGRA":
        bg_r1, bg_r2 = (26, 26, 26), (13, 13, 13)
        text_color = "white"
        accent_r = "#FFD700"
    elif nivel == "DORADA":
        bg_r1, bg_r2 = (255, 250, 240), (245, 235, 220)
        text_color = "#3D2914"
        accent_r = "#D4A00A"
    else:  # AZUL
        bg_r1, bg_r2 = (30, 136, 229), (21, 101, 192)
        text_color = "white"
        accent_r = "#90CAF9"

    reverso = Image.new('RGB', (W_r, H_r), bg_r1)
    draw_r = ImageDraw.Draw(reverso)

    # Degradado de fondo
    for y in range(H_r):
        factor = y / H_r * 0.3
        r = int(bg_r1[0] + (bg_r2[0] - bg_r1[0]) * factor)
        g = int(bg_r1[1] + (bg_r2[1] - bg_r1[1]) * factor)
        b = int(bg_r1[2] + (bg_r2[2] - bg_r1[2]) * factor)
        draw_r.line([(0, y), (W_r, y)], fill=(r, g, b))

    # ===== CURVAS ELEGANTES SEGÚN NIVEL =====
    if nivel == "NEGRA":
        # Curvas doradas superior derecha
        for t in range(200):
            angle = t / 200 * math.pi / 2
            x = W_r + 20 - int(300 * math.cos(angle))
            y = -80 + int(220 * math.sin(angle))
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W_r and 0 <= ny < H_r:
                        dist = abs(dx) + abs(dy)
                        intensity = max(0, (1 - dist / 6) * (1 - t / 220))
                        px = reverso.getpixel((nx, ny))
                        r = min(255, px[0] + int(200 * intensity))
                        g = min(255, px[1] + int(160 * intensity))
                        b = min(255, px[2] + int(50 * intensity))
                        reverso.putpixel((nx, ny), (r, g, b))
        # Curva inferior izquierda
        for t in range(180):
            angle = t / 180 * math.pi / 2
            x = -60 + int(250 * math.cos(angle))
            y = H_r + 40 - int(200 * math.sin(angle))
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W_r and 0 <= ny < H_r:
                        dist = abs(dx) + abs(dy)
                        intensity = max(0, (1 - dist / 6) * (1 - t / 200))
                        px = reverso.getpixel((nx, ny))
                        r = min(255, px[0] + int(180 * intensity))
                        g = min(255, px[1] + int(140 * intensity))
                        b = min(255, px[2] + int(40 * intensity))
                        reverso.putpixel((nx, ny), (r, g, b))

    elif nivel == "DORADA":
        # Curvas doradas
        for t in range(200):
            angle = t / 200 * math.pi / 2
            x = W_r + 20 - int(300 * math.cos(angle))
            y = -80 + int(220 * math.sin(angle))
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W_r and 0 <= ny < H_r:
                        dist = abs(dx) + abs(dy)
                        intensity = max(0, (1 - dist / 6) * (1 - t / 220))
                        px = reverso.getpixel((nx, ny))
                        r = min(255, int(px[0] * (1 - intensity * 0.1)))
                        g = min(255, int(px[1] * (1 - intensity * 0.15)))
                        b = max(0, int(px[2] - intensity * 100))
                        reverso.putpixel((nx, ny), (r, g, b))
        for t in range(180):
            angle = t / 180 * math.pi / 2
            x = -60 + int(250 * math.cos(angle))
            y = H_r + 40 - int(200 * math.sin(angle))
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W_r and 0 <= ny < H_r:
                        dist = abs(dx) + abs(dy)
                        intensity = max(0, (1 - dist / 6) * (1 - t / 200))
                        px = reverso.getpixel((nx, ny))
                        r = min(255, int(px[0] * (1 - intensity * 0.1)))
                        g = min(255, int(px[1] * (1 - intensity * 0.15)))
                        b = max(0, int(px[2] - intensity * 80))
                        reverso.putpixel((nx, ny), (r, g, b))

    else:  # AZUL
        # Curvas claras/turquesa
        for t in range(200):
            angle = t / 200 * math.pi / 2
            x = W_r + 20 - int(300 * math.cos(angle))
            y = -80 + int(220 * math.sin(angle))
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W_r and 0 <= ny < H_r:
                        dist = abs(dx) + abs(dy)
                        intensity = max(0, (1 - dist / 6) * (1 - t / 220))
                        px = reverso.getpixel((nx, ny))
                        r = min(255, px[0] + int(80 * intensity))
                        g = min(255, px[1] + int(100 * intensity))
                        b = min(255, px[2] + int(120 * intensity))
                        reverso.putpixel((nx, ny), (r, g, b))
        for t in range(180):
            angle = t / 180 * math.pi / 2
            x = -60 + int(250 * math.cos(angle))
            y = H_r + 40 - int(200 * math.sin(angle))
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W_r and 0 <= ny < H_r:
                        dist = abs(dx) + abs(dy)
                        intensity = max(0, (1 - dist / 6) * (1 - t / 200))
                        px = reverso.getpixel((nx, ny))
                        r = min(255, px[0] + int(60 * intensity))
                        g = min(255, px[1] + int(90 * intensity))
                        b = min(255, px[2] + int(100 * intensity))
                        reverso.putpixel((nx, ny), (r, g, b))

    draw_r = ImageDraw.Draw(reverso)

    # MARCO FOTO (izquierda) - más elegante
    foto_w, foto_h = 160, 240
    foto_x, foto_y = 40, (H_r - foto_h) // 2
    # Marco con doble borde
    draw_r.rounded_rectangle([foto_x - 6, foto_y - 6, foto_x + foto_w + 6, foto_y + foto_h + 6],
                            radius=18, fill=nv["icon_border"])
    draw_r.rounded_rectangle([foto_x - 2, foto_y - 2, foto_x + foto_w + 2, foto_y + foto_h + 2],
                            radius=15, fill="#1A1A1A" if nivel != "DORADA" else "#F5E6C8")
    draw_r.rounded_rectangle([foto_x, foto_y, foto_x + foto_w, foto_y + foto_h],
                            radius=12, fill="#2D2D2D" if nivel != "DORADA" else "#FFFFFF")

    # Foto del cliente
    try:
        foto_path = os.path.join(base, "tarjetas", "fotos", f"cliente_{cliente_id}.png")
        if os.path.exists(foto_path):
            foto = Image.open(foto_path).convert("RGB")
            foto = foto.resize((foto_w - 8, foto_h - 8), Image.Resampling.LANCZOS)
            reverso.paste(foto, (foto_x + 4, foto_y + 4))
            draw_r = ImageDraw.Draw(reverso)
        else:
            # Inicial del nombre
            draw_r.text((foto_x + foto_w//2, foto_y + foto_h//2), nombre[0].upper() if nombre else "?",
                       fill=nv["icon_border"], font=font_titulo, anchor='mm')
    except:
        draw_r.text((foto_x + foto_w//2, foto_y + foto_h//2), nombre[0].upper() if nombre else "?",
                   fill=nv["icon_border"], font=font_titulo, anchor='mm')

    # SECCIÓN DERECHA - Información
    rx = 240

    # Logo COMPLETO con fondo blanco (como en el frente)
    logo_size = 80
    logo_rx = W_r - logo_size - 25
    logo_ry = 20

    # Fondo blanco con borde para el logo
    draw_r.rounded_rectangle([logo_rx - 5, logo_ry - 5, logo_rx + logo_size + 5, logo_ry + logo_size + 5],
                            radius=15, fill=nv["icon_border"])
    draw_r.rounded_rectangle([logo_rx - 2, logo_ry - 2, logo_rx + logo_size + 2, logo_ry + logo_size + 2],
                            radius=12, fill="white")

    try:
        logo_path = os.path.join(base, "logo.png")
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            # NO quitar fondo blanco, mostrar logo completo
            logo = logo.resize((logo_size - 6, logo_size - 6), Image.Resampling.LANCZOS)
            temp = Image.new('RGBA', (W_r, H_r), (0, 0, 0, 0))
            temp.paste(logo, (logo_rx + 3, logo_ry + 3), logo)
            reverso = Image.alpha_composite(reverso.convert('RGBA'), temp).convert('RGB')
            draw_r = ImageDraw.Draw(reverso)
    except:
        pass

    # ========== NUEVO DISEÑO REVERSO - LIMPIO Y PROFESIONAL ==========

    # Centro de información (a la derecha de la foto)
    info_x = foto_x + foto_w + 30
    info_color = text_color if nivel != "DORADA" else "#5D4037"

    # Título "FARMACIAS MADRID" - Grande y elegante
    if nivel == "NEGRA" or nivel == "AZUL":
        draw_r.text((info_x + 150, 35), "FARMACIAS MADRID", fill="#00000055", font=font_titulo, anchor='mm')
    draw_r.text((info_x + 148, 33), "FARMACIAS MADRID", fill=text_color, font=font_titulo, anchor='mm')

    # Línea decorativa
    draw_r.line([(info_x + 20, 60), (info_x + 280, 60)], fill=accent_r, width=3)

    # NOMBRE DEL CLIENTE - Grande y destacado
    nombre_display = nombre.title()[:25] if nombre else "Cliente"
    draw_r.text((info_x + 150, 95), nombre_display, fill=text_color, font=font_nombre, anchor='mm')

    # Línea bajo el nombre
    draw_r.line([(info_x + 50, 120), (info_x + 250, 120)], fill=accent_r, width=1)

    # Información CENTRADA - Una sola columna limpia
    draw_r.text((info_x + 150, 145), "TARJETA SATURNOS", fill=accent_r, font=font_subtitulo, anchor='mm')
    draw_r.text((info_x + 150, 175), f"Miembro desde: {fecha_alta}", fill=info_color, font=font_small, anchor='mm')
    draw_r.text((info_x + 150, 200), f"Acumula: {pct_gen}% Genéricos | {pct_pat}% Patente", fill=info_color, font=font_small, anchor='mm')
    draw_r.text((info_x + 150, 225), "Tel: 775-320-0224", fill=accent_r, font=font_small, anchor='mm')

    # NIVEL badge (junto al logo)
    badge_w, badge_h = 90, 28
    badge_x = W_r - badge_w - 25
    badge_y = logo_ry + logo_size + 15
    draw_r.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=14, fill=nv["badge"])
    badge_txt_color = "white" if nivel != "DORADA" else "#5D4037"
    draw_r.text((badge_x + badge_w//2, badge_y + badge_h//2), f"NIVEL {nivel}", fill=badge_txt_color, font=font_badge, anchor='mm')

    # ========== CÓDIGO DE BARRAS - COMPACTO Y DELGADO ==========
    bc_width = 280  # Más chico
    bc_height = 40  # Más delgado
    bc_x = (W_r - bc_width) // 2 + 60  # Centrado
    bc_y = H_r - bc_height - 35

    # Fondo blanco compacto
    draw_r.rounded_rectangle([bc_x - 4, bc_y - 3, bc_x + bc_width + 4, bc_y + bc_height + 20],
                            radius=5, fill="white")

    try:
        barcode_path = generar_codigo_barras_img(codigo_tarjeta)
        if barcode_path and os.path.exists(barcode_path):
            bc_img = Image.open(barcode_path)
            bc_img = bc_img.resize((bc_width, bc_height), Image.Resampling.LANCZOS)
            reverso.paste(bc_img, (bc_x, bc_y))
            draw_r = ImageDraw.Draw(reverso)
    except:
        pass

    # Código texto debajo
    draw_r.text((bc_x + bc_width // 2, bc_y + bc_height + 10), codigo_tarjeta, fill="#1A1A1A", font=font_small, anchor='mm')

    # Borde elegante
    draw_r.rounded_rectangle([4, 4, W_r-5, H_r-5], radius=18, outline=nv["icon_border"], width=3)

    # Arcos decorativos en esquinas
    draw_r.arc([8, 8, 40, 40], 180, 270, fill=accent_r, width=2)
    draw_r.arc([W_r - 40, 8, W_r - 8, 40], 270, 360, fill=accent_r, width=2)
    draw_r.arc([8, H_r - 40, 40, H_r - 8], 90, 180, fill=accent_r, width=2)
    draw_r.arc([W_r - 40, H_r - 40, W_r - 8, H_r - 8], 0, 90, fill=accent_r, width=2)

    # Guardar en carpeta del nivel
    nivel_lower = nivel.lower()
    ruta_frontal = os.path.join(base, "tarjetas", nivel_lower, f"{codigo_tarjeta}_frontal.png")
    ruta_reverso = os.path.join(base, "tarjetas", nivel_lower, f"{codigo_tarjeta}_reverso.png")
    frontal.save(ruta_frontal, "PNG")
    reverso.save(ruta_reverso, "PNG")

    return ruta_frontal, ruta_reverso

# ===== MÓDULO MONEDERO ELECTRÓNICO SATURNOS =====
def ver_saturnos():
    limpiar()

    header_mod = tk.Frame(main, bg="#FFC107", height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="\u20B4 MONEDERO ELECTRÓNICO SATURNOS", font=("Segoe UI", 13, "bold"),
            bg="#FFC107", fg="#333").pack(side=tk.LEFT, padx=12, pady=10)

    notebook = ttk.Notebook(main)
    notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # ==================== PESTAÑA MONEDEROS ====================
    tab_mon = tk.Frame(notebook, bg="white")
    notebook.add(tab_mon, text="  Monederos  ")

    # Buscar cliente
    busq_frame = tk.Frame(tab_mon, bg="white")
    busq_frame.pack(fill=tk.X, padx=10, pady=8)
    tk.Label(busq_frame, text="Buscar cliente:", font=("Segoe UI", 10, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    busq_entry = tk.Entry(busq_frame, width=30, font=("Segoe UI", 9))
    busq_entry.pack(side=tk.LEFT, padx=5)

    # Info del cliente seleccionado
    info_sat = tk.Frame(tab_mon, bg="#FFF8E1", relief=tk.RIDGE, bd=1)
    info_sat.pack(fill=tk.X, padx=10, pady=5)
    lbl_saldo = tk.Label(info_sat, text="\u20B4 Saldo: 0", font=("Segoe UI", 18, "bold"), bg="#FFF8E1", fg="#F57F17")
    lbl_saldo.pack(side=tk.LEFT, padx=20, pady=10)
    lbl_acum = tk.Label(info_sat, text="Acumulado: 0", font=("Segoe UI", 10), bg="#FFF8E1", fg="#555")
    lbl_acum.pack(side=tk.LEFT, padx=15)
    lbl_gast = tk.Label(info_sat, text="Gastado: 0", font=("Segoe UI", 10), bg="#FFF8E1", fg="#555")
    lbl_gast.pack(side=tk.LEFT, padx=15)

    sel_cliente_id = tk.IntVar(value=0)

    # Tabla monederos
    cols_m = ("ID", "CLIENTE", "SALDO", "ACUMULADO", "GASTADO", "ALTA", "ACTIVO")
    tree_mon = ttk.Treeview(tab_mon, columns=cols_m, show="headings", height=12)
    for col in cols_m:
        tree_mon.heading(col, text=col)
    tree_mon.column("ID", width=40)
    tree_mon.column("CLIENTE", width=200)
    tree_mon.column("SALDO", width=100)
    tree_mon.column("ACUMULADO", width=100)
    tree_mon.column("GASTADO", width=100)
    tree_mon.column("ALTA", width=100)
    tree_mon.column("ACTIVO", width=60)
    scroll_m = ttk.Scrollbar(tab_mon, orient="vertical", command=tree_mon.yview)
    tree_mon.configure(yscrollcommand=scroll_m.set)
    tree_mon.pack(fill=tk.BOTH, expand=True, padx=10, pady=5, side=tk.LEFT)
    scroll_m.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def cargar_monederos(filtro=""):
        for item in tree_mon.get_children():
            tree_mon.delete(item)
        q = """SELECT m.id, cl.nombre, m.saldo_saturnos, m.total_acumulado, m.total_gastado, m.fecha_alta, m.activo
               FROM monederos m JOIN clientes cl ON m.cliente_id=cl.id"""
        params = []
        if filtro:
            q += " WHERE cl.nombre LIKE ? OR cl.telefono LIKE ?"
            params = [f"%{filtro}%", f"%{filtro}%"]
        q += " ORDER BY m.saldo_saturnos DESC"
        c.execute(q, params)
        for row in c.fetchall():
            tree_mon.insert("", "end", values=(row[0], row[1], f"{row[2]:,.0f}", f"{row[3]:,.0f}", f"{row[4]:,.0f}", row[5] or "", "Sí" if row[6] else "No"))

    def on_sel_monedero(event=None):
        sel = tree_mon.selection()
        if not sel:
            return
        vals = tree_mon.item(sel[0])["values"]
        lbl_saldo.config(text=f"\u20B4 Saldo: {vals[2]}")
        lbl_acum.config(text=f"Acumulado: {vals[3]}")
        lbl_gast.config(text=f"Gastado: {vals[4]}")

    tree_mon.bind("<<TreeviewSelect>>", on_sel_monedero)

    def buscar_mon(event=None):
        cargar_monederos(busq_entry.get())
    busq_entry.bind("<KeyRelease>", buscar_mon)

    btn_f = tk.Frame(busq_frame, bg="white")
    btn_f.pack(side=tk.RIGHT)

    def ajuste_manual():
        sel = tree_mon.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un monedero")
            return
        mid = tree_mon.item(sel[0])["values"][0]
        dlg = tk.Toplevel(main)
        dlg.title("Ajuste Manual de Saturnos")
        dlg.geometry("350x200")
        dlg.configure(bg="white")
        dlg.grab_set()
        tk.Label(dlg, text="Cantidad (positiva=sumar, negativa=restar):", font=("Segoe UI", 10), bg="white").pack(pady=10)
        cant_e = tk.Entry(dlg, width=15, font=("Segoe UI", 12))
        cant_e.pack(pady=5)
        tk.Label(dlg, text="Concepto:", font=("Segoe UI", 10), bg="white").pack(pady=5)
        concepto_e = tk.Entry(dlg, width=30, font=("Segoe UI", 9))
        concepto_e.pack(pady=5)
        def aplicar():
            try:
                cant = float(cant_e.get())
            except:
                messagebox.showwarning("Error", "Cantidad inválida")
                return
            c.execute("SELECT cliente_id, saldo_saturnos FROM monederos WHERE id=?", (mid,))
            row = c.fetchone()
            if not row:
                return
            cid, saldo = row
            nuevo = saldo + cant
            if nuevo < 0:
                nuevo = 0
            c.execute("UPDATE monederos SET saldo_saturnos=? WHERE id=?", (nuevo, mid))
            if cant > 0:
                c.execute("UPDATE monederos SET total_acumulado=total_acumulado+? WHERE id=?", (cant, mid))
            else:
                c.execute("UPDATE monederos SET total_gastado=total_gastado+? WHERE id=?", (abs(cant), mid))
            ahora = datetime.now()
            c.execute("""INSERT INTO movimientos_saturnos (cliente_id,tipo,cantidad,saldo_anterior,saldo_nuevo,concepto,usuario,fecha,hora)
                        VALUES (?,?,?,?,?,?,?,?,?)""",
                      (cid, "AJUSTE", cant, saldo, nuevo, concepto_e.get() or "Ajuste manual",
                       usuario_actual, ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S")))
            conn.commit()
            dlg.destroy()
            cargar_monederos()
            messagebox.showinfo("Ajuste", f"Ajuste de {cant:+,.0f} Saturnos aplicado")
        tk.Button(dlg, text="APLICAR", command=aplicar, bg="#FFC107", fg="#333",
                 font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=16, pady=4, cursor="hand2").pack(pady=10)

    tk.Button(btn_f, text="+ Ajuste Manual", command=ajuste_manual,
             bg="#FFC107", fg="#333", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=4)

    cargar_monederos()

    # ==================== PESTAÑA MOVIMIENTOS ====================
    tab_mov = tk.Frame(notebook, bg="white")
    notebook.add(tab_mov, text="  Movimientos  ")

    filt_mov = tk.Frame(tab_mov, bg="white")
    filt_mov.pack(fill=tk.X, padx=10, pady=8)
    tk.Label(filt_mov, text="Tipo:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    tipo_mov_var = tk.StringVar(value="TODOS")
    ttk.Combobox(filt_mov, textvariable=tipo_mov_var, width=14,
                values=["TODOS","ACUMULACION","REDIMIR","AJUSTE","EXPIRACION"], state="readonly").pack(side=tk.LEFT, padx=5)
    tk.Label(filt_mov, text="Cliente:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=10)
    cli_mov_entry = tk.Entry(filt_mov, width=20, font=("Segoe UI", 9))
    cli_mov_entry.pack(side=tk.LEFT, padx=5)

    cols_mv = ("FECHA", "HORA", "CLIENTE", "TIPO", "CANTIDAD", "SALDO ANT", "SALDO NVO", "CONCEPTO")
    tree_mov = ttk.Treeview(tab_mov, columns=cols_mv, show="headings", height=16)
    for col in cols_mv:
        tree_mov.heading(col, text=col)
    tree_mov.column("FECHA", width=90)
    tree_mov.column("HORA", width=70)
    tree_mov.column("CLIENTE", width=150)
    tree_mov.column("TIPO", width=100)
    tree_mov.column("CANTIDAD", width=80)
    tree_mov.column("SALDO ANT", width=80)
    tree_mov.column("SALDO NVO", width=80)
    tree_mov.column("CONCEPTO", width=200)
    tree_mov.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def cargar_movimientos():
        for item in tree_mov.get_children():
            tree_mov.delete(item)
        q = """SELECT ms.fecha, ms.hora, cl.nombre, ms.tipo, ms.cantidad, ms.saldo_anterior, ms.saldo_nuevo, ms.concepto
               FROM movimientos_saturnos ms JOIN clientes cl ON ms.cliente_id=cl.id WHERE 1=1"""
        params = []
        if tipo_mov_var.get() != "TODOS":
            q += " AND ms.tipo=?"
            params.append(tipo_mov_var.get())
        if cli_mov_entry.get():
            q += " AND cl.nombre LIKE ?"
            params.append(f"%{cli_mov_entry.get()}%")
        q += " ORDER BY ms.id DESC LIMIT 200"
        c.execute(q, params)
        for row in c.fetchall():
            tree_mov.insert("", "end", values=row)

    tk.Button(filt_mov, text="FILTRAR", command=cargar_movimientos,
             bg="#FFC107", fg="#333", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=10)
    cargar_movimientos()

    # ==================== PESTAÑA CONFIGURACIÓN ====================
    tab_cfg = tk.Frame(notebook, bg="white")
    notebook.add(tab_cfg, text="  Configuración  ")

    tk.Label(tab_cfg, text="CONFIGURACIÓN PROGRAMA SATURNOS", font=("Segoe UI", 14, "bold"),
            bg="white", fg="#F57F17").pack(pady=15)

    form_cfg = tk.Frame(tab_cfg, bg="white")
    form_cfg.pack(padx=30, pady=10)

    c.execute("SELECT * FROM configuracion_saturnos WHERE id=1")
    cfg = c.fetchone()
    cfg_vals = {
        "pct_gen": tk.StringVar(value=str(cfg[1] if cfg else 10.0)),
        "pct_pat": tk.StringVar(value=str(cfg[2] if cfg else 8.0)),
        "tasa": tk.StringVar(value=str(cfg[3] if cfg else 1.0)),
        "min_acum": tk.StringVar(value=str(cfg[4] if cfg else 50.0)),
        "min_red": tk.StringVar(value=str(cfg[5] if cfg else 100.0)),
        "dias_exp": tk.StringVar(value=str(cfg[6] if cfg else 365)),
        "activo": tk.IntVar(value=cfg[7] if cfg else 1),
    }
    campos_cfg = [
        ("Porcentaje genéricos (%):", "pct_gen", 0),
        ("Porcentaje patentes (%):", "pct_pat", 1),
        ("Tasa conversión (1 peso = X Saturnos):", "tasa", 2),
        ("Compra mínima para acumular ($):", "min_acum", 3),
        ("Mínimo para redimir (Saturnos):", "min_red", 4),
        ("Días expiración:", "dias_exp", 5),
    ]
    for label, key, row in campos_cfg:
        tk.Label(form_cfg, text=label, font=("Segoe UI", 10, "bold"), bg="white").grid(row=row, column=0, sticky="e", padx=8, pady=6)
        tk.Entry(form_cfg, textvariable=cfg_vals[key], width=15, font=("Segoe UI", 10)).grid(row=row, column=1, padx=8, pady=6, sticky="w")

    tk.Checkbutton(form_cfg, text="Programa Activo", variable=cfg_vals["activo"],
                  font=("Segoe UI", 10, "bold"), bg="white").grid(row=6, column=0, columnspan=2, pady=10)

    def guardar_cfg_sat():
        try:
            c.execute("""UPDATE configuracion_saturnos SET porcentaje_generico=?, porcentaje_patente=?,
                        tasa_conversion=?, minimo_acumular=?, minimo_redimir=?, dias_expiracion=?, activo=? WHERE id=1""",
                      (float(cfg_vals["pct_gen"].get()), float(cfg_vals["pct_pat"].get()),
                       float(cfg_vals["tasa"].get()), float(cfg_vals["min_acum"].get()),
                       float(cfg_vals["min_red"].get()), int(cfg_vals["dias_exp"].get()),
                       cfg_vals["activo"].get()))
            conn.commit()
            messagebox.showinfo("Guardado", "Configuración Saturnos actualizada")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(form_cfg, text="GUARDAR CAMBIOS", command=guardar_cfg_sat,
             bg="#FFC107", fg="#333", font=("Segoe UI", 11, "bold"),
             relief=tk.FLAT, padx=20, pady=6, cursor="hand2").grid(row=7, column=0, columnspan=2, pady=15)

    # ==================== PESTAÑA REPORTES ====================
    tab_rep = tk.Frame(notebook, bg="white")
    notebook.add(tab_rep, text="  Reportes  ")

    tk.Label(tab_rep, text="REPORTES PROGRAMA SATURNOS", font=("Segoe UI", 14, "bold"),
            bg="white", fg="#F57F17").pack(pady=15)

    rep_frame = tk.Frame(tab_rep, bg="white")
    rep_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def cargar_reportes():
        for w in rep_frame.winfo_children():
            w.destroy()
        hoy = datetime.now().strftime("%Y-%m-%d")
        mes = datetime.now().strftime("%Y-%m")

        c.execute("SELECT COALESCE(SUM(saldo_saturnos),0) FROM monederos WHERE activo=1")
        total_circ = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(cantidad),0) FROM movimientos_saturnos WHERE tipo='ACUMULACION' AND fecha=?", (hoy,))
        acum_hoy = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(cantidad),0) FROM movimientos_saturnos WHERE tipo='ACUMULACION' AND fecha LIKE ?", (f"{mes}%",))
        acum_mes = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(ABS(cantidad)),0) FROM movimientos_saturnos WHERE tipo='REDIMIR' AND fecha=?", (hoy,))
        red_hoy = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(ABS(cantidad)),0) FROM movimientos_saturnos WHERE tipo='REDIMIR' AND fecha LIKE ?", (f"{mes}%",))
        red_mes = c.fetchone()[0]

        datos = [
            ("Saturnos en circulación (total):", f"{total_circ:,.0f} \u20B4", "#F57F17"),
            ("Acumulados hoy:", f"+{acum_hoy:,.0f}", "#4CAF50"),
            ("Acumulados este mes:", f"+{acum_mes:,.0f}", "#4CAF50"),
            ("Redimidos hoy:", f"-{red_hoy:,.0f}", "#D32F2F"),
            ("Redimidos este mes:", f"-{red_mes:,.0f}", "#D32F2F"),
            ("Pasivo estimado:", f"${total_circ:,.2f}", "#1565C0"),
        ]
        for i, (label, val, color) in enumerate(datos):
            tk.Label(rep_frame, text=label, font=("Segoe UI", 11, "bold"), bg="white", fg="#333").grid(row=i, column=0, sticky="e", padx=10, pady=4)
            tk.Label(rep_frame, text=val, font=("Segoe UI", 14, "bold"), bg="white", fg=color).grid(row=i, column=1, sticky="w", padx=10, pady=4)

        # Top 10 clientes
        tk.Label(rep_frame, text="Top 10 clientes con más Saturnos:", font=("Segoe UI", 11, "bold"),
                bg="white", fg="#333").grid(row=len(datos), column=0, columnspan=2, pady=(15,5), sticky="w")

        c.execute("""SELECT cl.nombre, m.saldo_saturnos FROM monederos m
                    JOIN clientes cl ON m.cliente_id=cl.id WHERE m.activo=1
                    ORDER BY m.saldo_saturnos DESC LIMIT 10""")
        for j, (nombre, saldo) in enumerate(c.fetchall()):
            tk.Label(rep_frame, text=f"  {j+1}. {nombre}", font=("Segoe UI", 9), bg="white").grid(
                row=len(datos)+1+j, column=0, sticky="w", padx=15)
            tk.Label(rep_frame, text=f"{saldo:,.0f} \u20B4", font=("Segoe UI", 9, "bold"),
                    bg="white", fg="#F57F17").grid(row=len(datos)+1+j, column=1, sticky="w")

        # --- Estadísticas de Tarjetas ---
        base_row = len(datos) + 11
        tk.Label(rep_frame, text="ESTADÍSTICAS DE TARJETAS:", font=("Segoe UI", 11, "bold"),
                bg="white", fg="#1565C0").grid(row=base_row, column=0, columnspan=2, pady=(15,5), sticky="w")

        c.execute("SELECT COUNT(*) FROM monederos WHERE codigo_tarjeta IS NOT NULL")
        total_emitidas = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM monederos WHERE codigo_tarjeta IS NOT NULL AND estado_tarjeta='ACTIVA'")
        activas = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM monederos WHERE codigo_tarjeta IS NOT NULL AND estado_tarjeta='BLOQUEADA'")
        bloqueadas = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM monederos WHERE codigo_tarjeta IS NOT NULL AND estado_tarjeta='ANULADA'")
        anuladas = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM monederos WHERE codigo_tarjeta IS NOT NULL AND tarjeta_impresa=0")
        sin_imprimir = c.fetchone()[0]
        c.execute("""SELECT COUNT(*) FROM monederos WHERE codigo_tarjeta IS NOT NULL
                     AND fecha_emision < date('now', '-90 days') AND saldo_saturnos=0""")
        sin_uso_90 = c.fetchone()[0]
        c.execute("""SELECT COUNT(*) FROM monederos m
                     WHERE m.activo=1 AND (m.codigo_tarjeta IS NULL OR m.codigo_tarjeta='')""")
        sin_tarjeta = c.fetchone()[0]

        datos_tarj = [
            ("Tarjetas emitidas (total):", str(total_emitidas), "#1565C0"),
            ("Activas:", str(activas), "#4CAF50"),
            ("Bloqueadas:", str(bloqueadas), "#FF9800"),
            ("Anuladas:", str(anuladas), "#D32F2F"),
            ("Pendientes de impresión:", str(sin_imprimir), "#9C27B0"),
            ("Sin uso >90 días (saldo 0):", str(sin_uso_90), "#757575"),
            ("Clientes sin tarjeta:", str(sin_tarjeta), "#546E7A"),
        ]
        for k, (label, val, color) in enumerate(datos_tarj):
            tk.Label(rep_frame, text=label, font=("Segoe UI", 10), bg="white", fg="#333").grid(
                row=base_row+1+k, column=0, sticky="e", padx=10, pady=2)
            tk.Label(rep_frame, text=val, font=("Segoe UI", 12, "bold"), bg="white", fg=color).grid(
                row=base_row+1+k, column=1, sticky="w", padx=10, pady=2)

    cargar_reportes()

    # ==================== PESTAÑA TARJETAS ====================
    tab_tarj = tk.Frame(notebook, bg="white")
    notebook.add(tab_tarj, text="  Tarjetas  ")

    tarj_toolbar = tk.Frame(tab_tarj, bg="white")
    tarj_toolbar.pack(fill=tk.X, padx=10, pady=8)

    tk.Label(tarj_toolbar, text="Buscar:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    tarj_busq = tk.Entry(tarj_toolbar, width=25, font=("Segoe UI", 9))
    tarj_busq.pack(side=tk.LEFT, padx=5)

    def emitir_tarjeta():
        dlg = tk.Toplevel(main)
        dlg.title("Generar Tarjeta Saturnos")
        dlg.geometry("800x850")
        dlg.configure(bg="white")
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg="#FFC107", height=38)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="\u20B4 GENERAR TARJETA SATURNOS", font=("Segoe UI", 11, "bold"),
                bg="#FFC107", fg="#333").pack(side=tk.LEFT, padx=12, pady=8)

        # Cliente
        form = tk.Frame(dlg, bg="white")
        form.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(form, text="Cliente:", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w")
        cli_var_t = tk.StringVar()
        cli_combo_t = ttk.Combobox(form, textvariable=cli_var_t, width=40, state="readonly")
        c.execute("SELECT nombre FROM clientes WHERE id > 1")
        cli_combo_t['values'] = [r[0] for r in c.fetchall()]
        if cli_combo_t['values']:
            cli_combo_t.current(0)
        cli_combo_t.pack(anchor="w", pady=(2, 10))

        # === SELECCION DE NIVEL POR COLOR ===
        tk.Label(form, text="SELECCIONA NIVEL:", font=("Segoe UI", 11, "bold"),
                bg="white", fg="#333").pack(anchor="w", pady=(5, 5))

        nivel_var = tk.StringVar(value="AZUL")
        colores_frame = tk.Frame(form, bg="white")
        colores_frame.pack(fill=tk.X, pady=5)

        niveles_info = [
            ("AZUL",   "#2196F3", "white",   "+5%\nGRATIS"),
            ("DORADA", "#FFD700", "#333333",  "+10%\n$5K/mes"),
            ("NEGRA",  "#212121", "white",    "+15%\nPrepago"),
        ]

        nivel_btns = {}
        for i, (nv_name, nv_color, nv_fg, nv_desc) in enumerate(niveles_info):
            card = tk.Frame(colores_frame, bg=nv_color, relief=tk.RAISED, bd=2, cursor="hand2")
            card.grid(row=0, column=i, padx=10, pady=5, ipadx=15, ipady=10)

            tk.Label(card, text=nv_name, font=("Segoe UI", 14, "bold"),
                    bg=nv_color, fg=nv_fg).pack(pady=(5, 2))
            tk.Label(card, text=nv_desc, font=("Segoe UI", 9),
                    bg=nv_color, fg=nv_fg, justify="center").pack(pady=(0, 5))

            # Radio indicator
            rb = tk.Radiobutton(card, variable=nivel_var, value=nv_name,
                               bg=nv_color, activebackground=nv_color, selectcolor=nv_color,
                               indicatoron=True)
            rb.pack()
            nivel_btns[nv_name] = card

            def make_click(name, c_card):
                def click(e=None):
                    nivel_var.set(name)
                    for nn, cc in nivel_btns.items():
                        cc.config(relief=tk.RAISED, bd=2)
                    c_card.config(relief=tk.GROOVE, bd=4)
                    actualizar_preview()
                c_card.bind("<Button-1>", click)
                for child in c_card.winfo_children():
                    child.bind("<Button-1>", click)
            make_click(nv_name, card)

        # Marcar AZUL por defecto
        nivel_btns["AZUL"].config(relief=tk.GROOVE, bd=4)

        # === VISTA PREVIA ===
        preview_frame = tk.Frame(dlg, bg="#F5F5F5", relief=tk.RIDGE, bd=1)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        tk.Label(preview_frame, text="VISTA PREVIA:", font=("Segoe UI", 10, "bold"),
                bg="#F5F5F5", fg="#555").pack(anchor="w", padx=10, pady=5)

        canvas_prev = tk.Canvas(preview_frame, width=230, height=340, bg="#F5F5F5", highlightthickness=0)
        canvas_prev.pack(pady=5)
        preview_refs = {}

        def actualizar_preview():
            nombre = cli_var_t.get()
            if not nombre:
                return
            c.execute("SELECT id FROM clientes WHERE nombre=?", (nombre,))
            row = c.fetchone()
            if not row:
                return
            cid = row[0]
            nivel_sel = nivel_var.get()
            codigo_temp = f"SAT-PREVIEW-00000"
            try:
                ruta_f, ruta_r = generar_tarjeta_imagen(cid, codigo_temp, nivel_sel)
                if ruta_f and os.path.exists(ruta_f):
                    img_f = Image.open(ruta_f).resize((228, 336), Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img_f)
                    canvas_prev.delete("all")
                    canvas_prev.create_image(114, 168, image=tk_img)
                    preview_refs["img"] = tk_img
                    try: os.remove(ruta_f)
                    except: pass
                    try: os.remove(ruta_r)
                    except: pass
            except Exception:
                pass

        cli_var_t.trace_add("write", lambda *a: actualizar_preview())
        try: actualizar_preview()
        except: pass

        # === FOTO DEL CLIENTE ===
        foto_frame = tk.Frame(dlg, bg="white")
        foto_frame.pack(fill=tk.X, padx=15, pady=8)
        tk.Label(foto_frame, text="📷 Foto para la tarjeta:", font=("Segoe UI", 10, "bold"),
                bg="white", fg="#333").pack(side=tk.LEFT, padx=5)
        foto_path_var = tk.StringVar()

        # Preview de foto
        foto_preview_lbl = tk.Label(foto_frame, text="Sin foto", width=10, height=3,
                                   bg="#f0f0f0", relief=tk.SUNKEN)
        foto_preview_lbl.pack(side=tk.LEFT, padx=8)
        foto_preview_lbl._img_ref = None

        def examinar_foto():
            ruta = filedialog.askopenfilename(filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.bmp")])
            if ruta:
                foto_path_var.set(ruta)
                try:
                    # Mostrar preview de la foto
                    foto_prev = Image.open(ruta).resize((60, 80), Image.Resampling.LANCZOS)
                    tk_foto = ImageTk.PhotoImage(foto_prev)
                    foto_preview_lbl.config(image=tk_foto, text="", width=60, height=80)
                    foto_preview_lbl._img_ref = tk_foto
                except:
                    foto_preview_lbl.config(text="✓ Cargada", fg="#4CAF50")

        def capturar_camara():
            """Capturar foto desde la cámara usando OpenCV"""
            try:
                import cv2
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    messagebox.showerror("Error", "No se pudo abrir la cámara")
                    return

                # Ventana de captura
                cam_win = tk.Toplevel(dlg)
                cam_win.title("📷 Capturar Foto")
                cam_win.geometry("500x450")
                cam_win.configure(bg="#1A1A1A")
                cam_win.transient(dlg)
                cam_win.grab_set()

                cam_label = tk.Label(cam_win, bg="#1A1A1A")
                cam_label.pack(pady=10)

                foto_capturada = [None]
                running = [True]

                def actualizar_frame():
                    if running[0]:
                        ret, frame = cap.read()
                        if ret:
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            frame = cv2.resize(frame, (480, 360))
                            img = Image.fromarray(frame)
                            tk_img = ImageTk.PhotoImage(img)
                            cam_label.config(image=tk_img)
                            cam_label._img_ref = tk_img
                            foto_capturada[0] = frame
                        cam_win.after(30, actualizar_frame)

                def tomar_foto():
                    if foto_capturada[0] is not None:
                        # Guardar foto temporal
                        temp_path = os.path.join(_ensure_tarjetas_dirs(), "tarjetas", "fotos", "temp_captura.png")
                        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                        img = Image.fromarray(foto_capturada[0])
                        img.save(temp_path)
                        foto_path_var.set(temp_path)
                        # Mostrar preview
                        foto_prev = img.resize((60, 80), Image.Resampling.LANCZOS)
                        tk_foto = ImageTk.PhotoImage(foto_prev)
                        foto_preview_lbl.config(image=tk_foto, text="", width=60, height=80)
                        foto_preview_lbl._img_ref = tk_foto
                        cerrar_camara()

                def cerrar_camara():
                    running[0] = False
                    cap.release()
                    cam_win.destroy()

                btn_frame = tk.Frame(cam_win, bg="#1A1A1A")
                btn_frame.pack(pady=10)
                tk.Button(btn_frame, text="📸 CAPTURAR", command=tomar_foto,
                         bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"),
                         relief=tk.FLAT, padx=20, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=10)
                tk.Button(btn_frame, text="CANCELAR", command=cerrar_camara,
                         bg="#757575", fg="white", font=("Segoe UI", 10, "bold"),
                         relief=tk.FLAT, padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=10)

                cam_win.protocol("WM_DELETE_WINDOW", cerrar_camara)
                actualizar_frame()

            except ImportError:
                messagebox.showwarning("OpenCV", "Instala OpenCV para usar la cámara:\npip install opencv-python\n\nPor ahora usa 'Cargar Foto'")
            except Exception as e:
                messagebox.showerror("Error", f"Error con la cámara: {e}")

        def quitar_foto():
            foto_path_var.set("")
            foto_preview_lbl.config(image="", text="Sin foto", width=10, height=3)
            foto_preview_lbl._img_ref = None

        tk.Button(foto_frame, text="📷 CÁMARA", command=capturar_camara,
                 bg="#FF5722", fg="white", font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, padx=10, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=3)
        tk.Button(foto_frame, text="📁 CARGAR", command=examinar_foto,
                 bg="#2196F3", fg="white", font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, padx=10, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=3)
        tk.Button(foto_frame, text="✕", command=quitar_foto,
                 bg="#f44336", fg="white", font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, padx=6, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=2)

        # === BOTON GENERAR E IMPRIMIR (verde, al lado) ===
        def generar_e_imprimir():
            """Genera la tarjeta y la imprime directamente"""
            nombre = cli_var_t.get()
            if not nombre:
                messagebox.showwarning("Aviso", "Selecciona un cliente")
                return
            c.execute("SELECT id FROM clientes WHERE nombre=?", (nombre,))
            row = c.fetchone()
            if not row:
                return
            cid = row[0]
            nivel_sel = nivel_var.get()

            # Verificar tarjeta existente
            c.execute("SELECT codigo_tarjeta FROM monederos WHERE cliente_id=? AND estado_tarjeta='ACTIVA' AND codigo_tarjeta IS NOT NULL", (cid,))
            existente = c.fetchone()
            if existente:
                if not messagebox.askyesno("Tarjeta existente", f"Este cliente ya tiene tarjeta {existente[0]}.\n¿Anular anterior y emitir nueva?"):
                    return
                c.execute("UPDATE monederos SET estado_tarjeta='ANULADA' WHERE cliente_id=? AND estado_tarjeta='ACTIVA'", (cid,))

            # Guardar foto si se seleccionó
            if foto_path_var.get() and os.path.exists(foto_path_var.get()):
                try:
                    foto_dest = os.path.join(_ensure_tarjetas_dirs(), "tarjetas", "fotos", f"cliente_{cid}.png")
                    foto_original = Image.open(foto_path_var.get())
                    target_w, target_h = 172, 272
                    ratio = max(target_w / foto_original.width, target_h / foto_original.height)
                    new_size = (int(foto_original.width * ratio), int(foto_original.height * ratio))
                    foto_resized = foto_original.resize(new_size, Image.Resampling.LANCZOS)
                    left = (foto_resized.width - target_w) // 2
                    top = (foto_resized.height - target_h) // 2
                    foto_final = foto_resized.crop((left, top, left + target_w, top + target_h))
                    foto_final.save(foto_dest, "PNG")
                except:
                    pass

            # Generar tarjeta
            codigo = generar_codigo_tarjeta()
            ahora = datetime.now()
            ruta_f, ruta_r = generar_tarjeta_imagen(cid, codigo, nivel_sel)

            if not ruta_f:
                messagebox.showerror("Error", "No se pudo generar la tarjeta")
                return

            # Actualizar base de datos
            c.execute("SELECT id FROM monederos WHERE cliente_id=?", (cid,))
            mon = c.fetchone()
            if mon:
                c.execute("""UPDATE monederos SET codigo_tarjeta=?, nivel_tarjeta=?, fecha_emision=?,
                            tarjeta_impresa=1, estado_tarjeta='ACTIVA' WHERE cliente_id=?""",
                         (codigo, nivel_sel, ahora.strftime('%Y-%m-%d %H:%M'), cid))
            else:
                c.execute("""INSERT INTO monederos (cliente_id, saldo_saturnos, codigo_tarjeta, nivel_tarjeta,
                            fecha_emision, tarjeta_impresa, estado_tarjeta, activo, fecha_alta)
                            VALUES (?,0,?,?,?,1,'ACTIVA',1,?)""",
                         (cid, codigo, nivel_sel, ahora.strftime('%Y-%m-%d %H:%M'), ahora.strftime('%Y-%m-%d')))
            conn.commit()

            # Imprimir directamente
            try:
                os.startfile(ruta_f, "print")
                messagebox.showinfo("Tarjeta Generada", f"✓ Tarjeta {codigo} generada e impresa\n\nNivel: {nivel_sel}\nCliente: {nombre}")
            except Exception as e:
                messagebox.showinfo("Tarjeta Generada", f"✓ Tarjeta {codigo} generada\n\nGuardada en:\n{ruta_f}\n\n(No se pudo imprimir: {e})")

            dlg.destroy()

        tk.Button(foto_frame, text="🖨️ GENERAR E IMPRIMIR", command=generar_e_imprimir,
                 bg="#4CAF50", fg="white", font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, padx=12, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=8)

        # === BOTON GENERAR ===
        def emitir():
            nombre = cli_var_t.get()
            if not nombre:
                messagebox.showwarning("Aviso", "Selecciona un cliente")
                return
            c.execute("SELECT id FROM clientes WHERE nombre=?", (nombre,))
            row = c.fetchone()
            if not row:
                return
            cid = row[0]
            nivel_sel = nivel_var.get()

            c.execute("SELECT codigo_tarjeta FROM monederos WHERE cliente_id=? AND estado_tarjeta='ACTIVA' AND codigo_tarjeta IS NOT NULL", (cid,))
            existente = c.fetchone()
            if existente:
                if not messagebox.askyesno("Tarjeta existente", f"Este cliente ya tiene tarjeta {existente[0]}.\nAnular anterior y emitir nueva?"):
                    return
                c.execute("UPDATE monederos SET estado_tarjeta='ANULADA' WHERE cliente_id=? AND estado_tarjeta='ACTIVA'", (cid,))

            # Guardar foto si se selecciono (tamaño para tarjeta: 172x272)
            if foto_path_var.get() and os.path.exists(foto_path_var.get()):
                try:
                    foto_dest = os.path.join(_ensure_tarjetas_dirs(), "tarjetas", "fotos", f"cliente_{cid}.png")
                    foto_original = Image.open(foto_path_var.get())
                    # Redimensionar manteniendo proporción para llenar 172x272
                    target_w, target_h = 172, 272
                    ratio = max(target_w / foto_original.width, target_h / foto_original.height)
                    new_size = (int(foto_original.width * ratio), int(foto_original.height * ratio))
                    foto_resized = foto_original.resize(new_size, Image.Resampling.LANCZOS)
                    # Recortar al centro
                    left = (foto_resized.width - target_w) // 2
                    top = (foto_resized.height - target_h) // 2
                    foto_final = foto_resized.crop((left, top, left + target_w, top + target_h))
                    foto_final.save(foto_dest, "PNG")
                except Exception as e:
                    print(f"Error guardando foto: {e}")

            codigo = generar_codigo_tarjeta()
            ahora = datetime.now()
            ruta_f, ruta_r = generar_tarjeta_imagen(cid, codigo, nivel_sel)
            barcode_path = os.path.join(_ensure_tarjetas_dirs(), "tarjetas", "codigos", f"{codigo}.png")

            c.execute("SELECT id FROM monederos WHERE cliente_id=?", (cid,))
            if c.fetchone():
                c.execute("""UPDATE monederos SET codigo_tarjeta=?, codigo_barras_path=?,
                            tarjeta_impresa=0, fecha_emision=?, estado_tarjeta='ACTIVA' WHERE cliente_id=?""",
                          (codigo, barcode_path, ahora.strftime("%Y-%m-%d"), cid))
            else:
                c.execute("""INSERT INTO monederos (cliente_id,saldo_saturnos,total_acumulado,total_gastado,activo,fecha_alta,
                            codigo_tarjeta,codigo_barras_path,tarjeta_impresa,fecha_emision,estado_tarjeta)
                            VALUES (?,0,0,0,1,?,?,?,0,?,'ACTIVA')""",
                          (cid, ahora.strftime("%Y-%m-%d"), codigo, barcode_path, ahora.strftime("%Y-%m-%d")))
            conn.commit()
            registrar_auditoria("TARJETA_EMITIDA", "saturnos", f"Tarjeta {codigo} nivel {nivel_sel} para cliente {nombre}")

            dlg.destroy()
            cargar_tarjetas()

            # Mostrar resultado
            res_dlg = tk.Toplevel(main)
            res_dlg.title(f"Tarjeta Emitida - {codigo}")
            res_dlg.geometry("900x550")
            res_dlg.configure(bg="white")

            tk.Label(res_dlg, text=f"TARJETA EMITIDA: {codigo} (NIVEL {nivel_sel})", font=("Segoe UI", 14, "bold"),
                    bg="white", fg="#4CAF50").pack(pady=10)

            img_frame_r = tk.Frame(res_dlg, bg="white")
            img_frame_r.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            for ruta, label in [(ruta_f, "FRONTAL"), (ruta_r, "REVERSO")]:
                if ruta and os.path.exists(ruta):
                    f = tk.Frame(img_frame_r, bg="white")
                    f.pack(side=tk.LEFT, padx=10, expand=True)
                    tk.Label(f, text=label, font=("Segoe UI", 9, "bold"), bg="white").pack()
                    img = Image.open(ruta).resize((400, 252), Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img)
                    lbl = tk.Label(f, image=tk_img, bg="white")
                    lbl.pack(pady=5)
                    lbl._img_ref = tk_img

            btn_f = tk.Frame(res_dlg, bg="white")
            btn_f.pack(pady=10)

            def imprimir_tarjeta():
                if ruta_f and os.path.exists(ruta_f):
                    try:
                        os.startfile(ruta_f, "print")
                        c.execute("UPDATE monederos SET tarjeta_impresa=1 WHERE codigo_tarjeta=?", (codigo,))
                        conn.commit()
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo imprimir: {e}")

            def guardar_pdf():
                try:
                    from PIL import Image as PILImage
                    if ruta_f and ruta_r and os.path.exists(ruta_f) and os.path.exists(ruta_r):
                        img_f_pdf = PILImage.open(ruta_f).convert('RGB')
                        img_r_pdf = PILImage.open(ruta_r).convert('RGB')
                        pdf_path = os.path.join(_ensure_tarjetas_dirs(), "tarjetas", "pdfs", f"{codigo}.pdf")
                        img_f_pdf.save(pdf_path, "PDF", save_all=True, append_images=[img_r_pdf])
                        messagebox.showinfo("PDF", f"PDF guardado en:\n{pdf_path}")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

            def enviar_whatsapp():
                """Enviar tarjeta digital por WhatsApp"""
                try:
                    # Obtener teléfono del cliente
                    c.execute("SELECT telefono FROM clientes WHERE id=?", (cliente_id,))
                    tel_row = c.fetchone()
                    telefono = tel_row[0] if tel_row and tel_row[0] else ""

                    # Crear imagen combinada (frente y reverso lado a lado)
                    from PIL import Image as PILImage
                    if ruta_f and ruta_r and os.path.exists(ruta_f) and os.path.exists(ruta_r):
                        img_f = PILImage.open(ruta_f)
                        img_r = PILImage.open(ruta_r)

                        # Crear imagen combinada
                        total_w = img_f.width + img_r.width + 20
                        max_h = max(img_f.height, img_r.height)
                        combinada = PILImage.new('RGB', (total_w, max_h), 'white')
                        combinada.paste(img_f, (0, (max_h - img_f.height) // 2))
                        combinada.paste(img_r, (img_f.width + 20, (max_h - img_r.height) // 2))

                        # Guardar imagen combinada
                        digital_path = os.path.join(_ensure_tarjetas_dirs(), "tarjetas", "digital", f"{codigo}_digital.png")
                        os.makedirs(os.path.dirname(digital_path), exist_ok=True)
                        combinada.save(digital_path, "PNG")

                        # Limpiar número de teléfono
                        tel_limpio = ''.join(filter(str.isdigit, telefono))
                        if tel_limpio and not tel_limpio.startswith('52'):
                            tel_limpio = '52' + tel_limpio

                        # Mensaje predeterminado
                        mensaje = f"🎉 ¡Felicidades! Tu Tarjeta Saturnos {nivel_var.get()} está lista.\n\n💳 Código: {codigo}\n₴ Saldo: ${saldo:,.0f} Saturnos\n\n¡Gracias por ser parte de Farmacias Madrid!"

                        # Copiar imagen al portapapeles y mostrar instrucciones
                        import subprocess
                        # Abrir la imagen para que el usuario pueda copiarla
                        os.startfile(digital_path)

                        # Abrir WhatsApp Web con el número
                        import webbrowser
                        import urllib.parse
                        url = f"https://wa.me/{tel_limpio}?text={urllib.parse.quote(mensaje)}"
                        webbrowser.open(url)

                        messagebox.showinfo("WhatsApp",
                            f"1. Se abrió la imagen de la tarjeta\n"
                            f"2. Cópiala (Ctrl+C)\n"
                            f"3. Pégala en WhatsApp\n\n"
                            f"Imagen guardada en:\n{digital_path}")
                    else:
                        messagebox.showwarning("Aviso", "No se encontraron las imágenes de la tarjeta")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al enviar: {e}")

            tk.Button(btn_f, text="IMPRIMIR", command=imprimir_tarjeta,
                     bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
                     relief=tk.FLAT, padx=14, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=4)
            tk.Button(btn_f, text="📱 WHATSAPP", command=enviar_whatsapp,
                     bg="#25D366", fg="white", font=("Segoe UI", 10, "bold"),
                     relief=tk.FLAT, padx=14, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=4)
            tk.Button(btn_f, text="GUARDAR PDF", command=guardar_pdf,
                     bg="#1565C0", fg="white", font=("Segoe UI", 10, "bold"),
                     relief=tk.FLAT, padx=14, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=4)
            tk.Button(btn_f, text="CERRAR", command=res_dlg.destroy,
                     bg="#757575", fg="white", font=("Segoe UI", 10, "bold"),
                     relief=tk.FLAT, padx=14, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=4)

        btn_generar = tk.Button(dlg, text="GENERAR TARJETA", command=emitir,
                               bg="#4CAF50", fg="white", font=("Segoe UI", 13, "bold"),
                               relief=tk.FLAT, padx=30, pady=10, cursor="hand2")
        btn_generar.pack(pady=10)
        hover_bind(btn_generar, "#4CAF50", "#388E3C")

    tk.Button(tarj_toolbar, text="+ EMITIR NUEVA TARJETA", command=emitir_tarjeta,
             bg="#FFC107", fg="#333", font=("Segoe UI", 10, "bold"),
             relief=tk.FLAT, padx=14, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=10)

    # Tabla tarjetas
    cols_t = ("CÓDIGO", "CLIENTE", "SALDO", "EMISIÓN", "IMPRESA", "ESTADO")
    tree_tarj = ttk.Treeview(tab_tarj, columns=cols_t, show="headings", height=12)
    for col in cols_t:
        tree_tarj.heading(col, text=col)
    tree_tarj.column("CÓDIGO", width=170)
    tree_tarj.column("CLIENTE", width=200)
    tree_tarj.column("SALDO", width=90)
    tree_tarj.column("EMISIÓN", width=100)
    tree_tarj.column("IMPRESA", width=70)
    tree_tarj.column("ESTADO", width=90)
    tree_tarj.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    tarj_acciones = tk.Frame(tab_tarj, bg="white")
    tarj_acciones.pack(fill=tk.X, padx=10, pady=5)

    def cargar_tarjetas(filtro=""):
        for item in tree_tarj.get_children():
            tree_tarj.delete(item)
        q = """SELECT m.codigo_tarjeta, cl.nombre, m.saldo_saturnos, m.fecha_emision,
               m.tarjeta_impresa, m.estado_tarjeta
               FROM monederos m JOIN clientes cl ON m.cliente_id=cl.id
               WHERE m.codigo_tarjeta IS NOT NULL"""
        params = []
        if filtro:
            q += " AND (cl.nombre LIKE ? OR m.codigo_tarjeta LIKE ?)"
            params = [f"%{filtro}%", f"%{filtro}%"]
        q += " ORDER BY m.id DESC"
        c.execute(q, params)
        for row in c.fetchall():
            tree_tarj.insert("", "end", values=(
                row[0], row[1], f"{row[2]:,.0f}", row[3] or "",
                "Sí" if row[4] else "No", row[5] or "ACTIVA"))

    def buscar_tarj(event=None):
        cargar_tarjetas(tarj_busq.get())
    tarj_busq.bind("<KeyRelease>", buscar_tarj)

    def reimprimir_tarjeta():
        sel = tree_tarj.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una tarjeta")
            return
        codigo = tree_tarj.item(sel[0])["values"][0]
        c.execute("SELECT cliente_id FROM monederos WHERE codigo_tarjeta=?", (codigo,))
        row = c.fetchone()
        if row:
            ruta_f, ruta_r = generar_tarjeta_imagen(row[0], codigo)
            if ruta_f and os.path.exists(ruta_f):
                try:
                    os.startfile(ruta_f, "print")
                except:
                    messagebox.showinfo("Tarjeta", f"Guardada en: {ruta_f}")

    def anular_tarjeta():
        sel = tree_tarj.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una tarjeta")
            return
        codigo = tree_tarj.item(sel[0])["values"][0]
        if not messagebox.askyesno("Anular", f"¿Anular tarjeta {codigo}?\nEl monedero seguirá activo pero la tarjeta quedará inutilizable."):
            return
        c.execute("UPDATE monederos SET estado_tarjeta='ANULADA' WHERE codigo_tarjeta=?", (codigo,))
        conn.commit()
        cargar_tarjetas()
        messagebox.showinfo("Anulada", f"Tarjeta {codigo} anulada")

    def bloquear_tarjeta():
        sel = tree_tarj.selection()
        if not sel:
            return
        codigo = tree_tarj.item(sel[0])["values"][0]
        estado = tree_tarj.item(sel[0])["values"][5]
        if estado == "BLOQUEADA":
            c.execute("UPDATE monederos SET estado_tarjeta='ACTIVA' WHERE codigo_tarjeta=?", (codigo,))
            msg = "Tarjeta desbloqueada"
        else:
            c.execute("UPDATE monederos SET estado_tarjeta='BLOQUEADA' WHERE codigo_tarjeta=?", (codigo,))
            msg = "Tarjeta bloqueada (reportada como perdida)"
        conn.commit()
        cargar_tarjetas()
        messagebox.showinfo("Tarjeta", msg)

    tk.Button(tarj_acciones, text="REIMPRIMIR", command=reimprimir_tarjeta,
             bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=4)
    tk.Button(tarj_acciones, text="BLOQUEAR/DESBLOQUEAR", command=bloquear_tarjeta,
             bg="#FF9800", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=4)
    tk.Button(tarj_acciones, text="ANULAR", command=anular_tarjeta,
             bg="#D32F2F", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=4)

    cargar_tarjetas()

    # ==================== PESTANA GESTION USUARIOS ====================
    if nivel_actual == "ADMINISTRADOR":
        tab_users = tk.Frame(notebook, bg="white")
        notebook.add(tab_users, text="  Gestion Usuarios  ")

        tk.Label(tab_users, text="GESTION DE USUARIOS DEL SISTEMA", font=("Segoe UI", 12, "bold"),
                bg="white", fg="#333").pack(anchor="w", padx=15, pady=(10, 5))

        users_toolbar = tk.Frame(tab_users, bg="white")
        users_toolbar.pack(fill=tk.X, padx=10, pady=5)

        # Tabla usuarios
        cols_u = ("ID", "Nombre", "Usuario", "Nivel", "Rol", "Activo", "Ultimo Acceso")
        tree_users = ttk.Treeview(tab_users, columns=cols_u, show="headings", height=12)
        for col_u in cols_u:
            ancho_u = 40 if col_u == "ID" else 50 if col_u == "Activo" else 140 if col_u == "Ultimo Acceso" else 120
            tree_users.heading(col_u, text=col_u)
            tree_users.column(col_u, width=ancho_u)
        tree_users.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def cargar_usuarios():
            for item in tree_users.get_children():
                tree_users.delete(item)
            c.execute("""SELECT e.id, e.nombre, e.usuario, e.nivel,
                         COALESCE(r.nombre, e.nivel), e.activo, COALESCE(e.ultimo_acceso, '')
                         FROM empleados e LEFT JOIN roles r ON e.rol_id=r.id
                         ORDER BY e.id""")
            for row in c.fetchall():
                activo_txt = "Si" if row[5] else "No"
                tree_users.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], activo_txt, row[6]))

        def dialog_nuevo_usuario():
            import hashlib
            dlg_u = tk.Toplevel(main)
            dlg_u.title("Nuevo Usuario")
            dlg_u.geometry("400x420")
            dlg_u.configure(bg="white")
            dlg_u.grab_set()

            tk.Label(dlg_u, text="NUEVO USUARIO", font=("Segoe UI", 14, "bold"),
                    bg="white", fg=AZUL_FARMACIA).pack(pady=(15, 10))

            form_u = tk.Frame(dlg_u, bg="white")
            form_u.pack(padx=20, pady=5, fill=tk.X)

            tk.Label(form_u, text="Nombre:", font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(5,0))
            nombre_var = tk.StringVar()
            tk.Entry(form_u, textvariable=nombre_var, width=35, font=("Segoe UI", 10)).pack(fill=tk.X, ipady=3)

            tk.Label(form_u, text="Usuario:", font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(8,0))
            usuario_var_u = tk.StringVar()
            tk.Entry(form_u, textvariable=usuario_var_u, width=35, font=("Segoe UI", 10)).pack(fill=tk.X, ipady=3)

            tk.Label(form_u, text="Contrasena:", font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(8,0))
            pass_var = tk.StringVar()
            tk.Entry(form_u, textvariable=pass_var, width=35, font=("Segoe UI", 10), show="*").pack(fill=tk.X, ipady=3)

            tk.Label(form_u, text="Rol:", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w", pady=(12,0))

            rol_var = tk.StringVar(value="CAJERO")
            roles_frame = tk.Frame(form_u, bg="white")
            roles_frame.pack(anchor="w", pady=5)

            roles_opciones = [
                ("ADMINISTRADOR", "Acceso total"),
                ("GERENTE", "Gestion"),
                ("CAJERO", "Solo ventas"),
                ("REPARTIDOR", "Solo entregas"),
            ]
            for rol_nombre, rol_desc in roles_opciones:
                tk.Radiobutton(roles_frame, text=f"{rol_nombre} ({rol_desc})", variable=rol_var,
                              value=rol_nombre, font=("Segoe UI", 9), bg="white",
                              activebackground="white").pack(anchor="w", pady=1)

            def crear_usuario():
                nom = nombre_var.get().strip()
                usr = usuario_var_u.get().strip()
                pwd_u = pass_var.get().strip()
                rol = rol_var.get()

                if not nom or not usr or not pwd_u:
                    messagebox.showwarning("Aviso", "Todos los campos son obligatorios")
                    return

                c.execute("SELECT id FROM empleados WHERE usuario=?", (usr,))
                if c.fetchone():
                    messagebox.showwarning("Aviso", f"El usuario '{usr}' ya existe")
                    return

                # Hash de password con SHA256
                pwd_hash = hashlib.sha256(pwd_u.encode()).hexdigest()

                # Obtener rol_id
                nivel_map = {"ADMINISTRADOR": "ADMINISTRADOR", "GERENTE": "ADMINISTRADOR",
                             "CAJERO": "CAJERO", "REPARTIDOR": "REPARTIDOR"}
                c.execute("SELECT id FROM roles WHERE nombre=?", (rol,))
                rol_row = c.fetchone()
                rol_id = rol_row[0] if rol_row else 1

                c.execute("INSERT INTO empleados (nombre, usuario, password, nivel, activo, rol_id) VALUES (?,?,?,?,1,?)",
                          (nom, usr, pwd_hash, nivel_map.get(rol, "VENDEDOR"), rol_id))
                conn.commit()
                registrar_auditoria("CREAR_USUARIO", "usuarios", f"Usuario: {usr}, Rol: {rol}")
                dlg_u.destroy()
                cargar_usuarios()
                messagebox.showinfo("Creado", f"Usuario '{usr}' creado con rol {rol}")

            btn_crear = tk.Button(dlg_u, text="CREAR", command=crear_usuario,
                                 bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"),
                                 relief=tk.FLAT, padx=30, pady=8, cursor="hand2")
            btn_crear.pack(pady=10)
            hover_bind(btn_crear, "#4CAF50", "#388E3C")

        def editar_usuario():
            sel = tree_users.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecciona un usuario")
                return
            vals = tree_users.item(sel[0])["values"]
            uid = vals[0]

            dlg_e = tk.Toplevel(main)
            dlg_e.title(f"Editar Usuario - {vals[2]}")
            dlg_e.geometry("400x350")
            dlg_e.configure(bg="white")
            dlg_e.grab_set()

            tk.Label(dlg_e, text=f"EDITAR: {vals[1]}", font=("Segoe UI", 14, "bold"),
                    bg="white", fg=AZUL_FARMACIA).pack(pady=(15, 10))

            form_e = tk.Frame(dlg_e, bg="white")
            form_e.pack(padx=20, fill=tk.X)

            tk.Label(form_e, text="Nueva contrasena (dejar vacio para no cambiar):", font=("Segoe UI", 9), bg="white").pack(anchor="w")
            new_pass = tk.StringVar()
            tk.Entry(form_e, textvariable=new_pass, width=35, font=("Segoe UI", 10), show="*").pack(fill=tk.X, ipady=3, pady=(0,10))

            tk.Label(form_e, text="Rol:", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w")
            rol_var_e = tk.StringVar(value=vals[4])
            for rol_n in ["ADMINISTRADOR", "GERENTE", "CAJERO", "REPARTIDOR"]:
                tk.Radiobutton(form_e, text=rol_n, variable=rol_var_e, value=rol_n,
                              font=("Segoe UI", 9), bg="white").pack(anchor="w")

            activo_var_e = tk.BooleanVar(value=vals[5] == "Si")
            tk.Checkbutton(form_e, text="Usuario activo", variable=activo_var_e,
                          font=("Segoe UI", 9), bg="white").pack(anchor="w", pady=5)

            def guardar_edicion():
                import hashlib
                rol = rol_var_e.get()
                activo = 1 if activo_var_e.get() else 0

                c.execute("SELECT id FROM roles WHERE nombre=?", (rol,))
                rol_row = c.fetchone()
                rol_id = rol_row[0] if rol_row else 1

                nivel_map = {"ADMINISTRADOR": "ADMINISTRADOR", "GERENTE": "ADMINISTRADOR",
                             "CAJERO": "CAJERO", "REPARTIDOR": "REPARTIDOR"}

                if new_pass.get().strip():
                    pwd_hash = hashlib.sha256(new_pass.get().strip().encode()).hexdigest()
                    c.execute("UPDATE empleados SET password=?, nivel=?, rol_id=?, activo=? WHERE id=?",
                              (pwd_hash, nivel_map.get(rol, "VENDEDOR"), rol_id, activo, uid))
                else:
                    c.execute("UPDATE empleados SET nivel=?, rol_id=?, activo=? WHERE id=?",
                              (nivel_map.get(rol, "VENDEDOR"), rol_id, activo, uid))

                conn.commit()
                registrar_auditoria("EDITAR_USUARIO", "usuarios", f"Usuario ID: {uid}, Rol: {rol}")
                dlg_e.destroy()
                cargar_usuarios()
                messagebox.showinfo("Guardado", "Usuario actualizado")

            tk.Button(dlg_e, text="GUARDAR", command=guardar_edicion,
                     bg="#1565C0", fg="white", font=("Segoe UI", 11, "bold"),
                     relief=tk.FLAT, padx=25, pady=6, cursor="hand2").pack(pady=10)

        def eliminar_usuario():
            sel = tree_users.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecciona un usuario")
                return
            vals = tree_users.item(sel[0])["values"]
            if vals[0] == usuario_id:
                messagebox.showwarning("Aviso", "No puedes eliminar tu propio usuario")
                return
            if not messagebox.askyesno("Eliminar", f"Desactivar usuario '{vals[2]}'?\n(No se elimina, solo se desactiva)"):
                return
            c.execute("UPDATE empleados SET activo=0 WHERE id=?", (vals[0],))
            conn.commit()
            registrar_auditoria("DESACTIVAR_USUARIO", "usuarios", f"Usuario: {vals[2]}")
            cargar_usuarios()

        btn_nuevo = tk.Button(users_toolbar, text="+ NUEVO USUARIO", command=dialog_nuevo_usuario,
                             bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
                             relief=tk.FLAT, padx=14, pady=5, cursor="hand2")
        btn_nuevo.pack(side=tk.LEFT, padx=5)
        hover_bind(btn_nuevo, "#4CAF50", "#388E3C")

        btn_editar = tk.Button(users_toolbar, text="EDITAR", command=editar_usuario,
                              bg="#1565C0", fg="white", font=("Segoe UI", 10, "bold"),
                              relief=tk.FLAT, padx=14, pady=5, cursor="hand2")
        btn_editar.pack(side=tk.LEFT, padx=5)
        hover_bind(btn_editar, "#1565C0", "#1E88E5")

        btn_del = tk.Button(users_toolbar, text="DESACTIVAR", command=eliminar_usuario,
                           bg="#D32F2F", fg="white", font=("Segoe UI", 10, "bold"),
                           relief=tk.FLAT, padx=14, pady=5, cursor="hand2")
        btn_del.pack(side=tk.LEFT, padx=5)
        hover_bind(btn_del, "#D32F2F", "#EF5350")

        cargar_usuarios()


# ===== MODULO REPORTES GENERALES CON GRAFICAS =====
def ver_reportes():
    limpiar()

    header_mod = tk.Frame(main, bg="#00838F", height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="\u2261 REPORTES GENERALES", font=("Segoe UI", 13, "bold"),
            bg="#00838F", fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    notebook = ttk.Notebook(main)
    notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # ===== Colores para gráficas =====
    COLORES_GRAF = ["#2196F3","#4CAF50","#FF9800","#9C27B0","#E91E63",
                    "#00BCD4","#FF5722","#607D8B","#8BC34A","#FFC107",
                    "#3F51B5","#009688","#795548","#CDDC39","#F44336"]

    def dibujar_barras(canvas, datos, ancho_canvas, alto_canvas, titulo="", mostrar_valores=True, horizontal=False):
        """Dibuja gráfica de barras en un Canvas. datos = [(label, valor, color_opcional), ...]"""
        canvas.delete("all")
        if not datos:
            canvas.create_text(ancho_canvas//2, alto_canvas//2, text="Sin datos", font=("Segoe UI", 12), fill="#999")
            return

        margen_izq = 120 if horizontal else 50
        margen_der = 20
        margen_top = 35
        margen_bot = 60 if not horizontal else 20
        area_w = ancho_canvas - margen_izq - margen_der
        area_h = alto_canvas - margen_top - margen_bot

        if titulo:
            canvas.create_text(ancho_canvas//2, 14, text=titulo, font=("Segoe UI", 11, "bold"), fill="#333")

        max_val = max(d[1] for d in datos) if datos else 1
        if max_val == 0:
            max_val = 1

        if horizontal:
            bar_h = min(28, area_h // len(datos) - 4)
            y = margen_top
            for i, item in enumerate(datos):
                label = item[0][:18]
                val = item[1]
                color = item[2] if len(item) > 2 else COLORES_GRAF[i % len(COLORES_GRAF)]
                bar_w = int((val / max_val) * area_w) if max_val > 0 else 0
                # Label
                canvas.create_text(margen_izq - 5, y + bar_h//2, text=label, font=("Segoe UI", 8),
                                  fill="#333", anchor="e")
                # Barra
                if bar_w > 0:
                    canvas.create_rectangle(margen_izq, y, margen_izq + bar_w, y + bar_h,
                                           fill=color, outline="", width=0)
                # Valor
                if mostrar_valores:
                    txt = f"${val:,.0f}" if val >= 100 else f"{val:,.1f}"
                    canvas.create_text(margen_izq + bar_w + 5, y + bar_h//2, text=txt,
                                      font=("Segoe UI", 8, "bold"), fill=color, anchor="w")
                y += bar_h + 4
        else:
            n = len(datos)
            bar_w = min(50, (area_w // n) - 6)
            gap = (area_w - bar_w * n) // (n + 1)
            x = margen_izq + gap
            # Líneas guía
            for g in range(5):
                gy = margen_top + area_h - int((g / 4) * area_h)
                canvas.create_line(margen_izq, gy, ancho_canvas - margen_der, gy, fill="#E0E0E0", dash=(2,2))
                gval = (max_val / 4) * g
                txt = f"${gval:,.0f}" if gval >= 100 else f"{gval:,.1f}"
                canvas.create_text(margen_izq - 5, gy, text=txt, font=("Segoe UI", 7), fill="#999", anchor="e")

            for i, item in enumerate(datos):
                label = item[0][:10]
                val = item[1]
                color = item[2] if len(item) > 2 else COLORES_GRAF[i % len(COLORES_GRAF)]
                bar_h_px = int((val / max_val) * area_h) if max_val > 0 else 0
                y_top = margen_top + area_h - bar_h_px
                y_bot = margen_top + area_h
                if bar_h_px > 0:
                    canvas.create_rectangle(x, y_top, x + bar_w, y_bot, fill=color, outline="", width=0)
                if mostrar_valores:
                    txt = f"${val:,.0f}" if val >= 100 else f"{val:,.0f}"
                    canvas.create_text(x + bar_w//2, y_top - 10, text=txt, font=("Segoe UI", 7, "bold"), fill=color)
                canvas.create_text(x + bar_w//2, y_bot + 10, text=label, font=("Segoe UI", 7), fill="#333", angle=30)
                x += bar_w + gap

    def dibujar_pastel(canvas, datos, cx, cy, radio, titulo=""):
        """Dibuja gráfica de pastel. datos = [(label, valor), ...]"""
        canvas.delete("all")
        if not datos:
            canvas.create_text(cx, cy, text="Sin datos", font=("Segoe UI", 12), fill="#999")
            return

        total = sum(d[1] for d in datos)
        if total == 0:
            canvas.create_text(cx, cy, text="Sin datos", font=("Segoe UI", 12), fill="#999")
            return

        if titulo:
            canvas.create_text(cx, 14, text=titulo, font=("Segoe UI", 11, "bold"), fill="#333")

        start = 0
        for i, (label, val) in enumerate(datos):
            extent = (val / total) * 360
            color = COLORES_GRAF[i % len(COLORES_GRAF)]
            canvas.create_arc(cx - radio, cy - radio, cx + radio, cy + radio,
                            start=start, extent=extent, fill=color, outline="white", width=2)
            # Etiqueta
            import math
            mid_angle = math.radians(start + extent / 2)
            lx = cx + (radio + 30) * math.cos(mid_angle)
            ly = cy - (radio + 30) * math.sin(mid_angle)
            pct = (val / total) * 100
            canvas.create_text(lx, ly, text=f"{label[:12]}\n{pct:.1f}%", font=("Segoe UI", 7, "bold"),
                              fill=color, justify="center")
            start += extent

    def dibujar_lineas(canvas, series, ancho_canvas, alto_canvas, titulo="", labels_x=None):
        """Dibuja gráfica de líneas. series = [(nombre, [valores], color), ...]"""
        canvas.delete("all")
        if not series or not series[0][1]:
            canvas.create_text(ancho_canvas//2, alto_canvas//2, text="Sin datos", font=("Segoe UI", 12), fill="#999")
            return

        margen_izq = 60
        margen_der = 20
        margen_top = 35
        margen_bot = 50
        area_w = ancho_canvas - margen_izq - margen_der
        area_h = alto_canvas - margen_top - margen_bot

        if titulo:
            canvas.create_text(ancho_canvas//2, 14, text=titulo, font=("Segoe UI", 11, "bold"), fill="#333")

        all_vals = []
        for _, vals, _ in series:
            all_vals.extend(vals)
        max_val = max(all_vals) if all_vals else 1
        if max_val == 0:
            max_val = 1
        n_points = max(len(s[1]) for s in series)

        # Guías Y
        for g in range(5):
            gy = margen_top + area_h - int((g / 4) * area_h)
            canvas.create_line(margen_izq, gy, ancho_canvas - margen_der, gy, fill="#E0E0E0", dash=(2,2))
            gval = (max_val / 4) * g
            canvas.create_text(margen_izq - 5, gy, text=f"${gval:,.0f}" if gval >= 10 else f"{gval:.1f}",
                              font=("Segoe UI", 7), fill="#999", anchor="e")

        # Labels X
        if labels_x:
            step_x = area_w / max(n_points - 1, 1)
            for i, lbl in enumerate(labels_x[:n_points]):
                lx = margen_izq + i * step_x
                canvas.create_text(lx, margen_top + area_h + 15, text=lbl[:8],
                                  font=("Segoe UI", 7), fill="#555", angle=25)

        # Dibujar series
        for s_idx, (nombre, vals, color) in enumerate(series):
            step_x = area_w / max(len(vals) - 1, 1)
            points = []
            for i, v in enumerate(vals):
                px = margen_izq + i * step_x
                py = margen_top + area_h - int((v / max_val) * area_h)
                points.append((px, py))
            # Línea
            for i in range(len(points) - 1):
                canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1],
                                 fill=color, width=2, smooth=True)
            # Puntos
            for px, py in points:
                canvas.create_oval(px-3, py-3, px+3, py+3, fill=color, outline="white", width=1)
            # Leyenda
            ly = margen_top + area_h + 35 + s_idx * 14
            canvas.create_rectangle(margen_izq, ly - 5, margen_izq + 12, ly + 5, fill=color, outline="")
            canvas.create_text(margen_izq + 16, ly, text=nombre, font=("Segoe UI", 8), fill="#333", anchor="w")

    # ==================== TAB 1: DASHBOARD ====================
    tab_dash = tk.Frame(notebook, bg="white")
    notebook.add(tab_dash, text="  Dashboard  ")

    def cargar_dashboard():
        for w in tab_dash.winfo_children():
            w.destroy()

        hoy = datetime.now().strftime("%Y-%m-%d")
        mes = datetime.now().strftime("%Y-%m")
        anio = datetime.now().strftime("%Y")

        # KPIs superiores
        kpi_frame = tk.Frame(tab_dash, bg="white")
        kpi_frame.pack(fill=tk.X, padx=10, pady=10)

        c.execute("SELECT COUNT(*), COALESCE(SUM(total),0) FROM ventas WHERE fecha=?", (hoy,))
        v_hoy, t_hoy = c.fetchone()
        c.execute("SELECT COUNT(*), COALESCE(SUM(total),0) FROM ventas WHERE fecha LIKE ?", (f"{mes}%",))
        v_mes, t_mes = c.fetchone()
        c.execute("SELECT COUNT(*), COALESCE(SUM(total),0) FROM ventas WHERE fecha LIKE ?", (f"{anio}%",))
        v_anio, t_anio = c.fetchone()

        # Ticket promedio
        ticket_prom = t_hoy / v_hoy if v_hoy > 0 else 0
        # Clientes hoy
        c.execute("SELECT COUNT(DISTINCT cliente_id) FROM ventas WHERE fecha=? AND cliente_id>1", (hoy,))
        clientes_hoy = c.fetchone()[0]

        kpis = [
            ("VENTAS HOY", f"${t_hoy:,.2f}", f"{v_hoy} ventas", "#2196F3"),
            ("VENTAS MES", f"${t_mes:,.2f}", f"{v_mes} ventas", "#4CAF50"),
            ("VENTAS AÑO", f"${t_anio:,.2f}", f"{v_anio} ventas", "#FF9800"),
            ("TICKET PROM.", f"${ticket_prom:,.2f}", f"{clientes_hoy} clientes hoy", "#9C27B0"),
        ]
        for i, (titulo, valor, sub, color) in enumerate(kpis):
            card = tk.Frame(kpi_frame, bg=color, relief=tk.FLAT, bd=0)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
            tk.Label(card, text=titulo, font=("Segoe UI", 9, "bold"), bg=color, fg="#EEEEEE").pack(pady=(8,0), padx=10)
            tk.Label(card, text=valor, font=("Segoe UI", 20, "bold"), bg=color, fg="white").pack(padx=10)
            tk.Label(card, text=sub, font=("Segoe UI", 8), bg=color, fg="#FFFFFFAA").pack(pady=(0,8), padx=10)

        # Gráficas en 2 columnas
        graf_frame = tk.Frame(tab_dash, bg="white")
        graf_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        graf_frame.grid_columnconfigure(0, weight=1)
        graf_frame.grid_columnconfigure(1, weight=1)

        # --- Gráfica 1: Ventas últimos 7 días ---
        canvas_7d = tk.Canvas(graf_frame, bg="white", height=250, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_7d.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        datos_7d = []
        labels_7d = []
        for i in range(6, -1, -1):
            d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            d_short = (datetime.now() - timedelta(days=i)).strftime("%d/%m")
            c.execute("SELECT COALESCE(SUM(total),0) FROM ventas WHERE fecha=?", (d,))
            val = c.fetchone()[0]
            datos_7d.append(val)
            labels_7d.append(d_short)

        canvas_7d.update_idletasks()
        w7 = max(canvas_7d.winfo_width(), 400)
        dibujar_lineas(canvas_7d, [("Ventas $", datos_7d, "#2196F3")], w7, 250,
                      titulo="Ventas últimos 7 días", labels_x=labels_7d)

        # --- Gráfica 2: Ventas por método de pago (pastel) ---
        canvas_pago = tk.Canvas(graf_frame, bg="white", height=250, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_pago.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        c.execute("SELECT COALESCE(SUM(monto_efectivo),0) FROM ventas WHERE fecha LIKE ?", (f"{mes}%",))
        efec_mes = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(monto_tarjeta),0) FROM ventas WHERE fecha LIKE ?", (f"{mes}%",))
        tarj_mes = c.fetchone()[0]
        otros_mes = max(t_mes - efec_mes - tarj_mes, 0)

        datos_pago = []
        if efec_mes > 0: datos_pago.append(("Efectivo", efec_mes))
        if tarj_mes > 0: datos_pago.append(("Tarjeta", tarj_mes))
        if otros_mes > 0: datos_pago.append(("Otros", otros_mes))

        canvas_pago.update_idletasks()
        wp = max(canvas_pago.winfo_width(), 400)
        dibujar_pastel(canvas_pago, datos_pago, wp//2, 140, 80, titulo="Métodos de pago (mes)")

        # --- Gráfica 3: Top 5 categorías ---
        canvas_cat = tk.Canvas(graf_frame, bg="white", height=220, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_cat.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        c.execute("""SELECT p.categoria, SUM(dv.subtotal) as total FROM detalle_ventas dv
                     JOIN productos p ON dv.producto_id=p.id
                     JOIN ventas v ON dv.venta_id=v.id WHERE v.fecha LIKE ?
                     GROUP BY p.categoria ORDER BY total DESC LIMIT 5""", (f"{mes}%",))
        datos_cat = [(r[0] or "Sin cat.", r[1]) for r in c.fetchall()]

        canvas_cat.update_idletasks()
        wc = max(canvas_cat.winfo_width(), 400)
        dibujar_barras(canvas_cat, datos_cat, wc, 220, titulo="Top 5 categorías (mes)", horizontal=True)

        # --- Gráfica 4: Top 5 vendedores ---
        canvas_vend = tk.Canvas(graf_frame, bg="white", height=220, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_vend.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        c.execute("""SELECT e.nombre, SUM(v.total) FROM ventas v
                     JOIN empleados e ON v.vendedor_id=e.id WHERE v.fecha LIKE ?
                     GROUP BY v.vendedor_id ORDER BY SUM(v.total) DESC LIMIT 5""", (f"{mes}%",))
        datos_vend = [(r[0] or "Desconocido", r[1]) for r in c.fetchall()]

        canvas_vend.update_idletasks()
        wv = max(canvas_vend.winfo_width(), 400)
        dibujar_barras(canvas_vend, datos_vend, wv, 220, titulo="Top 5 vendedores (mes)", horizontal=True)

    tab_dash.after(100, cargar_dashboard)

    # ==================== TAB 2: VENTAS DETALLADAS ====================
    tab_ventas = tk.Frame(notebook, bg="white")
    notebook.add(tab_ventas, text="  Ventas Detalladas  ")

    filt_v = tk.Frame(tab_ventas, bg="white")
    filt_v.pack(fill=tk.X, padx=10, pady=8)

    tk.Label(filt_v, text="Desde:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    desde_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-01"))
    tk.Entry(filt_v, textvariable=desde_var, width=12, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=3)
    tk.Label(filt_v, text="Hasta:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    hasta_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    tk.Entry(filt_v, textvariable=hasta_var, width=12, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=3)

    tk.Label(filt_v, text="Agrupar:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    agrupar_var = tk.StringVar(value="DIA")
    ttk.Combobox(filt_v, textvariable=agrupar_var, width=10, state="readonly",
                values=["DIA","SEMANA","MES"]).pack(side=tk.LEFT, padx=3)

    vdet_body = tk.Frame(tab_ventas, bg="white")
    vdet_body.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def cargar_ventas_detalladas():
        for w in vdet_body.winfo_children():
            w.destroy()

        desde = desde_var.get()
        hasta = hasta_var.get()
        agr = agrupar_var.get()

        if agr == "DIA":
            group_expr = "v.fecha"
        elif agr == "SEMANA":
            group_expr = "strftime('%Y-W%W', v.fecha)"
        else:
            group_expr = "strftime('%Y-%m', v.fecha)"

        c.execute(f"""SELECT {group_expr} as periodo, COUNT(*), SUM(v.total),
                     COALESCE(SUM(v.monto_efectivo),0), COALESCE(SUM(v.monto_tarjeta),0),
                     AVG(v.total), COUNT(DISTINCT v.cliente_id)
                     FROM ventas v WHERE v.fecha>=? AND v.fecha<=?
                     GROUP BY periodo ORDER BY periodo DESC""", (desde, hasta))
        rows = c.fetchall()

        # Tabla
        cols_v = ("PERIODO","VENTAS","TOTAL","EFECTIVO","TARJETA","TICKET PROM.","CLIENTES")
        tree_v = ttk.Treeview(vdet_body, columns=cols_v, show="headings", height=10)
        for col in cols_v:
            tree_v.heading(col, text=col)
        tree_v.column("PERIODO", width=110)
        tree_v.column("VENTAS", width=70)
        tree_v.column("TOTAL", width=110)
        tree_v.column("EFECTIVO", width=100)
        tree_v.column("TARJETA", width=100)
        tree_v.column("TICKET PROM.", width=100)
        tree_v.column("CLIENTES", width=80)
        tree_v.pack(fill=tk.X, pady=5)

        totales = [0, 0, 0, 0]
        datos_graf = []
        labels_graf = []
        for r in rows:
            tree_v.insert("", "end", values=(r[0], r[1], f"${r[2]:,.2f}", f"${r[3]:,.2f}",
                          f"${r[4]:,.2f}", f"${r[5]:,.2f}", r[6]))
            totales[0] += r[1]
            totales[1] += r[2]
            totales[2] += r[3]
            totales[3] += r[4]
            datos_graf.append(r[2])
            labels_graf.append(str(r[0])[-5:])

        # Totales
        sum_f = tk.Frame(vdet_body, bg="#E3F2FD", relief=tk.RIDGE, bd=1)
        sum_f.pack(fill=tk.X, pady=5)
        tk.Label(sum_f, text=f"TOTAL: {totales[0]} ventas | ${totales[1]:,.2f} | "
                 f"Efectivo: ${totales[2]:,.2f} | Tarjeta: ${totales[3]:,.2f}",
                 font=("Segoe UI", 10, "bold"), bg="#E3F2FD", fg="#1565C0").pack(pady=6)

        # Gráfica de tendencia
        canvas_tend = tk.Canvas(vdet_body, bg="white", height=200, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_tend.pack(fill=tk.X, pady=5)

        datos_graf.reverse()
        labels_graf.reverse()
        canvas_tend.update_idletasks()
        wt = max(canvas_tend.winfo_width(), 700)
        dibujar_lineas(canvas_tend, [("Ventas $", datos_graf, "#2196F3")], wt, 200,
                      titulo=f"Tendencia de ventas ({agr.lower()})", labels_x=labels_graf)

    tk.Button(filt_v, text="GENERAR", command=cargar_ventas_detalladas,
             bg="#00838F", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=12, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=10)

    # ==================== TAB 3: PRODUCTOS ====================
    tab_prod = tk.Frame(notebook, bg="white")
    notebook.add(tab_prod, text="  Productos  ")

    def cargar_productos_reporte():
        for w in tab_prod.winfo_children():
            w.destroy()

        filt_p = tk.Frame(tab_prod, bg="white")
        filt_p.pack(fill=tk.X, padx=10, pady=8)
        tk.Label(filt_p, text="Periodo:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
        per_p = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        tk.Entry(filt_p, textvariable=per_p, width=10, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=3)

        body_p = tk.Frame(tab_prod, bg="white")
        body_p.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def generar_prod():
            for w in body_p.winfo_children():
                w.destroy()
            mes = per_p.get()

            # Layout 2 columnas
            left_p = tk.Frame(body_p, bg="white")
            left_p.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            right_p = tk.Frame(body_p, bg="white")
            right_p.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

            # Top 15 más vendidos
            tk.Label(left_p, text="TOP 15 MÁS VENDIDOS", font=("Segoe UI", 10, "bold"),
                    bg="white", fg="#00838F").pack(pady=5)

            c.execute("""SELECT p.nombre, SUM(dv.cantidad) as uds, SUM(dv.subtotal) as tot
                         FROM detalle_ventas dv JOIN productos p ON dv.producto_id=p.id
                         JOIN ventas v ON dv.venta_id=v.id WHERE v.fecha LIKE ?
                         GROUP BY dv.producto_id ORDER BY uds DESC LIMIT 15""", (f"{mes}%",))
            top = c.fetchall()

            cols_tp = ("PRODUCTO","UDS","TOTAL")
            tree_tp = ttk.Treeview(left_p, columns=cols_tp, show="headings", height=10)
            for col in cols_tp:
                tree_tp.heading(col, text=col)
            tree_tp.column("PRODUCTO", width=250)
            tree_tp.column("UDS", width=60)
            tree_tp.column("TOTAL", width=90)
            tree_tp.pack(fill=tk.X, pady=3)
            for r in top:
                tree_tp.insert("", "end", values=(r[0][:40], r[1], f"${r[2]:,.2f}"))

            # Gráfica barras top 10
            canvas_tp = tk.Canvas(left_p, bg="white", height=200, relief=tk.RIDGE, bd=1, highlightthickness=0)
            canvas_tp.pack(fill=tk.X, pady=5)
            datos_tp = [(r[0][:12], r[1]) for r in top[:10]]
            canvas_tp.update_idletasks()
            wtp = max(canvas_tp.winfo_width(), 450)
            dibujar_barras(canvas_tp, datos_tp, wtp, 200, titulo="Top 10 (unidades)")

            # Ventas por categoría
            tk.Label(right_p, text="VENTAS POR CATEGORÍA", font=("Segoe UI", 10, "bold"),
                    bg="white", fg="#00838F").pack(pady=5)

            c.execute("""SELECT p.categoria, SUM(dv.cantidad), SUM(dv.subtotal)
                         FROM detalle_ventas dv JOIN productos p ON dv.producto_id=p.id
                         JOIN ventas v ON dv.venta_id=v.id WHERE v.fecha LIKE ?
                         GROUP BY p.categoria ORDER BY SUM(dv.subtotal) DESC""", (f"{mes}%",))
            cats = c.fetchall()

            cols_cat = ("CATEGORÍA","UDS","TOTAL")
            tree_cat = ttk.Treeview(right_p, columns=cols_cat, show="headings", height=8)
            for col in cols_cat:
                tree_cat.heading(col, text=col)
            tree_cat.column("CATEGORÍA", width=150)
            tree_cat.column("UDS", width=70)
            tree_cat.column("TOTAL", width=100)
            tree_cat.pack(fill=tk.X, pady=3)
            for r in cats:
                tree_cat.insert("", "end", values=(r[0] or "Sin cat.", r[1], f"${r[2]:,.2f}"))

            # Pastel categorías
            canvas_cp = tk.Canvas(right_p, bg="white", height=200, relief=tk.RIDGE, bd=1, highlightthickness=0)
            canvas_cp.pack(fill=tk.X, pady=5)
            datos_cp = [(r[0] or "Sin cat.", r[2]) for r in cats[:8]]
            canvas_cp.update_idletasks()
            wcp = max(canvas_cp.winfo_width(), 450)
            dibujar_pastel(canvas_cp, datos_cp, wcp//2, 115, 70, titulo="Distribución por categoría")

        tk.Button(filt_p, text="GENERAR", command=generar_prod,
                 bg="#00838F", fg="white", font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, padx=12, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=10)

    cargar_productos_reporte()

    # ==================== TAB 4: CLIENTES ====================
    tab_cli = tk.Frame(notebook, bg="white")
    notebook.add(tab_cli, text="  Clientes  ")

    def cargar_clientes_reporte():
        for w in tab_cli.winfo_children():
            w.destroy()

        tk.Label(tab_cli, text="ANÁLISIS DE CLIENTES", font=("Segoe UI", 12, "bold"),
                bg="white", fg="#00838F").pack(pady=10)

        body_c = tk.Frame(tab_cli, bg="white")
        body_c.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # KPIs clientes
        kpi_c = tk.Frame(body_c, bg="white")
        kpi_c.pack(fill=tk.X, pady=5)

        c.execute("SELECT COUNT(*) FROM clientes WHERE id>1")
        total_cli = c.fetchone()[0]
        mes = datetime.now().strftime("%Y-%m")
        c.execute("SELECT COUNT(DISTINCT cliente_id) FROM ventas WHERE fecha LIKE ? AND cliente_id>1", (f"{mes}%",))
        cli_activos = c.fetchone()[0]
        c.execute("""SELECT COALESCE(AVG(total),0) FROM (
                     SELECT cliente_id, SUM(total) as total FROM ventas WHERE cliente_id>1
                     GROUP BY cliente_id)""")
        gasto_prom = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(saldo_saturnos),0) FROM monederos WHERE activo=1")
        sat_circ = c.fetchone()[0]

        for i, (titulo, valor, color) in enumerate([
            ("Total clientes", str(total_cli), "#2196F3"),
            ("Activos este mes", str(cli_activos), "#4CAF50"),
            ("Gasto prom/cliente", f"${gasto_prom:,.2f}", "#FF9800"),
            ("Saturnos circulando", f"{sat_circ:,.0f}", "#FFC107"),
        ]):
            cf = tk.Frame(kpi_c, bg=color, relief=tk.FLAT)
            cf.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
            tk.Label(cf, text=titulo, font=("Segoe UI", 8, "bold"), bg=color, fg="#EEEEEE").pack(pady=(6,0), padx=8)
            tk.Label(cf, text=valor, font=("Segoe UI", 16, "bold"), bg=color, fg="white").pack(pady=(0,6), padx=8)

        # Layout 2 columnas
        cols_frame = tk.Frame(body_c, bg="white")
        cols_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Top 10 clientes
        left_c = tk.Frame(cols_frame, bg="white")
        left_c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(left_c, text="TOP 10 CLIENTES (por gasto)", font=("Segoe UI", 10, "bold"),
                bg="white", fg="#00838F").pack(pady=5)

        c.execute("""SELECT cl.nombre, COUNT(v.id), SUM(v.total)
                     FROM ventas v JOIN clientes cl ON v.cliente_id=cl.id WHERE v.cliente_id>1
                     GROUP BY v.cliente_id ORDER BY SUM(v.total) DESC LIMIT 10""")
        top_cli = c.fetchall()

        cols_tc = ("CLIENTE","COMPRAS","TOTAL")
        tree_tc = ttk.Treeview(left_c, columns=cols_tc, show="headings", height=10)
        for col in cols_tc:
            tree_tc.heading(col, text=col)
        tree_tc.column("CLIENTE", width=180)
        tree_tc.column("COMPRAS", width=70)
        tree_tc.column("TOTAL", width=100)
        tree_tc.pack(fill=tk.X, pady=3)
        for r in top_cli:
            tree_tc.insert("", "end", values=(r[0], r[1], f"${r[2]:,.2f}"))

        # Gráfica
        canvas_tc = tk.Canvas(left_c, bg="white", height=200, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_tc.pack(fill=tk.X, pady=3)
        datos_tc = [(r[0][:15], r[2]) for r in top_cli[:8]]
        canvas_tc.update_idletasks()
        wtc = max(canvas_tc.winfo_width(), 400)
        dibujar_barras(canvas_tc, datos_tc, wtc, 200, titulo="Top clientes ($)", horizontal=True)

        # Frecuencia de compra
        right_c = tk.Frame(cols_frame, bg="white")
        right_c.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(right_c, text="FRECUENCIA DE COMPRA", font=("Segoe UI", 10, "bold"),
                bg="white", fg="#00838F").pack(pady=5)

        c.execute("""SELECT CASE
                     WHEN cnt>=20 THEN 'Frecuente (20+)'
                     WHEN cnt>=10 THEN 'Regular (10-19)'
                     WHEN cnt>=5 THEN 'Ocasional (5-9)'
                     WHEN cnt>=2 THEN 'Esporádico (2-4)'
                     ELSE 'Una vez (1)' END as seg, COUNT(*) as total
                     FROM (SELECT cliente_id, COUNT(*) as cnt FROM ventas WHERE cliente_id>1
                     GROUP BY cliente_id)
                     GROUP BY seg ORDER BY MIN(cnt) DESC""")
        freq = c.fetchall()

        canvas_freq = tk.Canvas(right_c, bg="white", height=220, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_freq.pack(fill=tk.X, pady=3)
        datos_freq = [(r[0], r[1]) for r in freq]
        canvas_freq.update_idletasks()
        wfr = max(canvas_freq.winfo_width(), 400)
        dibujar_pastel(canvas_freq, datos_freq, wfr//2, 125, 75, titulo="Segmentación de clientes")

        # Nuevos vs recurrentes
        tk.Label(right_c, text="CLIENTES POR MES", font=("Segoe UI", 10, "bold"),
                bg="white", fg="#00838F").pack(pady=5)
        canvas_cm = tk.Canvas(right_c, bg="white", height=180, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_cm.pack(fill=tk.X, pady=3)

        datos_cm = []
        labels_cm = []
        for i in range(5, -1, -1):
            d = datetime.now() - timedelta(days=i*30)
            m = d.strftime("%Y-%m")
            ml = d.strftime("%b")
            c.execute("SELECT COUNT(DISTINCT cliente_id) FROM ventas WHERE fecha LIKE ? AND cliente_id>1", (f"{m}%",))
            datos_cm.append(c.fetchone()[0])
            labels_cm.append(ml)

        canvas_cm.update_idletasks()
        wcm = max(canvas_cm.winfo_width(), 400)
        dibujar_lineas(canvas_cm, [("Clientes activos", datos_cm, "#4CAF50")], wcm, 180,
                      titulo="Clientes activos por mes", labels_x=labels_cm)

    tab_cli.after(200, cargar_clientes_reporte)

    # ==================== TAB 5: INVENTARIO ====================
    tab_inv = tk.Frame(notebook, bg="white")
    notebook.add(tab_inv, text="  Inventario  ")

    def cargar_inventario_reporte():
        for w in tab_inv.winfo_children():
            w.destroy()

        tk.Label(tab_inv, text="ANÁLISIS DE INVENTARIO", font=("Segoe UI", 12, "bold"),
                bg="white", fg="#00838F").pack(pady=10)

        body_i = tk.Frame(tab_inv, bg="white")
        body_i.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # KPIs
        kpi_i = tk.Frame(body_i, bg="white")
        kpi_i.pack(fill=tk.X, pady=5)

        c.execute("SELECT COUNT(*) FROM productos")
        total_prods = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(stock * precio_costo),0) FROM productos")
        valor_inv = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM productos WHERE stock<=10")
        stock_bajo = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM productos WHERE stock=0")
        agotados = c.fetchone()[0]

        for titulo, valor, color in [
            ("Total productos", f"{total_prods:,}", "#2196F3"),
            ("Valor inventario", f"${valor_inv:,.0f}", "#4CAF50"),
            ("Stock bajo (<=10)", str(stock_bajo), "#FF9800"),
            ("Agotados", str(agotados), "#D32F2F"),
        ]:
            cf = tk.Frame(kpi_i, bg=color, relief=tk.FLAT)
            cf.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
            tk.Label(cf, text=titulo, font=("Segoe UI", 8, "bold"), bg=color, fg="#EEEEEE").pack(pady=(6,0), padx=8)
            tk.Label(cf, text=valor, font=("Segoe UI", 16, "bold"), bg=color, fg="white").pack(pady=(0,6), padx=8)

        cols_fr = tk.Frame(body_i, bg="white")
        cols_fr.pack(fill=tk.BOTH, expand=True, pady=5)

        # Stock por categoría
        left_i = tk.Frame(cols_fr, bg="white")
        left_i.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(left_i, text="VALOR POR CATEGORÍA", font=("Segoe UI", 10, "bold"),
                bg="white", fg="#00838F").pack(pady=5)

        c.execute("""SELECT categoria, COUNT(*), SUM(stock), SUM(stock*precio_costo)
                     FROM productos GROUP BY categoria ORDER BY SUM(stock*precio_costo) DESC""")
        cat_inv = c.fetchall()

        cols_ci = ("CATEGORÍA","PRODS","STOCK","VALOR")
        tree_ci = ttk.Treeview(left_i, columns=cols_ci, show="headings", height=6)
        for col in cols_ci:
            tree_ci.heading(col, text=col)
        tree_ci.column("CATEGORÍA", width=120)
        tree_ci.column("PRODS", width=60)
        tree_ci.column("STOCK", width=70)
        tree_ci.column("VALOR", width=100)
        tree_ci.pack(fill=tk.X, pady=3)
        for r in cat_inv:
            tree_ci.insert("", "end", values=(r[0] or "Sin cat.", r[1], f"{r[2]:,}", f"${r[3]:,.0f}"))

        canvas_ci = tk.Canvas(left_i, bg="white", height=200, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_ci.pack(fill=tk.X, pady=3)
        datos_ci = [(r[0] or "Sin cat.", r[3]) for r in cat_inv[:6]]
        canvas_ci.update_idletasks()
        wci = max(canvas_ci.winfo_width(), 400)
        dibujar_pastel(canvas_ci, datos_ci, wci//2, 115, 70, titulo="Valor por categoría")

        # Productos con stock bajo
        right_i = tk.Frame(cols_fr, bg="white")
        right_i.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(right_i, text="PRODUCTOS CON STOCK BAJO", font=("Segoe UI", 10, "bold"),
                bg="white", fg="#D32F2F").pack(pady=5)

        c.execute("SELECT codigo, nombre, stock, precio_venta FROM productos WHERE stock<=10 ORDER BY stock ASC LIMIT 20")
        bajo = c.fetchall()

        cols_sb = ("CÓDIGO","PRODUCTO","STOCK","PRECIO")
        tree_sb = ttk.Treeview(right_i, columns=cols_sb, show="headings", height=12)
        for col in cols_sb:
            tree_sb.heading(col, text=col)
        tree_sb.column("CÓDIGO", width=80)
        tree_sb.column("PRODUCTO", width=200)
        tree_sb.column("STOCK", width=55)
        tree_sb.column("PRECIO", width=70)
        tree_sb.pack(fill=tk.BOTH, expand=True, pady=3)
        for r in bajo:
            tree_sb.insert("", "end", values=(r[0], r[1][:35], r[2], f"${r[3]:,.2f}"))

        # Rotación de inventario
        tk.Label(right_i, text="ROTACIÓN (más vendidos vs stock)", font=("Segoe UI", 9, "bold"),
                bg="white", fg="#00838F").pack(pady=(8,3))
        canvas_rot = tk.Canvas(right_i, bg="white", height=160, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_rot.pack(fill=tk.X, pady=3)

        mes = datetime.now().strftime("%Y-%m")
        c.execute("""SELECT p.nombre, SUM(dv.cantidad) as vendido, p.stock
                     FROM detalle_ventas dv JOIN productos p ON dv.producto_id=p.id
                     JOIN ventas v ON dv.venta_id=v.id WHERE v.fecha LIKE ?
                     GROUP BY dv.producto_id ORDER BY vendido DESC LIMIT 8""", (f"{mes}%",))
        rot = c.fetchall()

        canvas_rot.update_idletasks()
        wr = max(canvas_rot.winfo_width(), 400)
        if rot:
            datos_rot_v = [(r[0][:10], r[1]) for r in rot]
            dibujar_barras(canvas_rot, datos_rot_v, wr, 160, titulo="Unidades vendidas (mes)")

    tab_inv.after(300, cargar_inventario_reporte)

    # ==================== TAB 6: SATURNOS & OFERTAS ====================
    tab_so = tk.Frame(notebook, bg="white")
    notebook.add(tab_so, text="  Saturnos & Ofertas  ")

    def cargar_so_reporte():
        for w in tab_so.winfo_children():
            w.destroy()

        tk.Label(tab_so, text="REPORTES SATURNOS Y OFERTAS", font=("Segoe UI", 12, "bold"),
                bg="white", fg="#00838F").pack(pady=10)

        body_so = tk.Frame(tab_so, bg="white")
        body_so.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        hoy = datetime.now().strftime("%Y-%m-%d")
        mes = datetime.now().strftime("%Y-%m")

        # KPIs
        kpi_so = tk.Frame(body_so, bg="white")
        kpi_so.pack(fill=tk.X, pady=5)

        c.execute("SELECT COALESCE(SUM(saldo_saturnos),0) FROM monederos WHERE activo=1")
        sat_circ = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(cantidad),0) FROM movimientos_saturnos WHERE tipo='ACUMULACION' AND fecha LIKE ?", (f"{mes}%",))
        acum_mes = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(ABS(cantidad)),0) FROM movimientos_saturnos WHERE tipo='REDIMIR' AND fecha LIKE ?", (f"{mes}%",))
        red_mes = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM ofertas WHERE activa=1 AND fecha_inicio<=? AND fecha_fin>=?", (hoy, hoy))
        ofertas_act = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(descuento_aplicado),0) FROM ofertas_aplicadas WHERE fecha LIKE ?", (f"{mes}%",))
        desc_mes = c.fetchone()[0]

        for titulo, valor, color in [
            ("Saturnos circulando", f"{sat_circ:,.0f} \u20B4", "#FFC107"),
            ("Acumulados (mes)", f"+{acum_mes:,.0f}", "#4CAF50"),
            ("Redimidos (mes)", f"-{red_mes:,.0f}", "#D32F2F"),
            ("Ofertas activas", str(ofertas_act), "#FF5722"),
            ("Desc. ofertas (mes)", f"${desc_mes:,.2f}", "#9C27B0"),
        ]:
            cf = tk.Frame(kpi_so, bg=color, relief=tk.FLAT)
            cf.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            tk.Label(cf, text=titulo, font=("Segoe UI", 7, "bold"), bg=color, fg="#EEEEEE").pack(pady=(5,0), padx=6)
            tk.Label(cf, text=valor, font=("Segoe UI", 14, "bold"), bg=color, fg="white").pack(pady=(0,5), padx=6)

        cols_so = tk.Frame(body_so, bg="white")
        cols_so.pack(fill=tk.BOTH, expand=True, pady=5)

        # Saturnos últimos 6 meses
        left_so = tk.Frame(cols_so, bg="white")
        left_so.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(left_so, text="SATURNOS ÚLTIMOS 6 MESES", font=("Segoe UI", 10, "bold"),
                bg="white", fg="#FFC107").pack(pady=5)

        canvas_sat_m = tk.Canvas(left_so, bg="white", height=220, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_sat_m.pack(fill=tk.X, pady=3)

        acum_6 = []
        red_6 = []
        labels_6 = []
        for i in range(5, -1, -1):
            d = datetime.now() - timedelta(days=i*30)
            m = d.strftime("%Y-%m")
            ml = d.strftime("%b")
            c.execute("SELECT COALESCE(SUM(cantidad),0) FROM movimientos_saturnos WHERE tipo='ACUMULACION' AND fecha LIKE ?", (f"{m}%",))
            acum_6.append(c.fetchone()[0])
            c.execute("SELECT COALESCE(SUM(ABS(cantidad)),0) FROM movimientos_saturnos WHERE tipo='REDIMIR' AND fecha LIKE ?", (f"{m}%",))
            red_6.append(c.fetchone()[0])
            labels_6.append(ml)

        canvas_sat_m.update_idletasks()
        wsm = max(canvas_sat_m.winfo_width(), 400)
        dibujar_lineas(canvas_sat_m,
                      [("Acumulados", acum_6, "#4CAF50"), ("Redimidos", red_6, "#D32F2F")],
                      wsm, 220, titulo="Saturnos acumulados vs redimidos", labels_x=labels_6)

        # Top monederos
        tk.Label(left_so, text="TOP 10 MONEDEROS", font=("Segoe UI", 10, "bold"),
                bg="white", fg="#FFC107").pack(pady=5)
        c.execute("""SELECT cl.nombre, m.saldo_saturnos FROM monederos m
                     JOIN clientes cl ON m.cliente_id=cl.id WHERE m.activo=1
                     ORDER BY m.saldo_saturnos DESC LIMIT 10""")
        top_sat = c.fetchall()
        canvas_ts = tk.Canvas(left_so, bg="white", height=180, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_ts.pack(fill=tk.X, pady=3)
        datos_ts = [(r[0][:15], r[1]) for r in top_sat]
        canvas_ts.update_idletasks()
        wts = max(canvas_ts.winfo_width(), 400)
        dibujar_barras(canvas_ts, datos_ts, wts, 180, titulo="Saldo Saturnos", horizontal=True)

        # Ofertas
        right_so = tk.Frame(cols_so, bg="white")
        right_so.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(right_so, text="DESCUENTOS POR OFERTA", font=("Segoe UI", 10, "bold"),
                bg="white", fg="#FF5722").pack(pady=5)

        c.execute("""SELECT o.nombre, SUM(oa.descuento_aplicado), SUM(oa.cantidad)
                     FROM ofertas_aplicadas oa JOIN ofertas o ON oa.oferta_id=o.id
                     WHERE oa.fecha LIKE ?
                     GROUP BY o.id ORDER BY SUM(oa.descuento_aplicado) DESC LIMIT 8""", (f"{mes}%",))
        of_desc = c.fetchall()

        canvas_of = tk.Canvas(right_so, bg="white", height=200, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_of.pack(fill=tk.X, pady=3)
        datos_of = [(r[0][:15], r[1]) for r in of_desc]
        canvas_of.update_idletasks()
        wof = max(canvas_of.winfo_width(), 400)
        dibujar_barras(canvas_of, datos_of, wof, 200, titulo="Descuentos otorgados ($)", horizontal=True)

        # Ofertas por tipo
        tk.Label(right_so, text="OFERTAS POR TIPO", font=("Segoe UI", 10, "bold"),
                bg="white", fg="#FF5722").pack(pady=5)

        c.execute("SELECT tipo, COUNT(*) FROM ofertas GROUP BY tipo ORDER BY COUNT(*) DESC")
        of_tipo = c.fetchall()
        canvas_ot = tk.Canvas(right_so, bg="white", height=200, relief=tk.RIDGE, bd=1, highlightthickness=0)
        canvas_ot.pack(fill=tk.X, pady=3)
        datos_ot = [(r[0], r[1]) for r in of_tipo]
        canvas_ot.update_idletasks()
        wot = max(canvas_ot.winfo_width(), 400)
        dibujar_pastel(canvas_ot, datos_ot, wot//2, 115, 70, titulo="Distribución por tipo")

        # Saturnos extra por ofertas
        tk.Label(right_so, text="SATURNOS EXTRA (ofertas)", font=("Segoe UI", 10, "bold"),
                bg="white", fg="#FFC107").pack(pady=5)
        c.execute("SELECT COALESCE(SUM(saturnos_extra),0) FROM ofertas_aplicadas WHERE fecha LIKE ?", (f"{mes}%",))
        sat_extra_mes = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(saturnos_extra),0) FROM ofertas_aplicadas WHERE fecha=?", (hoy,))
        sat_extra_hoy = c.fetchone()[0]
        info_se = tk.Frame(right_so, bg="#FFF8E1", relief=tk.RIDGE, bd=1)
        info_se.pack(fill=tk.X, pady=3)
        tk.Label(info_se, text=f"Hoy: {sat_extra_hoy:,.0f} \u20B4  |  Mes: {sat_extra_mes:,.0f} \u20B4",
                font=("Segoe UI", 11, "bold"), bg="#FFF8E1", fg="#F57F17").pack(pady=6)

    tab_so.after(400, cargar_so_reporte)

    # ==================== TAB 7: EXPORTAR ====================
    tab_exp = tk.Frame(notebook, bg="white")
    notebook.add(tab_exp, text="  Exportar  ")

    tk.Label(tab_exp, text="EXPORTAR REPORTES", font=("Segoe UI", 14, "bold"),
            bg="white", fg="#00838F").pack(pady=20)

    exp_frame = tk.Frame(tab_exp, bg="white")
    exp_frame.pack(padx=30, pady=10)

    def exportar_csv(tipo):
        base = os.path.dirname(os.path.abspath(__file__))
        reportes_dir = os.path.join(base, "reportes")
        os.makedirs(reportes_dir, exist_ok=True)
        ahora = datetime.now().strftime("%Y%m%d_%H%M%S")

        if tipo == "ventas":
            ruta = os.path.join(reportes_dir, f"ventas_{ahora}.csv")
            c.execute("""SELECT v.folio, v.fecha, v.hora, e.nombre, cl.nombre, v.total, v.tipo_pago,
                         v.monto_efectivo, v.monto_tarjeta
                         FROM ventas v LEFT JOIN empleados e ON v.vendedor_id=e.id
                         LEFT JOIN clientes cl ON v.cliente_id=cl.id
                         ORDER BY v.fecha DESC, v.hora DESC""")
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("FOLIO,FECHA,HORA,VENDEDOR,CLIENTE,TOTAL,TIPO_PAGO,EFECTIVO,TARJETA\n")
                for r in c.fetchall():
                    f.write(",".join(str(x or "") for x in r) + "\n")

        elif tipo == "productos":
            ruta = os.path.join(reportes_dir, f"productos_{ahora}.csv")
            c.execute("SELECT codigo, nombre, categoria, laboratorio, precio_costo, precio_venta, stock FROM productos ORDER BY nombre")
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("CODIGO,NOMBRE,CATEGORIA,LABORATORIO,COSTO,PRECIO_VENTA,STOCK\n")
                for r in c.fetchall():
                    f.write(",".join(str(x or "") for x in r) + "\n")

        elif tipo == "clientes":
            ruta = os.path.join(reportes_dir, f"clientes_{ahora}.csv")
            c.execute("""SELECT cl.nombre, cl.telefono, cl.email, cl.direccion,
                         COALESCE(m.saldo_saturnos,0), COUNT(v.id), COALESCE(SUM(v.total),0)
                         FROM clientes cl LEFT JOIN monederos m ON cl.id=m.cliente_id
                         LEFT JOIN ventas v ON cl.id=v.cliente_id WHERE cl.id>1
                         GROUP BY cl.id ORDER BY COALESCE(SUM(v.total),0) DESC""")
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("NOMBRE,TELEFONO,EMAIL,DIRECCION,SATURNOS,NUM_COMPRAS,TOTAL_GASTADO\n")
                for r in c.fetchall():
                    f.write(",".join(str(x or "") for x in r) + "\n")

        elif tipo == "inventario":
            ruta = os.path.join(reportes_dir, f"inventario_{ahora}.csv")
            c.execute("SELECT codigo, nombre, categoria, laboratorio, stock, precio_costo, precio_venta, stock*precio_costo as valor FROM productos ORDER BY categoria, nombre")
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("CODIGO,NOMBRE,CATEGORIA,LABORATORIO,STOCK,COSTO,PRECIO_VENTA,VALOR_INVENTARIO\n")
                for r in c.fetchall():
                    f.write(",".join(str(x or "") for x in r) + "\n")

        elif tipo == "saturnos":
            ruta = os.path.join(reportes_dir, f"saturnos_{ahora}.csv")
            c.execute("""SELECT cl.nombre, m.saldo_saturnos, m.total_acumulado, m.total_gastado,
                         m.codigo_tarjeta, m.estado_tarjeta, m.fecha_alta
                         FROM monederos m JOIN clientes cl ON m.cliente_id=cl.id ORDER BY m.saldo_saturnos DESC""")
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("CLIENTE,SALDO,ACUMULADO,GASTADO,TARJETA,ESTADO,FECHA_ALTA\n")
                for r in c.fetchall():
                    f.write(",".join(str(x or "") for x in r) + "\n")
        else:
            return

        messagebox.showinfo("Exportado", f"Reporte exportado a:\n{ruta}")

    reportes_disponibles = [
        ("Reporte de Ventas", "ventas", "#2196F3",
         "Exporta todas las ventas con folio, fecha, vendedor, cliente, total y forma de pago"),
        ("Reporte de Productos", "productos", "#4CAF50",
         "Lista completa de productos con código, categoría, precios y stock"),
        ("Reporte de Clientes", "clientes", "#FF9800",
         "Clientes con datos de contacto, saldo Saturnos, número de compras y gasto total"),
        ("Reporte de Inventario", "inventario", "#9C27B0",
         "Inventario completo con valorización por producto"),
        ("Reporte de Saturnos", "saturnos", "#FFC107",
         "Monederos Saturnos con saldos, tarjetas y movimientos"),
    ]

    for i, (titulo, tipo, color, desc) in enumerate(reportes_disponibles):
        card = tk.Frame(exp_frame, bg="white", relief=tk.RIDGE, bd=1)
        card.grid(row=i, column=0, columnspan=3, sticky="ew", pady=4, padx=5)
        exp_frame.grid_columnconfigure(1, weight=1)

        tk.Label(card, text="\u2261", font=("Segoe UI", 18), bg=color, fg="white", width=3).pack(side=tk.LEFT, fill=tk.Y)
        info_f = tk.Frame(card, bg="white")
        info_f.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=6)
        tk.Label(info_f, text=titulo, font=("Segoe UI", 11, "bold"), bg="white", fg="#333").pack(anchor="w")
        tk.Label(info_f, text=desc, font=("Segoe UI", 8), bg="white", fg="#757575").pack(anchor="w")
        tk.Button(card, text="EXPORTAR CSV", command=lambda t=tipo: exportar_csv(t),
                 bg=color, fg="white", font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, padx=14, pady=6, cursor="hand2").pack(side=tk.RIGHT, padx=10, pady=6)


# ===== MÓDULO OFERTAS Y PROMOCIONES =====
def ver_ofertas():
    limpiar()

    header_mod = tk.Frame(main, bg="#FF5722", height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="\u2605 OFERTAS Y PROMOCIONES", font=("Segoe UI", 13, "bold"),
            bg="#FF5722", fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    notebook = ttk.Notebook(main)
    notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # ==================== PESTAÑA OFERTAS ACTIVAS ====================
    tab_activas = tk.Frame(notebook, bg="white")
    notebook.add(tab_activas, text="  Ofertas Activas  ")

    toolbar_act = tk.Frame(tab_activas, bg="white")
    toolbar_act.pack(fill=tk.X, padx=10, pady=8)

    tk.Label(toolbar_act, text="Buscar:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    busq_act = tk.Entry(toolbar_act, width=20, font=("Segoe UI", 9))
    busq_act.pack(side=tk.LEFT, padx=5)

    tk.Label(toolbar_act, text="Tipo:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    tipo_filtro = tk.StringVar(value="TODOS")
    ttk.Combobox(toolbar_act, textvariable=tipo_filtro, width=18, state="readonly",
                values=["TODOS","DESCUENTO_PORCENTAJE","DESCUENTO_MONTO","2X1","3X2","COMBO"]).pack(side=tk.LEFT, padx=5)

    tk.Label(toolbar_act, text="Estado:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    estado_filtro = tk.StringVar(value="ACTIVA")
    ttk.Combobox(toolbar_act, textvariable=estado_filtro, width=12, state="readonly",
                values=["ACTIVA","VENCIDA","PAUSADA","TODAS"]).pack(side=tk.LEFT, padx=5)

    cols_of = ("FOLIO", "NOMBRE", "TIPO", "DESCUENTO", "BONUS \u20B4", "INICIO", "FIN", "VENDIDAS", "ESTADO")
    tree_of = ttk.Treeview(tab_activas, columns=cols_of, show="headings", height=14)
    for col in cols_of:
        tree_of.heading(col, text=col)
    tree_of.column("FOLIO", width=120)
    tree_of.column("NOMBRE", width=180)
    tree_of.column("TIPO", width=130)
    tree_of.column("DESCUENTO", width=90)
    tree_of.column("BONUS \u20B4", width=70)
    tree_of.column("INICIO", width=90)
    tree_of.column("FIN", width=90)
    tree_of.column("VENDIDAS", width=75)
    tree_of.column("ESTADO", width=80)
    scroll_of = ttk.Scrollbar(tab_activas, orient="vertical", command=tree_of.yview)
    tree_of.configure(yscrollcommand=scroll_of.set)
    tree_of.pack(fill=tk.BOTH, expand=True, padx=10, pady=5, side=tk.LEFT)
    scroll_of.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def cargar_ofertas_activas(filtro=""):
        for item in tree_of.get_children():
            tree_of.delete(item)
        hoy = datetime.now().strftime("%Y-%m-%d")
        q = "SELECT folio, nombre, tipo, descuento_porcentaje, descuento_monto, bonus_saturnos_extra, fecha_inicio, fecha_fin, unidades_vendidas, limite_total, activa FROM ofertas WHERE 1=1"
        params = []
        if filtro:
            q += " AND (nombre LIKE ? OR folio LIKE ?)"
            params += [f"%{filtro}%", f"%{filtro}%"]
        if tipo_filtro.get() != "TODOS":
            q += " AND tipo=?"
            params.append(tipo_filtro.get())
        ef = estado_filtro.get()
        if ef == "ACTIVA":
            q += " AND activa=1 AND fecha_fin>=?"
            params.append(hoy)
        elif ef == "VENCIDA":
            q += " AND fecha_fin<?"
            params.append(hoy)
        elif ef == "PAUSADA":
            q += " AND activa=0"
        q += " ORDER BY fecha_creacion DESC"
        c.execute(q, params)
        for row in c.fetchall():
            folio, nombre, tipo, pct, monto, bonus, f_ini, f_fin, vendidas, limite, activa = row
            if tipo in ("DESCUENTO_PORCENTAJE", "2X1", "3X2"):
                desc_txt = f"-{pct:.0f}%" if pct else tipo
            else:
                desc_txt = f"${monto:.0f} OFF" if monto else "-"
            if tipo == "2X1":
                desc_txt = "2x1"
            elif tipo == "3X2":
                desc_txt = "3x2"
            vendidas_txt = f"{vendidas}/{limite}" if limite > 0 else str(vendidas)
            hoy_d = datetime.now().strftime("%Y-%m-%d")
            if not activa:
                estado = "PAUSADA"
            elif f_fin < hoy_d:
                estado = "VENCIDA"
            else:
                estado = "ACTIVA"
            tree_of.insert("", "end", values=(folio, nombre, tipo, desc_txt,
                           f"+{bonus:.0f}%", f_ini, f_fin, vendidas_txt, estado))

    def filtrar_ofertas(event=None):
        cargar_ofertas_activas(busq_act.get())

    busq_act.bind("<KeyRelease>", filtrar_ofertas)
    tk.Button(toolbar_act, text="FILTRAR", command=filtrar_ofertas,
             bg="#FF5722", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=5)

    # Botones acción ofertas activas
    acc_frame = tk.Frame(tab_activas, bg="white")
    acc_frame.pack(fill=tk.X, padx=10, pady=5, before=tree_of)

    def desactivar_oferta():
        sel = tree_of.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una oferta")
            return
        folio = tree_of.item(sel[0])["values"][0]
        estado = tree_of.item(sel[0])["values"][8]
        if estado == "ACTIVA":
            c.execute("UPDATE ofertas SET activa=0, modificado_por=?, fecha_modificacion=? WHERE folio=?",
                      (usuario_actual, datetime.now().strftime("%Y-%m-%d %H:%M"), folio))
            msg = "Oferta pausada"
        else:
            c.execute("UPDATE ofertas SET activa=1, modificado_por=?, fecha_modificacion=? WHERE folio=?",
                      (usuario_actual, datetime.now().strftime("%Y-%m-%d %H:%M"), folio))
            msg = "Oferta reactivada"
        conn.commit()
        cargar_ofertas_activas()
        messagebox.showinfo("Oferta", msg)

    def duplicar_oferta():
        sel = tree_of.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una oferta")
            return
        folio_orig = tree_of.item(sel[0])["values"][0]
        c.execute("SELECT * FROM ofertas WHERE folio=?", (folio_orig,))
        row = c.fetchone()
        if not row:
            return
        ahora = datetime.now()
        nuevo_folio = f"OF-{ahora.strftime('%Y%m%d%H%M%S')}"
        c.execute("""INSERT INTO ofertas (folio,nombre,descripcion,tipo,descuento_porcentaje,descuento_monto,
                    bonus_saturnos_extra,aplica_a,productos_ids,categorias,laboratorios,excluir_controlados,
                    fecha_inicio,fecha_fin,dias_semana,hora_inicio,hora_fin,limite_por_cliente,limite_total,
                    unidades_vendidas,activa,destacada,color_banner,creado_por,fecha_creacion)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,0,0,?,?,?)""",
                  (nuevo_folio, f"Copia - {row[2]}", row[3], row[4], row[5], row[6], row[7],
                   row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15],
                   row[16], row[17], row[18], row[19], row[23],
                   usuario_actual, ahora.strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        cargar_ofertas_activas()
        messagebox.showinfo("Duplicar", f"Oferta duplicada: {nuevo_folio}")

    tk.Button(acc_frame, text="PAUSAR/ACTIVAR", command=desactivar_oferta,
             bg="#FF9800", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=4)
    tk.Button(acc_frame, text="DUPLICAR", command=duplicar_oferta,
             bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=4)

    cargar_ofertas_activas()

    # ==================== PESTAÑA CREAR OFERTA ====================
    tab_crear = tk.Frame(notebook, bg="white")
    notebook.add(tab_crear, text="  Crear Oferta  ")

    canvas_crear = tk.Canvas(tab_crear, bg="white", highlightthickness=0)
    scrollbar_crear = ttk.Scrollbar(tab_crear, orient="vertical", command=canvas_crear.yview)
    form_crear = tk.Frame(canvas_crear, bg="white")

    form_crear.bind("<Configure>", lambda e: canvas_crear.configure(scrollregion=canvas_crear.bbox("all")))
    canvas_crear.create_window((0, 0), window=form_crear, anchor="nw")
    canvas_crear.configure(yscrollcommand=scrollbar_crear.set)
    canvas_crear.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_crear.pack(side=tk.RIGHT, fill=tk.Y)

    # Sección 1: Info General
    tk.Label(form_crear, text="SECCIÓN 1: INFORMACIÓN GENERAL", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#FF5722").grid(row=0, column=0, columnspan=3, pady=(15, 5), padx=15, sticky="w")

    tk.Label(form_crear, text="Nombre:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=1, column=0, sticky="e", padx=10, pady=5)
    nombre_of_var = tk.StringVar()
    tk.Entry(form_crear, textvariable=nombre_of_var, width=40, font=("Segoe UI", 10)).grid(row=1, column=1, padx=5, pady=5, sticky="w")

    tk.Label(form_crear, text="Descripción:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=2, column=0, sticky="ne", padx=10, pady=5)
    desc_text = tk.Text(form_crear, width=40, height=3, font=("Segoe UI", 9))
    desc_text.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    tk.Label(form_crear, text="Color banner:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=3, column=0, sticky="e", padx=10, pady=5)
    color_of_var = tk.StringVar(value="#FF5722")
    color_entry = tk.Entry(form_crear, textvariable=color_of_var, width=12, font=("Segoe UI", 10))
    color_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
    color_preview = tk.Label(form_crear, text="   ", bg="#FF5722", width=4, relief=tk.RIDGE)
    color_preview.grid(row=3, column=2, padx=5)
    def actualizar_color(*args):
        try:
            color_preview.config(bg=color_of_var.get())
        except:
            pass
    color_of_var.trace_add("write", actualizar_color)

    # Sección 2: Tipo de Oferta
    tk.Label(form_crear, text="SECCIÓN 2: TIPO DE OFERTA", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#FF5722").grid(row=4, column=0, columnspan=3, pady=(15, 5), padx=15, sticky="w")

    tipo_of_var = tk.StringVar(value="DESCUENTO_PORCENTAJE")
    tipos_oferta = [
        ("Descuento Porcentaje (% OFF)", "DESCUENTO_PORCENTAJE"),
        ("Descuento Monto Fijo ($ OFF)", "DESCUENTO_MONTO"),
        ("2x1 (Compra 2, paga 1)", "2X1"),
        ("3x2 (Compra 3, paga 2)", "3X2"),
        ("Combo/Paquete", "COMBO"),
    ]
    for i, (label, val) in enumerate(tipos_oferta):
        tk.Radiobutton(form_crear, text=label, variable=tipo_of_var, value=val,
                      font=("Segoe UI", 9), bg="white").grid(row=5+i, column=0, columnspan=2, sticky="w", padx=30)

    tk.Label(form_crear, text="Porcentaje (%):", font=("Segoe UI", 10), bg="white").grid(row=10, column=0, sticky="e", padx=10, pady=5)
    pct_of_var = tk.StringVar(value="20")
    tk.Entry(form_crear, textvariable=pct_of_var, width=8, font=("Segoe UI", 10)).grid(row=10, column=1, sticky="w", padx=5, pady=5)

    tk.Label(form_crear, text="Monto fijo ($):", font=("Segoe UI", 10), bg="white").grid(row=11, column=0, sticky="e", padx=10, pady=5)
    monto_of_var = tk.StringVar(value="0")
    tk.Entry(form_crear, textvariable=monto_of_var, width=8, font=("Segoe UI", 10)).grid(row=11, column=1, sticky="w", padx=5, pady=5)

    # Sección 3: Bonus Saturnos
    tk.Label(form_crear, text="SECCIÓN 3: BONUS SATURNOS EXTRA", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#FF5722").grid(row=12, column=0, columnspan=3, pady=(15, 5), padx=15, sticky="w")

    tk.Label(form_crear, text="% adicional Saturnos:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=13, column=0, sticky="e", padx=10, pady=5)
    bonus_of_var = tk.StringVar(value="15")
    tk.Entry(form_crear, textvariable=bonus_of_var, width=8, font=("Segoe UI", 10)).grid(row=13, column=1, sticky="w", padx=5, pady=5)
    tk.Label(form_crear, text="Ej: Normal 10% + 15% extra = 25% total", font=("Segoe UI", 8),
            bg="white", fg="#757575").grid(row=14, column=0, columnspan=3, sticky="w", padx=30)

    # Sección 4: Aplicabilidad
    tk.Label(form_crear, text="SECCIÓN 4: ¿A QUÉ SE APLICA?", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#FF5722").grid(row=15, column=0, columnspan=3, pady=(15, 5), padx=15, sticky="w")

    aplica_of_var = tk.StringVar(value="TODOS")
    for i, (label, val) in enumerate([
        ("Todos los productos", "TODOS"),
        ("Producto específico", "PRODUCTO"),
        ("Categoría completa", "CATEGORIA"),
        ("Laboratorio", "LABORATORIO"),
    ]):
        tk.Radiobutton(form_crear, text=label, variable=aplica_of_var, value=val,
                      font=("Segoe UI", 9), bg="white").grid(row=16+i, column=0, columnspan=2, sticky="w", padx=30)

    tk.Label(form_crear, text="Productos (códigos, coma):", font=("Segoe UI", 9), bg="white").grid(row=20, column=0, sticky="e", padx=10, pady=3)
    prods_of_var = tk.StringVar()
    tk.Entry(form_crear, textvariable=prods_of_var, width=40, font=("Segoe UI", 9)).grid(row=20, column=1, padx=5, pady=3, sticky="w")

    tk.Label(form_crear, text="Categorías (coma):", font=("Segoe UI", 9), bg="white").grid(row=21, column=0, sticky="e", padx=10, pady=3)
    cats_of_var = tk.StringVar()
    tk.Entry(form_crear, textvariable=cats_of_var, width=40, font=("Segoe UI", 9)).grid(row=21, column=1, padx=5, pady=3, sticky="w")

    tk.Label(form_crear, text="Laboratorios (coma):", font=("Segoe UI", 9), bg="white").grid(row=22, column=0, sticky="e", padx=10, pady=3)
    labs_of_var = tk.StringVar()
    tk.Entry(form_crear, textvariable=labs_of_var, width=40, font=("Segoe UI", 9)).grid(row=22, column=1, padx=5, pady=3, sticky="w")

    excl_ctrl_var = tk.IntVar(value=0)
    tk.Checkbutton(form_crear, text="Excluir medicamentos controlados", variable=excl_ctrl_var,
                  font=("Segoe UI", 9), bg="white").grid(row=23, column=0, columnspan=2, sticky="w", padx=30, pady=3)

    # Sección 5: Vigencia
    tk.Label(form_crear, text="SECCIÓN 5: VIGENCIA", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#FF5722").grid(row=24, column=0, columnspan=3, pady=(15, 5), padx=15, sticky="w")

    tk.Label(form_crear, text="Fecha inicio:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=25, column=0, sticky="e", padx=10, pady=5)
    fecha_ini_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    tk.Entry(form_crear, textvariable=fecha_ini_var, width=12, font=("Segoe UI", 10)).grid(row=25, column=1, sticky="w", padx=5, pady=5)

    tk.Label(form_crear, text="Fecha fin:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=26, column=0, sticky="e", padx=10, pady=5)
    fecha_fin_var = tk.StringVar(value=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))
    tk.Entry(form_crear, textvariable=fecha_fin_var, width=12, font=("Segoe UI", 10)).grid(row=26, column=1, sticky="w", padx=5, pady=5)

    tk.Label(form_crear, text="Días semana:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=27, column=0, sticky="e", padx=10, pady=5)
    dias_frame = tk.Frame(form_crear, bg="white")
    dias_frame.grid(row=27, column=1, sticky="w", padx=5, pady=5)
    dias_vars = {}
    for i, (num, dia) in enumerate([("1","Lun"),("2","Mar"),("3","Mié"),("4","Jue"),("5","Vie"),("6","Sáb"),("7","Dom")]):
        dias_vars[num] = tk.IntVar(value=1)
        tk.Checkbutton(dias_frame, text=dia, variable=dias_vars[num], font=("Segoe UI", 8),
                      bg="white").pack(side=tk.LEFT, padx=2)

    def sel_todos_dias():
        for v in dias_vars.values():
            v.set(1)
    tk.Button(dias_frame, text="Todos", command=sel_todos_dias, font=("Segoe UI", 7),
             bg="#E0E0E0", relief=tk.FLAT, padx=4, cursor="hand2").pack(side=tk.LEFT, padx=5)

    tk.Label(form_crear, text="Hora inicio:", font=("Segoe UI", 9), bg="white").grid(row=28, column=0, sticky="e", padx=10, pady=3)
    hora_ini_var = tk.StringVar(value="")
    tk.Entry(form_crear, textvariable=hora_ini_var, width=8, font=("Segoe UI", 9)).grid(row=28, column=1, sticky="w", padx=5, pady=3)

    tk.Label(form_crear, text="Hora fin:", font=("Segoe UI", 9), bg="white").grid(row=29, column=0, sticky="e", padx=10, pady=3)
    hora_fin_var = tk.StringVar(value="")
    tk.Entry(form_crear, textvariable=hora_fin_var, width=8, font=("Segoe UI", 9)).grid(row=29, column=1, sticky="w", padx=5, pady=3)

    # Sección 6: Límites
    tk.Label(form_crear, text="SECCIÓN 6: LÍMITES", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#FF5722").grid(row=30, column=0, columnspan=3, pady=(15, 5), padx=15, sticky="w")

    tk.Label(form_crear, text="Límite por cliente:", font=("Segoe UI", 10), bg="white").grid(row=31, column=0, sticky="e", padx=10, pady=5)
    lim_cli_var = tk.StringVar(value="0")
    tk.Entry(form_crear, textvariable=lim_cli_var, width=8, font=("Segoe UI", 10)).grid(row=31, column=1, sticky="w", padx=5, pady=5)
    tk.Label(form_crear, text="(0 = sin límite)", font=("Segoe UI", 8), bg="white", fg="#757575").grid(row=31, column=2, sticky="w")

    tk.Label(form_crear, text="Límite total:", font=("Segoe UI", 10), bg="white").grid(row=32, column=0, sticky="e", padx=10, pady=5)
    lim_tot_var = tk.StringVar(value="0")
    tk.Entry(form_crear, textvariable=lim_tot_var, width=8, font=("Segoe UI", 10)).grid(row=32, column=1, sticky="w", padx=5, pady=5)

    # Sección 7: Destacar
    tk.Label(form_crear, text="SECCIÓN 7: DESTACAR", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#FF5722").grid(row=33, column=0, columnspan=3, pady=(15, 5), padx=15, sticky="w")

    destacar_var = tk.IntVar(value=1)
    tk.Checkbutton(form_crear, text="Mostrar en banner principal de ventas", variable=destacar_var,
                  font=("Segoe UI", 10, "bold"), bg="white", fg="#FF5722").grid(row=34, column=0, columnspan=3, sticky="w", padx=30, pady=3)

    # Botones guardar
    btn_crear_frame = tk.Frame(form_crear, bg="white")
    btn_crear_frame.grid(row=36, column=0, columnspan=3, pady=20)

    def guardar_oferta():
        nombre = nombre_of_var.get().strip()
        if not nombre:
            messagebox.showwarning("Aviso", "El nombre de la oferta es obligatorio")
            return
        if not fecha_ini_var.get() or not fecha_fin_var.get():
            messagebox.showwarning("Aviso", "Las fechas son obligatorias")
            return

        ahora = datetime.now()
        folio = f"OF-{ahora.strftime('%Y%m%d%H%M%S')}"
        dias_sel = ",".join([k for k, v in dias_vars.items() if v.get()])
        if len(dias_sel) == len(dias_vars) * 2 - 1:
            dias_sel = "TODOS"

        try:
            c.execute("""INSERT INTO ofertas (folio,nombre,descripcion,tipo,descuento_porcentaje,descuento_monto,
                        bonus_saturnos_extra,aplica_a,productos_ids,categorias,laboratorios,excluir_controlados,
                        fecha_inicio,fecha_fin,dias_semana,hora_inicio,hora_fin,limite_por_cliente,limite_total,
                        unidades_vendidas,activa,destacada,color_banner,creado_por,fecha_creacion)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,1,?,?,?,?)""",
                      (folio, nombre, desc_text.get("1.0", tk.END).strip(),
                       tipo_of_var.get(), float(pct_of_var.get() or 0), float(monto_of_var.get() or 0),
                       float(bonus_of_var.get() or 15),
                       aplica_of_var.get(), prods_of_var.get(), cats_of_var.get(), labs_of_var.get(),
                       excl_ctrl_var.get(),
                       fecha_ini_var.get(), fecha_fin_var.get(), dias_sel,
                       hora_ini_var.get() or None, hora_fin_var.get() or None,
                       int(lim_cli_var.get() or 0), int(lim_tot_var.get() or 0),
                       destacar_var.get(), color_of_var.get(),
                       usuario_actual, ahora.strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            messagebox.showinfo("Oferta Creada", f"Oferta '{nombre}' creada con folio {folio}")
            cargar_ofertas_activas()
            cargar_historial()
            # Limpiar formulario
            nombre_of_var.set("")
            desc_text.delete("1.0", tk.END)
            pct_of_var.set("20")
            monto_of_var.set("0")
            prods_of_var.set("")
            cats_of_var.set("")
            labs_of_var.set("")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def limpiar_form():
        nombre_of_var.set("")
        desc_text.delete("1.0", tk.END)
        pct_of_var.set("20")
        monto_of_var.set("0")
        bonus_of_var.set("15")
        prods_of_var.set("")
        cats_of_var.set("")
        labs_of_var.set("")
        tipo_of_var.set("DESCUENTO_PORCENTAJE")
        aplica_of_var.set("TODOS")
        sel_todos_dias()

    tk.Button(btn_crear_frame, text="GUARDAR OFERTA", command=guardar_oferta,
             bg="#FF5722", fg="white", font=("Segoe UI", 12, "bold"),
             relief=tk.FLAT, padx=24, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=10)
    tk.Button(btn_crear_frame, text="LIMPIAR", command=limpiar_form,
             bg="#757575", fg="white", font=("Segoe UI", 10, "bold"),
             relief=tk.FLAT, padx=16, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=5)

    # ==================== PESTAÑA HISTORIAL ====================
    tab_hist = tk.Frame(notebook, bg="white")
    notebook.add(tab_hist, text="  Historial  ")

    filt_hist = tk.Frame(tab_hist, bg="white")
    filt_hist.pack(fill=tk.X, padx=10, pady=8)

    tk.Label(filt_hist, text="Periodo:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    per_ini_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-01"))
    tk.Entry(filt_hist, textvariable=per_ini_var, width=12, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=3)
    tk.Label(filt_hist, text="a", bg="white").pack(side=tk.LEFT, padx=3)
    per_fin_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    tk.Entry(filt_hist, textvariable=per_fin_var, width=12, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=3)

    cols_hist = ("FOLIO", "NOMBRE", "PERIODO", "TIPO", "PRODUCTOS VENDIDOS", "DESC TOTAL", "SATURNOS EXTRA", "ESTADO")
    tree_hist = ttk.Treeview(tab_hist, columns=cols_hist, show="headings", height=14)
    for col in cols_hist:
        tree_hist.heading(col, text=col)
    tree_hist.column("FOLIO", width=120)
    tree_hist.column("NOMBRE", width=160)
    tree_hist.column("PERIODO", width=160)
    tree_hist.column("TIPO", width=120)
    tree_hist.column("PRODUCTOS VENDIDOS", width=110)
    tree_hist.column("DESC TOTAL", width=100)
    tree_hist.column("SATURNOS EXTRA", width=100)
    tree_hist.column("ESTADO", width=80)
    tree_hist.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def cargar_historial():
        for item in tree_hist.get_children():
            tree_hist.delete(item)
        hoy = datetime.now().strftime("%Y-%m-%d")
        c.execute("""SELECT o.folio, o.nombre, o.fecha_inicio, o.fecha_fin, o.tipo, o.unidades_vendidas,
                     COALESCE(SUM(oa.descuento_aplicado),0), COALESCE(SUM(oa.saturnos_extra),0), o.activa
                     FROM ofertas o LEFT JOIN ofertas_aplicadas oa ON o.id=oa.oferta_id
                     WHERE o.fecha_creacion >= ? AND o.fecha_creacion <= ?
                     GROUP BY o.id ORDER BY o.id DESC""",
                  (per_ini_var.get(), per_fin_var.get() + " 23:59"))
        for row in c.fetchall():
            folio, nombre, f_ini, f_fin, tipo, vendidas, desc_tot, sat_extra, activa = row
            if not activa:
                estado = "PAUSADA"
            elif f_fin < hoy:
                estado = "VENCIDA"
            else:
                estado = "ACTIVA"
            tree_hist.insert("", "end", values=(folio, nombre, f"{f_ini} - {f_fin}", tipo,
                             vendidas, f"${desc_tot:,.2f}", f"{sat_extra:,.0f} \u20B4", estado))

    tk.Button(filt_hist, text="FILTRAR", command=cargar_historial,
             bg="#FF5722", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=10)

    # Detalle de oferta seleccionada
    det_hist_frame = tk.Frame(tab_hist, bg="#FFF3E0", relief=tk.RIDGE, bd=1)
    det_hist_frame.pack(fill=tk.X, padx=10, pady=5)
    det_hist_label = tk.Label(det_hist_frame, text="Selecciona una oferta para ver métricas",
                              font=("Segoe UI", 9), bg="#FFF3E0", fg="#555")
    det_hist_label.pack(pady=8, padx=10, anchor="w")

    def on_sel_hist(event=None):
        sel = tree_hist.selection()
        if not sel:
            return
        vals = tree_hist.item(sel[0])["values"]
        folio = vals[0]
        c.execute("""SELECT COALESCE(SUM(oa.precio_normal * oa.cantidad),0),
                     COALESCE(SUM(oa.precio_oferta * oa.cantidad),0),
                     COALESCE(SUM(oa.descuento_aplicado),0),
                     COALESCE(SUM(oa.saturnos_extra),0),
                     COUNT(DISTINCT oa.venta_id)
                     FROM ofertas_aplicadas oa JOIN ofertas o ON oa.oferta_id=o.id WHERE o.folio=?""", (folio,))
        r = c.fetchone()
        ingreso_normal, ingreso_oferta, desc_total, sat_total, num_ventas = r
        roi = ((ingreso_oferta / ingreso_normal) * 100) if ingreso_normal > 0 else 0
        det_hist_label.config(text=f"  {vals[1]}  |  Ventas: {num_ventas}  |  Ingreso: ${ingreso_oferta:,.2f}  |  "
                                   f"Descuento total: ${desc_total:,.2f}  |  Saturnos extra: {sat_total:,.0f} \u20B4  |  "
                                   f"ROI: {roi:.1f}%")

    tree_hist.bind("<<TreeviewSelect>>", on_sel_hist)
    cargar_historial()

    # ==================== PESTAÑA BANNERS ====================
    tab_ban = tk.Frame(notebook, bg="white")
    notebook.add(tab_ban, text="  Banners  ")

    tk.Label(tab_ban, text="BANNERS PROMOCIONALES", font=("Segoe UI", 14, "bold"),
            bg="white", fg="#FF5722").pack(pady=15)

    ban_toolbar = tk.Frame(tab_ban, bg="white")
    ban_toolbar.pack(fill=tk.X, padx=10, pady=5)

    def crear_banner_oferta():
        """Genera un banner visual para la oferta seleccionada."""
        dlg = tk.Toplevel(main)
        dlg.title("Crear Banner Promocional")
        dlg.geometry("750x550")
        dlg.configure(bg="white")
        dlg.grab_set()

        tk.Label(dlg, text="DISEÑADOR DE BANNER", font=("Segoe UI", 13, "bold"),
                bg="white", fg="#FF5722").pack(pady=10)

        form_b = tk.Frame(dlg, bg="white")
        form_b.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(form_b, text="Oferta:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        of_ban_var = tk.StringVar()
        c.execute("SELECT folio || ' - ' || nombre FROM ofertas WHERE activa=1 ORDER BY id DESC")
        of_list = [r[0] for r in c.fetchall()]
        of_combo = ttk.Combobox(form_b, textvariable=of_ban_var, width=40, values=of_list, state="readonly")
        of_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        if of_list:
            of_combo.current(0)

        tk.Label(form_b, text="Texto principal:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        txt_princ_var = tk.StringVar(value="20% OFF")
        tk.Entry(form_b, textvariable=txt_princ_var, width=30, font=("Segoe UI", 10)).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_b, text="Texto secundario:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        txt_sec_var = tk.StringVar(value="En vitaminas y suplementos")
        tk.Entry(form_b, textvariable=txt_sec_var, width=30, font=("Segoe UI", 10)).grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_b, text="Color fondo:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        color_ban_var = tk.StringVar(value="#FF5722")
        tk.Entry(form_b, textvariable=color_ban_var, width=12, font=("Segoe UI", 10)).grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Canvas preview
        preview_ban = tk.Canvas(dlg, width=600, height=200, bg="#F5F5F5", highlightthickness=1, highlightbackground="#CCC")
        preview_ban.pack(pady=10)
        preview_refs_ban = {}

        def generar_banner_preview():
            try:
                W, H = 600, 200
                color_bg = color_ban_var.get() or "#FF5722"
                img = Image.new('RGB', (W, H), color_bg)
                draw = ImageDraw.Draw(img)

                try:
                    font_big = ImageFont.truetype("segoeuib.ttf", 48)
                    font_med = ImageFont.truetype("segoeui.ttf", 22)
                    font_small = ImageFont.truetype("segoeui.ttf", 14)
                except:
                    font_big = ImageFont.load_default()
                    font_med = font_small = font_big

                # Texto principal
                draw.text((W // 2, 60), txt_princ_var.get(), fill='white', font=font_big, anchor='mt')
                # Texto secundario
                draw.text((W // 2, 120), txt_sec_var.get(), fill='#FFCCBC', font=font_med, anchor='mt')
                # Franja inferior
                draw.rectangle([0, H-35, W, H], fill='#00000040')
                draw.text((W // 2, H-18), "FARMACIAS MADRID  |  \u2605 Programa Saturnos", fill='white', font=font_small, anchor='mm')

                tk_img = ImageTk.PhotoImage(img)
                preview_ban.delete("all")
                preview_ban.create_image(300, 100, image=tk_img)
                preview_refs_ban["img"] = tk_img
                preview_refs_ban["pil"] = img
            except Exception as e:
                preview_ban.delete("all")
                preview_ban.create_text(300, 100, text=f"Error: {e}", fill="red")

        tk.Button(form_b, text="VISTA PREVIA", command=generar_banner_preview,
                 bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, padx=10, pady=3, cursor="hand2").grid(row=3, column=2, padx=5)

        def guardar_banner():
            generar_banner_preview()
            if "pil" not in preview_refs_ban:
                return
            base = os.path.dirname(os.path.abspath(__file__))
            ban_dir = os.path.join(base, "banners")
            os.makedirs(ban_dir, exist_ok=True)
            nombre_arch = f"banner_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            ruta = os.path.join(ban_dir, nombre_arch)
            preview_refs_ban["pil"].save(ruta)

            # Obtener oferta_id
            of_sel = of_ban_var.get()
            of_folio = of_sel.split(" - ")[0] if of_sel else ""
            c.execute("SELECT id FROM ofertas WHERE folio=?", (of_folio,))
            of_row = c.fetchone()
            oid = of_row[0] if of_row else None

            c.execute("SELECT COALESCE(MAX(orden),0)+1 FROM ofertas_banner")
            orden = c.fetchone()[0]
            c.execute("INSERT INTO ofertas_banner (oferta_id,imagen_path,orden,activo) VALUES (?,?,?,1)",
                      (oid, ruta, orden))
            conn.commit()
            cargar_banners()
            messagebox.showinfo("Banner", f"Banner guardado: {ruta}")

        btn_ban_f = tk.Frame(dlg, bg="white")
        btn_ban_f.pack(pady=10)
        tk.Button(btn_ban_f, text="GUARDAR BANNER", command=guardar_banner,
                 bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
                 relief=tk.FLAT, padx=14, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_ban_f, text="CERRAR", command=dlg.destroy,
                 bg="#757575", fg="white", font=("Segoe UI", 10, "bold"),
                 relief=tk.FLAT, padx=14, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)

    tk.Button(ban_toolbar, text="+ CREAR BANNER", command=crear_banner_oferta,
             bg="#FF5722", fg="white", font=("Segoe UI", 10, "bold"),
             relief=tk.FLAT, padx=14, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)

    # Tabla de banners
    cols_ban = ("ID", "OFERTA", "ARCHIVO", "ORDEN", "ACTIVO")
    tree_ban = ttk.Treeview(tab_ban, columns=cols_ban, show="headings", height=10)
    for col in cols_ban:
        tree_ban.heading(col, text=col)
    tree_ban.column("ID", width=50)
    tree_ban.column("OFERTA", width=200)
    tree_ban.column("ARCHIVO", width=300)
    tree_ban.column("ORDEN", width=60)
    tree_ban.column("ACTIVO", width=60)
    tree_ban.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def cargar_banners():
        for item in tree_ban.get_children():
            tree_ban.delete(item)
        c.execute("""SELECT b.id, COALESCE(o.nombre,'Sin oferta'), b.imagen_path, b.orden, b.activo
                     FROM ofertas_banner b LEFT JOIN ofertas o ON b.oferta_id=o.id
                     ORDER BY b.orden""")
        for row in c.fetchall():
            tree_ban.insert("", "end", values=(row[0], row[1], os.path.basename(row[2] or ""),
                            row[3], "Sí" if row[4] else "No"))

    ban_acc = tk.Frame(tab_ban, bg="white")
    ban_acc.pack(fill=tk.X, padx=10, pady=5)

    def toggle_banner():
        sel = tree_ban.selection()
        if not sel:
            return
        bid = tree_ban.item(sel[0])["values"][0]
        c.execute("UPDATE ofertas_banner SET activo = CASE WHEN activo=1 THEN 0 ELSE 1 END WHERE id=?", (bid,))
        conn.commit()
        cargar_banners()

    def eliminar_banner():
        sel = tree_ban.selection()
        if not sel:
            return
        bid = tree_ban.item(sel[0])["values"][0]
        if messagebox.askyesno("Eliminar", "¿Eliminar este banner?"):
            c.execute("DELETE FROM ofertas_banner WHERE id=?", (bid,))
            conn.commit()
            cargar_banners()

    def subir_orden():
        sel = tree_ban.selection()
        if not sel:
            return
        bid = tree_ban.item(sel[0])["values"][0]
        c.execute("UPDATE ofertas_banner SET orden=orden-1 WHERE id=?", (bid,))
        conn.commit()
        cargar_banners()

    def bajar_orden():
        sel = tree_ban.selection()
        if not sel:
            return
        bid = tree_ban.item(sel[0])["values"][0]
        c.execute("UPDATE ofertas_banner SET orden=orden+1 WHERE id=?", (bid,))
        conn.commit()
        cargar_banners()

    tk.Button(ban_acc, text="\u2191 Subir", command=subir_orden, bg="#1565C0", fg="white",
             font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(ban_acc, text="\u2193 Bajar", command=bajar_orden, bg="#1565C0", fg="white",
             font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(ban_acc, text="Activar/Desactivar", command=toggle_banner, bg="#FF9800", fg="white",
             font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(ban_acc, text="Eliminar", command=eliminar_banner, bg="#D32F2F", fg="white",
             font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=3)

    cargar_banners()

    # ==================== PESTAÑA REPORTES ====================
    tab_rep = tk.Frame(notebook, bg="white")
    notebook.add(tab_rep, text="  Reportes  ")

    tk.Label(tab_rep, text="REPORTES DE OFERTAS", font=("Segoe UI", 14, "bold"),
            bg="white", fg="#FF5722").pack(pady=15)

    rep_of_frame = tk.Frame(tab_rep, bg="white")
    rep_of_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def cargar_reportes_ofertas():
        for w in rep_of_frame.winfo_children():
            w.destroy()
        hoy = datetime.now().strftime("%Y-%m-%d")
        mes = datetime.now().strftime("%Y-%m")

        c.execute("SELECT COUNT(*) FROM ofertas WHERE activa=1 AND fecha_inicio<=? AND fecha_fin>=?", (hoy, hoy))
        activas_hoy = c.fetchone()[0]

        # Productos únicos en oferta
        c.execute("""SELECT COUNT(DISTINCT producto_codigo) FROM ofertas_aplicadas oa
                     JOIN ofertas o ON oa.oferta_id=o.id WHERE o.activa=1""")
        prods_oferta = c.fetchone()[0]

        c.execute("SELECT COALESCE(SUM(precio_oferta * cantidad),0) FROM ofertas_aplicadas WHERE fecha=?", (hoy,))
        ventas_of_hoy = c.fetchone()[0]

        c.execute("SELECT COALESCE(SUM(descuento_aplicado),0) FROM ofertas_aplicadas WHERE fecha=?", (hoy,))
        desc_hoy = c.fetchone()[0]

        c.execute("SELECT COALESCE(SUM(saturnos_extra),0) FROM ofertas_aplicadas WHERE fecha=?", (hoy,))
        sat_hoy = c.fetchone()[0]

        c.execute("SELECT COALESCE(SUM(descuento_aplicado),0) FROM ofertas_aplicadas WHERE fecha LIKE ?", (f"{mes}%",))
        desc_mes = c.fetchone()[0]

        c.execute("SELECT COALESCE(SUM(saturnos_extra),0) FROM ofertas_aplicadas WHERE fecha LIKE ?", (f"{mes}%",))
        sat_mes = c.fetchone()[0]

        datos = [
            ("Ofertas activas hoy:", str(activas_hoy), "#FF5722"),
            ("Productos en oferta:", str(prods_oferta), "#1565C0"),
            ("Ventas con oferta hoy:", f"${ventas_of_hoy:,.2f}", "#4CAF50"),
            ("Descuentos otorgados hoy:", f"${desc_hoy:,.2f}", "#D32F2F"),
            ("Saturnos extra hoy:", f"{sat_hoy:,.0f} \u20B4", "#FFC107"),
            ("Descuentos del mes:", f"${desc_mes:,.2f}", "#D32F2F"),
            ("Saturnos extra del mes:", f"{sat_mes:,.0f} \u20B4", "#FFC107"),
        ]

        for i, (label, val, color) in enumerate(datos):
            tk.Label(rep_of_frame, text=label, font=("Segoe UI", 11, "bold"), bg="white", fg="#333").grid(
                row=i, column=0, sticky="e", padx=10, pady=4)
            tk.Label(rep_of_frame, text=val, font=("Segoe UI", 14, "bold"), bg="white", fg=color).grid(
                row=i, column=1, sticky="w", padx=10, pady=4)

        # Top 5 ofertas más exitosas
        base_row = len(datos) + 1
        tk.Label(rep_of_frame, text="Top 5 ofertas más exitosas:", font=("Segoe UI", 11, "bold"),
                bg="white", fg="#333").grid(row=base_row, column=0, columnspan=2, pady=(15, 5), sticky="w")

        c.execute("""SELECT o.nombre, SUM(oa.cantidad) as uds, SUM(oa.precio_oferta * oa.cantidad) as ingreso,
                     SUM(oa.descuento_aplicado) as desc_total
                     FROM ofertas_aplicadas oa JOIN ofertas o ON oa.oferta_id=o.id
                     GROUP BY o.id ORDER BY uds DESC LIMIT 5""")
        for j, (nombre, uds, ingreso, desc_t) in enumerate(c.fetchall()):
            tk.Label(rep_of_frame, text=f"  {j+1}. {nombre}", font=("Segoe UI", 9), bg="white").grid(
                row=base_row+1+j, column=0, sticky="w", padx=15)
            tk.Label(rep_of_frame, text=f"{uds} uds | ${ingreso:,.2f} | Desc: ${desc_t:,.2f}",
                    font=("Segoe UI", 9, "bold"), bg="white", fg="#FF5722").grid(
                row=base_row+1+j, column=1, sticky="w")

    cargar_reportes_ofertas()


# ===== MÓDULO SISTEMA DE CRÉDITOS =====
def ver_creditos():
    limpiar()

    header_mod = tk.Frame(main, bg="#2E7D32", height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="💳 SISTEMA DE CRÉDITOS", font=("Segoe UI", 13, "bold"),
            bg="#2E7D32", fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    notebook = ttk.Notebook(main)
    notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # ==================== PESTAÑA SOLICITUDES ====================
    tab_sol = tk.Frame(notebook, bg="white")
    notebook.add(tab_sol, text="  Solicitudes  ")

    toolbar_sol = tk.Frame(tab_sol, bg="white")
    toolbar_sol.pack(fill=tk.X, padx=10, pady=8)

    def nueva_solicitud():
        dlg = tk.Toplevel(main)
        dlg.title("Nueva Solicitud de Crédito")
        dlg.geometry("600x550")
        dlg.configure(bg="white")
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg="#2E7D32", height=38)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="NUEVA SOLICITUD DE CRÉDITO", font=("Segoe UI", 11, "bold"),
                bg="#2E7D32", fg="white").pack(side=tk.LEFT, padx=12, pady=8)

        form = tk.Frame(dlg, bg="white")
        form.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Folio automático
        ahora = datetime.now()
        c.execute("SELECT COUNT(*) FROM creditos")
        num = c.fetchone()[0] + 1
        folio_cr = f"CRED-{ahora.strftime('%Y%m%d')}-{num:04d}"
        tk.Label(form, text=f"Folio: {folio_cr}", font=("Segoe UI", 11, "bold"), bg="white", fg="#2E7D32").grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        tk.Label(form, text="Cliente:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        cli_var = tk.StringVar()
        cli_combo = ttk.Combobox(form, textvariable=cli_var, width=30, state="readonly")
        c.execute("SELECT nombre FROM clientes WHERE id > 1")
        cli_combo['values'] = [r[0] for r in c.fetchall()]
        if cli_combo['values']:
            cli_combo.current(0)
        cli_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form, text="Tipo:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tipo_var = tk.StringVar(value="PERSONA")
        tipo_frame = tk.Frame(form, bg="white")
        tipo_frame.grid(row=2, column=1, sticky="w", padx=5)
        tk.Radiobutton(tipo_frame, text="Persona", variable=tipo_var, value="PERSONA", bg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(tipo_frame, text="Clínica", variable=tipo_var, value="CLINICA", bg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)

        tk.Label(form, text="Monto ($):", font=("Segoe UI", 10, "bold"), bg="white").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        monto_entry = tk.Entry(form, width=15, font=("Segoe UI", 10))
        monto_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Plazo (días):", font=("Segoe UI", 10, "bold"), bg="white").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        plazo_var = tk.StringVar(value="30")
        ttk.Combobox(form, textvariable=plazo_var, width=10, values=["15","30","45","60","90"], state="readonly").grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Documentos
        tk.Label(form, text="DOCUMENTOS:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=5, column=0, columnspan=2, pady=(10,5), sticky="w", padx=5)
        docs_frame = tk.Frame(form, bg="white")
        docs_frame.grid(row=6, column=0, columnspan=2, sticky="w", padx=5)
        docs = {}
        for dtype in ["INE", "Comprobante Domicilio", "Comprobante Ingresos"]:
            df = tk.Frame(docs_frame, bg="white")
            df.pack(fill=tk.X, pady=2)
            docs[dtype] = tk.StringVar()
            tk.Label(df, text=f"{dtype}:", font=("Segoe UI", 9), bg="white", width=22, anchor="w").pack(side=tk.LEFT)
            tk.Entry(df, textvariable=docs[dtype], width=30, font=("Segoe UI", 8), state="readonly").pack(side=tk.LEFT, padx=3)
            def browse(var=docs[dtype]):
                ruta = filedialog.askopenfilename(filetypes=[("Documentos","*.pdf *.png *.jpg *.jpeg")])
                if ruta:
                    var.set(ruta)
            tk.Button(df, text="Subir", command=browse, bg="#1565C0", fg="white", font=("Segoe UI", 7),
                     relief=tk.FLAT, padx=4, cursor="hand2").pack(side=tk.LEFT, padx=2)

        tk.Label(form, text="Observaciones:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=7, column=0, sticky="ne", padx=5, pady=5)
        obs_text = tk.Text(form, width=35, height=3, font=("Segoe UI", 9))
        obs_text.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        def registrar():
            if not cli_var.get():
                messagebox.showwarning("Aviso", "Selecciona un cliente")
                return
            try:
                monto = float(monto_entry.get())
            except:
                messagebox.showwarning("Aviso", "Monto inválido")
                return
            # Validar máximos
            c.execute("SELECT monto_max_persona, monto_max_clinica FROM config_creditos WHERE id=1")
            cfg = c.fetchone()
            maximo = cfg[1] if tipo_var.get() == "CLINICA" else cfg[0]
            if monto > maximo:
                messagebox.showwarning("Límite", f"Monto máximo para {tipo_var.get()}: ${maximo:,.2f}")
                return

            c.execute("SELECT id FROM clientes WHERE nombre=?", (cli_var.get(),))
            cid = c.fetchone()[0]
            plazo = int(plazo_var.get())
            venc = (ahora + timedelta(days=plazo)).strftime("%Y-%m-%d")
            docs_completos = sum(1 for d in docs.values() if d.get()) >= 2

            c.execute("""INSERT INTO creditos (folio,cliente_id,tipo,monto_aprobado,monto_usado,monto_disponible,
                        plazo_dias,fecha_aprobacion,fecha_vencimiento,estado,documentos_completos,observaciones)
                        VALUES (?,?,?,?,0,?,?,?,?,'PENDIENTE',?,?)""",
                      (folio_cr, cid, tipo_var.get(), monto, monto, plazo,
                       ahora.strftime("%Y-%m-%d"), venc, 1 if docs_completos else 0,
                       obs_text.get("1.0", tk.END).strip()))
            cred_id = c.lastrowid

            # Guardar documentos
            for dtype, var in docs.items():
                if var.get():
                    c.execute("""INSERT INTO documentos_credito (credito_id,cliente_id,tipo_documento,ruta_archivo,nombre_archivo,fecha_subida)
                                VALUES (?,?,?,?,?,?)""",
                              (cred_id, cid, dtype, var.get(), os.path.basename(var.get()), ahora.strftime("%Y-%m-%d")))
            conn.commit()
            dlg.destroy()
            cargar_solicitudes()
            messagebox.showinfo("Registrado", f"Solicitud {folio_cr} registrada")

        btn_frame = tk.Frame(dlg, bg="white")
        btn_frame.pack(fill=tk.X, padx=15, pady=10)
        tk.Button(btn_frame, text="REGISTRAR SOLICITUD", command=registrar,
                 bg="#2E7D32", fg="white", font=("Segoe UI", 11, "bold"),
                 relief=tk.FLAT, padx=16, pady=6, cursor="hand2").pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="CANCELAR", command=dlg.destroy,
                 bg="#757575", fg="white", font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, padx=12, pady=4, cursor="hand2").pack(side=tk.RIGHT, padx=5)

    tk.Button(toolbar_sol, text="+ NUEVA SOLICITUD", command=nueva_solicitud,
             bg="#2E7D32", fg="white", font=("Segoe UI", 11, "bold"),
             relief=tk.FLAT, padx=16, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=5)

    cols_sol = ("FOLIO", "CLIENTE", "TIPO", "MONTO", "PLAZO", "FECHA", "DOCS", "ESTADO")
    tree_sol = ttk.Treeview(tab_sol, columns=cols_sol, show="headings", height=10)
    for col in cols_sol:
        tree_sol.heading(col, text=col)
    tree_sol.column("FOLIO", width=150)
    tree_sol.column("CLIENTE", width=150)
    tree_sol.column("TIPO", width=80)
    tree_sol.column("MONTO", width=100)
    tree_sol.column("PLAZO", width=70)
    tree_sol.column("FECHA", width=90)
    tree_sol.column("DOCS", width=50)
    tree_sol.column("ESTADO", width=100)
    tree_sol.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    acciones_sol = tk.Frame(tab_sol, bg="white")
    acciones_sol.pack(fill=tk.X, padx=10, pady=5)

    def cargar_solicitudes():
        for item in tree_sol.get_children():
            tree_sol.delete(item)
        c.execute("""SELECT cr.folio, cl.nombre, cr.tipo, cr.monto_aprobado, cr.plazo_dias,
                    cr.fecha_aprobacion, cr.documentos_completos, cr.estado
                    FROM creditos cr JOIN clientes cl ON cr.cliente_id=cl.id
                    WHERE cr.estado IN ('PENDIENTE','APROBADO')
                    ORDER BY cr.id DESC""")
        for row in c.fetchall():
            tree_sol.insert("", "end", values=(row[0], row[1], row[2], f"${row[3]:,.2f}", f"{row[4]}d", row[5], "Sí" if row[6] else "No", row[7]))

    def aprobar_solicitud():
        sel = tree_sol.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una solicitud")
            return
        folio = tree_sol.item(sel[0])["values"][0]
        estado = tree_sol.item(sel[0])["values"][7]
        if estado != "PENDIENTE":
            messagebox.showwarning("Aviso", "Solo se pueden aprobar solicitudes PENDIENTES")
            return
        if not messagebox.askyesno("Aprobar", f"¿Aprobar crédito {folio}?"):
            return
        c.execute("UPDATE creditos SET estado='ACTIVO', aprobado_por=? WHERE folio=?", (usuario_actual, folio))
        conn.commit()
        cargar_solicitudes()
        messagebox.showinfo("Aprobado", f"Crédito {folio} ACTIVO")

    def rechazar_solicitud():
        sel = tree_sol.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una solicitud")
            return
        folio = tree_sol.item(sel[0])["values"][0]
        if not messagebox.askyesno("Rechazar", f"¿Rechazar crédito {folio}?"):
            return
        c.execute("UPDATE creditos SET estado='RECHAZADO' WHERE folio=?", (folio,))
        conn.commit()
        cargar_solicitudes()

    tk.Button(acciones_sol, text="APROBAR", command=aprobar_solicitud,
             bg="#4CAF50", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=12, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=4)
    tk.Button(acciones_sol, text="RECHAZAR", command=rechazar_solicitud,
             bg="#D32F2F", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=12, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=4)

    cargar_solicitudes()

    # ==================== PESTAÑA CRÉDITOS ACTIVOS ====================
    tab_act = tk.Frame(notebook, bg="white")
    notebook.add(tab_act, text="  Créditos Activos  ")

    cols_act = ("FOLIO", "CLIENTE", "TIPO", "APROBADO", "USADO", "DISPONIBLE", "VENCIMIENTO", "ESTADO")
    tree_act = ttk.Treeview(tab_act, columns=cols_act, show="headings", height=14)
    for col in cols_act:
        tree_act.heading(col, text=col)
    tree_act.column("FOLIO", width=140)
    tree_act.column("CLIENTE", width=140)
    tree_act.column("TIPO", width=80)
    tree_act.column("APROBADO", width=100)
    tree_act.column("USADO", width=90)
    tree_act.column("DISPONIBLE", width=100)
    tree_act.column("VENCIMIENTO", width=95)
    tree_act.column("ESTADO", width=80)
    tree_act.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def cargar_activos():
        for item in tree_act.get_children():
            tree_act.delete(item)
        c.execute("""SELECT cr.folio, cl.nombre, cr.tipo, cr.monto_aprobado, cr.monto_usado,
                    cr.monto_disponible, cr.fecha_vencimiento, cr.estado
                    FROM creditos cr JOIN clientes cl ON cr.cliente_id=cl.id
                    WHERE cr.estado='ACTIVO' ORDER BY cr.fecha_vencimiento""")
        for row in c.fetchall():
            tree_act.insert("", "end", values=(row[0], row[1], row[2], f"${row[3]:,.2f}", f"${row[4]:,.2f}", f"${row[5]:,.2f}", row[6], row[7]))

    cargar_activos()

    # ==================== PESTAÑA PAGOS ====================
    tab_pag = tk.Frame(notebook, bg="white")
    notebook.add(tab_pag, text="  Pagos  ")

    pago_toolbar = tk.Frame(tab_pag, bg="white")
    pago_toolbar.pack(fill=tk.X, padx=10, pady=8)

    tk.Label(pago_toolbar, text="Buscar crédito:", font=("Segoe UI", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    busq_cred_entry = tk.Entry(pago_toolbar, width=20, font=("Segoe UI", 9))
    busq_cred_entry.pack(side=tk.LEFT, padx=5)

    def registrar_pago():
        sel = tree_pagos.selection()
        if sel:
            # Seleccionado de historial — no aplica
            pass
        # Dialog de pago
        dlg = tk.Toplevel(main)
        dlg.title("Registrar Pago de Crédito")
        dlg.geometry("450x400")
        dlg.configure(bg="white")
        dlg.grab_set()

        tk.Label(dlg, text="REGISTRAR PAGO", font=("Segoe UI", 14, "bold"), bg="white", fg="#2E7D32").pack(pady=10)

        form = tk.Frame(dlg, bg="white")
        form.pack(padx=20, pady=10)

        tk.Label(form, text="Folio crédito:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        folio_pago_var = tk.StringVar()
        folio_combo = ttk.Combobox(form, textvariable=folio_pago_var, width=25, state="readonly")
        c.execute("SELECT folio FROM creditos WHERE estado='ACTIVO' AND monto_usado > 0")
        folio_combo['values'] = [r[0] for r in c.fetchall()]
        if folio_combo['values']:
            folio_combo.current(0)
        folio_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Monto ($):", font=("Segoe UI", 10, "bold"), bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        monto_pago = tk.Entry(form, width=15, font=("Segoe UI", 10))
        monto_pago.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Método:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        metodo_var = tk.StringVar(value="EFECTIVO")
        ttk.Combobox(form, textvariable=metodo_var, width=15,
                    values=["EFECTIVO","TARJETA","TRANSFERENCIA","SATURNOS"], state="readonly").grid(row=2, column=1, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Observaciones:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=3, column=0, sticky="ne", padx=5, pady=5)
        obs_pago = tk.Entry(form, width=28, font=("Segoe UI", 9))
        obs_pago.grid(row=3, column=1, padx=5, pady=5)

        def aplicar_pago():
            if not folio_pago_var.get():
                messagebox.showwarning("Aviso", "Selecciona un crédito")
                return
            try:
                monto = float(monto_pago.get())
            except:
                messagebox.showwarning("Error", "Monto inválido")
                return
            folio = folio_pago_var.get()
            c.execute("SELECT id, monto_usado, monto_disponible, monto_aprobado, cliente_id FROM creditos WHERE folio=?", (folio,))
            cr = c.fetchone()
            if not cr:
                return
            cred_id, usado, disp, aprobado, cid = cr

            if monto > usado:
                messagebox.showwarning("Aviso", f"Saldo deudor: ${usado:,.2f}")
                return

            # Si paga con Saturnos
            if metodo_var.get() == "SATURNOS":
                c.execute("SELECT saldo_saturnos FROM monederos WHERE cliente_id=? AND activo=1", (cid,))
                m = c.fetchone()
                if not m or m[0] < monto:
                    messagebox.showwarning("Saturnos", f"Saldo Saturnos insuficiente: {m[0] if m else 0:,.0f}")
                    return
                # Descontar saturnos
                saldo_ant = m[0]
                nuevo_saldo = saldo_ant - monto
                c.execute("UPDATE monederos SET saldo_saturnos=?, total_gastado=total_gastado+? WHERE cliente_id=?",
                          (nuevo_saldo, monto, cid))
                ahora = datetime.now()
                c.execute("""INSERT INTO movimientos_saturnos (cliente_id,tipo,cantidad,saldo_anterior,saldo_nuevo,concepto,usuario,fecha,hora)
                            VALUES (?,?,?,?,?,?,?,?,?)""",
                          (cid, "REDIMIR", -monto, saldo_ant, nuevo_saldo,
                           f"Pago crédito {folio}", usuario_actual, ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S")))

            ahora = datetime.now()
            folio_p = f"PAG-{ahora.strftime('%Y%m%d%H%M%S')}"
            c.execute("""INSERT INTO pagos_credito (credito_id,folio_pago,monto,tipo_pago,fecha,hora,usuario,observaciones)
                        VALUES (?,?,?,?,?,?,?,?)""",
                      (cred_id, folio_p, monto, metodo_var.get(), ahora.strftime("%Y-%m-%d"),
                       ahora.strftime("%H:%M:%S"), usuario_actual, obs_pago.get()))
            nuevo_usado = usado - monto
            nueva_disp = disp + monto
            c.execute("UPDATE creditos SET monto_usado=?, monto_disponible=? WHERE id=?",
                      (nuevo_usado, nueva_disp, cred_id))

            # Si pagó todo, verificar si aún está dentro de plazo para bonificación Saturnos
            if nuevo_usado <= 0:
                c.execute("SELECT fecha_vencimiento FROM creditos WHERE id=?", (cred_id,))
                venc = c.fetchone()[0]
                if ahora.strftime("%Y-%m-%d") <= venc:
                    # Bonificación 50 Saturnos por pagar antes de vencimiento
                    c.execute("SELECT saldo_saturnos FROM monederos WHERE cliente_id=? AND activo=1", (cid,))
                    m2 = c.fetchone()
                    if m2:
                        bonus_ant = m2[0]
                        bonus_nuevo = bonus_ant + 50
                        c.execute("UPDATE monederos SET saldo_saturnos=?, total_acumulado=total_acumulado+50 WHERE cliente_id=?",
                                  (bonus_nuevo, cid))
                        c.execute("""INSERT INTO movimientos_saturnos (cliente_id,tipo,cantidad,saldo_anterior,saldo_nuevo,concepto,usuario,fecha,hora)
                                    VALUES (?,?,?,?,?,?,?,?,?)""",
                                  (cid, "ACUMULACION", 50, bonus_ant, bonus_nuevo,
                                   "Bonificación pago anticipado", usuario_actual, ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S")))
                        messagebox.showinfo("Bonificación", "+50 Saturnos por pagar antes del vencimiento!")
                c.execute("UPDATE creditos SET estado='PAGADO' WHERE id=?", (cred_id,))

            conn.commit()
            dlg.destroy()
            cargar_pagos()
            cargar_activos()
            messagebox.showinfo("Pago", f"Pago ${monto:,.2f} registrado. Folio: {folio_p}")

        tk.Button(form, text="REGISTRAR PAGO", command=aplicar_pago,
                 bg="#2E7D32", fg="white", font=("Segoe UI", 11, "bold"),
                 relief=tk.FLAT, padx=16, pady=6, cursor="hand2").grid(row=4, column=0, columnspan=2, pady=15)

    tk.Button(pago_toolbar, text="+ REGISTRAR PAGO", command=registrar_pago,
             bg="#2E7D32", fg="white", font=("Segoe UI", 10, "bold"),
             relief=tk.FLAT, padx=12, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=10)

    cols_pag = ("FOLIO PAGO", "CRÉDITO", "MONTO", "MÉTODO", "FECHA", "HORA", "USUARIO")
    tree_pagos = ttk.Treeview(tab_pag, columns=cols_pag, show="headings", height=14)
    for col in cols_pag:
        tree_pagos.heading(col, text=col)
    tree_pagos.column("FOLIO PAGO", width=150)
    tree_pagos.column("CRÉDITO", width=150)
    tree_pagos.column("MONTO", width=100)
    tree_pagos.column("MÉTODO", width=100)
    tree_pagos.column("FECHA", width=90)
    tree_pagos.column("HORA", width=70)
    tree_pagos.column("USUARIO", width=100)
    tree_pagos.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def cargar_pagos(filtro=""):
        for item in tree_pagos.get_children():
            tree_pagos.delete(item)
        q = """SELECT pc.folio_pago, cr.folio, pc.monto, pc.tipo_pago, pc.fecha, pc.hora, pc.usuario
               FROM pagos_credito pc JOIN creditos cr ON pc.credito_id=cr.id"""
        params = []
        if filtro:
            q += " WHERE cr.folio LIKE ? OR pc.folio_pago LIKE ?"
            params = [f"%{filtro}%", f"%{filtro}%"]
        q += " ORDER BY pc.id DESC LIMIT 100"
        c.execute(q, params)
        for row in c.fetchall():
            tree_pagos.insert("", "end", values=(row[0], row[1], f"${row[2]:,.2f}", row[3], row[4], row[5], row[6]))

    def buscar_pagos(event=None):
        cargar_pagos(busq_cred_entry.get())
    busq_cred_entry.bind("<KeyRelease>", buscar_pagos)
    cargar_pagos()

    # ==================== PESTAÑA CONFIGURACIÓN ====================
    tab_cfg_cr = tk.Frame(notebook, bg="white")
    notebook.add(tab_cfg_cr, text="  Configuración  ")

    tk.Label(tab_cfg_cr, text="CONFIGURACIÓN DE CRÉDITOS", font=("Segoe UI", 14, "bold"),
            bg="white", fg="#2E7D32").pack(pady=15)

    form_cfg = tk.Frame(tab_cfg_cr, bg="white")
    form_cfg.pack(padx=30, pady=10)

    c.execute("SELECT * FROM config_creditos WHERE id=1")
    cc = c.fetchone()
    cc_vals = {
        "max_pers": tk.StringVar(value=str(cc[1] if cc else 5000)),
        "max_clin": tk.StringVar(value=str(cc[2] if cc else 50000)),
        "plazo_pers": tk.StringVar(value=str(cc[3] if cc else 30)),
        "plazo_clin": tk.StringVar(value=str(cc[4] if cc else 60)),
        "tasa_pers": tk.StringVar(value=str(cc[5] if cc else 0)),
        "tasa_clin": tk.StringVar(value=str(cc[6] if cc else 0)),
        "requiere_aval": tk.IntVar(value=cc[7] if cc else 0),
    }

    cfg_campos = [
        ("Monto máximo Persona ($):", "max_pers", 0),
        ("Monto máximo Clínica ($):", "max_clin", 1),
        ("Plazo Persona (días):", "plazo_pers", 2),
        ("Plazo Clínica (días):", "plazo_clin", 3),
        ("Tasa interés Persona (%):", "tasa_pers", 4),
        ("Tasa interés Clínica (%):", "tasa_clin", 5),
    ]
    for label, key, row in cfg_campos:
        tk.Label(form_cfg, text=label, font=("Segoe UI", 10, "bold"), bg="white").grid(row=row, column=0, sticky="e", padx=8, pady=6)
        tk.Entry(form_cfg, textvariable=cc_vals[key], width=15, font=("Segoe UI", 10)).grid(row=row, column=1, padx=8, pady=6, sticky="w")

    tk.Checkbutton(form_cfg, text="Requiere Aval", variable=cc_vals["requiere_aval"],
                  font=("Segoe UI", 10), bg="white").grid(row=6, column=0, columnspan=2, pady=8)

    def guardar_cfg_cr():
        try:
            c.execute("""UPDATE config_creditos SET monto_max_persona=?, monto_max_clinica=?,
                        plazo_persona_dias=?, plazo_clinica_dias=?, tasa_interes_persona=?,
                        tasa_interes_clinica=?, requiere_aval=? WHERE id=1""",
                      (float(cc_vals["max_pers"].get()), float(cc_vals["max_clin"].get()),
                       int(cc_vals["plazo_pers"].get()), int(cc_vals["plazo_clin"].get()),
                       float(cc_vals["tasa_pers"].get()), float(cc_vals["tasa_clin"].get()),
                       cc_vals["requiere_aval"].get()))
            conn.commit()
            messagebox.showinfo("Guardado", "Configuración de créditos actualizada")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(form_cfg, text="GUARDAR CAMBIOS", command=guardar_cfg_cr,
             bg="#2E7D32", fg="white", font=("Segoe UI", 11, "bold"),
             relief=tk.FLAT, padx=20, pady=6, cursor="hand2").grid(row=7, column=0, columnspan=2, pady=15)


def ver_configuracion():
    limpiar()

    header_mod = tk.Frame(main, bg="#757575", height=42)
    header_mod.pack(fill=tk.X)
    header_mod.pack_propagate(False)
    tk.Label(header_mod, text="⚙️ CONFIGURACIÓN DEL SISTEMA", font=("Segoe UI", 13, "bold"),
            bg="#757575", fg="white").pack(side=tk.LEFT, padx=12, pady=10)

    # Notebook con pestañas
    notebook = ttk.Notebook(main)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ===================== PESTAÑA SUCURSALES =====================
    tab_suc = tk.Frame(notebook, bg="white")
    notebook.add(tab_suc, text="  Sucursales  ")

    # Lista de sucursales
    frame_lista = tk.Frame(tab_suc, bg="white")
    frame_lista.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    tk.Label(frame_lista, text="SUCURSALES", font=("Segoe UI", 12, "bold"),
            bg="white", fg=AZUL_FARMACIA).pack(pady=(5,10))

    cols_s = ("ID", "NOMBRE", "ACTIVA")
    tree_suc = ttk.Treeview(frame_lista, columns=cols_s, show="headings", height=8)
    tree_suc.heading("ID", text="ID")
    tree_suc.heading("NOMBRE", text="Nombre")
    tree_suc.heading("ACTIVA", text="Activa")
    tree_suc.column("ID", width=40)
    tree_suc.column("NOMBRE", width=200)
    tree_suc.column("ACTIVA", width=60)
    tree_suc.pack(fill=tk.Y, expand=True)

    # Panel de edición
    frame_edit = tk.Frame(tab_suc, bg="white")
    frame_edit.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    tk.Label(frame_edit, text="EDITAR SUCURSAL", font=("Segoe UI", 12, "bold"),
            bg="white", fg=AZUL_FARMACIA).grid(row=0, column=0, columnspan=3, pady=(5,15))

    campos = {}
    labels_campos = [
        ("nombre", "Nombre:", 1), ("direccion", "Dirección:", 2),
        ("telefono", "Teléfono:", 3), ("email", "Email:", 4),
        ("rfc", "RFC:", 5), ("ciudad", "Ciudad:", 6),
        ("estado", "Estado:", 7), ("cp", "C.P.:", 8),
    ]
    for key, label, row in labels_campos:
        tk.Label(frame_edit, text=label, font=("Segoe UI", 9, "bold"),
                bg="white").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        var = tk.StringVar()
        tk.Entry(frame_edit, textvariable=var, width=40, font=("Segoe UI", 9)
                ).grid(row=row, column=1, columnspan=2, padx=5, pady=3, sticky="w")
        campos[key] = var

    # Logo
    tk.Label(frame_edit, text="Logo:", font=("Segoe UI", 9, "bold"),
            bg="white").grid(row=9, column=0, sticky="e", padx=5, pady=3)
    logo_var = tk.StringVar()
    tk.Entry(frame_edit, textvariable=logo_var, width=30, font=("Segoe UI", 9),
            state="readonly").grid(row=9, column=1, padx=5, pady=3, sticky="w")

    def seleccionar_logo():
        ruta = filedialog.askopenfilename(filetypes=[("Imágenes","*.png *.jpg *.jpeg *.bmp")])
        if ruta:
            logo_var.set(ruta)

    tk.Button(frame_edit, text="Examinar", command=seleccionar_logo,
             bg="#1565C0", fg="white", font=("Segoe UI", 8), relief=tk.FLAT,
             padx=6, cursor="hand2").grid(row=9, column=2, padx=3)

    # Activa
    activa_var = tk.IntVar(value=1)
    tk.Checkbutton(frame_edit, text="Sucursal Activa", variable=activa_var,
                  font=("Segoe UI", 10), bg="white").grid(row=10, column=1, pady=5, sticky="w")

    suc_id_editando = tk.IntVar(value=0)

    def cargar_sucursales():
        for item in tree_suc.get_children():
            tree_suc.delete(item)
        c.execute("SELECT id, nombre, activa FROM sucursales ORDER BY id")
        for row in c.fetchall():
            tree_suc.insert("", "end", values=(row[0], row[1], "Sí" if row[2] else "No"))

    def seleccionar_sucursal(event=None):
        sel = tree_suc.selection()
        if not sel:
            return
        sid = tree_suc.item(sel[0])["values"][0]
        suc_id_editando.set(sid)
        c.execute("SELECT nombre,direccion,telefono,email,rfc,ciudad,estado,cp,logo_path,activa FROM sucursales WHERE id=?", (sid,))
        row = c.fetchone()
        if row:
            for i, key in enumerate(["nombre","direccion","telefono","email","rfc","ciudad","estado","cp"]):
                campos[key].set(row[i] or "")
            logo_var.set(row[8] or "")
            activa_var.set(row[9])

    tree_suc.bind("<<TreeviewSelect>>", seleccionar_sucursal)

    def guardar_sucursal():
        sid = suc_id_editando.get()
        if sid <= 0:
            messagebox.showwarning("Aviso", "Selecciona una sucursal")
            return
        c.execute("""UPDATE sucursales SET nombre=?,direccion=?,telefono=?,email=?,rfc=?,
                     ciudad=?,estado=?,cp=?,logo_path=?,activa=? WHERE id=?""",
                  (campos["nombre"].get(), campos["direccion"].get(), campos["telefono"].get(),
                   campos["email"].get(), campos["rfc"].get(), campos["ciudad"].get(),
                   campos["estado"].get(), campos["cp"].get(), logo_var.get(),
                   activa_var.get(), sid))
        conn.commit()
        cargar_sucursales()
        obtener_sucursal()
        messagebox.showinfo("Guardado", "Sucursal actualizada correctamente")

    tk.Button(frame_edit, text="GUARDAR CAMBIOS", command=guardar_sucursal,
             bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
             relief=tk.FLAT, padx=16, pady=6, cursor="hand2"
             ).grid(row=11, column=1, pady=15, sticky="w")

    cargar_sucursales()

    # ===================== PESTAÑA IMPRESIÓN =====================
    tab_imp = tk.Frame(notebook, bg="white")
    notebook.add(tab_imp, text="  Impresión  ")

    tk.Label(tab_imp, text="CONFIGURACIÓN DE IMPRESIÓN", font=("Segoe UI", 14, "bold"),
            bg="white", fg=AZUL_FARMACIA).pack(pady=(20,15))

    form_imp = tk.Frame(tab_imp, bg="white")
    form_imp.pack(padx=30, pady=10)

    # Obtener config actual
    suc = obtener_sucursal()

    tk.Label(form_imp, text="Impresora:", font=("Segoe UI", 10, "bold"),
            bg="white").grid(row=0, column=0, sticky="e", padx=8, pady=8)
    imp_nombre_var = tk.StringVar(value=suc.get("impresora",""))
    tk.Entry(form_imp, textvariable=imp_nombre_var, width=35, font=("Segoe UI", 10)
            ).grid(row=0, column=1, padx=8, pady=8)
    tk.Label(form_imp, text="(Nombre de impresora o vacío para default)",
            font=("Segoe UI", 8), bg="white", fg="#999").grid(row=0, column=2, padx=4)

    tk.Label(form_imp, text="Ancho papel:", font=("Segoe UI", 10, "bold"),
            bg="white").grid(row=1, column=0, sticky="e", padx=8, pady=8)
    ancho_var = tk.StringVar(value=str(suc.get("ancho",80)))
    combo_ancho = ttk.Combobox(form_imp, textvariable=ancho_var, width=10,
                               values=["58", "80"], state="readonly")
    combo_ancho.grid(row=1, column=1, sticky="w", padx=8, pady=8)
    tk.Label(form_imp, text="mm (58mm térmica chica, 80mm térmica estándar)",
            font=("Segoe UI", 8), bg="white", fg="#999").grid(row=1, column=2, padx=4)

    tk.Label(form_imp, text="Copias:", font=("Segoe UI", 10, "bold"),
            bg="white").grid(row=2, column=0, sticky="e", padx=8, pady=8)
    copias_var = tk.StringVar(value=str(suc.get("copias",1)))
    tk.Spinbox(form_imp, textvariable=copias_var, from_=1, to=5, width=5,
              font=("Segoe UI", 10)).grid(row=2, column=1, sticky="w", padx=8, pady=8)

    auto_imp_var = tk.IntVar(value=suc.get("auto_imprimir",0))
    tk.Checkbutton(form_imp, text="Imprimir automáticamente después de cobrar",
                  variable=auto_imp_var, font=("Segoe UI", 10), bg="white"
                  ).grid(row=3, column=0, columnspan=3, pady=10, sticky="w", padx=8)

    def guardar_impresion():
        sid = suc.get("id", 1)
        c.execute("""UPDATE sucursales SET impresora_nombre=?, impresora_ancho=?,
                     copias_ticket=?, auto_imprimir=? WHERE id=?""",
                  (imp_nombre_var.get(), int(ancho_var.get()),
                   int(copias_var.get()), auto_imp_var.get(), sid))
        conn.commit()
        obtener_sucursal()
        messagebox.showinfo("Guardado", "Configuración de impresión actualizada")

    tk.Button(form_imp, text="GUARDAR CONFIGURACIÓN", command=guardar_impresion,
             bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"),
             relief=tk.FLAT, padx=20, pady=8, cursor="hand2"
             ).grid(row=4, column=0, columnspan=3, pady=20)

    # Vista previa
    tk.Label(tab_imp, text="Vista previa del ticket:", font=("Segoe UI", 10, "bold"),
            bg="white", fg="#555").pack(pady=(10,5))

    def ver_preview():
        items_demo = [("MED000001", "TEMPRA 500MG TAB CAJA 20", 85.50, 2, 171.00),
                      ("MED000002", "ADVIL 400MG CAP CAJA 10", 120.00, 1, 120.00)]
        texto = generar_texto_ticket("V20260130001", "2026-01-30", "10:30:00",
                                     "PUBLICO GENERAL", "EFECTIVO", items_demo, 291.00,
                                     {"efectivo": 300.0, "tarjeta": 0, "vale": 0, "cambio": 9.0, "tipo": "EFECTIVO"})
        prev_win = tk.Toplevel(main)
        prev_win.title("Vista Previa Ticket")
        prev_win.geometry("500x600")
        prev_win.configure(bg="white")
        txt = tk.Text(prev_win, font=("Courier New", 9), wrap=tk.NONE, bg="#FFFFF0")
        txt.insert("1.0", texto)
        txt.config(state=tk.DISABLED)
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tk.Button(tab_imp, text="VER VISTA PREVIA", command=ver_preview,
             bg="#1565C0", fg="white", font=("Segoe UI", 10, "bold"),
             relief=tk.FLAT, padx=16, pady=6, cursor="hand2").pack(pady=5)

    # ===================== PESTAÑA ESCÁNER =====================
    tab_scan = tk.Frame(notebook, bg="white")
    notebook.add(tab_scan, text="  Escáner  ")

    tk.Label(tab_scan, text="CONFIGURACIÓN DE ESCÁNER", font=("Segoe UI", 14, "bold"),
            bg="white", fg=AZUL_FARMACIA).pack(pady=(20,10))

    info_scan = tk.Frame(tab_scan, bg="#E3F2FD", relief=tk.RIDGE, bd=1)
    info_scan.pack(fill=tk.X, padx=20, pady=10)

    tk.Label(info_scan, text="Información del Escáner", font=("Segoe UI", 11, "bold"),
            bg="#E3F2FD", fg="#1565C0").pack(pady=(10,5))

    for txt in [
        "El escáner de códigos de barras funciona automáticamente.",
        "Formatos soportados: EAN-13, UPC-A, EAN-8, Códigos internos",
        "Detección automática: entrada rápida < 80ms entre teclas",
        "Sonido BEEP al escanear exitosamente",
        "Alerta sonora si el código no existe en el catálogo",
    ]:
        tk.Label(info_scan, text=f"  • {txt}", font=("Segoe UI", 9),
                bg="#E3F2FD", fg="#333", anchor="w").pack(fill=tk.X, padx=15)
    tk.Label(info_scan, text="", bg="#E3F2FD").pack(pady=3)

    # Historial de últimos escaneos
    tk.Label(tab_scan, text="ÚLTIMOS 10 CÓDIGOS ESCANEADOS", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#333").pack(pady=(15,5))

    cols_h = ("HORA", "CÓDIGO", "PRODUCTO")
    tree_scan = ttk.Treeview(tab_scan, columns=cols_h, show="headings", height=10)
    tree_scan.heading("HORA", text="Hora")
    tree_scan.heading("CÓDIGO", text="Código")
    tree_scan.heading("PRODUCTO", text="Producto")
    tree_scan.column("HORA", width=80)
    tree_scan.column("CÓDIGO", width=150)
    tree_scan.column("PRODUCTO", width=400)
    tree_scan.pack(fill=tk.X, padx=20, pady=5)

    for item in historial_escaner:
        tree_scan.insert("", "end", values=(item["hora"], item["codigo"], item["nombre"][:50]))

    def refrescar_historial():
        for item in tree_scan.get_children():
            tree_scan.delete(item)
        for item in historial_escaner:
            tree_scan.insert("", "end", values=(item["hora"], item["codigo"], item["nombre"][:50]))

    tk.Button(tab_scan, text="REFRESCAR", command=refrescar_historial,
             bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=12, pady=4, cursor="hand2").pack(pady=8)

    # Estadística: productos más escaneados
    tk.Label(tab_scan, text="PRODUCTOS MÁS VENDIDOS POR ESCÁNER", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#333").pack(pady=(10,5))

    # Contar frecuencias del historial
    from collections import Counter
    freq = Counter(item["codigo"] for item in historial_escaner)
    if freq:
        for codigo, count in freq.most_common(5):
            nombre = next((h["nombre"] for h in historial_escaner if h["codigo"]==codigo), "")
            tk.Label(tab_scan, text=f"  {codigo} - {nombre[:40]} ({count} veces)",
                    font=("Segoe UI", 9), bg="white", fg="#555", anchor="w").pack(fill=tk.X, padx=25)
    else:
        tk.Label(tab_scan, text="  Sin datos aún. Escanea productos en el módulo de Ventas.",
                font=("Segoe UI", 9), bg="white", fg="#999").pack(padx=25)

    # ===================== PESTAÑA AUDITORÍA =====================
    tab_audit = tk.Frame(notebook, bg="white")
    notebook.add(tab_audit, text="  Auditoría  ")

    tk.Label(tab_audit, text="📋 REGISTRO DE AUDITORÍA", font=("Segoe UI", 14, "bold"),
            bg="white", fg=AZUL_FARMACIA).pack(pady=(15,10))

    # Filtros
    filtros_audit = tk.Frame(tab_audit, bg="white")
    filtros_audit.pack(fill=tk.X, padx=20, pady=5)

    tk.Label(filtros_audit, text="Fecha:", font=("Segoe UI", 9, "bold"),
            bg="white").pack(side=tk.LEFT, padx=5)
    fecha_audit_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
    tk.Entry(filtros_audit, textvariable=fecha_audit_var, width=12, font=("Segoe UI", 9)
            ).pack(side=tk.LEFT, padx=5)

    tk.Label(filtros_audit, text="Acción:", font=("Segoe UI", 9, "bold"),
            bg="white").pack(side=tk.LEFT, padx=10)
    accion_audit_var = tk.StringVar(value="TODOS")
    ttk.Combobox(filtros_audit, textvariable=accion_audit_var, width=15,
                values=["TODOS", "VENTA", "COBRO", "LOGIN", "LOGOUT", "PRODUCTO", "CLIENTE", "OFERTA"],
                state="readonly").pack(side=tk.LEFT, padx=5)

    # Tabla de auditoría
    tree_audit_frame = tk.Frame(tab_audit, bg="white")
    tree_audit_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    cols_audit = ("ID", "FECHA", "HORA", "USUARIO", "ACCIÓN", "TABLA", "DETALLE")
    tree_audit = ttk.Treeview(tree_audit_frame, columns=cols_audit, show="headings", height=15)
    for col in cols_audit:
        tree_audit.heading(col, text=col)
    tree_audit.column("ID", width=50)
    tree_audit.column("FECHA", width=90)
    tree_audit.column("HORA", width=70)
    tree_audit.column("USUARIO", width=100)
    tree_audit.column("ACCIÓN", width=80)
    tree_audit.column("TABLA", width=80)
    tree_audit.column("DETALLE", width=350)

    scroll_audit = ttk.Scrollbar(tree_audit_frame, orient="vertical", command=tree_audit.yview)
    tree_audit.configure(yscrollcommand=scroll_audit.set)
    tree_audit.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll_audit.pack(side=tk.RIGHT, fill=tk.Y)

    def cargar_auditoria():
        for item in tree_audit.get_children():
            tree_audit.delete(item)
        fecha = fecha_audit_var.get()
        accion = accion_audit_var.get()
        query = "SELECT id, fecha, hora, usuario, accion, tabla_afectada, detalle FROM auditoria WHERE fecha=?"
        params = [fecha]
        if accion != "TODOS":
            query += " AND accion=?"
            params.append(accion)
        query += " ORDER BY id DESC LIMIT 200"
        try:
            c.execute(query, params)
            for row in c.fetchall():
                tree_audit.insert("", "end", values=row)
        except:
            # Crear tabla si no existe
            c.execute("""CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT, hora TEXT, usuario TEXT, accion TEXT,
                tabla_afectada TEXT, detalle TEXT)""")
            conn.commit()

    tk.Button(filtros_audit, text="🔍 BUSCAR", command=cargar_auditoria,
             bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=12, cursor="hand2").pack(side=tk.LEFT, padx=15)

    cargar_auditoria()

    # ===================== PESTAÑA VALES =====================
    tab_vales = tk.Frame(notebook, bg="white")
    notebook.add(tab_vales, text="  📄 Vales  ")

    tk.Label(tab_vales, text="📄 GENERAR VALE DE PEDIDO ESPECIAL", font=("Segoe UI", 14, "bold"),
            bg="white", fg=AZUL_FARMACIA).pack(pady=(15,10))

    tk.Label(tab_vales, text="Para medicamentos que no tenemos en stock y conseguimos para el cliente",
            font=("Segoe UI", 9), bg="white", fg="#666").pack(pady=(0,15))

    # Frame principal del vale
    vale_main = tk.Frame(tab_vales, bg="white")
    vale_main.pack(fill=tk.BOTH, expand=True, padx=20)

    # Frame izquierdo - Formulario
    vale_form = tk.Frame(vale_main, bg="#F5F5F5", relief=tk.RIDGE, bd=1)
    vale_form.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10), pady=5)

    tk.Label(vale_form, text="DATOS DEL VALE", font=("Segoe UI", 11, "bold"),
            bg="#F5F5F5", fg="#1565C0").pack(pady=(15,10))

    # Variables del vale
    vale_folio_var = tk.StringVar(value=f"VALE-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    vale_fecha_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
    vale_cliente_var = tk.StringVar()
    vale_telefono_var = tk.StringVar()
    vale_producto_var = tk.StringVar()
    vale_cantidad_var = tk.StringVar(value="1")
    vale_precio_est_var = tk.StringVar()
    vale_anticipo_var = tk.StringVar()
    vale_observaciones_var = tk.StringVar()

    campos_vale = tk.Frame(vale_form, bg="#F5F5F5")
    campos_vale.pack(padx=20, pady=10)

    labels_vale = [
        ("Folio:", vale_folio_var, 0, True),
        ("Fecha:", vale_fecha_var, 1, True),
        ("Cliente:", vale_cliente_var, 2, False),
        ("Teléfono:", vale_telefono_var, 3, False),
        ("Medicamento:", vale_producto_var, 4, False),
        ("Cantidad:", vale_cantidad_var, 5, False),
        ("Precio Estimado $:", vale_precio_est_var, 6, False),
        ("Anticipo $:", vale_anticipo_var, 7, False),
        ("Observaciones:", vale_observaciones_var, 8, False),
    ]

    for label, var, row, readonly in labels_vale:
        tk.Label(campos_vale, text=label, font=("Segoe UI", 9, "bold"),
                bg="#F5F5F5").grid(row=row, column=0, sticky="e", padx=5, pady=4)
        state = "readonly" if readonly else "normal"
        width = 40 if label != "Cantidad:" else 10
        tk.Entry(campos_vale, textvariable=var, width=width, font=("Segoe UI", 9),
                state=state).grid(row=row, column=1, sticky="w", padx=5, pady=4)

    # Botón buscar producto
    def buscar_producto_vale():
        busq = vale_producto_var.get()
        if len(busq) < 2:
            return
        c.execute("SELECT codigo, nombre, precio_venta FROM productos WHERE nombre LIKE ? LIMIT 20", (f"%{busq}%",))
        resultados = c.fetchall()
        if resultados:
            # Ventana de selección
            sel_win = tk.Toplevel(main)
            sel_win.title("Seleccionar Producto")
            sel_win.geometry("600x400")
            sel_win.configure(bg="white")

            tk.Label(sel_win, text="Selecciona el medicamento:", font=("Segoe UI", 11, "bold"),
                    bg="white").pack(pady=10)

            listbox = tk.Listbox(sel_win, font=("Segoe UI", 10), height=15)
            for r in resultados:
                listbox.insert(tk.END, f"{r[0]} - {r[1]} - ${r[2]:,.2f}")
            listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            def seleccionar():
                sel = listbox.curselection()
                if sel:
                    item = resultados[sel[0]]
                    vale_producto_var.set(item[1])
                    vale_precio_est_var.set(f"{item[2]:.2f}")
                    sel_win.destroy()

            tk.Button(sel_win, text="SELECCIONAR", command=seleccionar,
                     bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
                     relief=tk.FLAT, padx=15, pady=5).pack(pady=10)

    tk.Button(campos_vale, text="🔍", command=buscar_producto_vale,
             bg="#1565C0", fg="white", font=("Segoe UI", 9),
             relief=tk.FLAT, padx=6, cursor="hand2").grid(row=4, column=2, padx=3)

    # Frame derecho - Vista previa del vale
    vale_preview = tk.Frame(vale_main, bg="white", relief=tk.RIDGE, bd=2)
    vale_preview.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10,0), pady=5)

    tk.Label(vale_preview, text="VISTA PREVIA", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#1565C0").pack(pady=(10,5))

    preview_text = tk.Text(vale_preview, font=("Courier New", 9), width=45, height=25,
                          bg="#FFFFF0", wrap=tk.WORD)
    preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def actualizar_preview(*args):
        suc = obtener_sucursal()
        anticipo = float(vale_anticipo_var.get() or 0)
        precio = float(vale_precio_est_var.get() or 0)
        resta = precio - anticipo

        texto = f"""
╔══════════════════════════════════════════╗
║        *** VALE SOLICITADO ***           ║
╠══════════════════════════════════════════╣
║       🏥 FARMACIAS MADRID 🏥            ║
╠══════════════════════════════════════════╣
║  {suc.get('direccion', 'Dirección no configurada')[:40]}
║  Tel: {suc.get('telefono', '')}
║  RFC: {suc.get('rfc', '')}
╠══════════════════════════════════════════╣
║         VALE DE PEDIDO ESPECIAL          ║
╠══════════════════════════════════════════╣
║  Folio: {vale_folio_var.get()}
║  Fecha: {vale_fecha_var.get()}
╠══════════════════════════════════════════╣
║  CLIENTE: {vale_cliente_var.get()[:30]}
║  Teléfono: {vale_telefono_var.get()}
╠══════════════════════════════════════════╣
║  MEDICAMENTO SOLICITADO:
║  {vale_producto_var.get()[:40]}
║  Cantidad: {vale_cantidad_var.get()}
╠══════════════════════════════════════════╣
║  Precio Estimado:    $ {precio:>10,.2f}
║  Anticipo Recibido:  $ {anticipo:>10,.2f}
║  ─────────────────────────────────
║  RESTA POR PAGAR:    $ {resta:>10,.2f}
╠══════════════════════════════════════════╣
║  Observaciones:
║  {vale_observaciones_var.get()[:40]}
╠══════════════════════════════════════════╣
║                                          ║
║  Firma del Cliente: _________________    ║
║                                          ║
║  Firma Farmacias Madrid: ____________    ║
║                                          ║
╠══════════════════════════════════════════╣
║  * Este vale NO es comprobante fiscal    ║
║  * Vigencia: 15 días a partir de la fecha║
║  * Conserve este vale para recoger       ║
║    su medicamento                        ║
╚══════════════════════════════════════════╝
        www.farmaciasmadrid.com.mx
"""
        preview_text.config(state=tk.NORMAL)
        preview_text.delete("1.0", tk.END)
        preview_text.insert("1.0", texto)
        preview_text.config(state=tk.DISABLED)

    # Actualizar preview cuando cambien los campos
    for var in [vale_folio_var, vale_cliente_var, vale_telefono_var, vale_producto_var,
                vale_cantidad_var, vale_precio_est_var, vale_anticipo_var, vale_observaciones_var]:
        var.trace_add("write", actualizar_preview)

    actualizar_preview()

    # Botones de acción
    btns_vale = tk.Frame(tab_vales, bg="white")
    btns_vale.pack(fill=tk.X, padx=20, pady=15)

    def guardar_vale():
        if not vale_cliente_var.get() or not vale_producto_var.get():
            messagebox.showwarning("Datos incompletos", "Ingresa el cliente y el medicamento")
            return

        # Crear tabla si no existe
        c.execute("""CREATE TABLE IF NOT EXISTS vales_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio TEXT UNIQUE, fecha TEXT, hora TEXT,
            cliente_nombre TEXT, cliente_telefono TEXT,
            producto TEXT, cantidad INTEGER, precio_estimado REAL,
            anticipo REAL, resta REAL, observaciones TEXT,
            estado TEXT DEFAULT 'PENDIENTE', usuario TEXT,
            fecha_entrega TEXT, entregado_por TEXT)""")

        anticipo = float(vale_anticipo_var.get() or 0)
        precio = float(vale_precio_est_var.get() or 0)
        resta = precio - anticipo

        c.execute("""INSERT INTO vales_pedido (folio, fecha, hora, cliente_nombre, cliente_telefono,
                    producto, cantidad, precio_estimado, anticipo, resta, observaciones, usuario)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                 (vale_folio_var.get(), datetime.now().strftime('%Y-%m-%d'),
                  datetime.now().strftime('%H:%M:%S'), vale_cliente_var.get(),
                  vale_telefono_var.get(), vale_producto_var.get(),
                  int(vale_cantidad_var.get() or 1), precio, anticipo, resta,
                  vale_observaciones_var.get(), usuario_actual))
        conn.commit()

        messagebox.showinfo("Vale Guardado", f"Vale {vale_folio_var.get()} guardado correctamente")

        # Generar nuevo folio
        vale_folio_var.set(f"VALE-{datetime.now().strftime('%Y%m%d%H%M%S')}")

    def imprimir_vale():
        guardar_vale()
        # Generar archivo para imprimir
        suc = obtener_sucursal()
        anticipo = float(vale_anticipo_var.get() or 0)
        precio = float(vale_precio_est_var.get() or 0)
        resta = precio - anticipo

        contenido = f"""
========================================
        *** VALE SOLICITADO ***
========================================
       🏥 FARMACIAS MADRID 🏥
========================================
{suc.get('direccion', '')}
Tel: {suc.get('telefono', '')}
RFC: {suc.get('rfc', '')}
========================================
     VALE DE PEDIDO ESPECIAL
========================================
Folio: {vale_folio_var.get()}
Fecha: {vale_fecha_var.get()}
----------------------------------------
CLIENTE: {vale_cliente_var.get()}
Teléfono: {vale_telefono_var.get()}
----------------------------------------
MEDICAMENTO SOLICITADO:
{vale_producto_var.get()}
Cantidad: {vale_cantidad_var.get()}
----------------------------------------
Precio Estimado:    $ {precio:>10,.2f}
Anticipo Recibido:  $ {anticipo:>10,.2f}
----------------------------------------
RESTA POR PAGAR:    $ {resta:>10,.2f}
----------------------------------------
Observaciones:
{vale_observaciones_var.get()}
----------------------------------------


Firma Cliente: _____________________


Firma Farmacias Madrid: ____________


========================================
* Este vale NO es comprobante fiscal
* Vigencia: 15 días
* Conserve este vale
========================================
     www.farmaciasmadrid.com.mx
"""
        # Guardar archivo
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta = os.path.join(base_dir, f"vale_{vale_folio_var.get()}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)

        try:
            os.startfile(ruta, "print")
            messagebox.showinfo("Imprimiendo", "Vale enviado a imprimir")
        except:
            messagebox.showinfo("Archivo Guardado", f"Vale guardado en: {ruta}")

    def ver_vales_pendientes():
        """Muestra vales pendientes de entregar."""
        win = tk.Toplevel(main)
        win.title("📋 Vales Pendientes")
        win.geometry("900x500")
        win.configure(bg="white")

        tk.Label(win, text="📋 VALES PENDIENTES DE ENTREGA", font=("Segoe UI", 14, "bold"),
                bg="white", fg=AZUL_FARMACIA).pack(pady=15)

        cols = ("FOLIO", "FECHA", "CLIENTE", "TELÉFONO", "MEDICAMENTO", "ANTICIPO", "RESTA", "ESTADO")
        tree_vales = ttk.Treeview(win, columns=cols, show="headings", height=15)
        for col in cols:
            tree_vales.heading(col, text=col)
        tree_vales.column("FOLIO", width=130)
        tree_vales.column("FECHA", width=80)
        tree_vales.column("CLIENTE", width=120)
        tree_vales.column("TELÉFONO", width=100)
        tree_vales.column("MEDICAMENTO", width=200)
        tree_vales.column("ANTICIPO", width=80)
        tree_vales.column("RESTA", width=80)
        tree_vales.column("ESTADO", width=80)
        tree_vales.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        try:
            c.execute("""SELECT folio, fecha, cliente_nombre, cliente_telefono, producto,
                        anticipo, resta, estado FROM vales_pedido
                        WHERE estado='PENDIENTE' ORDER BY fecha DESC""")
            for row in c.fetchall():
                tree_vales.insert("", "end", values=(row[0], row[1], row[2], row[3],
                                                    row[4][:30], f"${row[5]:,.2f}", f"${row[6]:,.2f}", row[7]))
        except:
            pass

        def marcar_entregado():
            sel = tree_vales.selection()
            if not sel:
                return
            folio = tree_vales.item(sel[0])["values"][0]
            if messagebox.askyesno("Confirmar", f"¿Marcar vale {folio} como ENTREGADO?"):
                c.execute("""UPDATE vales_pedido SET estado='ENTREGADO', fecha_entrega=?, entregado_por=?
                            WHERE folio=?""", (datetime.now().strftime('%Y-%m-%d'), usuario_actual, folio))
                conn.commit()
                tree_vales.delete(sel[0])
                messagebox.showinfo("Entregado", "Vale marcado como entregado")

        tk.Button(win, text="✅ MARCAR COMO ENTREGADO", command=marcar_entregado,
                 bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
                 relief=tk.FLAT, padx=15, pady=8, cursor="hand2").pack(pady=15)

    tk.Button(btns_vale, text="💾 GUARDAR VALE", command=guardar_vale,
             bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"),
             relief=tk.FLAT, padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=10)

    tk.Button(btns_vale, text="🖨️ IMPRIMIR VALE", command=imprimir_vale,
             bg="#1565C0", fg="white", font=("Segoe UI", 11, "bold"),
             relief=tk.FLAT, padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=10)

    tk.Button(btns_vale, text="📋 VER PENDIENTES", command=ver_vales_pendientes,
             bg="#FF9800", fg="white", font=("Segoe UI", 11, "bold"),
             relief=tk.FLAT, padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=10)

    def enviar_vale_whatsapp():
        """Envía el vale por WhatsApp al cliente."""
        if not vale_cliente_var.get() or not vale_producto_var.get():
            messagebox.showwarning("Datos incompletos", "Ingresa el cliente y el medicamento")
            return

        # Guardar primero
        guardar_vale()

        suc = obtener_sucursal()
        anticipo = float(vale_anticipo_var.get() or 0)
        precio = float(vale_precio_est_var.get() or 0)
        resta = precio - anticipo

        # Mensaje para WhatsApp
        mensaje = f"""📋 *VALE SOLICITADO*
🏥 *FARMACIAS MADRID*

━━━━━━━━━━━━━━━━━━━━━
📄 *VALE DE PEDIDO ESPECIAL*
━━━━━━━━━━━━━━━━━━━━━

📌 *Folio:* {vale_folio_var.get()}
📅 *Fecha:* {vale_fecha_var.get()}

👤 *CLIENTE:*
• Nombre: {vale_cliente_var.get()}
• Teléfono: {vale_telefono_var.get()}

💊 *MEDICAMENTO SOLICITADO:*
{vale_producto_var.get()}
Cantidad: {vale_cantidad_var.get()}

━━━━━━━━━━━━━━━━━━━━━
💰 *RESUMEN DE PAGO:*
• Precio Estimado: ${precio:,.2f}
• Anticipo Recibido: ${anticipo:,.2f}
• *RESTA POR PAGAR: ${resta:,.2f}*
━━━━━━━━━━━━━━━━━━━━━

📝 Observaciones: {vale_observaciones_var.get() or 'Ninguna'}

⚠️ *IMPORTANTE:*
• Este vale NO es comprobante fiscal
• Vigencia: 15 días
• Conserve este vale para recoger su medicamento

🏥 *{suc.get('nombre', 'FARMACIAS MADRID')}*
📍 {suc.get('direccion', '')}
📞 {suc.get('telefono', '')}

_Gracias por su preferencia_
www.farmaciasmadrid.com.mx"""

        # Ventana para ingresar teléfono
        win_wa = tk.Toplevel(main)
        win_wa.title("📱 Enviar Vale por WhatsApp")
        win_wa.geometry("400x250")
        win_wa.configure(bg="white")
        win_wa.transient(main)
        win_wa.grab_set()

        tk.Label(win_wa, text="📱 ENVIAR VALE POR WHATSAPP", font=("Segoe UI", 12, "bold"),
                bg="white", fg="#25D366").pack(pady=15)

        tk.Label(win_wa, text="Teléfono del cliente (con código de país):",
                font=("Segoe UI", 10), bg="white").pack(pady=5)

        tel_vale_var = tk.StringVar()
        # Usar teléfono del cliente si tiene
        tel_cliente = vale_telefono_var.get().strip()
        if tel_cliente:
            # Agregar código de país si no tiene
            if not tel_cliente.startswith("52") and not tel_cliente.startswith("+"):
                tel_cliente = "52" + tel_cliente.replace(" ", "").replace("-", "")
            tel_vale_var.set(tel_cliente)
        else:
            tel_vale_var.set("52")

        entry_tel = tk.Entry(win_wa, textvariable=tel_vale_var, width=25, font=("Segoe UI", 14),
                            justify="center")
        entry_tel.pack(pady=10)

        def enviar_wa():
            telefono = tel_vale_var.get().strip().replace(" ", "").replace("-", "").replace("+", "")
            if len(telefono) < 10:
                messagebox.showwarning("Teléfono inválido", "Ingresa un número válido con código de país")
                return

            import urllib.parse
            url = f"https://wa.me/{telefono}?text={urllib.parse.quote(mensaje)}"
            import webbrowser
            webbrowser.open(url)
            win_wa.destroy()
            messagebox.showinfo("WhatsApp", "Vale enviado por WhatsApp")

        tk.Button(win_wa, text="📤 ENVIAR VALE", command=enviar_wa,
                 bg="#25D366", fg="white", font=("Segoe UI", 12, "bold"),
                 relief=tk.FLAT, padx=25, pady=10, cursor="hand2").pack(pady=20)

    tk.Button(btns_vale, text="📱 WHATSAPP", command=enviar_vale_whatsapp,
             bg="#25D366", fg="white", font=("Segoe UI", 11, "bold"),
             relief=tk.FLAT, padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=10)

    def limpiar_vale():
        vale_folio_var.set(f"VALE-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        vale_cliente_var.set("")
        vale_telefono_var.set("")
        vale_producto_var.set("")
        vale_cantidad_var.set("1")
        vale_precio_est_var.set("")
        vale_anticipo_var.set("")
        vale_observaciones_var.set("")

    tk.Button(btns_vale, text="🗑️ LIMPIAR", command=limpiar_vale,
             bg="#757575", fg="white", font=("Segoe UI", 11, "bold"),
             relief=tk.FLAT, padx=20, pady=10, cursor="hand2").pack(side=tk.RIGHT, padx=10)

    # ===================== PESTAÑA E-COMMERCE =====================
    tab_ecom = tk.Frame(notebook, bg="white")
    notebook.add(tab_ecom, text="  🛒 E-Commerce  ")

    tk.Label(tab_ecom, text="🛒 E-COMMERCE - AMAZON & MERCADO LIBRE", font=("Segoe UI", 14, "bold"),
            bg="white", fg="#FF9900").pack(pady=15)

    tk.Label(tab_ecom, text="Exporta tus productos para vender en Amazon y Mercado Libre",
            font=("Segoe UI", 10), bg="white", fg=GRIS_TEXTO).pack()

    # Frame principal dividido
    ecom_main = tk.Frame(tab_ecom, bg="white")
    ecom_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # --- PANEL IZQUIERDO: Exportar productos ---
    export_frame = tk.LabelFrame(ecom_main, text="📤 EXPORTAR CATÁLOGO", font=("Segoe UI", 11, "bold"),
                                 bg="white", fg="#FF9900")
    export_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10), pady=5)

    # Filtros de exportación
    tk.Label(export_frame, text="Filtrar productos a exportar:", font=("Segoe UI", 9, "bold"),
            bg="white").pack(anchor="w", padx=10, pady=(10,5))

    filt_ecom = tk.Frame(export_frame, bg="white")
    filt_ecom.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(filt_ecom, text="Categoría:", bg="white").pack(side=tk.LEFT)
    cat_ecom_var = tk.StringVar(value="TODAS")
    cat_combo = ttk.Combobox(filt_ecom, textvariable=cat_ecom_var, width=20, state="readonly")
    cat_combo['values'] = ["TODAS", "MEDICAMENTOS", "HIGIENE", "BELLEZA", "BEBÉS", "SUPLEMENTOS"]
    cat_combo.pack(side=tk.LEFT, padx=5)

    tk.Label(filt_ecom, text="Stock mínimo:", bg="white").pack(side=tk.LEFT, padx=(15,0))
    stock_min_var = tk.StringVar(value="1")
    tk.Entry(filt_ecom, textvariable=stock_min_var, width=6).pack(side=tk.LEFT, padx=5)

    solo_oferta_var = tk.IntVar(value=0)
    tk.Checkbutton(filt_ecom, text="Solo en oferta", variable=solo_oferta_var,
                  bg="white").pack(side=tk.LEFT, padx=15)

    # Info de productos
    info_export = tk.Frame(export_frame, bg="#FFF3E0", relief=tk.RIDGE, bd=1)
    info_export.pack(fill=tk.X, padx=10, pady=10)

    productos_count_var = tk.StringVar(value="Calculando productos...")
    tk.Label(info_export, textvariable=productos_count_var, font=("Segoe UI", 10),
            bg="#FFF3E0", fg="#E65100").pack(pady=8)

    def contar_productos():
        query = "SELECT COUNT(*) FROM productos WHERE stock > ?"
        params = [int(stock_min_var.get() or 0)]
        if cat_ecom_var.get() != "TODAS":
            query += " AND categoria=?"
            params.append(cat_ecom_var.get())
        if solo_oferta_var.get():
            query += " AND precio_oferta > 0"
        c.execute(query, params)
        count = c.fetchone()[0]
        productos_count_var.set(f"📦 {count:,} productos listos para exportar")

    cat_combo.bind("<<ComboboxSelected>>", lambda e: contar_productos())
    contar_productos()

    # Botones de exportación
    btns_export = tk.Frame(export_frame, bg="white")
    btns_export.pack(fill=tk.X, padx=10, pady=10)

    def exportar_amazon():
        """Exporta productos en formato Amazon Seller Central."""
        import csv
        query = "SELECT codigo, nombre, precio_venta, precio_oferta, stock, categoria, laboratorio FROM productos WHERE stock > ?"
        params = [int(stock_min_var.get() or 0)]
        if cat_ecom_var.get() != "TODAS":
            query += " AND categoria=?"
            params.append(cat_ecom_var.get())
        if solo_oferta_var.get():
            query += " AND precio_oferta > 0"

        c.execute(query, params)
        productos = c.fetchall()

        if not productos:
            messagebox.showwarning("Sin productos", "No hay productos para exportar con esos filtros")
            return

        ruta = filedialog.asksaveasfilename(defaultextension=".csv",
                                           filetypes=[("CSV", "*.csv")],
                                           initialfile=f"amazon_productos_{datetime.now().strftime('%Y%m%d')}.csv")
        if not ruta:
            return

        with open(ruta, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Headers de Amazon
            writer.writerow(['sku', 'product-name', 'standard-price', 'sale-price', 'quantity',
                           'product-category', 'brand', 'condition', 'fulfillment-channel'])
            for p in productos:
                precio = p[3] if p[3] and p[3] > 0 else p[2]
                writer.writerow([p[0], p[1], p[2], precio, p[4], p[5], p[6] or 'FARMACIAS MADRID', 'new', 'DEFAULT'])

        messagebox.showinfo("Exportado", f"✅ {len(productos)} productos exportados para Amazon\n\n{ruta}")
        os.startfile(os.path.dirname(ruta))

    def exportar_mercadolibre():
        """Exporta productos en formato Mercado Libre."""
        import csv
        query = "SELECT codigo, nombre, precio_venta, precio_oferta, stock, categoria, laboratorio FROM productos WHERE stock > ?"
        params = [int(stock_min_var.get() or 0)]
        if cat_ecom_var.get() != "TODAS":
            query += " AND categoria=?"
            params.append(cat_ecom_var.get())
        if solo_oferta_var.get():
            query += " AND precio_oferta > 0"

        c.execute(query, params)
        productos = c.fetchall()

        if not productos:
            messagebox.showwarning("Sin productos", "No hay productos para exportar con esos filtros")
            return

        ruta = filedialog.asksaveasfilename(defaultextension=".csv",
                                           filetypes=[("CSV", "*.csv")],
                                           initialfile=f"mercadolibre_{datetime.now().strftime('%Y%m%d')}.csv")
        if not ruta:
            return

        with open(ruta, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Headers de Mercado Libre
            writer.writerow(['id', 'titulo', 'precio', 'precio_promocion', 'cantidad_disponible',
                           'categoria', 'marca', 'condicion', 'tipo_publicacion', 'envio_gratis'])
            for p in productos:
                precio = p[3] if p[3] and p[3] > 0 else p[2]
                envio_gratis = "SI" if precio > 299 else "NO"
                writer.writerow([p[0], p[1], p[2], precio, p[4], p[5], p[6] or 'FARMACIAS MADRID',
                               'nuevo', 'gold_special', envio_gratis])

        messagebox.showinfo("Exportado", f"✅ {len(productos)} productos exportados para Mercado Libre\n\n{ruta}")
        os.startfile(os.path.dirname(ruta))

    def exportar_excel():
        """Exporta productos en formato Excel general."""
        query = "SELECT codigo, nombre, precio_venta, precio_oferta, stock, categoria, laboratorio FROM productos WHERE stock > ?"
        params = [int(stock_min_var.get() or 0)]
        if cat_ecom_var.get() != "TODAS":
            query += " AND categoria=?"
            params.append(cat_ecom_var.get())
        if solo_oferta_var.get():
            query += " AND precio_oferta > 0"

        c.execute(query, params)
        productos = c.fetchall()

        if not productos:
            messagebox.showwarning("Sin productos", "No hay productos para exportar")
            return

        ruta = filedialog.asksaveasfilename(defaultextension=".csv",
                                           filetypes=[("CSV/Excel", "*.csv")],
                                           initialfile=f"catalogo_productos_{datetime.now().strftime('%Y%m%d')}.csv")
        if not ruta:
            return

        import csv
        with open(ruta, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['CÓDIGO', 'NOMBRE', 'PRECIO', 'PRECIO OFERTA', 'STOCK', 'CATEGORÍA', 'MARCA'])
            for p in productos:
                writer.writerow(p)

        messagebox.showinfo("Exportado", f"✅ {len(productos)} productos exportados\n\n{ruta}")
        os.startfile(os.path.dirname(ruta))

    tk.Button(btns_export, text="🟠 AMAZON", command=exportar_amazon,
             bg="#FF9900", fg="white", font=("Segoe UI", 10, "bold"),
             relief=tk.FLAT, padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)

    tk.Button(btns_export, text="🟡 MERCADO LIBRE", command=exportar_mercadolibre,
             bg="#FFE600", fg="#333", font=("Segoe UI", 10, "bold"),
             relief=tk.FLAT, padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)

    tk.Button(btns_export, text="📊 EXCEL", command=exportar_excel,
             bg="#217346", fg="white", font=("Segoe UI", 10, "bold"),
             relief=tk.FLAT, padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)

    # Instrucciones
    instruc_frame = tk.Frame(export_frame, bg="#E3F2FD", relief=tk.RIDGE, bd=1)
    instruc_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(instruc_frame, text="📋 INSTRUCCIONES:", font=("Segoe UI", 9, "bold"),
            bg="#E3F2FD", fg="#1565C0").pack(anchor="w", padx=10, pady=(5,2))
    tk.Label(instruc_frame, text="1. Amazon: Sube el CSV en Seller Central > Inventario > Agregar productos",
            font=("Segoe UI", 8), bg="#E3F2FD", fg="#333").pack(anchor="w", padx=10)
    tk.Label(instruc_frame, text="2. Mercado Libre: Sube en Vendedor > Publicaciones > Carga masiva",
            font=("Segoe UI", 8), bg="#E3F2FD", fg="#333").pack(anchor="w", padx=10)
    tk.Label(instruc_frame, text="3. Revisa precios y stock antes de publicar",
            font=("Segoe UI", 8), bg="#E3F2FD", fg="#333").pack(anchor="w", padx=10, pady=(0,5))

    # --- PANEL DERECHO: Pedidos Online ---
    pedidos_frame = tk.LabelFrame(ecom_main, text="📦 PEDIDOS ONLINE", font=("Segoe UI", 11, "bold"),
                                  bg="white", fg="#1565C0")
    pedidos_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10,0), pady=5)

    # Crear tabla de pedidos si no existe
    c.execute("""CREATE TABLE IF NOT EXISTS pedidos_online (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plataforma TEXT, pedido_externo TEXT, fecha TEXT, hora TEXT,
        cliente TEXT, telefono TEXT, direccion TEXT,
        productos TEXT, total REAL, estado TEXT DEFAULT 'PENDIENTE',
        guia_envio TEXT, notas TEXT, fecha_envio TEXT, usuario TEXT)""")
    conn.commit()

    # Barra de herramientas
    toolbar_ped = tk.Frame(pedidos_frame, bg="white")
    toolbar_ped.pack(fill=tk.X, padx=10, pady=5)

    def agregar_pedido_manual():
        """Ventana para agregar pedido manual de Amazon/ML."""
        win = tk.Toplevel(main)
        win.title("📦 Agregar Pedido Online")
        win.geometry("500x550")
        win.configure(bg="white")
        win.transient(main)
        win.grab_set()

        tk.Label(win, text="📦 NUEVO PEDIDO ONLINE", font=("Segoe UI", 14, "bold"),
                bg="white", fg="#1565C0").pack(pady=15)

        form = tk.Frame(win, bg="white")
        form.pack(fill=tk.X, padx=20, pady=10)

        campos_ped = {}
        labels = [("plataforma", "Plataforma:", 0), ("pedido_ext", "# Pedido:", 1),
                 ("cliente", "Cliente:", 2), ("telefono", "Teléfono:", 3),
                 ("direccion", "Dirección:", 4), ("productos", "Productos:", 5),
                 ("total", "Total $:", 6), ("notas", "Notas:", 7)]

        for key, label, row in labels:
            tk.Label(form, text=label, font=("Segoe UI", 9, "bold"), bg="white").grid(
                row=row, column=0, sticky="e", padx=5, pady=5)
            if key == "plataforma":
                var = tk.StringVar(value="MERCADO LIBRE")
                combo = ttk.Combobox(form, textvariable=var, width=30, state="readonly")
                combo['values'] = ["AMAZON", "MERCADO LIBRE", "WHATSAPP", "FACEBOOK", "OTRO"]
                combo.grid(row=row, column=1, padx=5, pady=5, sticky="w")
            elif key == "productos" or key == "direccion":
                var = tk.StringVar()
                tk.Entry(form, textvariable=var, width=40, font=("Segoe UI", 9)).grid(
                    row=row, column=1, padx=5, pady=5, sticky="w")
            else:
                var = tk.StringVar()
                tk.Entry(form, textvariable=var, width=30, font=("Segoe UI", 9)).grid(
                    row=row, column=1, padx=5, pady=5, sticky="w")
            campos_ped[key] = var

        def guardar_pedido():
            if not campos_ped["cliente"].get() or not campos_ped["total"].get():
                messagebox.showwarning("Datos incompletos", "Ingresa cliente y total")
                return
            c.execute("""INSERT INTO pedidos_online (plataforma, pedido_externo, fecha, hora,
                        cliente, telefono, direccion, productos, total, usuario)
                        VALUES (?,?,?,?,?,?,?,?,?,?)""",
                     (campos_ped["plataforma"].get(), campos_ped["pedido_ext"].get(),
                      datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M'),
                      campos_ped["cliente"].get(), campos_ped["telefono"].get(),
                      campos_ped["direccion"].get(), campos_ped["productos"].get(),
                      float(campos_ped["total"].get() or 0), usuario_actual))
            conn.commit()
            messagebox.showinfo("Guardado", "Pedido registrado correctamente")
            win.destroy()
            cargar_pedidos_online()

        tk.Button(win, text="💾 GUARDAR PEDIDO", command=guardar_pedido,
                 bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"),
                 relief=tk.FLAT, padx=20, pady=10, cursor="hand2").pack(pady=20)

    tk.Button(toolbar_ped, text="➕ AGREGAR PEDIDO", command=agregar_pedido_manual,
             bg="#4CAF50", fg="white", font=("Segoe UI", 9, "bold"),
             relief=tk.FLAT, padx=10, pady=5, cursor="hand2").pack(side=tk.LEFT)

    estado_filtro = tk.StringVar(value="TODOS")
    ttk.Combobox(toolbar_ped, textvariable=estado_filtro, width=12, state="readonly",
                values=["TODOS", "PENDIENTE", "ENVIADO", "ENTREGADO", "CANCELADO"]).pack(side=tk.LEFT, padx=10)

    # Lista de pedidos
    cols_ped = ("ID", "PLATAFORMA", "PEDIDO", "FECHA", "CLIENTE", "TOTAL", "ESTADO")
    tree_pedidos = ttk.Treeview(pedidos_frame, columns=cols_ped, show="headings", height=10)
    for col in cols_ped:
        tree_pedidos.heading(col, text=col)
    tree_pedidos.column("ID", width=40)
    tree_pedidos.column("PLATAFORMA", width=90)
    tree_pedidos.column("PEDIDO", width=80)
    tree_pedidos.column("FECHA", width=80)
    tree_pedidos.column("CLIENTE", width=100)
    tree_pedidos.column("TOTAL", width=70)
    tree_pedidos.column("ESTADO", width=80)
    tree_pedidos.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def cargar_pedidos_online():
        for item in tree_pedidos.get_children():
            tree_pedidos.delete(item)
        query = "SELECT id, plataforma, pedido_externo, fecha, cliente, total, estado FROM pedidos_online"
        if estado_filtro.get() != "TODOS":
            query += f" WHERE estado='{estado_filtro.get()}'"
        query += " ORDER BY id DESC LIMIT 50"
        c.execute(query)
        for row in c.fetchall():
            tag = ""
            if row[6] == "PENDIENTE":
                tag = "pendiente"
            elif row[6] == "ENVIADO":
                tag = "enviado"
            tree_pedidos.insert("", "end", values=(row[0], row[1], row[2] or "-", row[3],
                                                   row[4][:20], f"${row[5]:,.2f}", row[6]), tags=(tag,))

    tree_pedidos.tag_configure("pendiente", background="#FFF3E0")
    tree_pedidos.tag_configure("enviado", background="#E8F5E9")

    estado_filtro.trace_add("write", lambda *args: cargar_pedidos_online())

    # Botones de acción
    acc_pedidos = tk.Frame(pedidos_frame, bg="white")
    acc_pedidos.pack(fill=tk.X, padx=10, pady=5)

    def marcar_enviado():
        sel = tree_pedidos.selection()
        if not sel:
            return
        pid = tree_pedidos.item(sel[0])["values"][0]
        guia = simpledialog.askstring("Guía de envío", "Ingresa número de guía:")
        if guia:
            c.execute("UPDATE pedidos_online SET estado='ENVIADO', guia_envio=?, fecha_envio=? WHERE id=?",
                     (guia, datetime.now().strftime('%Y-%m-%d'), pid))
            conn.commit()
            cargar_pedidos_online()

    def marcar_entregado_ped():
        sel = tree_pedidos.selection()
        if not sel:
            return
        pid = tree_pedidos.item(sel[0])["values"][0]
        c.execute("UPDATE pedidos_online SET estado='ENTREGADO' WHERE id=?", (pid,))
        conn.commit()
        cargar_pedidos_online()

    tk.Button(acc_pedidos, text="📤 MARCAR ENVIADO", command=marcar_enviado,
             bg="#FF9800", fg="white", font=("Segoe UI", 9),
             relief=tk.FLAT, padx=8, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=3)

    tk.Button(acc_pedidos, text="✅ ENTREGADO", command=marcar_entregado_ped,
             bg="#4CAF50", fg="white", font=("Segoe UI", 9),
             relief=tk.FLAT, padx=8, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=3)

    tk.Button(acc_pedidos, text="🔄 REFRESCAR", command=cargar_pedidos_online,
             bg="#1565C0", fg="white", font=("Segoe UI", 9),
             relief=tk.FLAT, padx=8, pady=4, cursor="hand2").pack(side=tk.RIGHT, padx=3)

    cargar_pedidos_online()

# ===== MODULO CARGO-GO (PAQUETERIA) =====

def asignar_repartidor_optimo(cp_destino, hora_pedido, peso_kg):
    """Algoritmo inteligente para asignar mejor repartidor."""
    cur = conn.cursor()
    cur.execute("""SELECT id, codigo, nombre, tarifa_base
                   FROM zonas_cdmx
                   WHERE ? BETWEEN cp_inicio AND cp_fin AND activa=1""", (cp_destino,))
    zona = cur.fetchone()
    if not zona:
        return {'error': True, 'mensaje': f'CP {cp_destino} fuera de cobertura'}
    zona_id, zona_codigo, zona_nombre, tarifa_base = zona

    cur.execute("""SELECT id, codigo, nombre, apellidos,
                          capacidad_diaria, entregas_hoy,
                          calificacion_promedio, ultimo_cp
                   FROM repartidores_cdmx
                   WHERE activo=1 AND disponible=1 AND zona_principal_id=?""", (zona_id,))
    repartidores = cur.fetchall()
    if not repartidores:
        # Buscar en todas las zonas como fallback
        cur.execute("""SELECT id, codigo, nombre, apellidos,
                              capacidad_diaria, entregas_hoy,
                              calificacion_promedio, ultimo_cp
                       FROM repartidores_cdmx
                       WHERE activo=1 AND disponible=1""")
        repartidores = cur.fetchall()
    if not repartidores:
        return {'error': True, 'mensaje': f'No hay repartidores disponibles para {zona_nombre}'}

    mejores = []
    for rep in repartidores:
        rep_id, rep_codigo, nombre, apellidos, capacidad, entregas_hoy, calificacion, ultimo_cp = rep
        score = 40  # zona match base
        if entregas_hoy < capacidad:
            score += (1 - entregas_hoy / capacidad) * 25
        score += (calificacion / 5.0) * 15
        if ultimo_cp and abs(ultimo_cp - cp_destino) < 1000:
            score += 10
        if entregas_hoy == 0:
            score += 10
        elif entregas_hoy < capacidad * 0.5:
            score += 7
        mejores.append({'id': rep_id, 'codigo': rep_codigo,
                        'nombre': f"{nombre} {apellidos}", 'score': score,
                        'entregas_hoy': entregas_hoy})

    mejores.sort(key=lambda x: x['score'], reverse=True)
    mejor = mejores[0]
    cur.execute("""SELECT COUNT(*) FROM envios_cargo
                   WHERE repartidor_id=? AND fecha_registro=?
                   AND estado IN ('ASIGNADO','EN_RUTA','RECIBIDO')""",
                (mejor['id'], datetime.now().strftime('%Y-%m-%d')))
    orden = cur.fetchone()[0] + 1
    tarifa = tarifa_base
    if peso_kg > 1:
        tarifa += (peso_kg - 1) * 20
    return {'error': False, 'repartidor_id': mejor['id'],
            'repartidor_nombre': mejor['nombre'],
            'zona_id': zona_id, 'zona_nombre': zona_nombre,
            'orden_entrega': orden, 'tarifa': tarifa,
            'tiempo_estimado': 45 + (orden - 1) * 15}


def generar_etiqueta_cargo(folio):
    """Genera etiqueta profesional para envio Cargo-GO."""
    try:
        cur = conn.cursor()
        cur.execute("""SELECT e.folio, e.fecha_registro, e.origen_nombre, e.origen_telefono,
                              e.destino_nombre, e.destino_telefono, e.destino_direccion,
                              e.destino_cp, e.contenido, e.peso_kg, e.fragil, e.total,
                              z.nombre as zona_nombre,
                              r.nombre as rep_nombre, r.apellidos as rep_apellidos
                       FROM envios_cargo e
                       LEFT JOIN zonas_cdmx z ON e.zona_cdmx_id = z.id
                       LEFT JOIN repartidores_cdmx r ON e.repartidor_id = r.id
                       WHERE e.folio=?""", (folio,))
        row = cur.fetchone()
        if not row:
            messagebox.showerror("Error", f"Folio {folio} no encontrado")
            return
        cols = [d[0] for d in cur.description]
        envio = dict(zip(cols, row))

        ancho, alto = 1181, 1772
        img = Image.new('RGB', (ancho, alto), color='white')
        draw = ImageDraw.Draw(img)
        try:
            font_titulo = ImageFont.truetype("arial.ttf", 48)
            font_grande = ImageFont.truetype("arialbd.ttf", 36)
            font_normal = ImageFont.truetype("arial.ttf", 28)
            font_chica = ImageFont.truetype("arial.ttf", 22)
        except:
            font_titulo = font_grande = font_normal = font_chica = ImageFont.load_default()

        y = 40
        # Header
        try:
            logo = Image.open("logo_cargo_go_horizontal.png")
            logo = logo.resize((400, 100))
            img.paste(logo, ((ancho - 400) // 2, y))
            y += 120
        except:
            draw.text((ancho // 2, y + 30), "CARGO-GO", font=font_titulo, fill='#001A4D', anchor="mt")
            y += 80

        draw.line([(50, y), (ancho - 50, y)], fill='#001A4D', width=3)
        y += 30
        draw.text((ancho // 2, y), f"FOLIO: {folio}", font=font_titulo, fill="black", anchor="mt")
        y += 70

        # Barcode
        try:
            import barcode as bc
            from barcode.writer import ImageWriter
            codigo = bc.get('code128', folio, writer=ImageWriter())
            os.makedirs("etiquetas_cargo", exist_ok=True)
            barcode_path = os.path.join("etiquetas_cargo", f"bc_{folio}")
            codigo.save(barcode_path)
            barcode_img = Image.open(f"{barcode_path}.png")
            barcode_img = barcode_img.resize((900, 200))
            img.paste(barcode_img, ((ancho - 900) // 2, y))
            y += 220
        except:
            draw.rectangle([200, y, ancho - 200, y + 100], outline="black", width=2)
            draw.text((ancho // 2, y + 50), folio, font=font_grande, fill="black", anchor="mm")
            y += 120

        fecha_str = envio.get('fecha_registro', '')
        draw.text((ancho // 2, y), f"{fecha_str} - EXPRESS 6 HORAS", font=font_chica, fill="#666666", anchor="mt")
        y += 50
        draw.line([(50, y), (ancho - 50, y)], fill='#FFD700', width=2)
        y += 30

        # Origen
        draw.text((60, y), "ORIGEN:", font=font_grande, fill='#001A4D')
        y += 50
        draw.text((80, y), str(envio.get('origen_nombre', '')), font=font_normal, fill="black")
        y += 45
        draw.text((80, y), f"Tel: {envio.get('origen_telefono', '')}", font=font_chica, fill="#666666")
        y += 50
        draw.line([(50, y), (ancho - 50, y)], fill="#DDDDDD", width=2)
        y += 30

        # Destino
        draw.text((60, y), "DESTINO:", font=font_grande, fill='#001A4D')
        y += 50
        draw.text((80, y), str(envio.get('destino_nombre', '')), font=font_normal, fill="black")
        y += 45
        draw.text((80, y), str(envio.get('destino_direccion', '')), font=font_chica, fill="#666666")
        y += 40
        draw.text((80, y), f"CP: {envio.get('destino_cp', '')} - {envio.get('zona_nombre', '')}",
                  font=font_chica, fill="#666666")
        y += 40
        draw.text((80, y), f"Tel: {envio.get('destino_telefono', '')}", font=font_chica, fill="#666666")
        y += 50
        draw.line([(50, y), (ancho - 50, y)], fill="#DDDDDD", width=2)
        y += 30

        # Paquete
        draw.text((60, y), "PAQUETE:", font=font_grande, fill='#001A4D')
        y += 50
        draw.text((80, y), f"Contenido: {envio.get('contenido', '')}", font=font_chica, fill="black")
        y += 35
        draw.text((80, y), f"Peso: {envio.get('peso_kg', '')} kg", font=font_chica, fill="black")
        y += 50
        if envio.get('fragil'):
            draw.rectangle([80, y, 300, y + 45], fill="#F44336")
            draw.text((190, y + 22), "FRAGIL", font=font_normal, fill="white", anchor="mm")
            y += 55
        draw.line([(50, y), (ancho - 50, y)], fill="#DDDDDD", width=2)
        y += 30

        # Repartidor
        draw.text((60, y), "REPARTIDOR:", font=font_grande, fill='#001A4D')
        y += 50
        draw.text((80, y), f"{envio.get('rep_nombre', '')} {envio.get('rep_apellidos', '')}",
                  font=font_normal, fill="black")
        y += 60

        # QR
        try:
            import qrcode
            qr = qrcode.QRCode(box_size=8, border=2)
            qr.add_data(f"CARGO-GO:{folio}")
            qr.make()
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((200, 200))
            img.paste(qr_img, (80, y))
        except:
            pass
        draw.text((310, y + 30), "Rastreo: CARGO-GO", font=font_chica, fill="black")
        draw.text((310, y + 65), f"Folio: {folio}", font=font_chica, fill="#2196F3")
        draw.text((310, y + 100), "WhatsApp: 775-320-0224", font=font_chica, fill="#4CAF50")
        y += 220

        # Total
        draw.text((ancho // 2, y), f"TOTAL: ${envio.get('total', 0):.2f}",
                  font=font_titulo, fill="#4CAF50", anchor="mt")

        os.makedirs("etiquetas_cargo", exist_ok=True)
        output_path = os.path.join("etiquetas_cargo", f"{folio}.png")
        img.save(output_path, "PNG")
        try:
            os.startfile(output_path)
        except:
            pass
        messagebox.showinfo("Etiqueta", f"Etiqueta guardada en:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error etiqueta", str(e))


def ver_cargo_go():
    """Modulo completo Cargo-GO - Punto de Venta Paqueteria."""
    limpiar()
    registrar_auditoria("VER", "cargo_go", "Acceso modulo Cargo-GO")

    # Header
    hdr = tk.Frame(main, bg="#001A4D", height=50)
    hdr.pack(fill=tk.X)
    hdr.pack_propagate(False)
    tk.Label(hdr, text="\u2708 CARGO-GO - Paqueteria Express",
             font=("Segoe UI", 14, "bold"), bg="#001A4D", fg="white").pack(side=tk.LEFT, padx=15, pady=12)
    tk.Label(hdr, text=f"Usuario: {usuario_actual}",
             font=("Segoe UI", 10), bg="#001A4D", fg="#FFD700").pack(side=tk.RIGHT, padx=15)

    notebook = ttk.Notebook(main)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ---- TAB 1: NUEVO ENVIO ----
    tab_nuevo = tk.Frame(notebook, bg="white")
    notebook.add(tab_nuevo, text="  Nuevo Envio  ")

    canvas_env = tk.Canvas(tab_nuevo, bg="white", highlightthickness=0)
    sb_env = ttk.Scrollbar(tab_nuevo, orient="vertical", command=canvas_env.yview)
    frm_scroll = tk.Frame(canvas_env, bg="white")
    frm_scroll.bind("<Configure>", lambda e: canvas_env.configure(scrollregion=canvas_env.bbox("all")))
    canvas_env.create_window((0, 0), window=frm_scroll, anchor="nw")
    canvas_env.configure(yscrollcommand=sb_env.set)
    canvas_env.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb_env.pack(side=tk.RIGHT, fill=tk.Y)
    canvas_env.bind_all("<MouseWheel>", lambda e: canvas_env.yview_scroll(-1 * (e.delta // 120), "units"))

    # ORIGEN
    tk.Label(frm_scroll, text="ORIGEN", font=("Segoe UI", 16, "bold"),
             bg="white", fg="#001A4D").pack(anchor=tk.W, padx=20, pady=(15, 5))
    f_orig = tk.LabelFrame(frm_scroll, text="Remitente", font=("Segoe UI", 10), bg="white")
    f_orig.pack(fill=tk.X, padx=20, pady=5)
    g_orig = tk.Frame(f_orig, bg="white")
    g_orig.pack(fill=tk.X, padx=15, pady=10)

    tk.Label(g_orig, text="Nombre:", font=FUENTE_NORMAL, bg="white").grid(row=0, column=0, sticky=tk.W, pady=3)
    orig_nombre = tk.StringVar(value="Chule")
    tk.Entry(g_orig, textvariable=orig_nombre, font=FUENTE_NORMAL, width=35).grid(row=0, column=1, pady=3, padx=8)
    tk.Label(g_orig, text="Telefono:", font=FUENTE_NORMAL, bg="white").grid(row=1, column=0, sticky=tk.W, pady=3)
    orig_tel = tk.StringVar(value="775-320-0224")
    tk.Entry(g_orig, textvariable=orig_tel, font=FUENTE_NORMAL, width=35).grid(row=1, column=1, pady=3, padx=8)

    # DESTINO
    tk.Label(frm_scroll, text="DESTINO", font=("Segoe UI", 16, "bold"),
             bg="white", fg="#001A4D").pack(anchor=tk.W, padx=20, pady=(15, 5))
    f_dest = tk.LabelFrame(frm_scroll, text="Destinatario", font=("Segoe UI", 10), bg="white")
    f_dest.pack(fill=tk.X, padx=20, pady=5)
    g_dest = tk.Frame(f_dest, bg="white")
    g_dest.pack(fill=tk.X, padx=15, pady=10)

    tk.Label(g_dest, text="Nombre:", font=FUENTE_NORMAL, bg="white").grid(row=0, column=0, sticky=tk.W, pady=3)
    dest_nombre = tk.StringVar()
    tk.Entry(g_dest, textvariable=dest_nombre, font=FUENTE_NORMAL, width=35).grid(row=0, column=1, pady=3, padx=8)

    tk.Label(g_dest, text="Telefono:", font=FUENTE_NORMAL, bg="white").grid(row=1, column=0, sticky=tk.W, pady=3)
    dest_tel = tk.StringVar()
    tk.Entry(g_dest, textvariable=dest_tel, font=FUENTE_NORMAL, width=35).grid(row=1, column=1, pady=3, padx=8)

    tk.Label(g_dest, text="CP (CDMX):", font=("Segoe UI", 10, "bold"),
             bg="white", fg="#FF9800").grid(row=2, column=0, sticky=tk.W, pady=3)
    dest_cp = tk.StringVar()
    tk.Entry(g_dest, textvariable=dest_cp, font=FUENTE_NORMAL, width=12).grid(row=2, column=1, sticky=tk.W, pady=3, padx=8)

    zona_lbl = tk.Label(g_dest, text="", font=("Segoe UI", 9, "bold"), bg="white", fg="#4CAF50")
    zona_lbl.grid(row=2, column=2, padx=5)

    tk.Label(g_dest, text="Direccion:", font=FUENTE_NORMAL, bg="white").grid(row=3, column=0, sticky=tk.W, pady=3)
    dest_dir = tk.StringVar()
    tk.Entry(g_dest, textvariable=dest_dir, font=FUENTE_NORMAL, width=35).grid(row=3, column=1, pady=3, padx=8)

    tk.Label(g_dest, text="Referencias:", font=FUENTE_NORMAL, bg="white").grid(row=4, column=0, sticky=tk.W, pady=3)
    dest_ref = tk.StringVar()
    tk.Entry(g_dest, textvariable=dest_ref, font=FUENTE_NORMAL, width=35).grid(row=4, column=1, pady=3, padx=8)

    # PAQUETE
    tk.Label(frm_scroll, text="PAQUETE", font=("Segoe UI", 16, "bold"),
             bg="white", fg="#001A4D").pack(anchor=tk.W, padx=20, pady=(15, 5))
    f_paq = tk.LabelFrame(frm_scroll, text="Detalles", font=("Segoe UI", 10), bg="white")
    f_paq.pack(fill=tk.X, padx=20, pady=5)
    g_paq = tk.Frame(f_paq, bg="white")
    g_paq.pack(fill=tk.X, padx=15, pady=10)

    tipo_paq = tk.StringVar(value="PAQUETE_CHICO")
    tk.Radiobutton(g_paq, text="Documento (< 0.5 kg) - $150", variable=tipo_paq, value="DOCUMENTO",
                   font=("Segoe UI", 9), bg="white").grid(row=0, column=0, columnspan=2, sticky=tk.W)
    tk.Radiobutton(g_paq, text="Paquete chico (0.5-1 kg) - $150", variable=tipo_paq, value="PAQUETE_CHICO",
                   font=("Segoe UI", 9), bg="white").grid(row=1, column=0, columnspan=2, sticky=tk.W)
    tk.Radiobutton(g_paq, text="Paquete mediano (1-5 kg) - $180", variable=tipo_paq, value="PAQUETE_MEDIANO",
                   font=("Segoe UI", 9), bg="white").grid(row=2, column=0, columnspan=2, sticky=tk.W)
    tk.Radiobutton(g_paq, text="Paquete grande (5-10 kg) - $250", variable=tipo_paq, value="PAQUETE_GRANDE",
                   font=("Segoe UI", 9), bg="white").grid(row=3, column=0, columnspan=2, sticky=tk.W)

    tk.Label(g_paq, text="Peso (kg):", font=FUENTE_NORMAL, bg="white").grid(row=4, column=0, sticky=tk.W, pady=8)
    peso_var = tk.StringVar(value="1.0")
    tk.Entry(g_paq, textvariable=peso_var, font=FUENTE_NORMAL, width=8).grid(row=4, column=1, sticky=tk.W, pady=8, padx=8)

    tk.Label(g_paq, text="Contenido:", font=FUENTE_NORMAL, bg="white").grid(row=5, column=0, sticky=tk.W, pady=3)
    contenido_var = tk.StringVar()
    tk.Entry(g_paq, textvariable=contenido_var, font=FUENTE_NORMAL, width=35).grid(row=5, column=1, pady=3, padx=8)

    fragil_var = tk.IntVar()
    tk.Checkbutton(g_paq, text="Fragil (manejo especial)", variable=fragil_var,
                   font=("Segoe UI", 9), bg="white").grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=3)

    # COTIZACION
    tk.Label(frm_scroll, text="COTIZACION", font=("Segoe UI", 16, "bold"),
             bg="white", fg="#001A4D").pack(anchor=tk.W, padx=20, pady=(15, 5))
    f_cot = tk.LabelFrame(frm_scroll, text="Costo del envio", font=("Segoe UI", 10), bg="#F5F5F5")
    f_cot.pack(fill=tk.X, padx=20, pady=5)
    g_cot = tk.Frame(f_cot, bg="#F5F5F5")
    g_cot.pack(fill=tk.X, padx=15, pady=10)

    tarifa_lbl = tk.Label(g_cot, text="Tarifa base: $0", font=FUENTE_NORMAL, bg="#F5F5F5")
    tarifa_lbl.grid(row=0, column=0, sticky=tk.W, pady=2)
    peso_lbl = tk.Label(g_cot, text="Cargo peso: $0", font=FUENTE_NORMAL, bg="#F5F5F5")
    peso_lbl.grid(row=1, column=0, sticky=tk.W, pady=2)
    sub_lbl = tk.Label(g_cot, text="Subtotal: $0", font=("Segoe UI", 11), bg="#F5F5F5")
    sub_lbl.grid(row=2, column=0, sticky=tk.W, pady=2)
    iva_lbl = tk.Label(g_cot, text="IVA (16%): $0", font=FUENTE_NORMAL, bg="#F5F5F5")
    iva_lbl.grid(row=3, column=0, sticky=tk.W, pady=2)
    total_lbl = tk.Label(g_cot, text="TOTAL: $0", font=("Segoe UI", 18, "bold"), bg="#F5F5F5", fg="#4CAF50")
    total_lbl.grid(row=4, column=0, sticky=tk.W, pady=8)
    rep_lbl = tk.Label(g_cot, text="Repartidor: --", font=("Segoe UI", 9), bg="#F5F5F5")
    rep_lbl.grid(row=5, column=0, sticky=tk.W, pady=2)

    _cargo_calc_data = {}

    def calcular_tarifa(*args):
        try:
            cp_str = dest_cp.get().strip()
            peso_str = peso_var.get().strip()
            if not cp_str or not peso_str:
                return
            cp = int(cp_str)
            peso = float(peso_str)
            resultado = asignar_repartidor_optimo(cp, "09:00:00", peso)
            if not resultado['error']:
                tarifa = resultado['tarifa']
                cargo_peso_extra = max(0, (peso - 1) * 20) if peso > 1 else 0
                subtotal = tarifa + cargo_peso_extra
                iva = subtotal * 0.16
                total = subtotal + iva
                tarifa_lbl.config(text=f"Tarifa base ({resultado['zona_nombre']}): ${tarifa:.0f}")
                peso_lbl.config(text=f"Cargo peso ({peso}kg): ${cargo_peso_extra:.0f}")
                sub_lbl.config(text=f"Subtotal: ${subtotal:.0f}")
                iva_lbl.config(text=f"IVA (16%): ${iva:.0f}")
                total_lbl.config(text=f"TOTAL: ${total:.0f}")
                rep_lbl.config(text=f"Repartidor: {resultado['repartidor_nombre']} - Orden #{resultado['orden_entrega']}")
                zona_lbl.config(text=f"OK {resultado['zona_nombre']}", fg="#4CAF50")
                _cargo_calc_data['resultado'] = resultado
            else:
                zona_lbl.config(text=resultado['mensaje'][:30], fg="#F44336")
        except:
            pass

    def detectar_zona(*args):
        cp_str = dest_cp.get().strip()
        if len(cp_str) >= 4:
            calcular_tarifa()

    dest_cp.trace_add('write', detectar_zona)
    peso_var.trace_add('write', calcular_tarifa)

    # BOTONES
    f_btns = tk.Frame(frm_scroll, bg="white")
    f_btns.pack(fill=tk.X, padx=20, pady=20)

    def generar_guia():
        if not dest_nombre.get().strip() or not dest_cp.get().strip():
            messagebox.showwarning("Datos incompletos", "Completa nombre y CP del destinatario")
            return
        try:
            cp = int(dest_cp.get().strip())
            peso = float(peso_var.get().strip()) if peso_var.get().strip() else 1.0
        except ValueError:
            messagebox.showerror("Error", "CP o peso invalido")
            return

        resultado = asignar_repartidor_optimo(cp, datetime.now().strftime('%H:%M:%S'), peso)
        if resultado['error']:
            messagebox.showerror("Error", resultado['mensaje'])
            return

        fecha = datetime.now().strftime('%Y%m%d')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM envios_cargo WHERE fecha_registro=?",
                    (datetime.now().strftime('%Y-%m-%d'),))
        num = cur.fetchone()[0] + 1
        folio = f"CGO-{fecha}-{num:05d}"

        tarifa = resultado['tarifa']
        cargo_peso_extra = max(0, (peso - 1) * 20) if peso > 1 else 0
        subtotal = tarifa + cargo_peso_extra
        iva = subtotal * 0.16
        total = subtotal + iva

        cur.execute("""INSERT INTO envios_cargo
                    (folio, origen_nombre, origen_telefono,
                     destino_nombre, destino_telefono, destino_direccion, destino_referencias, destino_cp,
                     zona_cdmx_id, tipo_paquete, contenido, peso_kg, fragil,
                     tarifa_base, cargo_peso, subtotal, iva, total,
                     repartidor_id, estado, orden_entrega,
                     fecha_registro, hora_registro, usuario_registro)
                    VALUES (?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?,?, ?,?,?)""",
                    (folio, orig_nombre.get(), orig_tel.get(),
                     dest_nombre.get(), dest_tel.get(), dest_dir.get(), dest_ref.get(), cp,
                     resultado['zona_id'], tipo_paq.get(), contenido_var.get(), peso, fragil_var.get(),
                     tarifa, cargo_peso_extra, subtotal, iva, total,
                     resultado['repartidor_id'], 'RECIBIDO', resultado['orden_entrega'],
                     datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S'), usuario_actual))

        envio_id = cur.lastrowid
        cur.execute("""INSERT INTO estados_envio
                    (envio_id, estado_nuevo, fecha, hora, notas, usuario)
                    VALUES (?,?,?,?,?,?)""",
                    (envio_id, 'RECIBIDO', datetime.now().strftime('%Y-%m-%d'),
                     datetime.now().strftime('%H:%M:%S'), 'Paquete recibido en sucursal', usuario_actual))
        cur.execute("UPDATE repartidores_cdmx SET entregas_hoy=entregas_hoy+1 WHERE id=?",
                    (resultado['repartidor_id'],))
        conn.commit()

        messagebox.showinfo("Guia Generada",
                            f"Folio: {folio}\n"
                            f"Total: ${total:.2f}\n"
                            f"Repartidor: {resultado['repartidor_nombre']}\n"
                            f"Zona: {resultado['zona_nombre']}")

        if messagebox.askyesno("Imprimir", "Generar etiqueta ahora?"):
            generar_etiqueta_cargo(folio)

        dest_nombre.set("")
        dest_tel.set("")
        dest_dir.set("")
        dest_ref.set("")
        dest_cp.set("")
        contenido_var.set("")
        peso_var.set("1.0")
        fragil_var.set(0)
        total_lbl.config(text="TOTAL: $0")
        rep_lbl.config(text="Repartidor: --")
        zona_lbl.config(text="")

    tk.Button(f_btns, text="GENERAR GUIA", command=generar_guia,
              font=("Segoe UI", 13, "bold"), bg="#4CAF50", fg="white",
              pady=12, padx=30, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=8)

    tk.Button(f_btns, text="COTIZAR", command=calcular_tarifa,
              font=("Segoe UI", 11, "bold"), bg="#2196F3", fg="white",
              pady=10, padx=20, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=8)

    # ---- TAB 2: RASTREAR ----
    tab_rastrear = tk.Frame(notebook, bg="white")
    notebook.add(tab_rastrear, text="  Rastrear  ")

    tk.Label(tab_rastrear, text="RASTREO DE ENVIOS", font=("Segoe UI", 14, "bold"),
             bg="white", fg="#001A4D").pack(pady=(20, 10))

    f_busq = tk.Frame(tab_rastrear, bg="white")
    f_busq.pack(pady=10)
    tk.Label(f_busq, text="Folio:", font=FUENTE_NORMAL, bg="white").pack(side=tk.LEFT, padx=5)
    rastreo_folio = tk.StringVar()
    tk.Entry(f_busq, textvariable=rastreo_folio, font=("Segoe UI", 12), width=25).pack(side=tk.LEFT, padx=5)

    rastreo_result = tk.Frame(tab_rastrear, bg="white")
    rastreo_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def buscar_rastreo():
        for w in rastreo_result.winfo_children():
            w.destroy()
        folio = rastreo_folio.get().strip()
        if not folio:
            messagebox.showwarning("Rastreo", "Ingresa un folio")
            return
        cur = conn.cursor()
        cur.execute("""SELECT e.folio, e.estado, e.destino_nombre, e.destino_cp, e.total,
                              e.fecha_registro, e.hora_registro,
                              z.nombre, r.nombre || ' ' || r.apellidos
                       FROM envios_cargo e
                       LEFT JOIN zonas_cdmx z ON e.zona_cdmx_id = z.id
                       LEFT JOIN repartidores_cdmx r ON e.repartidor_id = r.id
                       WHERE e.folio LIKE ?""", (f"%{folio}%",))
        rows = cur.fetchall()
        if not rows:
            tk.Label(rastreo_result, text="No se encontraron envios con ese folio",
                     font=FUENTE_NORMAL, bg="white", fg="#F44336").pack(pady=20)
            return

        for row in rows:
            f = tk.LabelFrame(rastreo_result, text=row[0], font=("Segoe UI", 11, "bold"), bg="white")
            f.pack(fill=tk.X, pady=5)
            estado_colores = {'RECIBIDO': '#FF9800', 'EN_TRANSITO': '#2196F3',
                              'EN_RUTA': '#9C27B0', 'ENTREGADO': '#4CAF50', 'CANCELADO': '#F44336'}
            color_est = estado_colores.get(row[1], '#666')
            info = tk.Frame(f, bg="white")
            info.pack(fill=tk.X, padx=10, pady=8)
            tk.Label(info, text=f"Estado: {row[1]}", font=("Segoe UI", 12, "bold"),
                     bg="white", fg=color_est).grid(row=0, column=0, sticky=tk.W, columnspan=2)
            for i, (label, val) in enumerate([("Destino:", row[2]), ("CP:", row[3]),
                                               ("Total:", f"${row[4]:.2f}" if row[4] else "$0"),
                                               ("Fecha:", f"{row[5]} {row[6]}"),
                                               ("Zona:", row[7]), ("Repartidor:", row[8])], 1):
                tk.Label(info, text=label, font=("Segoe UI", 9, "bold"), bg="white").grid(row=i, column=0, sticky=tk.W)
                tk.Label(info, text=str(val or ''), font=("Segoe UI", 9), bg="white").grid(row=i, column=1, sticky=tk.W, padx=10)

            # Historial de estados
            cur.execute("""SELECT estado_nuevo, fecha, hora, notas FROM estados_envio
                           WHERE envio_id=(SELECT id FROM envios_cargo WHERE folio=?)
                           ORDER BY id""", (row[0],))
            estados = cur.fetchall()
            if estados:
                tk.Label(info, text="Historial:", font=("Segoe UI", 9, "bold"),
                         bg="white").grid(row=len([("",""),("",""),("",""),("",""),("",""),("","")])+1, column=0, sticky=tk.W, pady=(5,0))
                for j, est in enumerate(estados):
                    tk.Label(info, text=f"  {est[1]} {est[2]} - {est[0]} {est[3] or ''}",
                             font=("Segoe UI", 8), bg="white", fg="#666").grid(
                        row=8+j, column=0, columnspan=2, sticky=tk.W)

            # Botones de cambio de estado
            btn_frame = tk.Frame(f, bg="white")
            btn_frame.pack(fill=tk.X, padx=10, pady=5)
            folio_actual = row[0]

            def cambiar_estado(fol, nuevo_estado):
                def _do():
                    cur2 = conn.cursor()
                    cur2.execute("SELECT estado FROM envios_cargo WHERE folio=?", (fol,))
                    anterior = cur2.fetchone()[0]
                    cur2.execute("UPDATE envios_cargo SET estado=? WHERE folio=?", (nuevo_estado, fol))
                    cur2.execute("""INSERT INTO estados_envio (envio_id, estado_anterior, estado_nuevo, fecha, hora, usuario)
                                    VALUES ((SELECT id FROM envios_cargo WHERE folio=?),?,?,?,?,?)""",
                                (fol, anterior, nuevo_estado,
                                 datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S'), usuario_actual))
                    if nuevo_estado == 'ENTREGADO':
                        cur2.execute("UPDATE envios_cargo SET fecha_entrega=?, hora_entrega=? WHERE folio=?",
                                     (datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S'), fol))
                    conn.commit()
                    messagebox.showinfo("Estado", f"{fol} -> {nuevo_estado}")
                    buscar_rastreo()
                return _do

            for est_txt, est_val, est_clr in [("En Transito", "EN_TRANSITO", "#2196F3"),
                                                ("En Ruta", "EN_RUTA", "#9C27B0"),
                                                ("Entregado", "ENTREGADO", "#4CAF50")]:
                tk.Button(btn_frame, text=est_txt, command=cambiar_estado(folio_actual, est_val),
                          font=("Segoe UI", 8, "bold"), bg=est_clr, fg="white",
                          relief=tk.FLAT, padx=8, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=3)

    tk.Button(f_busq, text="BUSCAR", command=buscar_rastreo,
              font=("Segoe UI", 10, "bold"), bg="#001A4D", fg="white",
              relief=tk.FLAT, padx=15, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=5)

    # ---- TAB 3: HISTORIAL ----
    tab_hist = tk.Frame(notebook, bg="white")
    notebook.add(tab_hist, text="  Historial  ")

    tk.Label(tab_hist, text="HISTORIAL DE ENVIOS", font=("Segoe UI", 14, "bold"),
             bg="white", fg="#001A4D").pack(pady=(15, 5))

    # Filtros
    f_filtros = tk.Frame(tab_hist, bg="white")
    f_filtros.pack(fill=tk.X, padx=15, pady=5)
    tk.Label(f_filtros, text="Estado:", font=FUENTE_NORMAL, bg="white").pack(side=tk.LEFT)
    filtro_estado = tk.StringVar(value="TODOS")
    combo_estado = ttk.Combobox(f_filtros, textvariable=filtro_estado, width=15,
                                values=["TODOS", "RECIBIDO", "EN_TRANSITO", "EN_RUTA", "ENTREGADO", "CANCELADO"])
    combo_estado.pack(side=tk.LEFT, padx=5)

    tk.Label(f_filtros, text="Fecha:", font=FUENTE_NORMAL, bg="white").pack(side=tk.LEFT, padx=(15, 0))
    filtro_fecha = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
    tk.Entry(f_filtros, textvariable=filtro_fecha, font=FUENTE_NORMAL, width=12).pack(side=tk.LEFT, padx=5)

    cols_hist = ("FOLIO", "FECHA", "DESTINO", "CP", "ZONA", "ESTADO", "TOTAL", "REPARTIDOR")
    tree_hist = ttk.Treeview(tab_hist, columns=cols_hist, show="headings", height=18)
    for col_name, w in [("FOLIO", 150), ("FECHA", 90), ("DESTINO", 130), ("CP", 60),
                         ("ZONA", 100), ("ESTADO", 90), ("TOTAL", 80), ("REPARTIDOR", 120)]:
        tree_hist.heading(col_name, text=col_name)
        tree_hist.column(col_name, width=w)
    tree_hist.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

    sb_hist = ttk.Scrollbar(tab_hist, orient="vertical", command=tree_hist.yview)
    tree_hist.configure(yscrollcommand=sb_hist.set)

    def cargar_historial():
        for item in tree_hist.get_children():
            tree_hist.delete(item)
        cur = conn.cursor()
        query = """SELECT e.folio, e.fecha_registro, e.destino_nombre, e.destino_cp,
                          z.nombre, e.estado, e.total,
                          r.nombre || ' ' || r.apellidos
                   FROM envios_cargo e
                   LEFT JOIN zonas_cdmx z ON e.zona_cdmx_id = z.id
                   LEFT JOIN repartidores_cdmx r ON e.repartidor_id = r.id
                   WHERE 1=1"""
        params = []
        if filtro_estado.get() != "TODOS":
            query += " AND e.estado=?"
            params.append(filtro_estado.get())
        if filtro_fecha.get().strip():
            query += " AND e.fecha_registro=?"
            params.append(filtro_fecha.get().strip())
        query += " ORDER BY e.id DESC LIMIT 100"
        cur.execute(query, params)
        for row in cur.fetchall():
            total_fmt = f"${row[6]:.2f}" if row[6] else "$0"
            tree_hist.insert("", "end", values=(row[0], row[1], row[2], row[3],
                                                 row[4] or '', row[5], total_fmt, row[7] or ''))

    tk.Button(f_filtros, text="BUSCAR", command=cargar_historial,
              font=("Segoe UI", 9, "bold"), bg="#001A4D", fg="white",
              relief=tk.FLAT, padx=12, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=10)

    def reimprimir_etiqueta():
        sel = tree_hist.selection()
        if not sel:
            messagebox.showwarning("Seleccion", "Selecciona un envio")
            return
        folio = tree_hist.item(sel[0])['values'][0]
        generar_etiqueta_cargo(str(folio))

    tk.Button(f_filtros, text="ETIQUETA", command=reimprimir_etiqueta,
              font=("Segoe UI", 9, "bold"), bg="#FF9800", fg="white",
              relief=tk.FLAT, padx=12, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=5)

    cargar_historial()

    # ---- TAB 4: REPARTIDORES ----
    tab_reps = tk.Frame(notebook, bg="white")
    notebook.add(tab_reps, text="  Repartidores  ")

    tk.Label(tab_reps, text="REPARTIDORES CDMX", font=("Segoe UI", 14, "bold"),
             bg="white", fg="#001A4D").pack(pady=(15, 10))

    cols_reps = ("CODIGO", "NOMBRE", "TELEFONO", "ZONA", "CAPACIDAD", "HOY", "CALIF", "ESTADO")
    tree_reps = ttk.Treeview(tab_reps, columns=cols_reps, show="headings", height=10)
    for cn, w in [("CODIGO", 100), ("NOMBRE", 140), ("TELEFONO", 110), ("ZONA", 120),
                   ("CAPACIDAD", 80), ("HOY", 60), ("CALIF", 60), ("ESTADO", 80)]:
        tree_reps.heading(cn, text=cn)
        tree_reps.column(cn, width=w)
    tree_reps.pack(fill=tk.X, padx=15, pady=5)

    def cargar_repartidores():
        for item in tree_reps.get_children():
            tree_reps.delete(item)
        cur = conn.cursor()
        cur.execute("""SELECT r.codigo, r.nombre || ' ' || r.apellidos, r.telefono,
                              z.nombre, r.capacidad_diaria, r.entregas_hoy,
                              r.calificacion_promedio, r.activo
                       FROM repartidores_cdmx r
                       LEFT JOIN zonas_cdmx z ON r.zona_principal_id = z.id""")
        for row in cur.fetchall():
            estado = "Activo" if row[7] else "Inactivo"
            tree_reps.insert("", "end", values=(row[0], row[1], row[2], row[3] or '',
                                                 row[4], row[5], f"{row[6]:.1f}", estado))
    cargar_repartidores()

    # Formulario agregar repartidor
    f_new_rep = tk.LabelFrame(tab_reps, text="Agregar/Editar Repartidor", font=("Segoe UI", 10), bg="white")
    f_new_rep.pack(fill=tk.X, padx=15, pady=10)
    g_rep = tk.Frame(f_new_rep, bg="white")
    g_rep.pack(fill=tk.X, padx=10, pady=8)

    tk.Label(g_rep, text="Nombre:", font=FUENTE_NORMAL, bg="white").grid(row=0, column=0, sticky=tk.W)
    rep_nom = tk.StringVar()
    tk.Entry(g_rep, textvariable=rep_nom, font=FUENTE_NORMAL, width=20).grid(row=0, column=1, padx=5)
    tk.Label(g_rep, text="Apellidos:", font=FUENTE_NORMAL, bg="white").grid(row=0, column=2, sticky=tk.W, padx=(10,0))
    rep_ape = tk.StringVar()
    tk.Entry(g_rep, textvariable=rep_ape, font=FUENTE_NORMAL, width=20).grid(row=0, column=3, padx=5)
    tk.Label(g_rep, text="Telefono:", font=FUENTE_NORMAL, bg="white").grid(row=1, column=0, sticky=tk.W, pady=5)
    rep_tel_var = tk.StringVar()
    tk.Entry(g_rep, textvariable=rep_tel_var, font=FUENTE_NORMAL, width=20).grid(row=1, column=1, padx=5)
    tk.Label(g_rep, text="Zona:", font=FUENTE_NORMAL, bg="white").grid(row=1, column=2, sticky=tk.W, padx=(10,0))
    rep_zona = tk.StringVar()
    cur_z = conn.cursor()
    cur_z.execute("SELECT id, nombre FROM zonas_cdmx WHERE activa=1")
    zonas_list = cur_z.fetchall()
    zonas_nombres = [f"{z[0]}-{z[1]}" for z in zonas_list]
    combo_zona = ttk.Combobox(g_rep, textvariable=rep_zona, values=zonas_nombres, width=20)
    combo_zona.grid(row=1, column=3, padx=5)

    def agregar_repartidor():
        if not rep_nom.get().strip():
            messagebox.showwarning("Datos", "Ingresa nombre del repartidor")
            return
        zona_sel = rep_zona.get()
        zona_id = int(zona_sel.split('-')[0]) if zona_sel and '-' in zona_sel else 1
        cur2 = conn.cursor()
        cur2.execute("SELECT COUNT(*) FROM repartidores_cdmx")
        num = cur2.fetchone()[0] + 1
        codigo = f"REP-CDMX-{num:03d}"
        cur2.execute("""INSERT INTO repartidores_cdmx (codigo, nombre, apellidos, telefono, zona_principal_id)
                        VALUES (?,?,?,?,?)""",
                     (codigo, rep_nom.get().strip(), rep_ape.get().strip(),
                      rep_tel_var.get().strip(), zona_id))
        conn.commit()
        messagebox.showinfo("OK", f"Repartidor {codigo} agregado")
        rep_nom.set("")
        rep_ape.set("")
        rep_tel_var.set("")
        cargar_repartidores()

    tk.Button(g_rep, text="AGREGAR", command=agregar_repartidor,
              font=("Segoe UI", 9, "bold"), bg="#4CAF50", fg="white",
              relief=tk.FLAT, padx=12, pady=4, cursor="hand2").grid(row=2, column=0, columnspan=2, pady=8)

    def reset_entregas_hoy():
        cur2 = conn.cursor()
        cur2.execute("UPDATE repartidores_cdmx SET entregas_hoy=0")
        conn.commit()
        messagebox.showinfo("OK", "Contadores reiniciados")
        cargar_repartidores()

    tk.Button(g_rep, text="REINICIAR CONTADORES HOY", command=reset_entregas_hoy,
              font=("Segoe UI", 9, "bold"), bg="#FF9800", fg="white",
              relief=tk.FLAT, padx=12, pady=4, cursor="hand2").grid(row=2, column=2, columnspan=2, pady=8)

    # ---- TAB 5: ESTADISTICAS ----
    tab_stats = tk.Frame(notebook, bg="white")
    notebook.add(tab_stats, text="  Estadisticas  ")

    tk.Label(tab_stats, text="ESTADISTICAS CARGO-GO", font=("Segoe UI", 14, "bold"),
             bg="white", fg="#001A4D").pack(pady=(15, 10))

    f_cards = tk.Frame(tab_stats, bg="white")
    f_cards.pack(fill=tk.X, padx=15, pady=10)

    cur_st = conn.cursor()
    hoy = datetime.now().strftime('%Y-%m-%d')

    # Total envios hoy
    cur_st.execute("SELECT COUNT(*) FROM envios_cargo WHERE fecha_registro=?", (hoy,))
    total_hoy = cur_st.fetchone()[0]

    # Total ingresos hoy
    cur_st.execute("SELECT COALESCE(SUM(total),0) FROM envios_cargo WHERE fecha_registro=?", (hoy,))
    ingresos_hoy = cur_st.fetchone()[0]

    # Entregados hoy
    cur_st.execute("SELECT COUNT(*) FROM envios_cargo WHERE fecha_registro=? AND estado='ENTREGADO'", (hoy,))
    entregados_hoy = cur_st.fetchone()[0]

    # Pendientes
    cur_st.execute("SELECT COUNT(*) FROM envios_cargo WHERE estado IN ('RECIBIDO','EN_TRANSITO','EN_RUTA')")
    pendientes = cur_st.fetchone()[0]

    # Total general
    cur_st.execute("SELECT COUNT(*), COALESCE(SUM(total),0) FROM envios_cargo")
    row_gen = cur_st.fetchone()
    total_general = row_gen[0]
    ingresos_general = row_gen[1]

    cards_data = [
        ("Envios Hoy", str(total_hoy), "#2196F3"),
        ("Ingresos Hoy", f"${ingresos_hoy:.0f}", "#4CAF50"),
        ("Entregados Hoy", str(entregados_hoy), "#9C27B0"),
        ("Pendientes", str(pendientes), "#FF9800"),
        ("Total Envios", str(total_general), "#001A4D"),
        ("Ingresos Total", f"${ingresos_general:.0f}", "#1B5E20"),
    ]

    for i, (titulo, valor, color) in enumerate(cards_data):
        card = tk.Frame(f_cards, bg=color, relief=tk.RAISED, bd=1)
        card.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="nsew")
        f_cards.columnconfigure(i % 3, weight=1)
        tk.Label(card, text=titulo, font=("Segoe UI", 10), bg=color, fg="white").pack(pady=(10, 2), padx=15)
        tk.Label(card, text=valor, font=("Segoe UI", 22, "bold"), bg=color, fg="white").pack(pady=(2, 10), padx=15)

    # Top zonas
    tk.Label(tab_stats, text="TOP ZONAS", font=("Segoe UI", 12, "bold"),
             bg="white", fg="#333").pack(anchor=tk.W, padx=20, pady=(15, 5))

    cur_st.execute("""SELECT z.nombre, COUNT(*) as total, COALESCE(SUM(e.total),0)
                      FROM envios_cargo e
                      LEFT JOIN zonas_cdmx z ON e.zona_cdmx_id = z.id
                      GROUP BY e.zona_cdmx_id ORDER BY total DESC LIMIT 5""")
    for row in cur_st.fetchall():
        tk.Label(tab_stats, text=f"  {row[0] or 'Sin zona'}: {row[1]} envios - ${row[2]:.0f}",
                 font=("Segoe UI", 10), bg="white", fg="#555").pack(anchor=tk.W, padx=25)

    # Top repartidores
    tk.Label(tab_stats, text="TOP REPARTIDORES", font=("Segoe UI", 12, "bold"),
             bg="white", fg="#333").pack(anchor=tk.W, padx=20, pady=(15, 5))

    cur_st.execute("""SELECT r.nombre || ' ' || r.apellidos, COUNT(*) as total,
                             COALESCE(SUM(e.total),0)
                      FROM envios_cargo e
                      LEFT JOIN repartidores_cdmx r ON e.repartidor_id = r.id
                      GROUP BY e.repartidor_id ORDER BY total DESC LIMIT 5""")
    for row in cur_st.fetchall():
        tk.Label(tab_stats, text=f"  {row[0] or 'Sin asignar'}: {row[1]} envios - ${row[2]:.0f}",
                 font=("Segoe UI", 10), bg="white", fg="#555").pack(anchor=tk.W, padx=25)

    # ---- TAB 6: ZONAS ----
    tab_zonas = tk.Frame(notebook, bg="white")
    notebook.add(tab_zonas, text="  Zonas  ")

    tk.Label(tab_zonas, text="ZONAS DE COBERTURA CDMX", font=("Segoe UI", 14, "bold"),
             bg="white", fg="#001A4D").pack(pady=(15, 10))

    cols_zonas = ("CODIGO", "ZONA", "DELEGACION", "CP INICIO", "CP FIN", "TARIFA", "ACTIVA")
    tree_zonas = ttk.Treeview(tab_zonas, columns=cols_zonas, show="headings", height=12)
    for cn, w in [("CODIGO", 100), ("ZONA", 150), ("DELEGACION", 130),
                   ("CP INICIO", 80), ("CP FIN", 80), ("TARIFA", 80), ("ACTIVA", 60)]:
        tree_zonas.heading(cn, text=cn)
        tree_zonas.column(cn, width=w)
    tree_zonas.pack(fill=tk.X, padx=15, pady=5)

    cur_zn = conn.cursor()
    cur_zn.execute("SELECT codigo, nombre, delegacion, cp_inicio, cp_fin, tarifa_base, activa FROM zonas_cdmx")
    for row in cur_zn.fetchall():
        tree_zonas.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4],
                                              f"${row[5]:.0f}", "Si" if row[6] else "No"))


# ===== INICIO DEL PROGRAMA =====
if __name__ == "__main__":
    splash_root = tk.Tk()
    splash_root.title("")
    splash = SplashScreen(splash_root)
    splash_root.mainloop()
