"""
Script para crear presentación promocional del Sistema POS
"""
import os
import sys
from datetime import datetime

# Intentar importar las librerías necesarias
try:
    from PIL import Image, ImageDraw, ImageFont, ImageGrab
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
except ImportError as e:
    print(f"Instalando dependencias necesarias...")
    os.system("pip install pillow reportlab pyautogui")
    from PIL import Image, ImageDraw, ImageFont, ImageGrab
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor

def crear_imagen_modulo(modulo, elementos, color_principal, output_path):
    """Crea una imagen profesional de módulo con fondo de agua"""
    import math
    W, H = 500, 350
    img = Image.new('RGB', (W, H), '#E3F2FD')
    draw = ImageDraw.Draw(img)

    # Fondo degradado azul agua
    for y in range(H):
        factor = y / H
        r = int(227 - factor * 30)
        g = int(242 - factor * 20)
        b = int(253 - factor * 10)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Ondas de agua decorativas
    for wave in range(3):
        offset_y = 280 + wave * 25
        for x in range(W):
            y = offset_y + int(8 * math.sin(x / 30 + wave))
            alpha = 100 - wave * 30
            draw.ellipse([x-2, y-2, x+2, y+2], fill=(255, 255, 255))

    try:
        font_titulo = ImageFont.truetype("segoeuib.ttf", 24)
        font_item = ImageFont.truetype("segoeui.ttf", 14)
        font_icon = ImageFont.truetype("segoeuib.ttf", 40)
    except:
        font_titulo = font_item = font_icon = ImageFont.load_default()

    # Header con color del módulo
    draw.rounded_rectangle([0, 0, W, 60], radius=0, fill=color_principal)
    draw.text((W//2, 30), modulo, fill='white', font=font_titulo, anchor='mm')

    # Marco de "pantalla"
    draw.rounded_rectangle([20, 80, W-20, H-40], radius=15, fill='white', outline='#BBDEFB', width=2)

    # Sombra sutil
    draw.rounded_rectangle([25, 85, W-15, H-35], radius=15, outline='#90CAF9', width=1)

    # Elementos del módulo
    y_pos = 110
    for i, elem in enumerate(elementos[:6]):
        # Icono circular
        draw.ellipse([40, y_pos-8, 56, y_pos+8], fill=color_principal)
        draw.text((48, y_pos), "✓", fill='white', font=font_item, anchor='mm')
        # Texto
        draw.text((70, y_pos), elem, fill='#333333', font=font_item, anchor='lm')
        y_pos += 32

    # Borde decorativo inferior
    draw.rectangle([0, H-8, W, H], fill=color_principal)

    img.save(output_path)
    return output_path

def crear_imagen_feature(titulo, descripcion, color, numero, output_path):
    """Crea una imagen para una característica"""
    W, H = 800, 200
    img = Image.new('RGB', (W, H), 'white')
    draw = ImageDraw.Draw(img)

    # Barra lateral de color
    draw.rectangle([0, 0, 15, H], fill=color)

    # Número grande
    try:
        font_num = ImageFont.truetype("segoeuib.ttf", 60)
        font_titulo = ImageFont.truetype("segoeuib.ttf", 28)
        font_desc = ImageFont.truetype("segoeui.ttf", 16)
    except:
        font_num = font_titulo = font_desc = ImageFont.load_default()

    # Círculo con número
    draw.ellipse([30, 70, 110, 150], fill=color)
    draw.text((70, 110), str(numero), fill='white', font=font_num, anchor='mm')

    # Título
    draw.text((130, 85), titulo, fill='#333333', font=font_titulo, anchor='lm')

    # Descripción
    draw.text((130, 130), descripcion, fill='#666666', font=font_desc, anchor='lm')

    img.save(output_path)
    return output_path

def dibujar_fondo_agua(c, width, height):
    """Dibuja fondo degradado azul agua en la página"""
    for i in range(100):
        factor = i / 100
        r = int(227 - factor * 40)
        g = int(242 - factor * 30)
        b = int(253 - factor * 20)
        c.setFillColorRGB(r/255, g/255, b/255)
        c.rect(0, height - (i * height/100), width, height/100 + 1, fill=True, stroke=False)

def crear_pdf_presentacion():
    """Crea el PDF de presentación"""

    base = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base, "presentacion")
    capturas_dir = os.path.join(output_dir, "capturas")
    os.makedirs(output_dir, exist_ok=True)

    # Usar capturas reales del sistema
    print("Cargando capturas reales del sistema...")
    img_dashboard = os.path.join(capturas_dir, "dashboard.png")
    img_ventas = os.path.join(capturas_dir, "ventas.png")
    img_monedero = os.path.join(capturas_dir, "saturnos.png")
    img_inventario = os.path.join(capturas_dir, "inventario.png")
    img_ofertas = os.path.join(capturas_dir, "ofertas.png")
    img_clientes = os.path.join(capturas_dir, "clientes.png")
    img_domicilio = os.path.join(capturas_dir, "domicilio.png")
    img_traspasos = os.path.join(capturas_dir, "traspasos.png")
    img_creditos = os.path.join(capturas_dir, "creditos.png")
    img_finanzas = os.path.join(capturas_dir, "finanzas.png")
    img_caja = os.path.join(capturas_dir, "caja.png")
    img_alertas = os.path.join(capturas_dir, "alertas.png")
    img_ecommerce = os.path.join(capturas_dir, "ecommerce.png")
    img_compras = os.path.join(capturas_dir, "compras.png")
    img_usuarios = os.path.join(capturas_dir, "usuarios.png")
    img_vales = os.path.join(capturas_dir, "vales.png")
    img_abonos = os.path.join(capturas_dir, "abonos.png")
    img_tarjeta_azul = os.path.join(capturas_dir, "tarjeta_azul.png")
    img_tarjeta_dorada = os.path.join(capturas_dir, "tarjeta_dorada.png")
    img_tarjeta_negra = os.path.join(capturas_dir, "tarjeta_negra.png")

    pdf_path = os.path.join(output_dir, "PUNTO_DE_VENTA_FARMACIA_MONEDERO_ELECTRONICO.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # ========== PÁGINA 1: PORTADA ==========
    # Fondo degradado (simulado con rectángulos)
    for i in range(100):
        factor = i / 100
        r = int(30 + factor * 20)
        g = int(136 + factor * 30)
        b = int(229 - factor * 50)
        c.setFillColorRGB(r/255, g/255, b/255)
        c.rect(0, height - (i * height/100), width, height/100, fill=True, stroke=False)

    # Logo/Título principal
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 42)
    c.drawCentredString(width/2, height - 180, "PUNTO DE VENTA")
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2, height - 225, "CON MONEDERO ELECTRÓNICO")

    c.setFont("Helvetica", 20)
    c.drawCentredString(width/2, height - 270, "Sistema Profesional para Farmacias")

    # Línea decorativa
    c.setStrokeColor(HexColor('#FFD700'))
    c.setLineWidth(3)
    c.line(width/2 - 100, height - 280, width/2 + 100, height - 280)

    # Subtítulo
    c.setFillColor(HexColor('#90CAF9'))
    c.setFont("Helvetica-Oblique", 18)
    c.drawCentredString(width/2, height - 320, "Para Farmacias y Comercios")

    # Características destacadas en la portada
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica", 14)
    # DESTACADO: CATÁLOGO PRECARGADO
    c.setFillColor(HexColor('#FFD700'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 380, "+45,000 PRODUCTOS")
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 405, "YA PRECARGADOS")

    features_portada = [
        "Sistema de lealtad con tarjetas premium",
        "Sistema de créditos integrado",
        "Tickets por WhatsApp - SIN PAPEL",
        "Multi-sucursal y E-Commerce"
    ]
    y_pos = height - 460
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica", 14)
    for feat in features_portada:
        c.drawCentredString(width/2, y_pos, f"• {feat}")
        y_pos -= 25

    # Contacto
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, 100, "DEMO GRATIS 15 MINUTOS")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, 75, "WhatsApp: 775-320-0224")

    c.showPage()

    # ========== PÁGINA 2: DASHBOARD PRINCIPAL ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#1565C0'))
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 40, "DASHBOARD EJECUTIVO")

    # Captura real del dashboard
    try:
        if os.path.exists(img_dashboard):
            c.drawImage(img_dashboard, 30, 80, width=width-60, height=height-180, preserveAspectRatio=True)
    except Exception as e:
        print(f"Error cargando dashboard: {e}")

    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 50, "Vista general con ventas del día, ofertas activas y accesos rápidos")

    c.showPage()

    # ========== PÁGINA 3: PUNTO DE VENTA ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#D32F2F'))
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 40, "PUNTO DE VENTA")

    # Captura real del punto de venta
    try:
        if os.path.exists(img_ventas):
            c.drawImage(img_ventas, 30, 80, width=width-60, height=height-180, preserveAspectRatio=True)
    except Exception as e:
        print(f"Error cargando ventas: {e}")

    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 50, "Cobro rápido • Búsqueda inteligente • Múltiples pagos • Descuentos automáticos")

    c.showPage()

    # ========== PÁGINA 4: MONEDERO SATURNOS ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#FFC107'))
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 40, "MONEDERO ELECTRÓNICO SATURNOS")

    # Captura real del monedero
    try:
        if os.path.exists(img_monedero):
            c.drawImage(img_monedero, 30, 80, width=width-60, height=height-180, preserveAspectRatio=True)
    except Exception as e:
        print(f"Error cargando saturnos: {e}")

    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 50, "3 niveles de membresía: AZUL, DORADA y NEGRA • Tarjetas personalizadas con foto")

    c.showPage()

    # ========== PÁGINA 5: TARJETAS PREMIUM ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#9C27B0'))
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 40, "TARJETAS PREMIUM SATURNOS")

    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height - 80, "3 Niveles de membresía con beneficios exclusivos")

    # Tarjeta AZUL
    try:
        if os.path.exists(img_tarjeta_azul):
            c.drawImage(img_tarjeta_azul, 20, height - 450, width=180, height=330, preserveAspectRatio=True)
            c.setFillColor(HexColor('#1E88E5'))
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(110, height - 470, "NIVEL AZUL +5%")
    except:
        pass

    # Tarjeta DORADA
    try:
        if os.path.exists(img_tarjeta_dorada):
            c.drawImage(img_tarjeta_dorada, 205, height - 450, width=180, height=330, preserveAspectRatio=True)
            c.setFillColor(HexColor('#FFC107'))
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(295, height - 470, "NIVEL DORADA +10%")
    except:
        pass

    # Tarjeta NEGRA
    try:
        if os.path.exists(img_tarjeta_negra):
            c.drawImage(img_tarjeta_negra, 390, height - 450, width=180, height=330, preserveAspectRatio=True)
            c.setFillColor(HexColor('#212121'))
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(480, height - 470, "NIVEL NEGRA +15%")
    except:
        pass

    c.setFillColor(HexColor('#FF5722'))
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width/2, 60, "Envío por WhatsApp • Impresión física de alta calidad")
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 40, "Diseño personalizado por $1,500 adicionales")

    c.showPage()

    # ========== PÁGINA 6: INVENTARIO ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#4CAF50'))
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 40, "INVENTARIO CON IMÁGENES")

    # Captura real del inventario
    try:
        if os.path.exists(img_inventario):
            c.drawImage(img_inventario, 30, 80, width=width-60, height=height-180, preserveAspectRatio=True)
    except Exception as e:
        print(f"Error cargando inventario: {e}")

    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 50, "Stock en tiempo real • Importar/Exportar Excel • Alertas de bajo stock")

    c.showPage()

    # ========== PÁGINA 7: OFERTAS ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#FF5722'))
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 40, "OFERTAS Y PROMOCIONES")

    # Captura real de ofertas
    try:
        if os.path.exists(img_ofertas):
            c.drawImage(img_ofertas, 30, 80, width=width-60, height=height-180, preserveAspectRatio=True)
    except Exception as e:
        print(f"Error cargando ofertas: {e}")

    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 50, "Paquetes especiales • Descuentos • Bonus Saturnos • Control de vigencia")

    c.showPage()

    # ========== PÁGINA 8: E-COMMERCE ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#FF5722'))
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 40, "E-COMMERCE: AMAZON Y MERCADOLIBRE")

    # Captura real de e-commerce
    try:
        if os.path.exists(img_ecommerce):
            c.drawImage(img_ecommerce, 30, 80, width=width-60, height=height-180, preserveAspectRatio=True)
    except Exception as e:
        print(f"Error cargando ecommerce: {e}")

    c.setFillColor(HexColor('#FFD700'))
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width/2, 50, "+45,060 PRODUCTOS LISTOS PARA EXPORTAR")

    c.showPage()

    # ========== PÁGINA 9: SISTEMA DE CRÉDITOS ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#FF5722'))
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 40, "SISTEMA DE CRÉDITOS")

    # Captura real de créditos
    try:
        if os.path.exists(img_creditos):
            c.drawImage(img_creditos, 30, 80, width=width-60, height=height-180, preserveAspectRatio=True)
    except Exception as e:
        print(f"Error cargando creditos: {e}")

    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 50, "Otorga crédito a clientes de confianza • Control de saldos • Historial de pagos")

    c.showPage()

    # ========== PÁGINA 10: FINANZAS Y REPORTES ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#9C27B0'))
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 40, "FINANZAS Y REPORTES")

    # Captura real de finanzas
    try:
        if os.path.exists(img_finanzas):
            c.drawImage(img_finanzas, 30, 80, width=width-60, height=height-180, preserveAspectRatio=True)
    except Exception as e:
        print(f"Error cargando finanzas: {e}")

    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 50, "Ventas del día • Ventas del mes • Top productos • Exportar CSV")

    c.showPage()

    # ========== PÁGINA 11: CORTE DE CAJA ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#FFEB3B'))
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 40, "CORTE DE CAJA")

    # Captura real de caja
    try:
        if os.path.exists(img_caja):
            c.drawImage(img_caja, 30, 80, width=width-60, height=height-180, preserveAspectRatio=True)
    except Exception as e:
        print(f"Error cargando caja: {e}")

    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 50, "Apertura de caja • Resumen de ventas • Efectivo y tarjeta • Historial de cortes")

    c.showPage()

    # ========== PÁGINA 12: MÁS MÓDULOS ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#00796B'))
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 40, "MÁS MÓDULOS INCLUIDOS")

    # Mostrar 4 capturas pequeñas
    try:
        if os.path.exists(img_clientes):
            c.drawImage(img_clientes, 30, height - 330, width=250, height=220, preserveAspectRatio=True)
            c.setFillColor(HexColor('#3F51B5'))
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(155, height - 350, "CLIENTES")
    except:
        pass

    try:
        if os.path.exists(img_domicilio):
            c.drawImage(img_domicilio, width - 280, height - 330, width=250, height=220, preserveAspectRatio=True)
            c.setFillColor(HexColor('#FF9800'))
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(width - 155, height - 350, "SERVICIO A DOMICILIO")
    except:
        pass

    try:
        if os.path.exists(img_traspasos):
            c.drawImage(img_traspasos, 30, 80, width=250, height=220, preserveAspectRatio=True)
            c.setFillColor(HexColor('#3F51B5'))
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(155, 60, "TRASPASOS ENTRE FARMACIAS")
    except:
        pass

    try:
        if os.path.exists(img_alertas):
            c.drawImage(img_alertas, width - 280, 80, width=250, height=220, preserveAspectRatio=True)
            c.setFillColor(HexColor('#F44336'))
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(width - 155, 60, "ALERTAS DE STOCK")
    except:
        pass

    c.showPage()

    # ========== PÁGINA 6: SUSCRIPCIONES ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#9C27B0'))
    c.rect(0, height - 80, width, 80, fill=True, stroke=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height - 50, "PLANES Y SUSCRIPCIONES")

    y = height - 130

    # Plan Básico
    c.setFillColor(HexColor('#E3F2FD'))
    c.roundRect(30, y - 160, 160, 180, 10, fill=True)
    c.setFillColor(HexColor('#1E88E5'))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(110, y - 10, "BÁSICO")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(110, y - 40, "$5,000")
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor('#333333'))
    c.drawCentredString(110, y - 65, "Punto de Venta")
    c.drawCentredString(110, y - 78, "Inventario")
    c.drawCentredString(110, y - 91, "Clientes")
    c.drawCentredString(110, y - 104, "Reportes básicos")
    c.drawCentredString(110, y - 120, "1 mes soporte")

    # Plan Profesional
    c.setFillColor(HexColor('#FFF8E1'))
    c.roundRect(210, y - 160, 160, 180, 10, fill=True)
    c.setFillColor(HexColor('#FF9800'))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(290, y - 10, "PROFESIONAL")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(290, y - 40, "$10,000")
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor('#333333'))
    c.drawCentredString(290, y - 65, "Todo del Básico +")
    c.drawCentredString(290, y - 78, "Monedero Saturnos")
    c.drawCentredString(290, y - 91, "Tarjetas Premium")
    c.drawCentredString(290, y - 104, "Ofertas/Promociones")
    c.drawCentredString(290, y - 120, "3 meses soporte")

    # Plan Premium
    c.setFillColor(HexColor('#212121'))
    c.roundRect(390, y - 160, 160, 180, 10, fill=True)
    c.setFillColor(HexColor('#FFD700'))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(470, y - 10, "PREMIUM")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(470, y - 40, "$15,000")
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor('#FFFFFF'))
    c.drawCentredString(470, y - 65, "Todo del Profesional +")
    c.drawCentredString(470, y - 78, "Personalización total")
    c.drawCentredString(470, y - 91, "Logo y colores")
    c.drawCentredString(470, y - 104, "Capacitación")
    c.drawCentredString(470, y - 120, "6 meses soporte")

    # OFERTÓN PRIMEROS 3 - ABAJO
    c.setFillColor(HexColor('#FF5722'))
    c.roundRect(60, y - 280, width - 120, 100, 15, fill=True)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, y - 200, "OFERTA PRIMEROS 3 CLIENTES")
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2, y - 240, "PLAN PREMIUM A SOLO $8,500")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, y - 265, "¡Ahorra $6,500! Incluye todo el sistema completo")

    # Diseño personalizado extra
    c.setFillColor(HexColor('#1E88E5'))
    c.roundRect(120, y - 350, width - 240, 50, 10, fill=True)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, y - 315, "🎨 DISEÑO PERSONALIZADO: $1,500")
    c.setFont("Helvetica", 11)
    c.drawCentredString(width/2, y - 335, "Por cada diseño diferente de tarjetas premium")

    # Nota
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, 50, "* Precios en pesos mexicanos, pago único. Soporte adicional: $600/mes")

    c.showPage()

    # ========== PÁGINA 7: CONTACTO ==========
    # Fondo
    for i in range(100):
        factor = i / 100
        r = int(30 + factor * 20)
        g = int(136 + factor * 30)
        b = int(229 - factor * 50)
        c.setFillColorRGB(r/255, g/255, b/255)
        c.rect(0, height - (i * height/100), width, height/100, fill=True, stroke=False)

    # BOTÓN PRUÉBAME - DEMO GRATIS
    c.setFillColor(HexColor('#FF5722'))
    c.roundRect(width/2 - 140, height - 240, 280, 80, 15, fill=True)
    c.setStrokeColor(HexColor('#FFFFFF'))
    c.setLineWidth(3)
    c.roundRect(width/2 - 140, height - 240, 280, 80, 15, fill=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width/2, height - 185, "¡PRUÉBAME!")
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 215, "DEMO GRATIS 15 MINUTOS")

    c.setFont("Helvetica", 16)
    c.setFillColor(HexColor('#FFD700'))
    c.drawCentredString(width/2, height - 280, "Sin compromiso - Conoce todas las funciones")

    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 350, "CONTACTO:")

    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - 390, "Tel: 775-320-0224")
    c.drawCentredString(width/2, height - 420, "WhatsApp: 775-320-0224")
    c.drawCentredString(width/2, height - 450, "Email: contacto@tuempresa.com")

    c.setFont("Helvetica-Oblique", 14)
    c.setFillColor(HexColor('#90CAF9'))
    c.drawCentredString(width/2, height - 520, "\"La mejor inversión para tu negocio\"")

    c.showPage()

    # ========== PÁGINA 8: PRODUCTOS DE ESPECIALIDAD ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#E91E63'))
    c.rect(0, height - 80, width, 80, fill=True, stroke=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 50, "PRODUCTOS DE ESPECIALIDAD")

    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 110, "YA INCLUIDOS CON PRECIOS ACTUALIZADOS:")

    y = height - 150

    productos_especialidad = [
        ("RYBELSUS 3MG", "$2,800", "Control de diabetes"),
        ("RYBELSUS 7MG", "$2,800", "Control de diabetes"),
        ("RYBELSUS 14MG", "$2,800", "Control de diabetes"),
        ("SAXENDA 6MG", "$5,500", "Control de peso"),
        ("OZEMPIC 0.25MG", "$3,200", "Diabetes tipo 2"),
        ("OZEMPIC 1MG", "$3,500", "Diabetes tipo 2"),
        ("TACROLIMUS 1MG", "$650", "Inmunosupresor"),
        ("APROVASC 300MG", "$850", "Hipertensión"),
        ("MICARDIS DUO", "$750", "Presión arterial"),
        ("LOXCELL", "$65", "Antibiótico"),
    ]

    c.setFont("Helvetica", 11)
    for nombre, precio, uso in productos_especialidad:
        c.setFillColor(HexColor('#E91E63'))
        c.circle(55, y - 3, 4, fill=True)
        c.setFillColor(HexColor('#333333'))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(70, y, nombre)
        c.setFillColor(HexColor('#4CAF50'))
        c.drawString(220, y, precio)
        c.setFillColor(HexColor('#666666'))
        c.setFont("Helvetica", 10)
        c.drawString(300, y, f"- {uso}")
        y -= 22

    # Nota ofertas
    c.setFillColor(HexColor('#FF5722'))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 30, "OFERTAS ACTIVAS:")
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 11)
    c.drawString(50, y - 55, "• TACROLIMUS 4x$2,000 (Ahorro de $600)")
    c.drawString(50, y - 75, "• APROVASC 2x$1,300 (Ahorro de $400)")
    c.drawString(50, y - 95, "• LOXCELL 4x$200 (Ahorro de $60)")
    c.drawString(50, y - 115, "• RYBELSUS 14MG Oferta especial")
    c.drawString(50, y - 135, "• SAXENDA Gran oferta con bonus Saturnos")

    c.setFillColor(HexColor('#1E88E5'))
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, 60, "* Precios sujetos a cambios. Base de datos actualizable.")

    c.showPage()

    # ========== PÁGINA 9: BIOLÓGICOS Y ONCOLÓGICOS ==========
    dibujar_fondo_agua(c, width, height)
    c.setFillColor(HexColor('#673AB7'))
    c.rect(0, height - 80, width, 80, fill=True, stroke=False)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height - 50, "BIOLÓGICOS Y ONCOLÓGICOS")

    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 110, "MEDICAMENTOS DE ALTA ESPECIALIDAD:")

    y = height - 140

    biologicos = [
        ("HERCEPTIN (Trastuzumab)", "$28,000 - $35,000", "Cáncer de mama"),
        ("AVASTIN (Bevacizumab)", "$15,000 - $25,000", "Diversos tipos de cáncer"),
        ("RITUXAN (Rituximab)", "$18,000 - $30,000", "Linfomas y artritis"),
        ("HUMIRA (Adalimumab)", "$12,000 - $18,000", "Artritis reumatoide"),
        ("ENBREL (Etanercept)", "$10,000 - $15,000", "Artritis y psoriasis"),
        ("REMICADE (Infliximab)", "$15,000 - $22,000", "Enfermedades autoinmunes"),
        ("KEYTRUDA (Pembrolizumab)", "$80,000 - $120,000", "Inmunoterapia cáncer"),
        ("OPDIVO (Nivolumab)", "$70,000 - $100,000", "Inmunoterapia cáncer"),
        ("REVLIMID (Lenalidomida)", "$40,000 - $60,000", "Mieloma múltiple"),
        ("IMBRUVICA (Ibrutinib)", "$50,000 - $80,000", "Leucemia y linfoma"),
    ]

    c.setFont("Helvetica", 10)
    for nombre, precio, uso in biologicos:
        c.setFillColor(HexColor('#673AB7'))
        c.circle(55, y - 3, 4, fill=True)
        c.setFillColor(HexColor('#333333'))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(65, y, nombre)
        c.setFillColor(HexColor('#4CAF50'))
        c.setFont("Helvetica", 9)
        c.drawString(250, y, precio)
        c.setFillColor(HexColor('#666666'))
        c.drawString(380, y, f"- {uso}")
        y -= 20

    # Nota importante
    c.setFillColor(HexColor('#FF5722'))
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width/2, y - 30, "IMPORTANTE: Requieren receta médica especializada")
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, y - 50, "Precios referenciales. Consultar disponibilidad y precio actual.")
    c.drawCentredString(width/2, y - 65, "Se manejan bajo pedido especial con proveedores certificados.")

    c.save()

    print(f"\n{'='*60}")
    print(f"  PDF CREADO EXITOSAMENTE")
    print(f"  Ubicación: {pdf_path}")
    print(f"{'='*60}")

    # Abrir el PDF
    os.startfile(pdf_path)

    return pdf_path

if __name__ == "__main__":
    crear_pdf_presentacion()
