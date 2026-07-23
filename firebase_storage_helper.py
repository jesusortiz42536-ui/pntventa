"""
FARMACIAS MADRID - Helper de Firebase Storage
Sube imagenes (tarjetas virtuales, fotos) a Firebase Storage y regresa su URL publica,
para poder enviarlas por WhatsApp (Twilio necesita una URL publica, no un archivo local).

CONFIGURACION REQUERIDA (una sola vez):
  1. En Firebase Console > Configuracion del proyecto > Cuentas de servicio
     > Generar nueva clave privada. Descarga el JSON.
  2. Guarda ese archivo como 'firebase_credentials.json' en esta misma carpeta
     (o cambia CREDENCIALES_PATH abajo).
  3. pip install firebase-admin

Si no esta configurado, subir_imagen() regresa None y el resto del sistema
sigue funcionando (solo no se podra enviar la imagen, nada mas el texto).
"""
import os

CREDENCIALES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "firebase_credentials.json")
BUCKET_NAME = "farmacias-madrid.firebasestorage.app"  # Ajustar si tu bucket tiene otro nombre

_app = None
_disponible = None


def _inicializar():
    global _app, _disponible
    if _disponible is not None:
        return _disponible
    if not os.path.exists(CREDENCIALES_PATH):
        print(f"[Storage] No se encontro {CREDENCIALES_PATH}. Sube la imagen manualmente o configura las credenciales.")
        _disponible = False
        return False
    try:
        import firebase_admin
        from firebase_admin import credentials
        cred = credentials.Certificate(CREDENCIALES_PATH)
        _app = firebase_admin.initialize_app(cred, {"storageBucket": BUCKET_NAME})
        _disponible = True
    except ImportError:
        print("[Storage] Falta instalar: pip install firebase-admin")
        _disponible = False
    except Exception as e:
        print(f"[Storage] Error inicializando Firebase: {e}")
        _disponible = False
    return _disponible


def subir_imagen(ruta_local, nombre_remoto):
    """Sube una imagen local a Firebase Storage y regresa su URL publica.
    nombre_remoto: ej. 'tarjetas/SAT-000123.png'
    Regresa None si Firebase Storage no esta configurado o si falla la subida."""
    if not _inicializar():
        return None
    try:
        from firebase_admin import storage
        bucket = storage.bucket()
        blob = bucket.blob(nombre_remoto)
        blob.upload_from_filename(ruta_local)
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"[Storage] Error subiendo {ruta_local}: {e}")
        return None
