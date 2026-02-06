===============================================================
  FARMACIAS MADRID - Sistema Punto de Venta (POS)
  Version: Enero 2026
===============================================================

COMO EJECUTAR:
  python SISTEMA.py

CREDENCIALES:
  Usuario: admin     | Password: admin123  (ADMINISTRADOR)
  Usuario: super     | Password: root123   (ADMINISTRADOR)
  Usuario: jperez    | Password: pass123   (VENDEDOR)

REQUISITOS:
  - Python 3.8 o superior
  - Librerias: tkinter (incluido), Pillow, openpyxl
  - Instalar dependencias: pip install Pillow openpyxl

CARACTERISTICAS DEL SISTEMA:
  - Punto de venta con lector de codigos de barras
  - Catalogo de 47,982 productos COFEPRIS
  - Pago mixto: efectivo, tarjeta, vale
  - Servicio a domicilio con repartidores
  - Control de inventario y alertas de stock
  - Gestion de clientes con puntos de lealtad
  - Gestion de compras y proveedores
  - Reportes financieros y corte de caja
  - Gestion de usuarios y permisos
  - Configuracion del sistema

ARCHIVOS PRINCIPALES:
  SISTEMA.py                          - Sistema principal POS
  INSTALAR.py                         - Instalador de base de datos
  farmacia.db                         - Base de datos (47,982 productos)
  IMPORTAR_DESDE_EXCEL.py             - Importador de catalogo Excel
  CATALOGO_COMPLETO_COFEPRIS.xlsx     - Catalogo COFEPRIS completo
  CATALOGO_COMPLETO_COMBINADO.xlsx    - Catalogo combinado
  CATALOGO_FARMACIAS_MADRID_COMPLETO.xlsx - Catalogo Farmacias Madrid
  logo.png                            - Logo del sistema

SCRIPTS AUXILIARES:
  ACTUALIZAR_PRECIOS.py               - Actualizador de precios
  AGREGAR_PRECIOS_MULTIFARMACIAS.py   - Precios de multiples farmacias
  AGREGAR_HOSPITALARIOS.py            - Productos hospitalarios
  AGREGAR_HOSPITALARIOS_V2.py         - Hospitalarios v2
  EXPORTAR_EXCEL.py                   - Exportar datos a Excel
  COMBINAR_CATALOGO.py                - Combinar catalogos
  INTEGRAR_COFEPRIS.py                - Integrar datos COFEPRIS
  AGREGAR_MAYORISTAS.py               - Agregar mayoristas
  MARCAR_CONTROLADOS.py               - Marcar medicamentos controlados

===============================================================
  (c) 2026 Farmacias Madrid - Todos los derechos reservados
===============================================================
