"""
AGREGAR MEDICAMENTOS HOSPITALARIOS Y ONCOLOGICOS
Agrega categorias especializadas: anestesicos, soluciones IV,
quimioterapias, inmunoterapias, analgesicos opioides, antibioticos IV,
medicamentos de soporte oncologico, etc.
"""
import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")

random.seed(2026)

# ============================================================
#  CATALOGOS DE MEDICAMENTOS HOSPITALARIOS Y ONCOLOGICOS
# ============================================================

ANESTESICOS = [
    # (nombre_comercial, principio_activo, presentaciones[])
    # Cada presentacion: (concentracion, forma, piezas, precio_base)
    ("DIPRIVAN", "PROPOFOL", [
        ("200MG/20ML", "AMPOLLETA", "5 AMP", 1850),
        ("500MG/50ML", "FRASCO VIAL", "1 FCO", 1200),
        ("1G/100ML", "FRASCO INFUSION", "1 FCO", 2100),
    ]),
    ("DORMICUM", "MIDAZOLAM", [
        ("5MG/5ML", "AMPOLLETA", "5 AMP", 380),
        ("15MG/3ML", "AMPOLLETA", "5 AMP", 620),
        ("50MG/10ML", "AMPOLLETA", "5 AMP", 950),
    ]),
    ("AMIDATE", "ETOMIDATO", [
        ("20MG/10ML", "AMPOLLETA", "5 AMP", 2800),
        ("40MG/20ML", "AMPOLLETA", "5 AMP", 4500),
    ]),
    ("KETALAR", "KETAMINA", [
        ("500MG/10ML", "FRASCO VIAL", "1 FCO", 450),
        ("200MG/20ML", "AMPOLLETA", "5 AMP", 780),
    ]),
    ("XYLOCAINA", "LIDOCAINA", [
        ("1% 50ML", "FRASCO VIAL", "1 FCO", 85),
        ("2% 50ML", "FRASCO VIAL", "1 FCO", 95),
        ("2% C/EPINEFRINA 50ML", "FRASCO VIAL", "1 FCO", 120),
        ("5% PESADA 2ML", "AMPOLLETA", "25 AMP", 650),
        ("10% SPRAY 80ML", "SPRAY", "1 FCO", 380),
    ]),
    ("MARCAINA", "BUPIVACAINA", [
        ("0.5% 20ML", "FRASCO VIAL", "1 FCO", 180),
        ("0.5% PESADA 4ML", "AMPOLLETA", "5 AMP", 420),
        ("0.75% 20ML", "FRASCO VIAL", "1 FCO", 220),
    ]),
    ("NAROPIN", "ROPIVACAINA", [
        ("7.5MG/ML 20ML", "AMPOLLETA", "5 AMP", 1950),
        ("10MG/ML 20ML", "AMPOLLETA", "5 AMP", 2200),
        ("2MG/ML 100ML", "BOLSA INFUSION", "5 BOLSAS", 3800),
    ]),
    ("SEVORANE", "SEVOFLURANO", [
        ("250ML", "FRASCO INHALACION", "1 FCO", 3200),
    ]),
    ("SUPRANE", "DESFLURANO", [
        ("240ML", "FRASCO INHALACION", "1 FCO", 4800),
    ]),
    ("ULTIVA", "REMIFENTANILO", [
        ("1MG", "FRASCO VIAL LIOFILIZADO", "5 VIALES", 3500),
        ("2MG", "FRASCO VIAL LIOFILIZADO", "5 VIALES", 5200),
        ("5MG", "FRASCO VIAL LIOFILIZADO", "5 VIALES", 8500),
    ]),
    ("SUFENTA", "SUFENTANILO", [
        ("50MCG/ML 5ML", "AMPOLLETA", "5 AMP", 2800),
        ("250MCG/5ML", "AMPOLLETA", "5 AMP", 4200),
    ]),
    ("TRACRIUM", "ATRACURIO", [
        ("25MG/2.5ML", "AMPOLLETA", "5 AMP", 680),
        ("50MG/5ML", "AMPOLLETA", "5 AMP", 1100),
    ]),
    ("NIMBEX", "CISATRACURIO", [
        ("10MG/5ML", "AMPOLLETA", "5 AMP", 1850),
        ("20MG/10ML", "FRASCO VIAL", "1 FCO", 950),
    ]),
    ("ESMERON", "ROCURONIO", [
        ("50MG/5ML", "FRASCO VIAL", "10 VIALES", 3200),
        ("100MG/10ML", "FRASCO VIAL", "10 VIALES", 5500),
    ]),
    ("BRIDION", "SUGAMMADEX", [
        ("200MG/2ML", "FRASCO VIAL", "10 VIALES", 12500),
    ]),
]

SOLUCIONES_IV = [
    ("SOLUCION SALINA", "CLORURO DE SODIO 0.9%", [
        ("100ML", "BOLSA IV", "24 BOLSAS", 420),
        ("250ML", "BOLSA IV", "24 BOLSAS", 580),
        ("500ML", "BOLSA IV", "24 BOLSAS", 750),
        ("1000ML", "BOLSA IV", "12 BOLSAS", 520),
    ]),
    ("SOLUCION GLUCOSADA", "GLUCOSA 5%", [
        ("250ML", "BOLSA IV", "24 BOLSAS", 600),
        ("500ML", "BOLSA IV", "24 BOLSAS", 780),
        ("1000ML", "BOLSA IV", "12 BOLSAS", 550),
    ]),
    ("SOLUCION GLUCOSADA", "GLUCOSA 10%", [
        ("500ML", "BOLSA IV", "24 BOLSAS", 850),
        ("1000ML", "BOLSA IV", "12 BOLSAS", 620),
    ]),
    ("SOLUCION GLUCOSADA", "GLUCOSA 50%", [
        ("50ML", "AMPOLLETA", "25 AMP", 680),
    ]),
    ("SOLUCION HARTMANN", "RINGER LACTATO", [
        ("500ML", "BOLSA IV", "24 BOLSAS", 790),
        ("1000ML", "BOLSA IV", "12 BOLSAS", 560),
    ]),
    ("SOLUCION MIXTA", "GLUCOSA 5% + NACL 0.9%", [
        ("500ML", "BOLSA IV", "24 BOLSAS", 800),
        ("1000ML", "BOLSA IV", "12 BOLSAS", 570),
    ]),
    ("MANITOL", "MANITOL 20%", [
        ("250ML", "FRASCO IV", "12 FRASCOS", 850),
        ("500ML", "FRASCO IV", "12 FRASCOS", 1200),
    ]),
    ("ALBUMINA HUMANA", "ALBUMINA 20%", [
        ("50ML", "FRASCO VIAL", "1 FCO", 1800),
        ("100ML", "FRASCO VIAL", "1 FCO", 3200),
    ]),
    ("ALBUMINA HUMANA", "ALBUMINA 5%", [
        ("250ML", "FRASCO VIAL", "1 FCO", 2100),
        ("500ML", "FRASCO VIAL", "1 FCO", 3800),
    ]),
    ("VOLUVEN", "HIDROXIETILALMIDON 6%", [
        ("500ML", "BOLSA IV", "10 BOLSAS", 2800),
    ]),
    ("GELAFUNDINA", "GELATINA SUCCINILADA 4%", [
        ("500ML", "BOLSA IV", "10 BOLSAS", 2200),
    ]),
    ("BICARBONATO DE SODIO", "BICARBONATO DE SODIO 7.5%", [
        ("50ML", "FRASCO VIAL", "10 FRASCOS", 350),
        ("10ML", "AMPOLLETA", "50 AMP", 480),
    ]),
    ("CLORURO DE POTASIO", "KCL CONCENTRADO", [
        ("14.9% 10ML", "AMPOLLETA", "50 AMP", 520),
        ("14.9% 50ML", "FRASCO VIAL", "10 FRASCOS", 380),
    ]),
    ("NUTRICION PARENTERAL", "NPT ESTANDAR", [
        ("1000ML CENTRAL", "BOLSA 3 CAMARAS", "4 BOLSAS", 4200),
        ("1500ML CENTRAL", "BOLSA 3 CAMARAS", "4 BOLSAS", 5800),
        ("1000ML PERIFERICO", "BOLSA 3 CAMARAS", "4 BOLSAS", 3600),
    ]),
    ("SMOFKABIVEN", "NPT LIPIDICA", [
        ("1477ML CENTRAL", "BOLSA 3 CAMARAS", "4 BOLSAS", 6500),
        ("1904ML CENTRAL", "BOLSA 3 CAMARAS", "4 BOLSAS", 8200),
    ]),
    ("AGUA INYECTABLE", "AGUA BIDESTILADA", [
        ("5ML", "AMPOLLETA", "100 AMP", 280),
        ("10ML", "AMPOLLETA", "100 AMP", 380),
        ("500ML", "FRASCO IV", "24 FRASCOS", 620),
    ]),
]

QUIMIOTERAPIAS = [
    ("TAXOL", "PACLITAXEL", [
        ("30MG/5ML", "FRASCO VIAL", "1 FCO", 1800),
        ("100MG/16.7ML", "FRASCO VIAL", "1 FCO", 4500),
        ("300MG/50ML", "FRASCO VIAL", "1 FCO", 12000),
    ]),
    ("TAXOTERE", "DOCETAXEL", [
        ("20MG/0.5ML", "FRASCO VIAL", "1 FCO", 3200),
        ("80MG/2ML", "FRASCO VIAL", "1 FCO", 9800),
        ("160MG/4ML", "FRASCO VIAL", "1 FCO", 18000),
    ]),
    ("CISPLATINO", "CISPLATINO", [
        ("10MG/20ML", "FRASCO VIAL", "1 FCO", 350),
        ("50MG/100ML", "FRASCO VIAL", "1 FCO", 1200),
        ("100MG/100ML", "FRASCO VIAL", "1 FCO", 2200),
    ]),
    ("CARBOPLATINO", "CARBOPLATINO", [
        ("150MG/15ML", "FRASCO VIAL", "1 FCO", 800),
        ("450MG/45ML", "FRASCO VIAL", "1 FCO", 2100),
    ]),
    ("OXALIPLATINO", "OXALIPLATINO", [
        ("50MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 2800),
        ("100MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 5200),
        ("200MG/40ML", "FRASCO VIAL", "1 FCO", 9500),
    ]),
    ("ADRIBLASTINA", "DOXORRUBICINA", [
        ("10MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 450),
        ("50MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 1800),
    ]),
    ("CAELYX", "DOXORRUBICINA LIPOSOMAL", [
        ("20MG/10ML", "FRASCO VIAL", "1 FCO", 12500),
        ("50MG/25ML", "FRASCO VIAL", "1 FCO", 28000),
    ]),
    ("ONCOVIN", "VINCRISTINA", [
        ("1MG/1ML", "FRASCO VIAL", "1 FCO", 380),
        ("2MG/2ML", "FRASCO VIAL", "1 FCO", 650),
    ]),
    ("GEMZAR", "GEMCITABINA", [
        ("200MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 1200),
        ("1G", "FRASCO VIAL LIOFILIZADO", "1 FCO", 4800),
        ("2G", "FRASCO VIAL LIOFILIZADO", "1 FCO", 8500),
    ]),
    ("XELODA", "CAPECITABINA", [
        ("500MG", "TABLETAS", "CAJA 120 PIEZAS", 8500),
    ]),
    ("FLUOROURACILO", "5-FLUOROURACILO", [
        ("250MG/5ML", "AMPOLLETA", "10 AMP", 380),
        ("500MG/10ML", "AMPOLLETA", "10 AMP", 650),
        ("5G/100ML", "FRASCO VIAL", "1 FCO", 1800),
    ]),
    ("ALIMTA", "PEMETREXED", [
        ("100MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 8500),
        ("500MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 35000),
    ]),
    ("CICLOFOSFAMIDA", "CICLOFOSFAMIDA", [
        ("200MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 180),
        ("500MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 380),
        ("1G", "FRASCO VIAL LIOFILIZADO", "1 FCO", 650),
    ]),
    ("IFOSFAMIDA", "IFOSFAMIDA", [
        ("1G", "FRASCO VIAL LIOFILIZADO", "1 FCO", 850),
        ("2G", "FRASCO VIAL LIOFILIZADO", "1 FCO", 1500),
    ]),
    ("LEUKERAN", "CLORAMBUCILO", [
        ("2MG", "TABLETAS", "CAJA 25 PIEZAS", 3200),
    ]),
    ("MYLERAN", "BUSULFAN", [
        ("2MG", "TABLETAS", "CAJA 100 PIEZAS", 4800),
        ("60MG/10ML", "AMPOLLETA IV", "8 AMP", 32000),
    ]),
    ("VELCADE", "BORTEZOMIB", [
        ("3.5MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 18000),
    ]),
    ("REVLIMID", "LENALIDOMIDA", [
        ("5MG", "CAPSULAS", "CAJA 21 PIEZAS", 28000),
        ("10MG", "CAPSULAS", "CAJA 21 PIEZAS", 42000),
        ("25MG", "CAPSULAS", "CAJA 21 PIEZAS", 65000),
    ]),
    ("VIDAZA", "AZACITIDINA", [
        ("100MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 12000),
    ]),
    ("TEMODAR", "TEMOZOLOMIDA", [
        ("20MG", "CAPSULAS", "CAJA 5 PIEZAS", 3500),
        ("100MG", "CAPSULAS", "CAJA 5 PIEZAS", 12000),
        ("250MG", "CAPSULAS", "CAJA 5 PIEZAS", 28000),
    ]),
]

INMUNOTERAPIAS = [
    ("KEYTRUDA", "PEMBROLIZUMAB", [
        ("100MG/4ML", "FRASCO VIAL", "1 FCO", 85000),
    ]),
    ("OPDIVO", "NIVOLUMAB", [
        ("40MG/4ML", "FRASCO VIAL", "1 FCO", 28000),
        ("100MG/10ML", "FRASCO VIAL", "1 FCO", 65000),
        ("240MG/24ML", "FRASCO VIAL", "1 FCO", 145000),
    ]),
    ("TECENTRIQ", "ATEZOLIZUMAB", [
        ("1200MG/20ML", "FRASCO VIAL", "1 FCO", 120000),
        ("840MG/14ML", "FRASCO VIAL", "1 FCO", 85000),
    ]),
    ("IMFINZI", "DURVALUMAB", [
        ("500MG/10ML", "FRASCO VIAL", "1 FCO", 75000),
    ]),
    ("YERVOY", "IPILIMUMAB", [
        ("50MG/10ML", "FRASCO VIAL", "1 FCO", 95000),
        ("200MG/40ML", "FRASCO VIAL", "1 FCO", 350000),
    ]),
    ("HERCEPTIN", "TRASTUZUMAB", [
        ("150MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 18000),
        ("440MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 48000),
    ]),
    ("KADCYLA", "TRASTUZUMAB EMTANSINA", [
        ("100MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 42000),
        ("160MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 65000),
    ]),
    ("AVASTIN", "BEVACIZUMAB", [
        ("100MG/4ML", "FRASCO VIAL", "1 FCO", 8500),
        ("400MG/16ML", "FRASCO VIAL", "1 FCO", 32000),
    ]),
    ("ERBITUX", "CETUXIMAB", [
        ("100MG/20ML", "FRASCO VIAL", "1 FCO", 9500),
        ("500MG/100ML", "FRASCO VIAL", "1 FCO", 42000),
    ]),
    ("RITUXAN", "RITUXIMAB", [
        ("100MG/10ML", "FRASCO VIAL", "2 FRASCOS", 18000),
        ("500MG/50ML", "FRASCO VIAL", "1 FCO", 38000),
    ]),
    ("GLEEVEC", "IMATINIB", [
        ("100MG", "TABLETAS", "CAJA 60 PIEZAS", 32000),
        ("400MG", "TABLETAS", "CAJA 30 PIEZAS", 52000),
    ]),
    ("TARCEVA", "ERLOTINIB", [
        ("100MG", "TABLETAS", "CAJA 30 PIEZAS", 22000),
        ("150MG", "TABLETAS", "CAJA 30 PIEZAS", 28000),
    ]),
    ("IBRANCE", "PALBOCICLIB", [
        ("75MG", "CAPSULAS", "CAJA 21 PIEZAS", 45000),
        ("100MG", "CAPSULAS", "CAJA 21 PIEZAS", 55000),
        ("125MG", "CAPSULAS", "CAJA 21 PIEZAS", 65000),
    ]),
    ("TAGRISSO", "OSIMERTINIB", [
        ("40MG", "TABLETAS", "CAJA 30 PIEZAS", 72000),
        ("80MG", "TABLETAS", "CAJA 30 PIEZAS", 95000),
    ]),
    ("JAKAVI", "RUXOLITINIB", [
        ("5MG", "TABLETAS", "CAJA 56 PIEZAS", 48000),
        ("15MG", "TABLETAS", "CAJA 56 PIEZAS", 68000),
        ("20MG", "TABLETAS", "CAJA 56 PIEZAS", 78000),
    ]),
]

SOPORTE_ONCOLOGICO = [
    ("ZOFRAN", "ONDANSETRON", [
        ("4MG/2ML", "AMPOLLETA", "5 AMP", 380),
        ("8MG/4ML", "AMPOLLETA", "5 AMP", 620),
        ("8MG", "TABLETAS", "CAJA 10 PIEZAS", 450),
    ]),
    ("KYTRIL", "GRANISETRON", [
        ("1MG/1ML", "AMPOLLETA", "5 AMP", 1200),
        ("1MG", "TABLETAS", "CAJA 10 PIEZAS", 850),
    ]),
    ("ALOXI", "PALONOSETRÓN", [
        ("0.25MG/5ML", "FRASCO VIAL", "1 FCO", 3800),
    ]),
    ("NEUPOGEN", "FILGRASTIM", [
        ("300MCG/ML", "JERINGA PRELLENADA", "5 JERINGAS", 8500),
        ("480MCG/0.5ML", "JERINGA PRELLENADA", "5 JERINGAS", 12000),
    ]),
    ("NEULASTA", "PEGFILGRASTIM", [
        ("6MG/0.6ML", "JERINGA PRELLENADA", "1 JERINGA", 22000),
    ]),
    ("EPOGEN", "ERITROPOYETINA", [
        ("2000UI/ML", "FRASCO VIAL", "6 FRASCOS", 3200),
        ("4000UI/ML", "FRASCO VIAL", "6 FRASCOS", 5800),
        ("10000UI/ML", "FRASCO VIAL", "6 FRASCOS", 12000),
        ("40000UI/ML", "JERINGA PRELLENADA", "1 JERINGA", 8500),
    ]),
    ("LEUCOVORIN", "ACIDO FOLINICO", [
        ("15MG", "TABLETAS", "CAJA 12 PIEZAS", 280),
        ("50MG/5ML", "AMPOLLETA", "5 AMP", 450),
        ("200MG/20ML", "FRASCO VIAL", "1 FCO", 850),
    ]),
    ("MESNA", "MESNA", [
        ("400MG/4ML", "AMPOLLETA", "15 AMP", 1200),
    ]),
    ("ZOMETA", "ACIDO ZOLEDRONICO", [
        ("4MG/5ML", "FRASCO VIAL", "1 FCO", 4500),
    ]),
    ("XGEVA", "DENOSUMAB", [
        ("120MG/1.7ML", "FRASCO VIAL", "1 FCO", 12000),
    ]),
    ("DEXAMETASONA", "DEXAMETASONA", [
        ("8MG/2ML", "AMPOLLETA", "100 AMP", 1800),
        ("4MG", "TABLETAS", "CAJA 30 PIEZAS", 120),
    ]),
]

ANTIBIOTICOS_IV = [
    ("TAZOCIN", "PIPERACILINA/TAZOBACTAM", [
        ("4.5G", "FRASCO VIAL", "12 VIALES", 3800),
    ]),
    ("MERREM", "MEROPENEM", [
        ("500MG", "FRASCO VIAL", "10 VIALES", 4200),
        ("1G", "FRASCO VIAL", "10 VIALES", 7500),
    ]),
    ("TIENAM", "IMIPENEM/CILASTATINA", [
        ("500MG/500MG", "FRASCO VIAL", "10 VIALES", 5800),
    ]),
    ("CANCIDAS", "CASPOFUNGINA", [
        ("50MG", "FRASCO VIAL", "1 FCO", 8500),
        ("70MG", "FRASCO VIAL", "1 FCO", 11000),
    ]),
    ("VFEND", "VORICONAZOL", [
        ("200MG", "FRASCO VIAL", "1 FCO", 5500),
        ("200MG", "TABLETAS", "CAJA 14 PIEZAS", 12000),
    ]),
    ("AMBISOME", "ANFOTERICINA B LIPOSOMAL", [
        ("50MG", "FRASCO VIAL LIOFILIZADO", "10 VIALES", 65000),
    ]),
    ("ZYVOX", "LINEZOLID", [
        ("600MG/300ML", "BOLSA IV", "10 BOLSAS", 18000),
        ("600MG", "TABLETAS", "CAJA 10 PIEZAS", 8500),
    ]),
    ("CUBICIN", "DAPTOMICINA", [
        ("350MG", "FRASCO VIAL", "1 FCO", 5200),
        ("500MG", "FRASCO VIAL", "1 FCO", 7200),
    ]),
    ("VANCOMICINA", "VANCOMICINA", [
        ("500MG", "FRASCO VIAL", "10 VIALES", 1200),
        ("1G", "FRASCO VIAL", "10 VIALES", 1800),
    ]),
    ("INVANZ", "ERTAPENEM", [
        ("1G", "FRASCO VIAL", "1 FCO", 2800),
    ]),
    ("FORTUM", "CEFTAZIDIMA", [
        ("1G", "FRASCO VIAL", "10 VIALES", 1500),
        ("2G", "FRASCO VIAL", "10 VIALES", 2800),
    ]),
    ("ROCEPHIN", "CEFTRIAXONA", [
        ("500MG", "FRASCO VIAL", "1 FCO", 85),
        ("1G", "FRASCO VIAL", "1 FCO", 120),
        ("1G IV", "FRASCO VIAL", "10 VIALES", 850),
    ]),
    ("FLAGYL IV", "METRONIDAZOL IV", [
        ("500MG/100ML", "BOLSA IV", "24 BOLSAS", 1200),
    ]),
    ("TARGOCID", "TEICOPLANINA", [
        ("200MG", "FRASCO VIAL", "1 FCO", 1800),
        ("400MG", "FRASCO VIAL", "1 FCO", 3200),
    ]),
]

ANALGESICOS_HOSPITALARIOS = [
    ("MORFINA", "MORFINA", [
        ("10MG/ML 1ML", "AMPOLLETA", "50 AMP", 1800),
        ("2MG/ML 2ML", "AMPOLLETA", "50 AMP", 950),
        ("10MG", "TABLETAS LP", "CAJA 60 PIEZAS", 380),
        ("30MG", "TABLETAS LP", "CAJA 60 PIEZAS", 850),
    ]),
    ("FENTANILO", "FENTANILO", [
        ("0.1MG/2ML", "AMPOLLETA", "50 AMP", 2200),
        ("0.5MG/10ML", "AMPOLLETA", "50 AMP", 5500),
        ("25MCG/H", "PARCHE TRANSDERMICO", "CAJA 5 PARCHES", 1200),
        ("50MCG/H", "PARCHE TRANSDERMICO", "CAJA 5 PARCHES", 1800),
        ("75MCG/H", "PARCHE TRANSDERMICO", "CAJA 5 PARCHES", 2500),
        ("100MCG/H", "PARCHE TRANSDERMICO", "CAJA 5 PARCHES", 3200),
    ]),
    ("OXYCONTIN", "OXICODONA", [
        ("10MG", "TABLETAS LP", "CAJA 30 PIEZAS", 850),
        ("20MG", "TABLETAS LP", "CAJA 30 PIEZAS", 1500),
        ("40MG", "TABLETAS LP", "CAJA 30 PIEZAS", 2800),
    ]),
    ("TRAMADOL IV", "TRAMADOL", [
        ("100MG/2ML", "AMPOLLETA", "50 AMP", 1200),
        ("50MG", "CAPSULAS", "CAJA 30 PIEZAS", 180),
        ("100MG", "TABLETAS LP", "CAJA 30 PIEZAS", 350),
    ]),
    ("BUPRENORFINA", "BUPRENORFINA", [
        ("0.3MG/ML", "AMPOLLETA", "6 AMP", 280),
        ("35MCG/H", "PARCHE TRANSDERMICO", "CAJA 4 PARCHES", 1500),
        ("52.5MCG/H", "PARCHE TRANSDERMICO", "CAJA 4 PARCHES", 2200),
    ]),
    ("NALBUFINA", "NALBUFINA", [
        ("10MG/ML 1ML", "AMPOLLETA", "50 AMP", 1800),
    ]),
    ("KETOROLACO IV", "KETOROLACO IV", [
        ("30MG/ML 1ML", "AMPOLLETA", "50 AMP", 850),
        ("60MG/2ML", "AMPOLLETA", "50 AMP", 1200),
    ]),
    ("METAMIZOL IV", "METAMIZOL SODICO", [
        ("1G/2ML", "AMPOLLETA", "50 AMP", 480),
        ("2.5G/5ML", "AMPOLLETA", "50 AMP", 850),
    ]),
]

LABORATORIOS_HOSP = [
    "PFIZER", "ROCHE", "MERCK", "NOVARTIS", "BAXTER", "FRESENIUS KABI",
    "ASTRAZENECA", "BRISTOL-MYERS SQUIBB", "LILLY", "AMGEN", "PISA",
    "JANSSEN", "ABBVIE", "BAYER", "SANOFI", "GSK", "TAKEDA",
    "MSD", "BOEHRINGER", "CELGENE",
]

# Categorias nuevas
CATEGORIAS_DATOS = {
    "ANESTESICOS": ANESTESICOS,
    "SOLUCIONES IV": SOLUCIONES_IV,
    "QUIMIOTERAPIA": QUIMIOTERAPIAS,
    "INMUNOTERAPIA": INMUNOTERAPIAS,
    "SOPORTE ONCOLOGICO": SOPORTE_ONCOLOGICO,
    "ANTIBIOTICOS IV": ANTIBIOTICOS_IV,
    "ANALGESICOS HOSPITALARIOS": ANALGESICOS_HOSPITALARIOS,
}

# Margenes multifarmacias (hospitalarios tienen menos variacion)
MARGENES_HOSP = {
    "precio_fahorro":     (1.03, 1.12),
    "precio_guadalajara": (1.05, 1.15),
    "precio_sanpablo":    (1.08, 1.20),
    "precio_benavides":   (1.06, 1.18),
    "precio_walmart":     (1.02, 1.10),
    "precio_sams":        (0.92, 1.05),
    "precio_moderna":     (1.01, 1.08),
}


def main():
    print("=" * 70)
    print("  AGREGAR MEDICAMENTOS HOSPITALARIOS Y ONCOLOGICOS")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT MAX(id) FROM productos")
    max_id = c.fetchone()[0] or 0
    next_id = max_id + 1

    total_insertados = 0
    resumen = {}

    for categoria, medicamentos in CATEGORIAS_DATOS.items():
        count_cat = 0
        prefijo = "HOS"

        for comercial, principio, presentaciones in medicamentos:
            lab = random.choice(LABORATORIOS_HOSP)

            for concentracion, forma, piezas, precio_base in presentaciones:
                codigo = f"{prefijo}{next_id:06d}"

                nombre = f"{comercial} ({principio}) {concentracion} {forma} {piezas} - {lab}"

                precio_venta = round(precio_base * random.uniform(0.95, 1.05), 2)
                precio_costo = round(precio_venta * 0.6, 2)
                stock = random.randint(5, 100)
                lote = f"L{random.randint(20250101, 20261231)}"
                caducidad = (datetime.now() + timedelta(days=random.randint(90, 730))).strftime("%Y-%m-%d")

                # Precios multifarmacias
                precio_sim = precio_venta
                precios_multi = {}
                for col, (lo, hi) in MARGENES_HOSP.items():
                    precios_multi[col] = round(precio_sim * random.uniform(lo, hi), 2)

                c.execute("""INSERT INTO productos
                    (id, codigo, nombre, categoria, laboratorio, precio_costo, precio_venta,
                     aplica_iva, stock, lote, caducidad,
                     precio_similares, precio_fahorro, precio_guadalajara, precio_sanpablo,
                     precio_benavides, precio_walmart, precio_sams, precio_moderna)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (next_id, codigo, nombre, categoria, lab, precio_costo, precio_venta,
                     1, stock, lote, caducidad,
                     precio_sim,
                     precios_multi["precio_fahorro"],
                     precios_multi["precio_guadalajara"],
                     precios_multi["precio_sanpablo"],
                     precios_multi["precio_benavides"],
                     precios_multi["precio_walmart"],
                     precios_multi["precio_sams"],
                     precios_multi["precio_moderna"]))

                next_id += 1
                count_cat += 1
                total_insertados += 1

        resumen[categoria] = count_cat
        print(f"  {categoria:<28} {count_cat:>4} productos agregados")

    conn.commit()

    # Resumen
    print(f"\n{'=' * 70}")
    print(f"  RESUMEN")
    print(f"{'=' * 70}")
    print(f"  Total productos nuevos: {total_insertados}")
    print(f"  Total en base de datos: {next_id - 1}")
    print()

    for cat, count in resumen.items():
        print(f"    {cat:<28} {count:>4}")

    # Muestra por categoria
    print(f"\n{'=' * 70}")
    print("  MUESTRA DE PRODUCTOS AGREGADOS")
    print(f"{'=' * 70}")

    for categoria in CATEGORIAS_DATOS.keys():
        print(f"\n  --- {categoria} ---")
        c.execute("""SELECT nombre, precio_venta, precio_sams, precio_sanpablo
                     FROM productos WHERE categoria=? LIMIT 3""", (categoria,))
        for row in c.fetchall():
            print(f"    {row[0][:65]}")
            print(f"      PVenta: ${row[1]:,.2f}  |  Sams: ${row[2]:,.2f}  |  SanPablo: ${row[3]:,.2f}")

    # Estadisticas de precios por categoria
    print(f"\n{'=' * 70}")
    print("  PRECIO PROMEDIO POR CATEGORIA")
    print(f"{'=' * 70}")
    print(f"  {'CATEGORIA':<28} {'PROMEDIO':>12} {'MIN':>12} {'MAX':>12}")
    print(f"  {'-'*66}")

    for categoria in CATEGORIAS_DATOS.keys():
        c.execute("""SELECT ROUND(AVG(precio_venta),2), ROUND(MIN(precio_venta),2),
                     ROUND(MAX(precio_venta),2)
                     FROM productos WHERE categoria=?""", (categoria,))
        stats = c.fetchone()
        print(f"  {categoria:<28} ${stats[0]:>10,.2f} ${stats[1]:>10,.2f} ${stats[2]:>10,.2f}")

    conn.close()
    print(f"\n{'=' * 70}")
    print("  COMPLETADO")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
