"""
Crea imágenes de muestra del sistema basadas en el diseño real
"""
from PIL import Image, ImageDraw, ImageFont
import os

base = os.path.dirname(os.path.abspath(__file__))
capturas_dir = os.path.join(base, "presentacion", "capturas")
os.makedirs(capturas_dir, exist_ok=True)

def crear_captura_sistema(nombre, titulo, color_header, elementos, color_menu="#1A237E"):
    """Crea una captura simulada del sistema"""
    W, H = 800, 500
    img = Image.new('RGB', (W, H), '#F5F5F5')
    draw = ImageDraw.Draw(img)

    try:
        font_header = ImageFont.truetype("segoeuib.ttf", 18)
        font_titulo = ImageFont.truetype("segoeuib.ttf", 22)
        font_menu = ImageFont.truetype("segoeui.ttf", 12)
        font_content = ImageFont.truetype("segoeui.ttf", 14)
        font_small = ImageFont.truetype("segoeui.ttf", 11)
    except:
        font_header = font_titulo = font_menu = font_content = font_small = ImageFont.load_default()

    # Header del sistema
    draw.rectangle([0, 0, W, 40], fill="#1A237E")
    draw.text((50, 20), "FARMACIAS MADRID", fill='white', font=font_header, anchor='lm')

    # Menú superior
    menu_items = ["Dashboard", "Ventas", "Inventario", "Clientes", "Reportes", "Saturnos", "Ofertas"]
    x_menu = 200
    for item in menu_items:
        draw.text((x_menu, 20), item, fill='#90CAF9', font=font_small, anchor='lm')
        x_menu += 80

    # Menú lateral
    menu_lateral = [
        ("DASHBOARD", "#1565C0"),
        ("VENTAS", "#D32F2F"),
        ("DOMICILIO", "#FF9800"),
        ("INVENTARIO", "#4CAF50"),
        ("OFERTAS", "#FF5722"),
        ("CLIENTES", "#3F51B5"),
        ("ABONOS", "#607D8B"),
        ("SATURNOS", "#FFC107"),
        ("CARGO-GO", "#37474F"),
        ("COMPRAS", "#E91E63"),
        ("FINANZAS", "#9C27B0"),
        ("REPORTES", "#00796B"),
        ("CREDITOS", "#FF5722"),
        ("CAJA", "#FFEB3B"),
        ("ALERTAS", "#F44336"),
    ]

    y_menu = 50
    for item, color in menu_lateral:
        draw.rectangle([0, y_menu, 110, y_menu + 28], fill=color)
        draw.text((10, y_menu + 14), item, fill='white', font=font_small, anchor='lm')
        y_menu += 30

    # Área de contenido
    draw.rectangle([120, 50, W-10, 90], fill=color_header)
    draw.text((130, 70), titulo, fill='white', font=font_titulo, anchor='lm')

    # Contenido específico del módulo
    y_content = 110
    for elem in elementos:
        if elem.startswith("BOX:"):
            # Dibujar caja de estadística
            parts = elem.split("|")
            valor = parts[1] if len(parts) > 1 else ""
            label = parts[2] if len(parts) > 2 else ""
            x_box = int(parts[3]) if len(parts) > 3 else 140
            draw.rounded_rectangle([x_box, y_content, x_box + 120, y_content + 70], radius=5, fill='white', outline='#E0E0E0')
            draw.text((x_box + 60, y_content + 25), valor, fill='#1E88E5', font=font_titulo, anchor='mm')
            draw.text((x_box + 60, y_content + 55), label, fill='#666666', font=font_small, anchor='mm')
        elif elem.startswith("TABLE:"):
            # Dibujar encabezado de tabla
            cols = elem.replace("TABLE:", "").split("|")
            x_col = 140
            draw.rectangle([130, y_content, W-20, y_content + 25], fill='#E3F2FD')
            for col in cols:
                draw.text((x_col, y_content + 12), col, fill='#333333', font=font_small, anchor='lm')
                x_col += 100
            y_content += 30
        elif elem.startswith("ROW:"):
            # Dibujar fila de tabla
            cols = elem.replace("ROW:", "").split("|")
            x_col = 140
            for col in cols:
                draw.text((x_col, y_content + 10), col, fill='#666666', font=font_small, anchor='lm')
                x_col += 100
            y_content += 25
        elif elem.startswith("BUTTON:"):
            # Dibujar botón
            parts = elem.split("|")
            texto = parts[1] if len(parts) > 1 else "Botón"
            color_btn = parts[2] if len(parts) > 2 else "#1E88E5"
            x_btn = int(parts[3]) if len(parts) > 3 else 140
            draw.rounded_rectangle([x_btn, y_content, x_btn + 120, y_content + 35], radius=5, fill=color_btn)
            draw.text((x_btn + 60, y_content + 17), texto, fill='white', font=font_content, anchor='mm')
        elif elem.startswith("ALERT:"):
            # Dibujar alerta/oferta
            parts = elem.split("|")
            texto = parts[1] if len(parts) > 1 else ""
            color_alert = parts[2] if len(parts) > 2 else "#FF5722"
            draw.rounded_rectangle([130, y_content, W-20, y_content + 30], radius=5, fill=color_alert)
            draw.text((140, y_content + 15), texto, fill='white', font=font_content, anchor='lm')
            y_content += 35
        elif elem.startswith("CARD:"):
            # Dibujar tarjeta de nivel
            parts = elem.split("|")
            nivel = parts[1] if len(parts) > 1 else "AZUL"
            x_card = int(parts[2]) if len(parts) > 2 else 140
            colores_nivel = {"AZUL": "#1E88E5", "DORADA": "#FFC107", "NEGRA": "#212121"}
            color_card = colores_nivel.get(nivel, "#1E88E5")
            draw.rounded_rectangle([x_card, y_content, x_card + 100, y_content + 130], radius=10, fill=color_card)
            draw.text((x_card + 50, y_content + 30), nivel, fill='white', font=font_content, anchor='mm')
            draw.text((x_card + 50, y_content + 55), "+5%" if nivel == "AZUL" else "+10%" if nivel == "DORADA" else "+15%", fill='white', font=font_small, anchor='mm')
        else:
            # Texto simple
            draw.text((140, y_content), elem, fill='#333333', font=font_content, anchor='lm')
            y_content += 25

    # Guardar
    output_path = os.path.join(capturas_dir, f"{nombre}.png")
    img.save(output_path)
    print(f"✓ Creada: {output_path}")
    return output_path

# Crear todas las capturas
print("\n" + "="*50)
print("  CREANDO CAPTURAS DEL SISTEMA")
print("="*50 + "\n")

# Dashboard
crear_captura_sistema("dashboard", "DASHBOARD EJECUTIVO", "#1565C0", [
    "BOX:|$180.38|VENTAS HOY|140",
    "BOX:|1|TICKETS HOY|270",
    "BOX:|0|SATURNOS HOY|400",
    "BOX:|$180.38|VENTAS MES|530",
    "",
    "",
    "",
    "META MENSUAL: $180.38 / $500,000.00 (0.0%)",
    "",
    "ALERT:TACROLIMUS 4x$2000 PAQUETE (hasta 2026-03-07)|#FF5722",
    "ALERT:APROVASC 2x$1300 PAQUETE (hasta 2026-03-07)|#FF9800",
    "ALERT:LOXCELL 4x$200 PAQUETE (hasta 2026-03-07)|#4CAF50",
])

# Punto de Venta
crear_captura_sistema("ventas", "PUNTO DE VENTA", "#D32F2F", [
    "ALERT:OFERTA: RYBELSUS 14MG OFERTA PRECIO_ESPECIAL + 15%|#FFC107",
    "",
    "Folio: V20260205174723    Vendedor: ADMIN",
    "",
    "Escanea un producto...",
    "Normal: $0.00    Oferta (35%): $0.00",
    "Ganas: 0 Saturnos",
    "",
    "TABLE:CÓDIGO|DESCRIPCIÓN|PRECIO|OFERTA|CANT|SUBTOTAL",
    "",
    "BUTTON:+ 1|#4CAF50|500",
    "BUTTON:- 1|#FF9800|630",
    "",
    "ALERT:ABONAR A CRÉDITO - ¿El cliente tiene crédito pendiente?|#607D8B",
])

# Monedero Saturnos
crear_captura_sistema("saturnos", "MONEDERO ELECTRÓNICO SATURNOS", "#FFC107", [
    "Generar Tarjeta Saturnos",
    "",
    "Cliente: Juan Gomez",
    "",
    "SELECCIONA NIVEL:",
    "",
    "CARD:AZUL|150",
    "CARD:DORADA|270",
    "CARD:NEGRA|390",
    "",
    "",
    "",
    "",
    "",
    "BUTTON:GENERAR TARJETA|#FFC107|300",
])

# Sistema de Créditos
crear_captura_sistema("creditos", "SISTEMA DE CRÉDITOS", "#FF5722", [
    "Solicitudes    Créditos Activos    Pagos    Configuración",
    "",
    "BUTTON:+ NUEVA SOLICITUD|#4CAF50|140",
    "",
    "TABLE:FOLIO|CLIENTE|TIPO|MONTO|PLAZO|FECHA|DOCS|ESTADO",
    "",
    "",
    "",
    "",
    "",
    "BUTTON:APROBAR|#4CAF50|140",
    "BUTTON:RECHAZAR|#F44336|280",
])

# Inventario
crear_captura_sistema("inventario", "INVENTARIO - CON IMÁGENES", "#4CAF50", [
    "Buscar:                    Categoría: TODAS",
    "",
    "BUTTON:IMPORTAR EXCEL|#FF5722|140",
    "BUTTON:EXPORTAR EXCEL|#4CAF50|280",
    "",
    "Vista: ○ Lista  ○ Tarjetas",
    "",
    "45,060 productos listos para exportar",
    "",
    "TABLE:CÓDIGO|NOMBRE|CATEGORÍA|STOCK|PRECIO",
])

# Ofertas
crear_captura_sistema("ofertas", "OFERTAS Y PROMOCIONES", "#FF5722", [
    "BUTTON:+ NUEVA OFERTA|#4CAF50|140",
    "",
    "OFERTAS ACTIVAS:",
    "",
    "ALERT:TACROLIMUS 4x$2000 - PAQUETE - Ahorro $600|#FF5722",
    "ALERT:APROVASC 2x$1300 - PAQUETE - Ahorro $400|#FF9800",
    "ALERT:LOXCELL 4x$200 - PAQUETE - Ahorro $60|#4CAF50",
    "ALERT:RYBELSUS 14MG OFERTA - PRECIO ESPECIAL|#E91E63",
    "ALERT:SAXENDA GRAN OFERTA - +20 Saturnos Bonus|#673AB7",
])

# Finanzas
crear_captura_sistema("finanzas", "FINANZAS Y REPORTES", "#9C27B0", [
    "BUTTON:Ventas del día|#1E88E5|140",
    "BUTTON:Ventas del mes|#4CAF50|280",
    "BUTTON:Top 10 productos|#FF9800|420",
    "BUTTON:Exportar CSV|#607D8B|560",
    "",
    "VENTAS DEL DIA - 2026-02-05",
    "",
    "TABLE:FOLIO|HORA|VENDEDOR|TOTAL|PAGO",
    "ROW:V20260205150914|15:09:14|ADMIN|$180.38|EFECTIVO",
    "",
    "",
    "Total del día: $180.38  |  Ventas: 1  |  Efectivo: $180.38  |  Tarjeta: $0.00",
])

# Corte de Caja
crear_captura_sistema("caja", "CORTE DE CAJA", "#FFEB3B", [
    "APERTURA DE CAJA",
    "Fecha: 2026-02-05    Cajero: ADMIN",
    "Monto inicial en caja: 0.00",
    "",
    "RESUMEN DE VENTAS DEL DIA",
    "Número de ventas: 1",
    "Total ventas: $180.38",
    "Efectivo: $180.38",
    "Tarjeta: $0.00",
    "",
    "BUTTON:GUARDAR CORTE|#1E88E5|300",
    "BUTTON:IMPRIMIR CORTE|#4CAF50|450",
])

# Alertas de Stock
crear_captura_sistema("alertas", "ALERTAS DE STOCK", "#F44336", [
    "BUTTON:Stock bajo|#F44336|140",
    "BUTTON:Por caducar|#FF9800|280",
    "BUTTON:Generar orden|#4CAF50|420",
    "",
    "PRODUCTOS CON STOCK BAJO (< 10 unidades)",
    "",
    "TABLE:CÓDIGO|PRODUCTO|CATEGORÍA|STOCK|PRECIO",
    "ROW:ESP000003|HUMIRA 40MG|ESPECIALIDAD|5|$18,500",
    "ROW:ESP000011|HERCEPTIN|ESPECIALIDAD|5|$32,000",
    "ROW:ESP000013|KEYTRUDA|ESPECIALIDAD|5|$85,000",
    "",
    "Total productos con stock bajo: 49",
])

# E-Commerce
crear_captura_sistema("ecommerce", "E-COMMERCE - AMAZON & MERCADO LIBRE", "#FF5722", [
    "Exporta tus productos para vender en Amazon y Mercado Libre",
    "",
    "EXPORTAR CATÁLOGO",
    "Filtrar productos a exportar:",
    "Categoría: TODAS    Stock mínimo: 1",
    "",
    "45,060 productos listos para exportar",
    "",
    "BUTTON:AMAZON|#FF9800|140",
    "BUTTON:MERCADO LIBRE|#FFE600|280",
    "BUTTON:EXCEL|#4CAF50|420",
    "",
    "PEDIDOS ONLINE",
    "TABLE:ID|PLATAFORMA|PEDIDO|FECHA|CLIENTE|TOTAL|ESTADO",
])

# Clientes
crear_captura_sistema("clientes", "CLIENTES", "#3F51B5", [
    "BUTTON:+ NUEVO CLIENTE|#4CAF50|140",
    "",
    "TABLE:ID|NOMBRE|TELÉFONO|DIRECCIÓN",
    "ROW:1|PUBLICO GENERAL||",
    "ROW:2|Juan Gomez|7751234567|Calle Principal 123",
    "ROW:3|Maria Lopez|7759876543|Av Juarez 456",
    "ROW:5|JESUS ORTIZ ORTIZ|7753200224|LAZARO CARDENAS 109",
])

# Traspasos
crear_captura_sistema("traspasos", "TRASPASOS ENTRE FARMACIAS", "#3F51B5", [
    "BUTTON:+ NUEVO TRASPASO|#4CAF50|140",
    "",
    "Sucursal: TODAS    Desde: 2026-01-06    Hasta: 2026-02-05",
    "",
    "TRASPASOS PENDIENTES",
    "TABLE:FOLIO|FECHA|ORIGEN|DESTINO|MOTIVO|PRODUCTOS|ESTADO",
    "",
    "BUTTON:CONFIRMAR|#FF5722|140",
    "BUTTON:COMPLETAR|#4CAF50|280",
    "BUTTON:CANCELAR|#F44336|420",
    "",
    "HISTORIAL DE TRASPASOS",
    "TABLE:FOLIO|FECHA|ORIGEN|DESTINO|MOTIVO|PRODUCTOS|ESTADO|CONFIRMÓ",
])

# Domicilio
crear_captura_sistema("domicilio", "SERVICIO A DOMICILIO", "#FF9800", [
    "BUTTON:+ NUEVA ENTREGA|#4CAF50|600",
    "",
    "ENTREGAS ACTIVAS",
    "TABLE:ID|CLIENTE|DIRECCIÓN|REPARTIDOR|MOTO|ESTADO|HORA SAL.",
    "",
    "BUTTON:ENVIAR|#1E88E5|140",
    "BUTTON:ENTREGADO|#4CAF50|280",
    "BUTTON:CANCELAR|#F44336|420",
    "",
    "HISTORIAL DE HOY",
    "Fecha: 2026-02-05    Repartidor: TODOS",
    "TABLE:ID|CLIENTE|TOTAL|REPARTIDOR|MOTO|ESTADO|HORA SAL.|HORA LLEG.",
])

print("\n" + "="*50)
print("  CAPTURAS CREADAS EXITOSAMENTE")
print(f"  Ubicación: {capturas_dir}")
print("="*50)
print("\nAhora ejecuta: python crear_presentacion.py")
