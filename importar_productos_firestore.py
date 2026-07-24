"""
FARMACIAS MADRID - Importar productos a Firestore (con fotos)
================================================================
Qué hace:
  1. Sube las ~72 imágenes de imagenes/productos/ a Firebase Storage
     UNA SOLA VEZ cada una (no una por producto - se reutiliza la URL).
  2. Lee los 45,000 productos de farmacia.db
  3. Crea/actualiza cada producto en Firestore (colección "productos")
     con su campo imagen_url apuntando a la foto ya subida.

REQUISITOS (una sola vez):
  pip install firebase-admin --break-system-packages
  Coloca tu firebase_credentials.json en esta misma carpeta
  (Firebase Console > Configuración del proyecto > Cuentas de servicio > Generar nueva clave privada)

USO:
  python3 importar_productos_firestore.py
"""
import os
import sqlite3
import sys

CREDENCIALES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "firebase_credentials.json")
BUCKET_NAME = "farmacias-madrid.firebasestorage.app"  # Ajusta si tu bucket se llama distinto
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagenes", "productos")
LOTE_FIRESTORE = 400  # Firestore permite maximo 500 escrituras por batch, dejamos margen


def conectar_firebase():
    if not os.path.exists(CREDENCIALES_PATH):
        print(f"❌ No encontré {CREDENCIALES_PATH}")
        print("   Ve a Firebase Console > Configuración del proyecto > Cuentas de servicio")
        print("   > Generar nueva clave privada, y guarda el JSON con ese nombre en esta carpeta.")
        sys.exit(1)
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, storage
    except ImportError:
        print("❌ Falta instalar: pip install firebase-admin --break-system-packages")
        sys.exit(1)

    cred = credentials.Certificate(CREDENCIALES_PATH)
    firebase_admin.initialize_app(cred, {"storageBucket": BUCKET_NAME})
    return firestore.client(), storage.bucket()


def subir_imagenes(bucket):
    """Sube cada imagen unica de imagenes/productos/ y regresa {nombre_archivo: url_publica}."""
    if not os.path.exists(IMG_DIR):
        print(f"⚠️  No existe {IMG_DIR}, no se subirán fotos.")
        return {}

    urls = {}
    archivos = [f for f in os.listdir(IMG_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    print(f"\n📸 Subiendo {len(archivos)} imágenes a Firebase Storage...")

    for i, archivo in enumerate(archivos, 1):
        ruta_local = os.path.join(IMG_DIR, archivo)
        destino = f"productos_fotos/{archivo}"
        try:
            blob = bucket.blob(destino)
            blob.upload_from_filename(ruta_local)
            blob.make_public()
            urls[archivo] = blob.public_url
            print(f"  [{i}/{len(archivos)}] ✓ {archivo}")
        except Exception as e:
            print(f"  [{i}/{len(archivos)}] ✗ {archivo}: {e}")

    print(f"✓ {len(urls)} imágenes subidas correctamente.\n")
    return urls


def importar_productos(db, urls_fotos):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""SELECT codigo, nombre, categoria, laboratorio, precio_costo, precio_venta,
                        stock, imagen, precio_oferta, codigo_barras FROM productos""")
    filas = c.fetchall()
    total = len(filas)
    print(f"📦 Importando {total:,} productos a Firestore...")

    batch = db.batch()
    en_lote = 0
    importados = 0
    sin_imagen = 0

    for row in filas:
        codigo, nombre, categoria, laboratorio, precio_costo, precio_venta, stock, imagen_path, precio_oferta, codigo_barras = row

        nombre_archivo = os.path.basename(imagen_path) if imagen_path else None
        imagen_url = urls_fotos.get(nombre_archivo, "")
        if not imagen_url:
            sin_imagen += 1

        doc_ref = db.collection("productos").document(codigo)
        batch.set(doc_ref, {
            "codigo": codigo,
            "nombre": nombre,
            "categoria": categoria,
            "laboratorio": laboratorio,
            "precio_costo": precio_costo,
            "precio_venta": precio_venta,
            "precio_oferta": precio_oferta,
            "stock": stock,
            "codigo_barras": codigo_barras,
            "imagen_url": imagen_url,
        })
        en_lote += 1
        importados += 1

        if en_lote >= LOTE_FIRESTORE:
            batch.commit()
            batch = db.batch()
            en_lote = 0
            print(f"  {importados:,}/{total:,} productos subidos...")

    if en_lote > 0:
        batch.commit()

    print(f"\n✅ {importados:,} productos importados a Firestore.")
    print(f"   {importados - sin_imagen:,} con foto de marca | {sin_imagen:,} sin foto (placeholder o marca no catalogada)")


if __name__ == "__main__":
    print("=" * 60)
    print("  IMPORTAR PRODUCTOS A FIRESTORE - FARMACIAS MADRID")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"❌ No encontré {DB_PATH}. Corre primero INSTALAR.py")
        sys.exit(1)

    db, bucket = conectar_firebase()
    urls_fotos = subir_imagenes(bucket)
    importar_productos(db, urls_fotos)

    print("\n🎉 Listo. Los productos ya están en Firestore con su imagen_url.")
