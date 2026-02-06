"""
FARMACIAS MADRID - API REST para Repartidores
Flask API en puerto 5000 para la app movil de repartidores.

Endpoints:
  GET  /api/entregas              - Lista entregas pendientes/en curso
  GET  /api/entregas/<id>         - Detalle de una entrega
  POST /api/entregas/<id>/iniciar - Marcar entrega como EN CAMINO
  POST /api/entregas/<id>/completar - Marcar entrega como ENTREGADA
  GET  /api/repartidor/<id>       - Info del repartidor
  GET  /api/stats/<repartidor_id> - Estadisticas del repartidor

Uso:
  pip install flask flask-cors
  python api_repartidores.py
"""

import sqlite3
import os
from datetime import datetime

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    FLASK_DISPONIBLE = True
except ImportError:
    FLASK_DISPONIBLE = False

if not FLASK_DISPONIBLE:
    print("=" * 50)
    print("  ERROR: Flask no instalado")
    print("  Ejecuta: pip install flask flask-cors")
    print("=" * 50)
    exit(1)

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def registrar_auditoria(conn, accion, datos=""):
    try:
        ahora = datetime.now()
        conn.execute("INSERT INTO auditoria (usuario_id, usuario_nombre, accion, modulo, datos, ip, fecha, hora) VALUES (?,?,?,?,?,?,?,?)",
                     (0, "API_REPARTIDORES", accion, "domicilio", str(datos)[:500],
                      request.remote_addr if request else "api",
                      ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S")))
    except Exception:
        pass


# === ENDPOINTS ===

@app.route('/api/entregas', methods=['GET'])
def listar_entregas():
    """Lista entregas. Filtros: ?estado=PENDIENTE&repartidor_id=1"""
    db = get_db()
    estado = request.args.get('estado', None)
    repartidor_id = request.args.get('repartidor_id', None)

    query = """SELECT e.id, e.venta_id, e.direccion, e.referencia, e.telefono_cliente,
                      e.estado, e.hora_salida, e.hora_llegada, e.metodo_pago_entrega,
                      e.monto_cobrar, e.cambio_llevar, e.notas, e.fecha, e.num_moto,
                      c.nombre as cliente_nombre, r.nombre as repartidor_nombre
               FROM entregas e
               LEFT JOIN clientes c ON e.cliente_id = c.id
               LEFT JOIN repartidores r ON e.repartidor_id = r.id
               WHERE 1=1"""
    params = []

    if estado:
        query += " AND e.estado = ?"
        params.append(estado)
    if repartidor_id:
        query += " AND e.repartidor_id = ?"
        params.append(int(repartidor_id))

    query += " ORDER BY e.id DESC LIMIT 50"

    rows = db.execute(query, params).fetchall()
    entregas = []
    for row in rows:
        entregas.append({
            "id": row["id"],
            "venta_id": row["venta_id"],
            "direccion": row["direccion"],
            "referencia": row["referencia"],
            "telefono_cliente": row["telefono_cliente"],
            "estado": row["estado"],
            "hora_salida": row["hora_salida"],
            "hora_llegada": row["hora_llegada"],
            "metodo_pago": row["metodo_pago_entrega"],
            "monto_cobrar": row["monto_cobrar"],
            "cambio_llevar": row["cambio_llevar"],
            "notas": row["notas"],
            "fecha": row["fecha"],
            "num_moto": row["num_moto"],
            "cliente_nombre": row["cliente_nombre"],
            "repartidor_nombre": row["repartidor_nombre"],
        })

    db.close()
    return jsonify({"ok": True, "entregas": entregas, "total": len(entregas)})


@app.route('/api/entregas/<int:entrega_id>', methods=['GET'])
def detalle_entrega(entrega_id):
    """Detalle de una entrega especifica."""
    db = get_db()
    row = db.execute("""SELECT e.*, c.nombre as cliente_nombre, c.telefono as cliente_tel,
                               r.nombre as repartidor_nombre, r.telefono as repartidor_tel
                        FROM entregas e
                        LEFT JOIN clientes c ON e.cliente_id = c.id
                        LEFT JOIN repartidores r ON e.repartidor_id = r.id
                        WHERE e.id = ?""", (entrega_id,)).fetchone()
    db.close()

    if not row:
        return jsonify({"ok": False, "error": "Entrega no encontrada"}), 404

    return jsonify({
        "ok": True,
        "entrega": {
            "id": row["id"],
            "venta_id": row["venta_id"],
            "direccion": row["direccion"],
            "referencia": row["referencia"],
            "telefono_cliente": row["telefono_cliente"],
            "estado": row["estado"],
            "hora_salida": row["hora_salida"],
            "hora_llegada": row["hora_llegada"],
            "metodo_pago": row["metodo_pago_entrega"],
            "monto_cobrar": row["monto_cobrar"],
            "cambio_llevar": row["cambio_llevar"],
            "notas": row["notas"],
            "fecha": row["fecha"],
            "num_moto": row["num_moto"],
            "cliente_nombre": row["cliente_nombre"],
            "cliente_tel": row["cliente_tel"],
            "repartidor_nombre": row["repartidor_nombre"],
            "repartidor_tel": row["repartidor_tel"],
        }
    })


@app.route('/api/entregas/<int:entrega_id>/iniciar', methods=['POST'])
def iniciar_entrega(entrega_id):
    """Marca entrega como EN CAMINO."""
    db = get_db()
    row = db.execute("SELECT estado FROM entregas WHERE id=?", (entrega_id,)).fetchone()

    if not row:
        db.close()
        return jsonify({"ok": False, "error": "Entrega no encontrada"}), 404

    if row["estado"] not in ("PENDIENTE", "ASIGNADO"):
        db.close()
        return jsonify({"ok": False, "error": f"No se puede iniciar, estado actual: {row['estado']}"}), 400

    hora_salida = datetime.now().strftime("%H:%M:%S")
    db.execute("UPDATE entregas SET estado='EN CAMINO', hora_salida=? WHERE id=?",
               (hora_salida, entrega_id))

    registrar_auditoria(db, "ENTREGA_INICIADA", f"Entrega #{entrega_id} en camino")
    db.commit()
    db.close()

    return jsonify({"ok": True, "mensaje": "Entrega en camino", "hora_salida": hora_salida})


@app.route('/api/entregas/<int:entrega_id>/completar', methods=['POST'])
def completar_entrega(entrega_id):
    """Marca entrega como ENTREGADA."""
    db = get_db()
    row = db.execute("SELECT estado FROM entregas WHERE id=?", (entrega_id,)).fetchone()

    if not row:
        db.close()
        return jsonify({"ok": False, "error": "Entrega no encontrada"}), 404

    if row["estado"] != "EN CAMINO":
        db.close()
        return jsonify({"ok": False, "error": f"Solo se pueden completar entregas EN CAMINO, actual: {row['estado']}"}), 400

    hora_llegada = datetime.now().strftime("%H:%M:%S")
    notas = ""
    if request.json and "notas" in request.json:
        notas = request.json["notas"]

    db.execute("UPDATE entregas SET estado='ENTREGADO', hora_llegada=?, notas=COALESCE(notas,'')||? WHERE id=?",
               (hora_llegada, f" | Nota entrega: {notas}" if notas else "", entrega_id))

    registrar_auditoria(db, "ENTREGA_COMPLETADA", f"Entrega #{entrega_id} entregada")
    db.commit()
    db.close()

    return jsonify({"ok": True, "mensaje": "Entrega completada", "hora_llegada": hora_llegada})


@app.route('/api/repartidor/<int:repartidor_id>', methods=['GET'])
def info_repartidor(repartidor_id):
    """Info del repartidor."""
    db = get_db()
    row = db.execute("SELECT * FROM repartidores WHERE id=?", (repartidor_id,)).fetchone()
    db.close()

    if not row:
        return jsonify({"ok": False, "error": "Repartidor no encontrado"}), 404

    return jsonify({
        "ok": True,
        "repartidor": {
            "id": row["id"],
            "nombre": row["nombre"],
            "telefono": row["telefono"],
            "num_moto": row["num_moto"],
            "activo": row["activo"],
        }
    })


@app.route('/api/stats/<int:repartidor_id>', methods=['GET'])
def stats_repartidor(repartidor_id):
    """Estadisticas del repartidor."""
    db = get_db()
    hoy = datetime.now().strftime("%Y-%m-%d")

    # Entregas hoy
    row = db.execute("SELECT COUNT(*) as total FROM entregas WHERE repartidor_id=? AND fecha=? AND estado='ENTREGADO'",
                     (repartidor_id, hoy)).fetchone()
    entregas_hoy = row["total"]

    # Entregas pendientes
    row = db.execute("SELECT COUNT(*) as total FROM entregas WHERE repartidor_id=? AND estado IN ('PENDIENTE','ASIGNADO','EN CAMINO')",
                     (repartidor_id,)).fetchone()
    pendientes = row["total"]

    # Total entregas (historico)
    row = db.execute("SELECT COUNT(*) as total FROM entregas WHERE repartidor_id=? AND estado='ENTREGADO'",
                     (repartidor_id,)).fetchone()
    total_entregas = row["total"]

    # Monto cobrado hoy
    row = db.execute("SELECT COALESCE(SUM(monto_cobrar),0) as total FROM entregas WHERE repartidor_id=? AND fecha=? AND estado='ENTREGADO'",
                     (repartidor_id, hoy)).fetchone()
    monto_hoy = row["total"]

    db.close()

    return jsonify({
        "ok": True,
        "stats": {
            "entregas_hoy": entregas_hoy,
            "pendientes": pendientes,
            "total_entregas": total_entregas,
            "monto_cobrado_hoy": monto_hoy,
        }
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check."""
    return jsonify({
        "ok": True,
        "servicio": "Farmacias Madrid - API Repartidores",
        "version": "3.0",
        "timestamp": datetime.now().isoformat()
    })


# === MAIN ===
if __name__ == '__main__':
    print("=" * 50)
    print("  FARMACIAS MADRID - API Repartidores")
    print("  Puerto: 5000")
    print("=" * 50)
    print()
    print("Endpoints disponibles:")
    print("  GET  /api/health")
    print("  GET  /api/entregas")
    print("  GET  /api/entregas/<id>")
    print("  POST /api/entregas/<id>/iniciar")
    print("  POST /api/entregas/<id>/completar")
    print("  GET  /api/repartidor/<id>")
    print("  GET  /api/stats/<repartidor_id>")
    print()

    app.run(host='0.0.0.0', port=5000, debug=True)
