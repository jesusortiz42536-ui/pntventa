"""
Cargo-GO API REST - Backend completo
Paqueteria + Marketplace
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import hashlib
import os

app = Flask(__name__, static_folder='app_cargo_go')
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_marketplace_tables():
    """Crear tablas del marketplace si no existen."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS negocios_marketplace (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            tipo TEXT DEFAULT 'TIENDA',
            nombre TEXT NOT NULL,
            descripcion TEXT,
            logo_url TEXT,
            banner_url TEXT,
            propietario_nombre TEXT,
            propietario_telefono TEXT,
            propietario_email TEXT,
            direccion TEXT,
            cp TEXT,
            ciudad TEXT DEFAULT 'Tulancingo',
            horario_apertura TEXT DEFAULT '09:00',
            horario_cierre TEXT DEFAULT '21:00',
            dias_servicio TEXT DEFAULT 'L,M,Mi,J,V,S',
            costo_envio REAL DEFAULT 0,
            pedido_minimo REAL DEFAULT 0,
            tiempo_preparacion INTEGER DEFAULT 30,
            calificacion_promedio REAL DEFAULT 5.0,
            total_pedidos INTEGER DEFAULT 0,
            suscripcion_mensual REAL DEFAULT 500,
            activo INTEGER DEFAULT 0,
            verificado INTEGER DEFAULT 0,
            destacado INTEGER DEFAULT 0,
            fecha_registro TEXT
        );

        CREATE TABLE IF NOT EXISTS productos_marketplace (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            negocio_id INTEGER,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            precio_oferta REAL,
            categoria TEXT,
            imagen_url TEXT,
            disponible INTEGER DEFAULT 1,
            destacado INTEGER DEFAULT 0,
            orden_menu INTEGER DEFAULT 0,
            FOREIGN KEY (negocio_id) REFERENCES negocios_marketplace(id)
        );

        CREATE TABLE IF NOT EXISTS pedidos_marketplace (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio TEXT UNIQUE,
            negocio_id INTEGER,
            cliente_nombre TEXT,
            cliente_telefono TEXT,
            cliente_direccion TEXT,
            cliente_cp TEXT,
            subtotal REAL,
            costo_envio REAL,
            total REAL,
            estado TEXT DEFAULT 'PENDIENTE',
            fecha TEXT,
            hora TEXT,
            FOREIGN KEY (negocio_id) REFERENCES negocios_marketplace(id)
        );

        CREATE TABLE IF NOT EXISTS items_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            producto_id INTEGER,
            cantidad INTEGER,
            precio_unitario REAL,
            subtotal REAL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos_marketplace(id)
        );
    """)

    # Insertar negocios demo si la tabla esta vacia
    count = conn.execute("SELECT COUNT(*) FROM negocios_marketplace").fetchone()[0]
    if count == 0:
        negocios_demo = [
            ("NEG-001", "FARMACIA", "Farmacia Central", "Medicamentos, perfumeria y mas",
             "Juan Perez", "7751234567", "farmacia@mail.com",
             "Av. Juarez 123, Centro", "43600", "Tulancingo",
             "08:00", "22:00", "L,M,Mi,J,V,S,D", 35, 100, 20, 4.8, 156, 1, 1, 1),
            ("NEG-002", "RESTAURANTE", "Tacos Don Pancho", "Los mejores tacos de Tulancingo",
             "Francisco Lopez", "7759876543", "tacos@mail.com",
             "Calle 5 de Mayo 45", "43600", "Tulancingo",
             "10:00", "23:00", "L,M,Mi,J,V,S,D", 25, 80, 25, 4.9, 312, 1, 1, 1),
            ("NEG-003", "ABARROTES", "Super Express 24h", "Abarrotes, bebidas y snacks a domicilio",
             "Maria Garcia", "7751112233", "super@mail.com",
             "Blvd. Revolucion 890", "43600", "Tulancingo",
             "07:00", "23:00", "L,M,Mi,J,V,S,D", 30, 50, 15, 4.7, 89, 1, 1, 0),
            ("NEG-004", "PANADERIA", "Pan de Casa", "Pan artesanal recien horneado",
             "Rosa Martinez", "7754445566", "pan@mail.com",
             "Calle Hidalgo 67", "43600", "Tulancingo",
             "06:00", "20:00", "L,M,Mi,J,V,S", 20, 60, 15, 4.6, 67, 1, 1, 0),
            ("NEG-005", "FLORERIA", "Flores y Detalles", "Arreglos florales para toda ocasion",
             "Ana Ruiz", "7757778899", "flores@mail.com",
             "Plaza Constitucion 12", "43600", "Tulancingo",
             "09:00", "19:00", "L,M,Mi,J,V,S", 40, 200, 45, 4.9, 45, 1, 1, 1),
            ("NEG-006", "PAPELERIA", "Office Max Express", "Papeleria, copias e impresiones",
             "Carlos Diaz", "7752223344", "office@mail.com",
             "Av. 21 de Marzo 234", "43600", "Tulancingo",
             "08:00", "20:00", "L,M,Mi,J,V,S", 25, 30, 10, 4.5, 34, 1, 1, 0),
        ]

        for n in negocios_demo:
            conn.execute("""
                INSERT INTO negocios_marketplace
                (codigo, tipo, nombre, descripcion,
                 propietario_nombre, propietario_telefono, propietario_email,
                 direccion, cp, ciudad,
                 horario_apertura, horario_cierre, dias_servicio,
                 costo_envio, pedido_minimo, tiempo_preparacion,
                 calificacion_promedio, total_pedidos,
                 activo, verificado, destacado, fecha_registro)
                VALUES (?,?,?,?, ?,?,?, ?,?,?, ?,?,?, ?,?,?, ?,?, ?,?,?,?)
            """, (*n, datetime.now().strftime('%Y-%m-%d')))

        # Productos demo
        productos_demo = [
            # Farmacia
            (1, "Paracetamol 500mg", "Caja 20 tabletas", 45.00, None, "Medicamentos", 1, 1, 1),
            (1, "Ibuprofeno 400mg", "Caja 10 tabletas", 38.00, 32.00, "Medicamentos", 1, 0, 2),
            (1, "Vitamina C 1g", "Tubo efervescente 10 pzas", 89.00, None, "Vitaminas", 1, 1, 3),
            (1, "Gel Antibacterial 500ml", "Desinfectante", 55.00, 45.00, "Higiene", 1, 0, 4),
            # Tacos
            (2, "Tacos al Pastor (5)", "Con pina, cebolla y cilantro", 65.00, None, "Tacos", 1, 1, 1),
            (2, "Tacos de Bistec (5)", "Carne asada con guacamole", 75.00, None, "Tacos", 1, 1, 2),
            (2, "Quesadillas (3)", "Con queso Oaxaca", 55.00, None, "Antojitos", 1, 0, 3),
            (2, "Refresco 600ml", "Coca-Cola, Pepsi o Fanta", 22.00, None, "Bebidas", 1, 0, 4),
            # Super
            (3, "Leche 1L", "Leche entera Santa Clara", 28.00, None, "Lacteos", 1, 0, 1),
            (3, "Pan Bimbo Grande", "Pan blanco rebanado", 52.00, None, "Panaderia", 1, 0, 2),
            (3, "Refresco 2L Coca-Cola", "Familiar", 35.00, 30.00, "Bebidas", 1, 1, 3),
            # Panaderia
            (4, "Concha (6 pzas)", "Pan dulce tradicional", 42.00, None, "Pan dulce", 1, 1, 1),
            (4, "Cuerno (6 pzas)", "Pan de mantequilla", 48.00, None, "Pan dulce", 1, 0, 2),
            (4, "Bolillo (12 pzas)", "Pan blanco fresco", 24.00, None, "Pan salado", 1, 0, 3),
            # Floreria
            (5, "Ramo 12 Rosas Rojas", "Con follaje y envoltura premium", 350.00, None, "Ramos", 1, 1, 1),
            (5, "Arreglo Cumpleanos", "Flores mixtas con globo", 450.00, 399.00, "Arreglos", 1, 1, 2),
            (5, "Girasoles (6 pzas)", "Ramo con envoltura kraft", 280.00, None, "Ramos", 1, 0, 3),
            # Papeleria
            (6, "Copias B/N (10)", "Carta o oficio", 15.00, None, "Copias", 1, 0, 1),
            (6, "Impresion Color (1)", "Carta", 8.00, None, "Impresiones", 1, 0, 2),
            (6, "Cuaderno Profesional", "100 hojas rayadas", 35.00, None, "Papeleria", 1, 0, 3),
        ]

        for p in productos_demo:
            conn.execute("""
                INSERT INTO productos_marketplace
                (negocio_id, nombre, descripcion, precio, precio_oferta,
                 categoria, disponible, destacado, orden_menu)
                VALUES (?,?,?,?,?, ?,?,?,?)
            """, p)

    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════
# SERVIR ARCHIVOS ESTATICOS
# ═══════════════════════════════════════════════════════

@app.route('/')
def index():
    return send_from_directory('app_cargo_go', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('app_cargo_go', path)


# ═══════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    usuario = data.get('usuario', '')
    password = data.get('password', '')

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db()
    user = conn.execute("""
        SELECT id, usuario, nombre, nivel FROM empleados
        WHERE usuario=? AND password=?
    """, (usuario, password_hash)).fetchone()
    conn.close()

    if user:
        return jsonify({'success': True, 'usuario': dict(user)})

    # Permitir login demo
    if usuario == 'admin' and password == 'admin':
        return jsonify({
            'success': True,
            'usuario': {'id': 0, 'usuario': 'admin', 'nombre': 'Administrador', 'nivel': 'ADMIN'}
        })

    return jsonify({'success': False, 'error': 'Credenciales incorrectas'}), 401


# ═══════════════════════════════════════════════════════
# ZONAS Y REPARTIDORES
# ═══════════════════════════════════════════════════════

@app.route('/api/zonas', methods=['GET'])
def obtener_zonas():
    conn = get_db()
    zonas = conn.execute("SELECT * FROM zonas_cdmx WHERE activa=1").fetchall()
    conn.close()
    return jsonify([dict(z) for z in zonas])


@app.route('/api/detectar-zona/<int:cp>', methods=['GET'])
def detectar_zona(cp):
    conn = get_db()
    zona = conn.execute("""
        SELECT * FROM zonas_cdmx
        WHERE ? BETWEEN cp_inicio AND cp_fin AND activa=1
    """, (cp,)).fetchone()
    conn.close()

    if zona:
        return jsonify(dict(zona))
    return jsonify({'error': 'CP no encontrado'}), 404


@app.route('/api/repartidores', methods=['GET'])
def obtener_repartidores():
    conn = get_db()
    reps = conn.execute("""
        SELECT r.*, z.nombre as zona_nombre
        FROM repartidores_cdmx r
        LEFT JOIN zonas_cdmx z ON r.zona_principal_id = z.id
        WHERE r.activo=1
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in reps])


# ═══════════════════════════════════════════════════════
# COTIZAR Y CREAR ENVIOS
# ═══════════════════════════════════════════════════════

@app.route('/api/cotizar', methods=['POST'])
def cotizar_envio():
    data = request.json
    cp = data.get('cp')
    peso = float(data.get('peso', 1.0))

    conn = get_db()

    zona = conn.execute("""
        SELECT * FROM zonas_cdmx
        WHERE ? BETWEEN cp_inicio AND cp_fin AND activa=1
    """, (cp,)).fetchone()

    if not zona:
        conn.close()
        return jsonify({'error': 'Codigo postal fuera de cobertura'}), 404

    rep = conn.execute("""
        SELECT * FROM repartidores_cdmx
        WHERE zona_principal_id=? AND activo=1 AND disponible=1
        ORDER BY entregas_hoy ASC LIMIT 1
    """, (zona['id'],)).fetchone()

    if not rep:
        # Buscar en cualquier zona
        rep = conn.execute("""
            SELECT * FROM repartidores_cdmx
            WHERE activo=1 AND disponible=1
            ORDER BY entregas_hoy ASC LIMIT 1
        """).fetchone()

    conn.close()

    if not rep:
        return jsonify({'error': 'No hay repartidores disponibles'}), 404

    tarifa_base = zona['tarifa_base']
    cargo_peso = max(0, (peso - 1) * 20)
    subtotal = tarifa_base + cargo_peso
    iva = subtotal * 0.16
    total = subtotal + iva

    return jsonify({
        'zona_id': zona['id'],
        'zona_nombre': zona['nombre'],
        'repartidor_id': rep['id'],
        'repartidor_nombre': f"{rep['nombre']} {rep['apellidos']}",
        'tarifa_base': tarifa_base,
        'cargo_peso': round(cargo_peso, 2),
        'subtotal': round(subtotal, 2),
        'iva': round(iva, 2),
        'total': round(total, 2)
    })


@app.route('/api/envios', methods=['POST'])
def crear_envio():
    data = request.json
    conn = get_db()

    fecha = datetime.now().strftime('%Y%m%d')
    num = conn.execute("""
        SELECT COUNT(*) + 1 FROM envios_cargo
        WHERE fecha_registro=?
    """, (datetime.now().strftime('%Y-%m-%d'),)).fetchone()[0]

    folio = f"CGO-{fecha}-{num:05d}"

    conn.execute("""
        INSERT INTO envios_cargo
        (folio, origen_nombre, origen_telefono,
         destino_nombre, destino_telefono, destino_cp,
         destino_direccion, destino_referencias,
         zona_cdmx_id, peso_kg, contenido, tipo_paquete,
         tarifa_base, cargo_peso, subtotal, iva, total,
         repartidor_id, estado,
         fecha_registro, hora_registro, usuario_registro)
        VALUES (?,?,?, ?,?,?, ?,?, ?,?,?,?, ?,?,?,?,?, ?,?, ?,?,?)
    """, (
        folio,
        data.get('origen_nombre'),
        data.get('origen_telefono'),
        data.get('destino_nombre'),
        data.get('destino_telefono'),
        data.get('destino_cp'),
        data.get('destino_direccion'),
        data.get('destino_referencias', ''),
        data.get('zona_id'),
        data.get('peso'),
        data.get('contenido'),
        data.get('tipo_paquete', 'PAQUETE_CHICO'),
        data.get('tarifa_base'),
        data.get('cargo_peso'),
        data.get('subtotal'),
        data.get('iva'),
        data.get('total'),
        data.get('repartidor_id'),
        'RECIBIDO',
        datetime.now().strftime('%Y-%m-%d'),
        datetime.now().strftime('%H:%M:%S'),
        data.get('usuario', 'app')
    ))

    envio_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    conn.execute("""
        INSERT INTO estados_envio
        (envio_id, estado_nuevo, fecha, hora, notas)
        VALUES (?,?,?,?,?)
    """, (
        envio_id, 'RECIBIDO',
        datetime.now().strftime('%Y-%m-%d'),
        datetime.now().strftime('%H:%M:%S'),
        'Paquete recibido en sucursal'
    ))

    conn.execute("""
        UPDATE repartidores_cdmx
        SET entregas_hoy = entregas_hoy + 1
        WHERE id=?
    """, (data.get('repartidor_id'),))

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'folio': folio,
        'mensaje': 'Envio creado exitosamente'
    })


# ═══════════════════════════════════════════════════════
# RASTREO
# ═══════════════════════════════════════════════════════

@app.route('/api/rastrear/<folio>', methods=['GET'])
def rastrear_envio(folio):
    conn = get_db()

    envio = conn.execute("""
        SELECT e.*, z.nombre as zona_nombre,
               r.nombre as rep_nombre, r.apellidos as rep_apellidos
        FROM envios_cargo e
        LEFT JOIN zonas_cdmx z ON e.zona_cdmx_id = z.id
        LEFT JOIN repartidores_cdmx r ON e.repartidor_id = r.id
        WHERE e.folio=?
    """, (folio,)).fetchone()

    if not envio:
        conn.close()
        return jsonify({'error': 'Envio no encontrado'}), 404

    estados = conn.execute("""
        SELECT * FROM estados_envio
        WHERE envio_id=?
        ORDER BY id DESC
    """, (envio['id'],)).fetchall()
    conn.close()

    return jsonify({
        'envio': dict(envio),
        'historial': [dict(e) for e in estados]
    })


@app.route('/api/historial', methods=['GET'])
def obtener_historial():
    conn = get_db()
    envios = conn.execute("""
        SELECT e.*, z.nombre as zona_nombre
        FROM envios_cargo e
        LEFT JOIN zonas_cdmx z ON e.zona_cdmx_id = z.id
        ORDER BY e.fecha_registro DESC, e.hora_registro DESC
        LIMIT 50
    """).fetchall()
    conn.close()
    return jsonify([dict(e) for e in envios])


# ═══════════════════════════════════════════════════════
# MARKETPLACE - NEGOCIOS
# ═══════════════════════════════════════════════════════

@app.route('/api/negocios', methods=['GET'])
def obtener_negocios():
    conn = get_db()
    negocios = conn.execute("""
        SELECT * FROM negocios_marketplace
        WHERE activo=1
        ORDER BY destacado DESC, calificacion_promedio DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(n) for n in negocios])


@app.route('/api/negocios/<int:negocio_id>', methods=['GET'])
def obtener_negocio(negocio_id):
    conn = get_db()
    negocio = conn.execute("""
        SELECT * FROM negocios_marketplace WHERE id=?
    """, (negocio_id,)).fetchone()
    conn.close()

    if not negocio:
        return jsonify({'error': 'Negocio no encontrado'}), 404
    return jsonify(dict(negocio))


@app.route('/api/negocios/<int:negocio_id>/productos', methods=['GET'])
def obtener_productos_negocio(negocio_id):
    conn = get_db()
    productos = conn.execute("""
        SELECT * FROM productos_marketplace
        WHERE negocio_id=? AND disponible=1
        ORDER BY destacado DESC, orden_menu ASC
    """, (negocio_id,)).fetchall()
    conn.close()
    return jsonify([dict(p) for p in productos])


@app.route('/api/negocios/registro', methods=['POST'])
def registrar_negocio():
    data = request.json
    conn = get_db()

    num = conn.execute("SELECT COUNT(*) + 1 FROM negocios_marketplace").fetchone()[0]
    codigo = f"NEG-{num:03d}"

    conn.execute("""
        INSERT INTO negocios_marketplace
        (codigo, tipo, nombre, descripcion, propietario_nombre,
         propietario_telefono, propietario_email,
         direccion, cp, ciudad,
         horario_apertura, horario_cierre, dias_servicio,
         costo_envio, suscripcion_mensual,
         activo, verificado, destacado, fecha_registro)
        VALUES (?,?,?,?,?, ?,?, ?,?,?, ?,?,?, ?,?, ?,?,?,?)
    """, (
        codigo,
        data.get('tipo', 'TIENDA'),
        data.get('nombre'),
        data.get('descripcion', ''),
        data.get('propietario_nombre'),
        data.get('propietario_telefono'),
        data.get('propietario_email', ''),
        data.get('direccion'),
        data.get('cp', '43600'),
        data.get('ciudad', 'Tulancingo'),
        data.get('horario_apertura', '09:00'),
        data.get('horario_cierre', '21:00'),
        data.get('dias_servicio', 'L,M,Mi,J,V,S'),
        float(data.get('costo_envio', 35)),
        float(data.get('suscripcion_mensual', 500)),
        0, 0, 0,
        datetime.now().strftime('%Y-%m-%d')
    ))

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'codigo': codigo,
        'mensaje': 'Negocio registrado. En revision para activacion.'
    })


# ═══════════════════════════════════════════════════════
# ESTADISTICAS
# ═══════════════════════════════════════════════════════

@app.route('/api/stats', methods=['GET'])
def obtener_estadisticas():
    conn = get_db()
    hoy = datetime.now().strftime('%Y-%m-%d')

    envios_hoy = conn.execute(
        "SELECT COUNT(*) FROM envios_cargo WHERE fecha_registro=?", (hoy,)
    ).fetchone()[0]

    en_ruta = conn.execute(
        "SELECT COUNT(*) FROM envios_cargo WHERE estado IN ('EN_RUTA','ASIGNADO')"
    ).fetchone()[0]

    entregados = conn.execute(
        "SELECT COUNT(*) FROM envios_cargo WHERE estado='ENTREGADO' AND fecha_registro=?", (hoy,)
    ).fetchone()[0]

    ingresos = conn.execute(
        "SELECT COALESCE(SUM(total), 0) FROM envios_cargo WHERE fecha_registro=?", (hoy,)
    ).fetchone()[0]

    total_envios = conn.execute(
        "SELECT COUNT(*) FROM envios_cargo"
    ).fetchone()[0]

    negocios_activos = conn.execute(
        "SELECT COUNT(*) FROM negocios_marketplace WHERE activo=1"
    ).fetchone()[0]

    repartidores_activos = conn.execute(
        "SELECT COUNT(*) FROM repartidores_cdmx WHERE activo=1 AND disponible=1"
    ).fetchone()[0]

    conn.close()

    return jsonify({
        'envios_hoy': envios_hoy,
        'en_ruta': en_ruta,
        'entregados': entregados,
        'ingresos_hoy': round(ingresos, 2),
        'total_envios': total_envios,
        'negocios_activos': negocios_activos,
        'repartidores_activos': repartidores_activos
    })


# ═══════════════════════════════════════════════════════
# FARMACIAS MADRID - PUNTO DE VENTA INTEGRADO
# ═══════════════════════════════════════════════════════

@app.route('/api/farmacia/productos', methods=['GET'])
def farmacia_productos():
    """Obtener productos de la farmacia con filtros."""
    categoria = request.args.get('categoria', '')
    busqueda = request.args.get('q', '')
    limite = int(request.args.get('limite', 50))
    offset = int(request.args.get('offset', 0))

    conn = get_db()
    query = "SELECT * FROM productos WHERE stock > 0"
    params = []

    if categoria:
        if categoria == 'ofertas':
            query += " AND precio_oferta > 0 AND precio_oferta < precio_venta"
        elif categoria == 'hospitalario':
            query += " AND (categoria LIKE '%HOSPITAL%' OR nombre LIKE '%INYECT%' OR nombre LIKE '%AMPOLLA%')"
        elif categoria == 'generico':
            query += " AND laboratorio IN ('AMSA', 'PISA', 'ULTRA', 'BRULUART', 'MAVER')"
        elif categoria == 'patente':
            query += " AND laboratorio NOT IN ('AMSA', 'PISA', 'ULTRA', 'BRULUART', 'MAVER')"
        elif categoria == 'especialidad':
            query += " AND categoria = 'ESPECIALIDAD'"
        else:
            query += " AND categoria = ?"
            params.append(categoria.upper())

    if busqueda:
        query += " AND (nombre LIKE ? OR laboratorio LIKE ? OR codigo_barras LIKE ?)"
        busqueda_param = f"%{busqueda}%"
        params.extend([busqueda_param, busqueda_param, busqueda_param])

    query += " ORDER BY nombre ASC LIMIT ? OFFSET ?"
    params.extend([limite, offset])

    productos = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([{
        'id': p['id'],
        'codigo': p['codigo'],
        'nombre': p['nombre'],
        'categoria': p['categoria'],
        'laboratorio': p['laboratorio'],
        'precio': p['precio_venta'],
        'precioOferta': p['precio_oferta'] if p['precio_oferta'] and p['precio_oferta'] > 0 else None,
        'stock': p['stock'],
        'imagen': p['imagen']
    } for p in productos])


@app.route('/api/farmacia/producto/<int:producto_id>', methods=['GET'])
def farmacia_producto_detalle(producto_id):
    """Obtener detalle de un producto."""
    conn = get_db()
    producto = conn.execute("SELECT * FROM productos WHERE id=?", (producto_id,)).fetchone()
    conn.close()

    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404

    return jsonify({
        'id': producto['id'],
        'codigo': producto['codigo'],
        'nombre': producto['nombre'],
        'categoria': producto['categoria'],
        'laboratorio': producto['laboratorio'],
        'precioCosto': producto['precio_costo'],
        'precioVenta': producto['precio_venta'],
        'precioOferta': producto['precio_oferta'],
        'stock': producto['stock'],
        'lote': producto['lote'],
        'caducidad': producto['caducidad'],
        'codigoBarras': producto['codigo_barras'],
        'imagen': producto['imagen'],
        'aplicaIva': producto['aplica_iva'] == 1
    })


@app.route('/api/farmacia/buscar', methods=['GET'])
def farmacia_buscar():
    """Busqueda rapida de productos."""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])

    conn = get_db()
    productos = conn.execute("""
        SELECT id, codigo, nombre, laboratorio, precio_venta, precio_oferta, stock
        FROM productos
        WHERE stock > 0 AND (nombre LIKE ? OR codigo LIKE ? OR codigo_barras = ?)
        ORDER BY nombre ASC
        LIMIT 20
    """, (f"%{q}%", f"%{q}%", q)).fetchall()
    conn.close()

    return jsonify([{
        'id': p['id'],
        'codigo': p['codigo'],
        'nombre': p['nombre'],
        'laboratorio': p['laboratorio'],
        'precio': p['precio_venta'],
        'precioOferta': p['precio_oferta'] if p['precio_oferta'] and p['precio_oferta'] > 0 else None,
        'stock': p['stock']
    } for p in productos])


@app.route('/api/farmacia/categorias', methods=['GET'])
def farmacia_categorias():
    """Obtener categorias disponibles con conteo."""
    conn = get_db()
    categorias = conn.execute("""
        SELECT categoria, COUNT(*) as total
        FROM productos WHERE stock > 0
        GROUP BY categoria
        ORDER BY total DESC
    """).fetchall()
    conn.close()
    return jsonify([{'nombre': c['categoria'], 'total': c['total']} for c in categorias])


@app.route('/api/farmacia/ofertas', methods=['GET'])
def farmacia_ofertas():
    """Obtener productos en oferta."""
    conn = get_db()
    ofertas = conn.execute("""
        SELECT id, codigo, nombre, laboratorio, precio_venta, precio_oferta, stock, imagen
        FROM productos
        WHERE stock > 0 AND precio_oferta > 0 AND precio_oferta < precio_venta
        ORDER BY (precio_venta - precio_oferta) DESC
        LIMIT 50
    """).fetchall()
    conn.close()

    return jsonify([{
        'id': o['id'],
        'codigo': o['codigo'],
        'nombre': o['nombre'],
        'laboratorio': o['laboratorio'],
        'precioOriginal': o['precio_venta'],
        'precioOferta': o['precio_oferta'],
        'descuento': round((1 - o['precio_oferta'] / o['precio_venta']) * 100),
        'stock': o['stock'],
        'imagen': o['imagen']
    } for o in ofertas])


@app.route('/api/farmacia/pedido', methods=['POST'])
def farmacia_crear_pedido():
    """Crear un pedido desde la app."""
    data = request.json
    conn = get_db()

    # Generar folio
    fecha = datetime.now().strftime('%Y%m%d')
    num = conn.execute("""
        SELECT COUNT(*) + 1 FROM pedidos_marketplace
        WHERE fecha LIKE ?
    """, (f"{datetime.now().strftime('%Y-%m-%d')}%",)).fetchone()[0]
    folio = f"FM-{fecha}-{num:04d}"

    # Insertar pedido
    conn.execute("""
        INSERT INTO pedidos_marketplace
        (folio, negocio_id, cliente_nombre, cliente_telefono,
         cliente_direccion, cliente_cp, subtotal, costo_envio, total,
         estado, fecha, hora)
        VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?, 'PENDIENTE', ?, ?)
    """, (
        folio,
        data.get('cliente_nombre'),
        data.get('cliente_telefono'),
        data.get('cliente_direccion'),
        data.get('cliente_cp', '43600'),
        data.get('subtotal', 0),
        data.get('costo_envio', 35),
        data.get('total', 0),
        datetime.now().strftime('%Y-%m-%d'),
        datetime.now().strftime('%H:%M:%S')
    ))

    pedido_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Guardar items del pedido (crear tabla si no existe)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items_pedido (
            id INTEGER PRIMARY KEY,
            pedido_id INTEGER,
            producto_id INTEGER,
            cantidad INTEGER,
            precio_unitario REAL,
            subtotal REAL
        )
    """)

    for item in data.get('items', []):
        conn.execute("""
            INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (pedido_id, item['producto_id'], item['cantidad'], item['precio'], item['cantidad'] * item['precio']))

        # Descontar stock
        conn.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (item['cantidad'], item['producto_id']))

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'folio': folio,
        'pedido_id': pedido_id,
        'mensaje': 'Pedido creado exitosamente'
    })


# ═══════════════════════════════════════════════════════
# PEDIDOS APP - GESTION COMPLETA
# ═══════════════════════════════════════════════════════

# Lista temporal de pedidos pendientes (para notificaciones)
pedidos_nuevos = []

@app.route('/api/farmacia/pedidos', methods=['GET'])
def farmacia_obtener_pedidos():
    """Obtener todos los pedidos con filtros."""
    estado = request.args.get('estado', '')
    fecha = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))

    conn = get_db()
    query = """
        SELECT p.*,
               (SELECT COUNT(*) FROM items_pedido WHERE pedido_id = p.id) as total_items
        FROM pedidos_marketplace p
        WHERE p.negocio_id = 1
    """
    params = []

    if estado:
        query += " AND p.estado = ?"
        params.append(estado)

    if fecha:
        query += " AND p.fecha = ?"
        params.append(fecha)

    query += " ORDER BY p.id DESC LIMIT 100"

    pedidos = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([{
        'id': p['id'],
        'folio': p['folio'],
        'cliente_nombre': p['cliente_nombre'],
        'cliente_telefono': p['cliente_telefono'],
        'cliente_direccion': p['cliente_direccion'],
        'subtotal': p['subtotal'],
        'costo_envio': p['costo_envio'],
        'total': p['total'],
        'estado': p['estado'],
        'fecha': p['fecha'],
        'hora': p['hora'],
        'total_items': p['total_items']
    } for p in pedidos])


@app.route('/api/farmacia/pedidos/<int:pedido_id>', methods=['GET'])
def farmacia_pedido_detalle(pedido_id):
    """Obtener detalle completo de un pedido."""
    conn = get_db()

    pedido = conn.execute("""
        SELECT * FROM pedidos_marketplace WHERE id = ?
    """, (pedido_id,)).fetchone()

    if not pedido:
        conn.close()
        return jsonify({'error': 'Pedido no encontrado'}), 404

    items = conn.execute("""
        SELECT i.*, p.nombre, p.codigo
        FROM items_pedido i
        LEFT JOIN productos p ON i.producto_id = p.id
        WHERE i.pedido_id = ?
    """, (pedido_id,)).fetchall()
    conn.close()

    return jsonify({
        'pedido': dict(pedido),
        'items': [{
            'producto_id': i['producto_id'],
            'nombre': i['nombre'],
            'codigo': i['codigo'],
            'cantidad': i['cantidad'],
            'precio_unitario': i['precio_unitario'],
            'subtotal': i['subtotal']
        } for i in items]
    })


@app.route('/api/farmacia/pedidos/<int:pedido_id>/estado', methods=['PUT'])
def farmacia_actualizar_estado(pedido_id):
    """Actualizar estado de un pedido."""
    data = request.json
    nuevo_estado = data.get('estado')

    estados_validos = ['PENDIENTE', 'CONFIRMADO', 'PREPARANDO', 'LISTO', 'EN_CAMINO', 'ENTREGADO', 'CANCELADO']
    if nuevo_estado not in estados_validos:
        return jsonify({'error': 'Estado no válido'}), 400

    conn = get_db()
    conn.execute("UPDATE pedidos_marketplace SET estado = ? WHERE id = ?", (nuevo_estado, pedido_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'mensaje': f'Pedido actualizado a {nuevo_estado}'})


@app.route('/api/farmacia/pedidos/nuevos', methods=['GET'])
def farmacia_pedidos_nuevos():
    """Obtener pedidos nuevos (para polling/notificaciones)."""
    conn = get_db()
    pedidos = conn.execute("""
        SELECT id, folio, cliente_nombre, total, fecha, hora
        FROM pedidos_marketplace
        WHERE negocio_id = 1 AND estado = 'PENDIENTE'
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()
    conn.close()

    return jsonify({
        'count': len(pedidos),
        'pedidos': [dict(p) for p in pedidos]
    })


@app.route('/api/farmacia/pedidos/stats', methods=['GET'])
def farmacia_pedidos_stats():
    """Estadísticas de pedidos del día."""
    conn = get_db()
    hoy = datetime.now().strftime('%Y-%m-%d')

    stats = {
        'pendientes': conn.execute("SELECT COUNT(*) FROM pedidos_marketplace WHERE fecha=? AND estado='PENDIENTE'", (hoy,)).fetchone()[0],
        'confirmados': conn.execute("SELECT COUNT(*) FROM pedidos_marketplace WHERE fecha=? AND estado='CONFIRMADO'", (hoy,)).fetchone()[0],
        'preparando': conn.execute("SELECT COUNT(*) FROM pedidos_marketplace WHERE fecha=? AND estado='PREPARANDO'", (hoy,)).fetchone()[0],
        'en_camino': conn.execute("SELECT COUNT(*) FROM pedidos_marketplace WHERE fecha=? AND estado='EN_CAMINO'", (hoy,)).fetchone()[0],
        'entregados': conn.execute("SELECT COUNT(*) FROM pedidos_marketplace WHERE fecha=? AND estado='ENTREGADO'", (hoy,)).fetchone()[0],
        'cancelados': conn.execute("SELECT COUNT(*) FROM pedidos_marketplace WHERE fecha=? AND estado='CANCELADO'", (hoy,)).fetchone()[0],
        'ventas_hoy': conn.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos_marketplace WHERE fecha=? AND estado='ENTREGADO'", (hoy,)).fetchone()[0],
        'total_pedidos': conn.execute("SELECT COUNT(*) FROM pedidos_marketplace WHERE fecha=?", (hoy,)).fetchone()[0],
    }
    conn.close()

    return jsonify(stats)


# ═══════════════════════════════════════════════════════
# PANEL WEB DE PEDIDOS
# ═══════════════════════════════════════════════════════

@app.route('/pedidos')
def panel_pedidos():
    """Panel web para ver y gestionar pedidos."""
    return '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📦 Panel de Pedidos - Farmacias Madrid</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; }

        .header { background: linear-gradient(135deg, #001B44, #0D3B66); color: white; padding: 20px; }
        .header h1 { font-size: 24px; display: flex; align-items: center; gap: 10px; }
        .header .stats { display: flex; gap: 20px; margin-top: 15px; flex-wrap: wrap; }
        .stat-box { background: rgba(255,255,255,0.15); padding: 12px 20px; border-radius: 10px; text-align: center; }
        .stat-box .number { font-size: 28px; font-weight: bold; color: #FFD700; }
        .stat-box .label { font-size: 12px; opacity: 0.9; }

        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }

        .filters { display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }
        .filter-btn { padding: 10px 20px; border: none; border-radius: 25px; cursor: pointer; font-weight: 600; transition: all 0.2s; }
        .filter-btn.active { background: #001B44; color: white; }
        .filter-btn:not(.active) { background: white; color: #333; border: 2px solid #e0e0e0; }
        .filter-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }

        .pedidos-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }

        .pedido-card { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); transition: all 0.2s; }
        .pedido-card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.12); }
        .pedido-card.nuevo { border-left: 4px solid #E53935; animation: pulse 2s infinite; }

        @keyframes pulse { 0%, 100% { box-shadow: 0 2px 12px rgba(0,0,0,0.08); } 50% { box-shadow: 0 2px 20px rgba(229,57,53,0.3); } }

        .pedido-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .pedido-folio { font-weight: bold; color: #001B44; font-size: 16px; }
        .pedido-estado { padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase; }
        .estado-PENDIENTE { background: #FFF3E0; color: #E65100; }
        .estado-CONFIRMADO { background: #E3F2FD; color: #1565C0; }
        .estado-PREPARANDO { background: #F3E5F5; color: #7B1FA2; }
        .estado-EN_CAMINO { background: #E8F5E9; color: #2E7D32; }
        .estado-ENTREGADO { background: #E8F5E9; color: #1B5E20; }
        .estado-CANCELADO { background: #FFEBEE; color: #C62828; }

        .cliente-info { margin-bottom: 15px; }
        .cliente-nombre { font-weight: 600; font-size: 15px; color: #333; }
        .cliente-telefono { color: #666; font-size: 14px; margin-top: 4px; }
        .cliente-direccion { color: #888; font-size: 13px; margin-top: 4px; }

        .pedido-total { display: flex; justify-content: space-between; align-items: center; padding-top: 15px; border-top: 1px solid #eee; }
        .total-label { color: #666; }
        .total-amount { font-size: 22px; font-weight: bold; color: #001B44; }

        .pedido-actions { display: flex; gap: 10px; margin-top: 15px; }
        .action-btn { flex: 1; padding: 10px; border: none; border-radius: 10px; cursor: pointer; font-weight: 600; font-size: 13px; transition: all 0.2s; }
        .btn-confirmar { background: #4CAF50; color: white; }
        .btn-preparar { background: #9C27B0; color: white; }
        .btn-enviar { background: #2196F3; color: white; }
        .btn-entregar { background: #001B44; color: white; }
        .btn-whatsapp { background: #25D366; color: white; }
        .btn-cancelar { background: #f5f5f5; color: #666; }
        .action-btn:hover { opacity: 0.9; transform: scale(1.02); }

        .empty-state { text-align: center; padding: 60px 20px; color: #888; }
        .empty-state .icon { font-size: 64px; margin-bottom: 20px; }

        .notification { position: fixed; top: 20px; right: 20px; background: #E53935; color: white; padding: 16px 24px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); display: none; z-index: 1000; animation: slideIn 0.3s ease; }
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

        .hora { font-size: 13px; color: #999; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📦 Panel de Pedidos</h1>
        <div class="stats" id="stats">
            <div class="stat-box"><div class="number" id="stat-pendientes">-</div><div class="label">Pendientes</div></div>
            <div class="stat-box"><div class="number" id="stat-preparando">-</div><div class="label">Preparando</div></div>
            <div class="stat-box"><div class="number" id="stat-encamino">-</div><div class="label">En Camino</div></div>
            <div class="stat-box"><div class="number" id="stat-entregados">-</div><div class="label">Entregados</div></div>
            <div class="stat-box"><div class="number" id="stat-ventas">$0</div><div class="label">Ventas Hoy</div></div>
        </div>
    </div>

    <div class="container">
        <div class="filters">
            <button class="filter-btn active" data-filter="">Todos</button>
            <button class="filter-btn" data-filter="PENDIENTE">🔴 Pendientes</button>
            <button class="filter-btn" data-filter="CONFIRMADO">🔵 Confirmados</button>
            <button class="filter-btn" data-filter="PREPARANDO">🟣 Preparando</button>
            <button class="filter-btn" data-filter="EN_CAMINO">🟢 En Camino</button>
            <button class="filter-btn" data-filter="ENTREGADO">✅ Entregados</button>
        </div>

        <!-- Respuestas Rápidas WhatsApp -->
        <div style="background:#25D366; color:white; padding:15px 20px; border-radius:14px; margin-bottom:20px;">
            <div style="font-weight:bold; margin-bottom:10px;">💬 Respuestas Rápidas WhatsApp (click para copiar)</div>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <button onclick="copyQuickReply('saludo')" style="background:white; color:#25D366; border:none; padding:8px 16px; border-radius:20px; cursor:pointer; font-weight:600;">👋 Saludo</button>
                <button onclick="copyQuickReply('disponibilidad')" style="background:white; color:#25D366; border:none; padding:8px 16px; border-radius:20px; cursor:pointer; font-weight:600;">📋 Disponibilidad</button>
                <button onclick="copyQuickReply('horario')" style="background:white; color:#25D366; border:none; padding:8px 16px; border-radius:20px; cursor:pointer; font-weight:600;">⏰ Horario</button>
                <button onclick="copyQuickReply('ubicacion')" style="background:white; color:#25D366; border:none; padding:8px 16px; border-radius:20px; cursor:pointer; font-weight:600;">📍 Ubicación</button>
                <button onclick="copyQuickReply('agotado')" style="background:white; color:#25D366; border:none; padding:8px 16px; border-radius:20px; cursor:pointer; font-weight:600;">😔 Agotado</button>
                <button onclick="copyQuickReply('gracias')" style="background:white; color:#25D366; border:none; padding:8px 16px; border-radius:20px; cursor:pointer; font-weight:600;">🙏 Gracias</button>
            </div>
        </div>

        <div class="pedidos-grid" id="pedidos-container">
            <div class="empty-state">
                <div class="icon">📦</div>
                <p>Cargando pedidos...</p>
            </div>
        </div>
    </div>

    <div class="notification" id="notification">🔔 ¡Nuevo pedido recibido!</div>

    <audio id="notification-sound" preload="auto">
        <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2teleAsPXLXp5bl2BAAAjuD3xnYtFS+Z6vOjWwcAFqnv8ZE2BgA0wfbyewsAUNn15F8AAGru9M0mAABt/fWWEQAAWPn0kAkAAD/x9IcFAAI17/R3AAAJL+30bQAAECvr9GUAABgo6PRdAAAdJef0VQAAH" type="audio/wav">
    </audio>

    <script>
        let currentFilter = '';
        let lastPedidoCount = 0;

        // Cargar estadísticas
        async function loadStats() {
            try {
                const res = await fetch('/api/farmacia/pedidos/stats');
                const data = await res.json();
                document.getElementById('stat-pendientes').textContent = data.pendientes;
                document.getElementById('stat-preparando').textContent = data.preparando;
                document.getElementById('stat-encamino').textContent = data.en_camino;
                document.getElementById('stat-entregados').textContent = data.entregados;
                document.getElementById('stat-ventas').textContent = '$' + data.ventas_hoy.toLocaleString();
            } catch (e) { console.error(e); }
        }

        // Cargar pedidos
        async function loadPedidos() {
            try {
                const url = '/api/farmacia/pedidos' + (currentFilter ? '?estado=' + currentFilter : '');
                const res = await fetch(url);
                const pedidos = await res.json();

                if (pedidos.length > lastPedidoCount && lastPedidoCount > 0) {
                    showNotification();
                }
                lastPedidoCount = pedidos.length;

                renderPedidos(pedidos);
            } catch (e) { console.error(e); }
        }

        function renderPedidos(pedidos) {
            const container = document.getElementById('pedidos-container');

            if (pedidos.length === 0) {
                container.innerHTML = '<div class="empty-state"><div class="icon">📭</div><p>No hay pedidos</p></div>';
                return;
            }

            container.innerHTML = pedidos.map(p => `
                <div class="pedido-card ${p.estado === 'PENDIENTE' ? 'nuevo' : ''}">
                    <div class="pedido-header">
                        <span class="pedido-folio">${p.folio}</span>
                        <span class="pedido-estado estado-${p.estado}">${p.estado.replace('_', ' ')}</span>
                    </div>
                    <div class="cliente-info">
                        <div class="cliente-nombre">👤 ${p.cliente_nombre || 'Sin nombre'}</div>
                        <div class="cliente-telefono">📱 ${p.cliente_telefono || 'Sin teléfono'}</div>
                        <div class="cliente-direccion">📍 ${p.cliente_direccion || 'Sin dirección'}</div>
                    </div>
                    <div class="hora">🕐 ${p.hora} - ${p.total_items} productos</div>
                    <div class="pedido-total">
                        <span class="total-label">Total:</span>
                        <span class="total-amount">$${p.total?.toLocaleString() || 0}</span>
                    </div>
                    <div class="pedido-actions">
                        ${getActionButtons(p)}
                    </div>
                </div>
            `).join('');
        }

        function getActionButtons(p) {
            const tel = p.cliente_telefono?.replace(/\D/g, '') || '';
            const whatsBtn = tel ? `<button class="action-btn btn-whatsapp" onclick="sendWhatsApp('${tel}', '${p.folio}', '${p.estado}')">💬</button>` : '';

            switch(p.estado) {
                case 'PENDIENTE':
                    return `<button class="action-btn btn-confirmar" onclick="updateEstado(${p.id}, 'CONFIRMADO')">✓ Confirmar</button>${whatsBtn}<button class="action-btn btn-cancelar" onclick="updateEstado(${p.id}, 'CANCELADO')">✕</button>`;
                case 'CONFIRMADO':
                    return `<button class="action-btn btn-preparar" onclick="updateEstado(${p.id}, 'PREPARANDO')">🍳 Preparar</button>${whatsBtn}`;
                case 'PREPARANDO':
                    return `<button class="action-btn btn-enviar" onclick="updateEstado(${p.id}, 'EN_CAMINO')">🚚 Enviar</button>${whatsBtn}`;
                case 'EN_CAMINO':
                    return `<button class="action-btn btn-entregar" onclick="updateEstado(${p.id}, 'ENTREGADO')">✅ Entregado</button>${whatsBtn}`;
                default:
                    return whatsBtn || '<span style="color:#999">Sin acciones</span>';
            }
        }

        async function updateEstado(id, estado) {
            try {
                await fetch(`/api/farmacia/pedidos/${id}/estado`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ estado })
                });
                loadPedidos();
                loadStats();
            } catch (e) { alert('Error al actualizar'); }
        }

        function sendWhatsApp(tel, folio, estado) {
            const msgs = {
                'PENDIENTE': `Hola! 👋

Recibimos tu pedido *${folio}* de *Farmacias Madrid*.

✅ En breve lo confirmamos y te avisamos cuando esté listo.

¿Tu dirección es correcta? Por favor confírmanos. 🙏`,
                'CONFIRMADO': `¡Hola! 🎉

Tu pedido *${folio}* ha sido *CONFIRMADO*.

⏳ Ya lo estamos preparando.
📦 Te avisamos cuando salga a entrega.

Tiempo estimado: *30-45 minutos*`,
                'PREPARANDO': `¡Hola! 📦

Tu pedido *${folio}* está siendo preparado.

🧑‍🍳 Estamos alistando tus productos.
🚚 Pronto saldrá a entrega.

¡Gracias por tu paciencia!`,
                'EN_CAMINO': `¡Hola! 🚚

*¡Tu pedido va en camino!*

📦 Pedido: *${folio}*
⏱️ Llegará en aprox. *20-30 minutos*

El repartidor te contactará al llegar.
¡Gracias por tu compra! 🙏`,
                'ENTREGADO': `¡Hola! ⭐

Tu pedido *${folio}* ha sido *ENTREGADO*.

¡Gracias por comprar en *Farmacias Madrid*!

💳 Recuerda acumular tus *Saturnos* en tu próxima compra.

¿Todo llegó bien? Tu opinión nos importa. 🙏`
            };
            const msg = msgs[estado] || `Información sobre tu pedido ${folio}`;
            window.open(`https://wa.me/52${tel}?text=${encodeURIComponent(msg)}`);
        }

        // Respuestas rápidas adicionales
        const quickReplies = {
            saludo: `¡Hola! 👋 Bienvenido a *Farmacias Madrid*.

¿En qué podemos ayudarte?

1️⃣ Ver productos
2️⃣ Consultar disponibilidad
3️⃣ Estado de mi pedido
4️⃣ Tarjeta Monedero

Escríbenos y con gusto te atendemos. 🙏`,

            disponibilidad: `¡Hola! 📋

Para consultar disponibilidad, por favor envíanos:
• Nombre del medicamento
• Presentación (tabletas, jarabe, etc.)

Te confirmamos stock y precio en minutos. 💊`,

            horario: `📍 *Farmacias Madrid*

⏰ Horario:
Lun-Sáb: 8:00am - 10:00pm
Dom: 9:00am - 8:00pm

🚚 Entregas a domicilio disponibles
📱 Pedidos por app y WhatsApp

¡Te esperamos!`,

            ubicacion: `📍 *Ubicación Farmacias Madrid*

🏥 Tulancingo, Hidalgo

🚚 *Entrega a domicilio* en toda la zona
⏱️ Tiempo promedio: 30-45 min

¿Te enviamos tu pedido? 🛵`,

            agotado: `Lo sentimos 😔

El producto que buscas está *temporalmente agotado*.

¿Te gustaría que te avisemos cuando llegue?
También podemos sugerirte alternativas similares.

¿Cómo prefieres? 🤔`,

            gracias: `¡Gracias por tu compra! 🙏

Fue un placer atenderte.

⭐ Si quedaste satisfecho, recomiéndanos con tus amigos y familia.

💳 Recuerda acumular *Saturnos* en tu Tarjeta Monedero.

¡Hasta pronto! 👋`
        };

        function copyQuickReply(key) {
            const text = quickReplies[key];
            navigator.clipboard.writeText(text).then(() => {
                alert('✅ Copiado al portapapeles');
            });
        }

        function showNotification() {
            const notif = document.getElementById('notification');
            const sound = document.getElementById('notification-sound');
            notif.style.display = 'block';
            try { sound.play(); } catch(e) {}
            setTimeout(() => { notif.style.display = 'none'; }, 5000);
        }

        // Filtros
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.filter;
                loadPedidos();
            });
        });

        // Iniciar
        loadStats();
        loadPedidos();

        // Auto-refresh cada 10 segundos
        setInterval(() => { loadPedidos(); loadStats(); }, 10000);
    </script>
</body>
</html>'''


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

if __name__ == '__main__':
    os.makedirs('app_cargo_go', exist_ok=True)
    os.makedirs('app_cargo_go/assets', exist_ok=True)

    init_marketplace_tables()

    print("=" * 50)
    print("  CARGO-GO API + PWA")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
