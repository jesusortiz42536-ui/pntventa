"""
FARMACIAS MADRID - Servicio WhatsApp Business via Twilio
Envia notificaciones automaticas a clientes via WhatsApp.

Configuracion:
  1. Crear cuenta en Twilio (twilio.com)
  2. Activar WhatsApp Sandbox o Business API
  3. Configurar las variables TWILIO_SID, TWILIO_TOKEN, TWILIO_WHATSAPP_FROM
"""

import sqlite3
import json
from datetime import datetime

# === CONFIGURACION TWILIO ===
# Cambiar estos valores por los de tu cuenta Twilio
TWILIO_SID = "TU_ACCOUNT_SID"
TWILIO_TOKEN = "TU_AUTH_TOKEN"
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"  # Numero Twilio sandbox

# === CONFIGURACION DE MENSAJES ===
MENSAJES_ACTIVOS = {
    "ticket_digital": True,
    "saturnos": True,
    "ofertas": True,
    "delivery": True,
    "recordatorio_credito": True,
}

# Intentar importar twilio
try:
    from twilio.rest import Client
    TWILIO_DISPONIBLE = True
except ImportError:
    TWILIO_DISPONIBLE = False
    print("[WhatsApp] Twilio no instalado. Ejecuta: pip install twilio")


class WhatsAppService:
    def __init__(self, db_path="farmacia.db"):
        self.db_path = db_path
        self.client = None
        if TWILIO_DISPONIBLE and TWILIO_SID != "TU_ACCOUNT_SID":
            try:
                self.client = Client(TWILIO_SID, TWILIO_TOKEN)
                print("[WhatsApp] Servicio conectado a Twilio")
            except Exception as e:
                print(f"[WhatsApp] Error conectando a Twilio: {e}")
        self._ensure_log_table()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _ensure_log_table(self):
        conn = self._get_conn()
        conn.execute("""CREATE TABLE IF NOT EXISTS whatsapp_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefono TEXT,
            tipo_mensaje TEXT,
            contenido TEXT,
            estado TEXT,
            sid_twilio TEXT,
            fecha TEXT,
            hora TEXT
        )""")
        conn.commit()
        conn.close()

    def _log_mensaje(self, telefono, tipo, contenido, estado, sid=""):
        conn = self._get_conn()
        ahora = datetime.now()
        conn.execute("INSERT INTO whatsapp_log (telefono, tipo_mensaje, contenido, estado, sid_twilio, fecha, hora) VALUES (?,?,?,?,?,?,?)",
                     (telefono, tipo, contenido[:500], estado, sid,
                      ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S")))
        conn.commit()
        conn.close()

    def _enviar(self, telefono, mensaje):
        """Envia un mensaje WhatsApp via Twilio."""
        if not self.client:
            self._log_mensaje(telefono, "envio", mensaje, "NO_CONFIGURADO")
            return False

        try:
            to_number = f"whatsapp:+52{telefono}" if not telefono.startswith("whatsapp:") else telefono
            msg = self.client.messages.create(
                body=mensaje,
                from_=TWILIO_WHATSAPP_FROM,
                to=to_number
            )
            self._log_mensaje(telefono, "envio", mensaje, "ENVIADO", msg.sid)
            return True
        except Exception as e:
            self._log_mensaje(telefono, "envio", mensaje, f"ERROR: {str(e)}")
            return False

    # === TEMPLATES DE MENSAJES ===

    def enviar_ticket_digital(self, telefono, folio, total, items_texto, sucursal):
        """Envia ticket digital de compra."""
        if not MENSAJES_ACTIVOS.get("ticket_digital"):
            return False
        mensaje = (
            f"FARMACIAS MADRID - {sucursal}\n"
            f"{'='*30}\n"
            f"TICKET DIGITAL\n"
            f"Folio: {folio}\n"
            f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"{'='*30}\n"
            f"{items_texto}\n"
            f"{'='*30}\n"
            f"TOTAL: ${total:,.2f}\n"
            f"{'='*30}\n"
            f"Gracias por tu compra!\n"
            f"Acumula Saturnos en cada compra"
        )
        return self._enviar(telefono, mensaje)

    def enviar_saturnos(self, telefono, nombre_cliente, saturnos_ganados, saldo_total):
        """Notifica saturnos ganados."""
        if not MENSAJES_ACTIVOS.get("saturnos"):
            return False
        mensaje = (
            f"FARMACIAS MADRID - Monedero Saturnos\n"
            f"{'='*30}\n"
            f"Hola {nombre_cliente}!\n\n"
            f"Ganaste *{saturnos_ganados:,.0f} Saturnos* en tu compra\n\n"
            f"Tu saldo actual: *{saldo_total:,.0f} Saturnos*\n\n"
            f"Acumula mas en tu proxima visita!"
        )
        return self._enviar(telefono, mensaje)

    def enviar_oferta(self, telefono, nombre_oferta, descripcion, descuento, fecha_fin):
        """Envia notificacion de oferta."""
        if not MENSAJES_ACTIVOS.get("ofertas"):
            return False
        mensaje = (
            f"FARMACIAS MADRID - OFERTA ESPECIAL!\n"
            f"{'='*30}\n"
            f"*{nombre_oferta}*\n"
            f"{descripcion}\n\n"
            f"Descuento: *{descuento}*\n"
            f"Valido hasta: {fecha_fin}\n\n"
            f"Visitanos en cualquiera de nuestras 5 sucursales!"
        )
        return self._enviar(telefono, mensaje)

    def enviar_delivery(self, telefono, folio, repartidor, estado, hora_estimada=""):
        """Notifica estado de entrega a domicilio."""
        if not MENSAJES_ACTIVOS.get("delivery"):
            return False

        estados_msg = {
            "ASIGNADO": f"Tu pedido {folio} ha sido asignado al repartidor {repartidor}.",
            "EN_CAMINO": f"Tu pedido {folio} va en camino! Repartidor: {repartidor}.",
            "ENTREGADO": f"Tu pedido {folio} ha sido entregado. Gracias por tu compra!",
        }
        texto_estado = estados_msg.get(estado, f"Tu pedido {folio} esta en estado: {estado}")

        mensaje = (
            f"FARMACIAS MADRID - Delivery\n"
            f"{'='*30}\n"
            f"{texto_estado}\n"
        )
        if hora_estimada:
            mensaje += f"Hora estimada: {hora_estimada}\n"
        mensaje += "\nGracias por tu preferencia!"

        return self._enviar(telefono, mensaje)

    def enviar_recordatorio_credito(self, telefono, nombre_cliente, folio_credito, monto_pendiente, fecha_vencimiento):
        """Recordatorio de pago de credito."""
        if not MENSAJES_ACTIVOS.get("recordatorio_credito"):
            return False
        mensaje = (
            f"FARMACIAS MADRID - Recordatorio\n"
            f"{'='*30}\n"
            f"Hola {nombre_cliente},\n\n"
            f"Te recordamos que tu credito {folio_credito} tiene un saldo pendiente de *${monto_pendiente:,.2f}*\n\n"
            f"Fecha de vencimiento: {fecha_vencimiento}\n\n"
            f"Realiza tu pago en cualquiera de nuestras sucursales.\n"
            f"Gracias!"
        )
        return self._enviar(telefono, mensaje)

    def enviar_masivo_ofertas(self):
        """Envia ofertas activas a todos los clientes con telefono."""
        conn = self._get_conn()
        cursor = conn.cursor()

        hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""SELECT nombre, tipo, descuento_porcentaje, descuento_monto, fecha_fin
                         FROM ofertas WHERE activa=1 AND destacada=1 AND fecha_inicio<=? AND fecha_fin>=?""",
                       (hoy, hoy))
        ofertas = cursor.fetchall()

        if not ofertas:
            conn.close()
            return 0

        cursor.execute("SELECT telefono FROM clientes WHERE telefono!='' AND telefono IS NOT NULL AND id>1")
        clientes = cursor.fetchall()
        conn.close()

        enviados = 0
        for tel_row in clientes:
            tel = tel_row[0]
            if not tel or len(tel) < 10:
                continue
            for of in ofertas:
                nombre, tipo, pct, monto, fin = of
                if tipo == "DESCUENTO_PORCENTAJE":
                    desc = f"-{pct:.0f}%"
                elif tipo == "2X1":
                    desc = "2x1"
                elif tipo == "3X2":
                    desc = "3x2"
                else:
                    desc = f"${monto:.0f} OFF"
                if self.enviar_oferta(tel, nombre, "", desc, fin):
                    enviados += 1
        return enviados

    def obtener_log(self, limite=50):
        """Obtiene el log de mensajes enviados."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM whatsapp_log ORDER BY id DESC LIMIT ?", (limite,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def obtener_estadisticas(self):
        """Estadisticas de mensajes."""
        conn = self._get_conn()
        cursor = conn.cursor()
        hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM whatsapp_log WHERE fecha=? AND estado='ENVIADO'", (hoy,))
        enviados_hoy = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM whatsapp_log WHERE estado='ENVIADO'")
        total_enviados = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM whatsapp_log WHERE estado LIKE 'ERROR%'")
        total_errores = cursor.fetchone()[0]
        conn.close()
        return {
            "enviados_hoy": enviados_hoy,
            "total_enviados": total_enviados,
            "total_errores": total_errores,
        }


# === USO STANDALONE ===
if __name__ == "__main__":
    print("=" * 50)
    print("  FARMACIAS MADRID - WhatsApp Service")
    print("=" * 50)

    ws = WhatsAppService()

    if not TWILIO_DISPONIBLE:
        print("\n[!] Twilio no instalado.")
        print("    Ejecuta: pip install twilio")
        print("    Luego configura TWILIO_SID y TWILIO_TOKEN")
    elif TWILIO_SID == "TU_ACCOUNT_SID":
        print("\n[!] Configura tus credenciales de Twilio:")
        print("    TWILIO_SID = 'tu_account_sid'")
        print("    TWILIO_TOKEN = 'tu_auth_token'")
        print("    TWILIO_WHATSAPP_FROM = 'whatsapp:+1...'")
    else:
        print("\n[OK] Servicio WhatsApp listo")

    stats = ws.obtener_estadisticas()
    print(f"\nEstadisticas:")
    print(f"  Enviados hoy: {stats['enviados_hoy']}")
    print(f"  Total enviados: {stats['total_enviados']}")
    print(f"  Total errores: {stats['total_errores']}")

    print("\nMensajes activos:")
    for tipo, activo in MENSAJES_ACTIVOS.items():
        estado = "ACTIVO" if activo else "DESACTIVADO"
        print(f"  {tipo}: {estado}")

    print("\n" + "=" * 50)
