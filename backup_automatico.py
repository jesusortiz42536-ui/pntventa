"""
FARMACIAS MADRID - Sistema de Respaldos Automaticos
Crea respaldos ZIP de la base de datos y archivos del sistema.
Limpia respaldos antiguos (max 30).
Opcion de envio por email.
Programacion automatica con schedule.

Uso:
  python backup_automatico.py           # Ejecuta un respaldo inmediato
  python backup_automatico.py --auto    # Inicia programacion automatica
"""

import os
import sys
import zipfile
import shutil
import sqlite3
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# === CONFIGURACION ===
DB_PATH = "farmacia.db"
BACKUP_DIR = "respaldos"
MAX_RESPALDOS = 30
ARCHIVOS_EXTRA = ["SISTEMA.py", "INSTALAR.py", "logo.png"]  # Archivos adicionales a respaldar

# Configuracion email (opcional)
EMAIL_ACTIVO = False
EMAIL_FROM = "tu_correo@gmail.com"
EMAIL_TO = "destino@farmaciasmadrid.com"
EMAIL_SMTP = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_PASSWORD = "tu_app_password"

# Horario de respaldo automatico
HORA_RESPALDO = "23:00"  # 11 PM


def crear_respaldo():
    """Crea un respaldo ZIP de la base de datos y archivos del sistema."""
    print(f"\n{'='*50}")
    print(f"  FARMACIAS MADRID - Respaldo Automatico")
    print(f"{'='*50}")

    # Crear directorio de respaldos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backup_dir = os.path.join(base_dir, BACKUP_DIR)
    os.makedirs(backup_dir, exist_ok=True)

    # Nombre del archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"backup_farmacia_{timestamp}.zip"
    zip_path = os.path.join(backup_dir, zip_name)

    print(f"\nCreando respaldo: {zip_name}")

    archivos_respaldados = []

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Respaldar base de datos
            db_path = os.path.join(base_dir, DB_PATH)
            if os.path.exists(db_path):
                # Crear copia temporal para evitar bloqueos
                db_temp = os.path.join(backup_dir, f"temp_{DB_PATH}")
                try:
                    conn = sqlite3.connect(db_path)
                    backup_conn = sqlite3.connect(db_temp)
                    conn.backup(backup_conn)
                    backup_conn.close()
                    conn.close()
                    zipf.write(db_temp, DB_PATH)
                    os.remove(db_temp)
                    size_db = os.path.getsize(db_path)
                    archivos_respaldados.append((DB_PATH, size_db))
                    print(f"  [OK] {DB_PATH} ({size_db/1024/1024:.1f} MB)")
                except Exception as e:
                    # Fallback: copiar directamente
                    shutil.copy2(db_path, db_temp)
                    zipf.write(db_temp, DB_PATH)
                    os.remove(db_temp)
                    print(f"  [OK] {DB_PATH} (copia directa)")
            else:
                print(f"  [!] {DB_PATH} no encontrado")

            # Respaldar archivos extra
            for archivo in ARCHIVOS_EXTRA:
                ruta = os.path.join(base_dir, archivo)
                if os.path.exists(ruta):
                    zipf.write(ruta, archivo)
                    size_f = os.path.getsize(ruta)
                    archivos_respaldados.append((archivo, size_f))
                    print(f"  [OK] {archivo} ({size_f/1024:.1f} KB)")

            # Respaldar carpeta de tickets si existe
            tickets_dir = os.path.join(base_dir, "tickets")
            if os.path.exists(tickets_dir):
                for f in os.listdir(tickets_dir):
                    fpath = os.path.join(tickets_dir, f)
                    if os.path.isfile(fpath):
                        zipf.write(fpath, os.path.join("tickets", f))
                print(f"  [OK] Carpeta tickets/")

        zip_size = os.path.getsize(zip_path)
        print(f"\nRespaldo creado exitosamente!")
        print(f"  Archivo: {zip_path}")
        print(f"  Tamano: {zip_size/1024/1024:.2f} MB")
        print(f"  Archivos: {len(archivos_respaldados)}")

        # Registrar en BD
        _registrar_respaldo(zip_name, zip_path, zip_size, len(archivos_respaldados))

        # Limpiar respaldos antiguos
        _limpiar_respaldos(backup_dir)

        # Enviar por email si esta activo
        if EMAIL_ACTIVO:
            _enviar_email(zip_path, zip_name)

        return zip_path

    except Exception as e:
        print(f"\n[ERROR] Error creando respaldo: {e}")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        return None


def _registrar_respaldo(nombre, ruta, tamano, num_archivos):
    """Registra el respaldo en la tabla de auditoria."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, DB_PATH)
        conn = sqlite3.connect(db_path)
        # Asegurar tabla auditoria
        conn.execute("""CREATE TABLE IF NOT EXISTS auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER,
            usuario_nombre TEXT, accion TEXT, modulo TEXT, datos TEXT,
            ip TEXT, fecha TEXT, hora TEXT)""")
        ahora = datetime.now()
        conn.execute("INSERT INTO auditoria (usuario_id, usuario_nombre, accion, modulo, datos, ip, fecha, hora) VALUES (?,?,?,?,?,?,?,?)",
                     (0, "SISTEMA", "RESPALDO", "backup",
                      f"Archivo: {nombre}, Tamano: {tamano/1024/1024:.2f}MB, Archivos: {num_archivos}",
                      "local", ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception:
        pass


def _limpiar_respaldos(backup_dir):
    """Elimina respaldos antiguos, mantiene solo los ultimos MAX_RESPALDOS."""
    archivos = []
    for f in os.listdir(backup_dir):
        if f.startswith("backup_farmacia_") and f.endswith(".zip"):
            ruta = os.path.join(backup_dir, f)
            archivos.append((ruta, os.path.getmtime(ruta)))

    archivos.sort(key=lambda x: x[1], reverse=True)

    if len(archivos) > MAX_RESPALDOS:
        eliminados = 0
        for ruta, _ in archivos[MAX_RESPALDOS:]:
            try:
                os.remove(ruta)
                eliminados += 1
            except Exception:
                pass
        if eliminados > 0:
            print(f"\n  Limpieza: {eliminados} respaldos antiguos eliminados (max: {MAX_RESPALDOS})")


def _enviar_email(zip_path, zip_name):
    """Envia el respaldo por email."""
    if not EMAIL_ACTIVO:
        return False

    print(f"\nEnviando respaldo por email a {EMAIL_TO}...")

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = f"Respaldo Farmacias Madrid - {datetime.now().strftime('%d/%m/%Y %H:%M')}"

        # Adjuntar ZIP
        with open(zip_path, 'rb') as f:
            part = MIMEBase('application', 'zip')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{zip_name}"')
            msg.attach(part)

        server = smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"  [OK] Email enviado exitosamente")
        return True

    except Exception as e:
        print(f"  [ERROR] Error enviando email: {e}")
        return False


def programar_respaldos():
    """Programa respaldos automaticos usando schedule."""
    try:
        import schedule
        import time
    except ImportError:
        print("[!] schedule no instalado. Ejecuta: pip install schedule")
        print("    Ejecutando respaldo unico...")
        crear_respaldo()
        return

    print(f"\n{'='*50}")
    print(f"  RESPALDO AUTOMATICO PROGRAMADO")
    print(f"  Hora: {HORA_RESPALDO} diariamente")
    print(f"  Max respaldos: {MAX_RESPALDOS}")
    print(f"  Email: {'ACTIVO' if EMAIL_ACTIVO else 'DESACTIVADO'}")
    print(f"{'='*50}")
    print(f"\nEsperando... (Ctrl+C para detener)\n")

    schedule.every().day.at(HORA_RESPALDO).do(crear_respaldo)

    # Respaldo inmediato al iniciar
    crear_respaldo()

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\nRespaldo automatico detenido.")


def listar_respaldos():
    """Lista todos los respaldos existentes."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backup_dir = os.path.join(base_dir, BACKUP_DIR)

    if not os.path.exists(backup_dir):
        print("No hay respaldos aun.")
        return []

    archivos = []
    for f in sorted(os.listdir(backup_dir), reverse=True):
        if f.startswith("backup_farmacia_") and f.endswith(".zip"):
            ruta = os.path.join(backup_dir, f)
            size = os.path.getsize(ruta)
            fecha = datetime.fromtimestamp(os.path.getmtime(ruta))
            archivos.append({
                "nombre": f,
                "ruta": ruta,
                "tamano": size,
                "fecha": fecha.strftime("%Y-%m-%d %H:%M:%S"),
            })

    print(f"\nRespaldos encontrados: {len(archivos)}")
    print(f"{'='*70}")
    for i, a in enumerate(archivos, 1):
        print(f"  {i}. {a['nombre']}  ({a['tamano']/1024/1024:.2f} MB)  {a['fecha']}")
    print(f"{'='*70}")

    return archivos


# === MAIN ===
if __name__ == "__main__":
    if "--auto" in sys.argv:
        programar_respaldos()
    elif "--listar" in sys.argv:
        listar_respaldos()
    else:
        resultado = crear_respaldo()
        if resultado:
            print(f"\nRespaldo completado: {resultado}")
        else:
            print(f"\nError en el respaldo")
        print()
        listar_respaldos()
