"""
AGREGAR OFERTAS NUEVAS - FARMACIAS MADRID
Agrega los productos y ofertas de las imágenes promocionales
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")

def main():
    print("=" * 60)
    print("  AGREGAR OFERTAS NUEVAS - FARMACIAS MADRID")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Fechas de vigencia (1 mes)
    hoy = datetime.now().strftime('%Y-%m-%d')
    fin = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    # Productos a agregar/actualizar
    productos = [
        # (codigo, nombre, precio_venta, precio_oferta, categoria, laboratorio, imagen)
        ("RYBELSUS14", "RYBELSUS 14MG SEMAGLUTIDA 30 TABLETAS - NOVO NORDISK", 4200.00, 3200.00, "MEDICAMENTOS", "NOVO NORDISK", "imagenes/ofertas/rybelsus_14mg.jpg"),
        ("RYBELSUS7", "RYBELSUS 7MG SEMAGLUTIDA 30 TABLETAS - NOVO NORDISK", 4200.00, 3200.00, "MEDICAMENTOS", "NOVO NORDISK", "imagenes/ofertas/rybelsus_7mg.jpg"),
        ("RYBELSUS3", "RYBELSUS 3MG SEMAGLUTIDA 30 TABLETAS - NOVO NORDISK", 3500.00, 2800.00, "MEDICAMENTOS", "NOVO NORDISK", "imagenes/ofertas/rybelsus_3mg.jpg"),
        ("SAXENDA6", "SAXENDA 6MG/ML LIRAGLUTIDA 3 PLUMAS - NOVO NORDISK", 5500.00, 4500.00, "MEDICAMENTOS", "NOVO NORDISK", "imagenes/ofertas/saxenda_6mg.jpg"),
        ("TACROLIMUS1", "TACROLIMUS 1MG 50 CAPSULAS - VANQUISH", 650.00, 500.00, "MEDICAMENTOS", "VANQUISH", "imagenes/ofertas/tacrolimus_4x2000.jpg"),
        ("APROVASC300", "APROVASC 300MG/10MG 28 TABLETAS - SANOFI", 850.00, 650.00, "MEDICAMENTOS", "SANOFI", "imagenes/ofertas/aprovasc_2x1300.jpg"),
        ("LOXCELL1", "LOXCELL ALBENDAZOL QUINFAMIDA 1 TABLETA - ADULTOS", 65.00, 50.00, "MEDICAMENTOS", "LOXCELL", "imagenes/ofertas/loxcell_4x200.jpg"),
        ("INSULINAGL", "INSULINA GLARGINA 100 UI/ML 10ML - PISA", 280.00, 200.00, "MEDICAMENTOS", "PISA", "imagenes/ofertas/insulina_glargina_4x800.jpg"),
        ("JANUMET50", "JANUMET 50MG/850MG SITAGLIPTINA METFORMINA 56 TAB - MSD", 1200.00, 600.00, "MEDICAMENTOS", "MSD", "imagenes/ofertas/janumet_3cajas_50off.jpg"),
    ]

    print("\n--- AGREGANDO/ACTUALIZANDO PRODUCTOS ---")
    for prod in productos:
        codigo, nombre, precio, precio_of, cat, lab, img = prod

        # Verificar si existe
        c.execute("SELECT id FROM productos WHERE codigo=?", (codigo,))
        existe = c.fetchone()

        if existe:
            c.execute("""UPDATE productos SET nombre=?, precio_venta=?, precio_oferta=?,
                        categoria=?, laboratorio=?, imagen=? WHERE codigo=?""",
                     (nombre, precio, precio_of, cat, lab, img, codigo))
            print(f"  [ACTUALIZADO] {nombre[:50]}")
        else:
            c.execute("""INSERT INTO productos (codigo, nombre, precio_venta, precio_costo, precio_oferta,
                        categoria, laboratorio, stock, imagen)
                        VALUES (?,?,?,?,?,?,?,?,?)""",
                     (codigo, nombre, precio, precio*0.6, precio_of, cat, lab, 100, img))
            print(f"  [NUEVO] {nombre[:50]}")

    # Ofertas especiales (paquetes)
    ofertas = [
        # (nombre, tipo, desc_pct, desc_monto, bonus_sat, productos_aplicables, destacada, color, imagen)
        ("TACROLIMUS 4x$2000", "PAQUETE", 0, 600, 15, "TACROLIMUS1", 1, "#FF5722", "imagenes/ofertas/tacrolimus_4x2000.jpg"),
        ("APROVASC 2x$1300", "PAQUETE", 0, 400, 10, "APROVASC300", 1, "#FF9800", "imagenes/ofertas/aprovasc_2x1300.jpg"),
        ("LOXCELL 4x$200", "PAQUETE", 0, 60, 10, "LOXCELL1", 1, "#4CAF50", "imagenes/ofertas/loxcell_4x200.jpg"),
        ("INSULINA 4x$800", "PAQUETE", 0, 320, 15, "INSULINAGL", 1, "#2196F3", "imagenes/ofertas/insulina_glargina_4x800.jpg"),
        ("JANUMET 3 CAJAS -50%", "DESCUENTO_PORCENTAJE", 50, 0, 20, "JANUMET50", 1, "#9C27B0", "imagenes/ofertas/janumet_3cajas_50off.jpg"),
        ("RYBELSUS 7MG OFERTA", "PRECIO_ESPECIAL", 0, 1000, 15, "RYBELSUS7", 1, "#E91E63", "imagenes/ofertas/rybelsus_7mg.jpg"),
        ("RYBELSUS 14MG OFERTA", "PRECIO_ESPECIAL", 0, 1000, 15, "RYBELSUS14", 1, "#E91E63", "imagenes/ofertas/rybelsus_14mg.jpg"),
        ("SAXENDA GRAN OFERTA", "PRECIO_ESPECIAL", 0, 1000, 20, "SAXENDA6", 1, "#673AB7", "imagenes/ofertas/saxenda_6mg.jpg"),
    ]

    print("\n--- AGREGANDO OFERTAS ESPECIALES ---")
    for oferta in ofertas:
        nombre, tipo, pct, monto, bonus, prods, dest, color, img = oferta

        # Generar folio único
        folio = f"OF{datetime.now().strftime('%Y%m%d%H%M%S')}{ofertas.index(oferta)}"

        # Verificar si existe
        c.execute("SELECT id FROM ofertas WHERE nombre=?", (nombre,))
        existe = c.fetchone()

        if existe:
            c.execute("""UPDATE ofertas SET tipo=?, descuento_porcentaje=?, descuento_monto=?,
                        bonus_saturnos_extra=?, productos_ids=?, destacada=?, color_banner=?,
                        fecha_inicio=?, fecha_fin=?, activa=1 WHERE nombre=?""",
                     (tipo, pct, monto, bonus, prods, dest, color, hoy, fin, nombre))
            print(f"  [ACTUALIZADA] {nombre}")
        else:
            c.execute("""INSERT INTO ofertas (folio, nombre, descripcion, tipo, descuento_porcentaje, descuento_monto,
                        bonus_saturnos_extra, aplica_a, productos_ids, categorias, laboratorios,
                        fecha_inicio, fecha_fin, activa, destacada, color_banner, unidades_vendidas, creado_por, fecha_creacion)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,1,?,?,0,?,?)""",
                     (folio, nombre, f"Oferta especial {nombre}", tipo, pct, monto, bonus, "PRODUCTOS", prods, "", "", hoy, fin, dest, color, "SISTEMA", hoy))
            print(f"  [NUEVA] {nombre}")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("  OFERTAS AGREGADAS CORRECTAMENTE")
    print("=" * 60)

if __name__ == "__main__":
    main()
