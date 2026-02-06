"""
AGREGAR MEDICAMENTOS HOSPITALARIOS Y ONCOLOGICOS V2
Solo agrega lo que FALTA en el catalogo actual:
- Vasopresores, sedantes ICU, relajantes musculares adicionales
- Hormonoterapias oncologicas
- Electrolitos IV concentrados
- Medicamentos de soporte adicionales
"""
import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmacia.db")
random.seed(2026_02)

MARGENES = {
    "precio_fahorro":     (1.03, 1.12),
    "precio_guadalajara": (1.05, 1.15),
    "precio_sanpablo":    (1.08, 1.20),
    "precio_benavides":   (1.06, 1.18),
    "precio_walmart":     (1.02, 1.10),
    "precio_sams":        (0.92, 1.05),
    "precio_moderna":     (1.01, 1.08),
}

LABS = [
    "PFIZER", "ROCHE", "MERCK", "NOVARTIS", "BAXTER", "FRESENIUS KABI",
    "ASTRAZENECA", "BRISTOL-MYERS SQUIBB", "LILLY", "AMGEN", "PISA",
    "JANSSEN", "ABBVIE", "BAYER", "SANOFI", "GSK", "TAKEDA",
    "MSD", "BOEHRINGER", "HOSPIRA", "APP PHARMACEUTICALS", "SANDOZ",
    "MYLAN", "TEVA", "ACCORD", "DR. REDDY'S",
]

# ============================================================
#  MEDICAMENTOS NUEVOS (SOLO LO QUE FALTA)
# ============================================================

NUEVOS = {
    # ---- VASOPRESORES E INOTROPICOS ----
    "VASOPRESORES": [
        ("LEVOPHED", "NOREPINEFRINA", [
            ("4MG/4ML", "AMPOLLETA", "10 AMP", 1850),
            ("8MG/8ML", "AMPOLLETA", "10 AMP", 3200),
            ("4MG/4ML", "AMPOLLETA", "50 AMP", 8500),
        ]),
        ("NOREPINEFRINA GENERICA", "NOREPINEFRINA", [
            ("4MG/4ML", "AMPOLLETA", "10 AMP", 650),
            ("8MG/8ML", "AMPOLLETA", "10 AMP", 1100),
        ]),
        ("INTROPIN", "DOPAMINA", [
            ("200MG/5ML", "AMPOLLETA", "5 AMP", 280),
            ("200MG/5ML", "AMPOLLETA", "50 AMP", 2200),
            ("400MG/10ML", "AMPOLLETA", "5 AMP", 480),
        ]),
        ("DOPAMINA GENERICA", "DOPAMINA", [
            ("200MG/5ML", "AMPOLLETA", "50 AMP", 1200),
        ]),
        ("PITRESSIN", "VASOPRESINA", [
            ("20UI/ML 1ML", "AMPOLLETA", "10 AMP", 3800),
            ("20UI/ML 1ML", "AMPOLLETA", "25 AMP", 8500),
        ]),
        ("VASOPRESINA GENERICA", "VASOPRESINA", [
            ("20UI/ML 1ML", "AMPOLLETA", "10 AMP", 1500),
        ]),
        ("DOBUTREX", "DOBUTAMINA", [
            ("250MG/20ML", "FRASCO VIAL", "1 FCO", 180),
            ("250MG/20ML", "FRASCO VIAL", "10 FRASCOS", 1500),
        ]),
        ("ADRENALIN", "EPINEFRINA", [
            ("1MG/ML 1ML", "AMPOLLETA", "50 AMP", 850),
            ("1MG/ML 1ML", "AMPOLLETA", "100 AMP", 1500),
        ]),
        ("ISUPREL", "ISOPROTERENOL", [
            ("0.2MG/ML 5ML", "AMPOLLETA", "10 AMP", 12000),
        ]),
        ("MILRINONA GENERICA", "MILRINONA", [
            ("10MG/10ML", "FRASCO VIAL", "10 FRASCOS", 5500),
            ("50MG/50ML", "BOLSA PREMEZCLADA", "5 BOLSAS", 8200),
        ]),
        ("FENILEFRINA IV", "FENILEFRINA", [
            ("10MG/ML 1ML", "AMPOLLETA", "25 AMP", 2200),
            ("100MCG/ML 10ML", "JERINGA PRELLENADA", "10 JER", 4500),
        ]),
        ("EFEDRINA IV", "EFEDRINA", [
            ("50MG/ML 1ML", "AMPOLLETA", "25 AMP", 1800),
        ]),
        ("NITROPRUSIATO", "NITROPRUSIATO DE SODIO", [
            ("50MG", "FRASCO VIAL LIOFILIZADO", "5 VIALES", 2800),
        ]),
        ("NITROGLICERINA IV", "NITROGLICERINA", [
            ("50MG/10ML", "AMPOLLETA", "10 AMP", 1200),
            ("25MG/250ML", "BOLSA PREMEZCLADA", "5 BOLSAS", 3500),
        ]),
    ],

    # ---- SEDANTES UCI ----
    "SEDANTES UCI": [
        ("PRECEDEX", "DEXMEDETOMIDINA", [
            ("200MCG/2ML", "FRASCO VIAL", "5 VIALES", 4800),
            ("200MCG/2ML", "FRASCO VIAL", "25 VIALES", 22000),
            ("400MCG/100ML", "BOLSA PREMEZCLADA", "4 BOLSAS", 8500),
        ]),
        ("DEXMEDETOMIDINA GENERICA", "DEXMEDETOMIDINA", [
            ("200MCG/2ML", "FRASCO VIAL", "5 VIALES", 1800),
            ("200MCG/2ML", "FRASCO VIAL", "25 VIALES", 8200),
        ]),
        ("MIDAZOLAM IV CONCENTRADO", "MIDAZOLAM", [
            ("50MG/10ML", "FRASCO VIAL", "10 FRASCOS", 1800),
            ("5MG/ML 100ML", "BOLSA INFUSION", "5 BOLSAS", 3200),
        ]),
        ("PROPOFOL INFUSION", "PROPOFOL", [
            ("1% 20ML", "AMPOLLETA", "50 AMP", 12000),
            ("2% 50ML", "FRASCO VIAL", "10 FRASCOS", 8500),
        ]),
        ("CLONIDINA IV", "CLONIDINA", [
            ("150MCG/ML 1ML", "AMPOLLETA", "5 AMP", 280),
            ("500MCG/ML 10ML EPIDURAL", "FRASCO VIAL", "1 FCO", 650),
        ]),
    ],

    # ---- RELAJANTES MUSCULARES FALTANTES ----
    "RELAJANTES MUSCULARES": [
        ("ANECTINE", "SUCCINILCOLINA", [
            ("200MG/10ML", "FRASCO VIAL", "10 FRASCOS", 2800),
            ("500MG", "FRASCO VIAL LIOFILIZADO", "6 VIALES", 3500),
            ("100MG/5ML", "AMPOLLETA", "10 AMP", 1500),
        ]),
        ("QUELICIN", "SUCCINILCOLINA", [
            ("200MG/10ML", "FRASCO VIAL MULTIDOSIS", "1 FCO", 450),
        ]),
        ("PAVULON", "PANCURONIO", [
            ("4MG/2ML", "AMPOLLETA", "25 AMP", 1800),
        ]),
        ("NORCURON", "VECURONIO", [
            ("4MG", "FRASCO VIAL LIOFILIZADO", "10 VIALES", 1200),
            ("10MG", "FRASCO VIAL LIOFILIZADO", "10 VIALES", 2500),
        ]),
        ("DANTRIUM IV", "DANTROLENO", [
            ("20MG", "FRASCO VIAL LIOFILIZADO", "6 VIALES", 18000),
            ("250MG", "SUSPENSION ORAL", "FRASCO 60ML", 2200),
        ]),
    ],

    # ---- ELECTROLITOS IV CONCENTRADOS ----
    "ELECTROLITOS IV": [
        ("SULFATO DE MAGNESIO", "SULFATO DE MAGNESIO", [
            ("10% 10ML", "AMPOLLETA", "50 AMP", 420),
            ("20% 10ML", "AMPOLLETA", "50 AMP", 520),
            ("50% 10ML", "AMPOLLETA", "50 AMP", 650),
            ("50% 2ML", "AMPOLLETA", "100 AMP", 850),
        ]),
        ("GLUCONATO DE CALCIO", "GLUCONATO DE CALCIO 10%", [
            ("10ML", "AMPOLLETA", "50 AMP", 480),
            ("10ML", "AMPOLLETA", "100 AMP", 850),
        ]),
        ("CLORURO DE CALCIO", "CLORURO DE CALCIO 10%", [
            ("10ML", "AMPOLLETA", "25 AMP", 380),
        ]),
        ("FOSFATO DE POTASIO", "FOSFATO DE POTASIO", [
            ("15ML", "AMPOLLETA", "25 AMP", 520),
        ]),
        ("CLORURO DE SODIO HIPERTONICO", "NACL 3%", [
            ("500ML", "BOLSA IV", "12 BOLSAS", 850),
        ]),
        ("CLORURO DE SODIO HIPERTONICO", "NACL 7.5%", [
            ("100ML", "FRASCO IV", "10 FRASCOS", 680),
        ]),
        ("DEXTROSA HIPERTONICA", "GLUCOSA 50%", [
            ("50ML", "FRASCO VIAL", "25 FRASCOS", 780),
        ]),
        ("OLIGOELEMENTOS", "OLIGOELEMENTOS TRAZA", [
            ("10ML", "AMPOLLETA", "25 AMP", 1200),
        ]),
        ("CERNEVIT", "MULTIVITAMINICO IV", [
            ("LIOFILIZADO", "FRASCO VIAL", "10 VIALES", 2800),
        ]),
        ("ADDAMEL", "ELECTROLITOS CONCENTRADOS", [
            ("10ML", "AMPOLLETA", "20 AMP", 1500),
        ]),
    ],

    # ---- HORMONOTERAPIA ONCOLOGICA ----
    "HORMONOTERAPIA": [
        ("NOLVADEX", "TAMOXIFENO", [
            ("10MG", "TABLETAS", "CAJA 30 PIEZAS", 350),
            ("20MG", "TABLETAS", "CAJA 30 PIEZAS", 580),
            ("20MG", "TABLETAS", "CAJA 60 PIEZAS", 1050),
        ]),
        ("TAMOXIFENO GENERICO", "TAMOXIFENO", [
            ("20MG", "TABLETAS", "CAJA 14 PIEZAS", 85),
            ("20MG", "TABLETAS", "CAJA 30 PIEZAS", 150),
        ]),
        ("FEMARA", "LETROZOL", [
            ("2.5MG", "TABLETAS", "CAJA 30 PIEZAS", 4200),
        ]),
        ("LETROZOL GENERICO", "LETROZOL", [
            ("2.5MG", "TABLETAS", "CAJA 30 PIEZAS", 450),
        ]),
        ("CASODEX", "BICALUTAMIDA", [
            ("50MG", "TABLETAS", "CAJA 28 PIEZAS", 5800),
            ("150MG", "TABLETAS", "CAJA 28 PIEZAS", 12000),
        ]),
        ("BICALUTAMIDA GENERICA", "BICALUTAMIDA", [
            ("50MG", "TABLETAS", "CAJA 28 PIEZAS", 850),
        ]),
        ("ARIMIDEX", "ANASTROZOL", [
            ("1MG", "TABLETAS", "CAJA 28 PIEZAS", 3800),
        ]),
        ("ANASTROZOL GENERICO", "ANASTROZOL", [
            ("1MG", "TABLETAS", "CAJA 28 PIEZAS", 280),
        ]),
        ("ZOLADEX", "GOSERELINA", [
            ("3.6MG", "IMPLANTE SC", "1 JERINGA", 4500),
            ("10.8MG", "IMPLANTE SC", "1 JERINGA", 12000),
        ]),
        ("LUPRON DEPOT", "LEUPROLIDA", [
            ("3.75MG", "SUSPENSION INYECTABLE", "1 KIT", 5200),
            ("7.5MG", "SUSPENSION INYECTABLE", "1 KIT", 8500),
            ("22.5MG", "SUSPENSION INYECTABLE", "1 KIT", 18000),
        ]),
        ("MEGACE", "MEGESTROL", [
            ("160MG", "TABLETAS", "CAJA 30 PIEZAS", 1200),
            ("40MG/ML", "SUSPENSION ORAL", "FRASCO 240ML", 2800),
        ]),
        ("FASLODEX", "FULVESTRANT", [
            ("250MG/5ML", "JERINGA PRELLENADA", "2 JERINGAS", 15000),
        ]),
        ("ABIRATERONA", "ABIRATERONA", [
            ("250MG", "TABLETAS", "CAJA 120 PIEZAS", 42000),
            ("500MG", "TABLETAS", "CAJA 60 PIEZAS", 45000),
        ]),
        ("ENZALUTAMIDA", "ENZALUTAMIDA", [
            ("40MG", "CAPSULAS", "CAJA 112 PIEZAS", 58000),
        ]),
        ("FLUTAMIDA", "FLUTAMIDA", [
            ("250MG", "CAPSULAS", "CAJA 90 PIEZAS", 1200),
        ]),
    ],

    # ---- SOPORTE ONCOLOGICO ADICIONAL ----
    "SOPORTE ONCOLOGICO": [
        ("ARANESP", "DARBEPOYETINA", [
            ("20MCG/0.5ML", "JERINGA PRELLENADA", "4 JERINGAS", 6500),
            ("40MCG/0.4ML", "JERINGA PRELLENADA", "4 JERINGAS", 12000),
            ("150MCG/0.3ML", "JERINGA PRELLENADA", "1 JERINGA", 8500),
            ("300MCG/0.6ML", "JERINGA PRELLENADA", "1 JERINGA", 15000),
            ("500MCG/ML", "JERINGA PRELLENADA", "1 JERINGA", 22000),
        ]),
        ("EMEND", "APREPITANT", [
            ("80MG/125MG", "CAPSULAS", "KIT 3 DIAS", 2800),
        ]),
        ("IVEMEND", "FOSAPREPITANT", [
            ("150MG", "FRASCO VIAL", "1 FCO", 3500),
        ]),
        ("AKYNZEO", "NETUPITANT/PALONOSETRÓN", [
            ("300MG/0.5MG", "CAPSULAS", "CAJA 1 PIEZA", 4200),
        ]),
        ("NULOJIX", "BELATACEPT", [
            ("250MG", "FRASCO VIAL LIOFILIZADO", "2 VIALES", 28000),
        ]),
        ("SANDOSTATIN LAR", "OCTREOTIDA", [
            ("10MG", "SUSPENSION INYECTABLE", "1 KIT", 8500),
            ("20MG", "SUSPENSION INYECTABLE", "1 KIT", 15000),
            ("30MG", "SUSPENSION INYECTABLE", "1 KIT", 22000),
        ]),
        ("GRANISETRÓN GENERICO", "GRANISETRÓN IV", [
            ("1MG/ML 1ML", "AMPOLLETA", "5 AMP", 380),
            ("3MG/3ML", "AMPOLLETA", "5 AMP", 850),
        ]),
        ("DEXAMETASONA IV CONCENTRADA", "DEXAMETASONA IV", [
            ("8MG/2ML", "AMPOLLETA", "50 AMP", 850),
            ("20MG/5ML", "AMPOLLETA", "10 AMP", 1200),
            ("4MG/ML 30ML", "FRASCO VIAL MULTIDOSIS", "1 FCO", 280),
        ]),
        ("RASBURICASA", "RASBURICASA", [
            ("1.5MG", "FRASCO VIAL", "3 VIALES", 18000),
            ("7.5MG", "FRASCO VIAL", "1 FCO", 25000),
        ]),
        ("PLERIXAFOR", "PLERIXAFOR", [
            ("20MG/ML 1.2ML", "FRASCO VIAL", "1 FCO", 85000),
        ]),
    ],

    # ---- QUIMIOTERAPIAS ADICIONALES ----
    "QUIMIOTERAPIA": [
        ("ABRAXANE", "PACLITAXEL ALBUMINA", [
            ("100MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 18000),
        ]),
        ("ELOXATIN", "OXALIPLATINO", [
            ("50MG/10ML GENERICO", "FRASCO VIAL", "1 FCO", 1200),
            ("100MG/20ML GENERICO", "FRASCO VIAL", "1 FCO", 2200),
        ]),
        ("ETOPOSIDO IV", "ETOPOSIDO", [
            ("100MG/5ML", "AMPOLLETA", "10 AMP", 850),
            ("500MG/25ML", "FRASCO VIAL", "1 FCO", 1800),
        ]),
        ("ETOPOSIDO ORAL", "ETOPOSIDO", [
            ("50MG", "CAPSULAS", "CAJA 20 PIEZAS", 3500),
        ]),
        ("VINORELBINA IV", "VINORELBINA", [
            ("10MG/ML 1ML", "FRASCO VIAL", "1 FCO", 1500),
            ("10MG/ML 5ML", "FRASCO VIAL", "1 FCO", 6500),
        ]),
        ("NAVELBINE ORAL", "VINORELBINA ORAL", [
            ("20MG", "CAPSULAS BLANDAS", "CAJA 1 PIEZA", 2800),
            ("30MG", "CAPSULAS BLANDAS", "CAJA 1 PIEZA", 3800),
        ]),
        ("DAUNORRUBICINA", "DAUNORRUBICINA", [
            ("20MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 580),
        ]),
        ("IRINOTECAN", "IRINOTECAN", [
            ("40MG/2ML", "FRASCO VIAL", "1 FCO", 850),
            ("100MG/5ML", "FRASCO VIAL", "1 FCO", 1800),
            ("300MG/15ML", "FRASCO VIAL", "1 FCO", 4500),
        ]),
        ("TOPOTECAN", "TOPOTECAN", [
            ("4MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 5200),
        ]),
        ("BLEOMICINA", "BLEOMICINA", [
            ("15UI", "FRASCO VIAL LIOFILIZADO", "1 FCO", 680),
        ]),
        ("MITOMICINA C", "MITOMICINA", [
            ("2MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 280),
            ("10MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 850),
            ("20MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 1500),
            ("40MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 2800),
        ]),
        ("CITARABINA", "CITARABINA", [
            ("100MG", "FRASCO VIAL", "1 FCO", 120),
            ("500MG", "FRASCO VIAL", "1 FCO", 350),
            ("1G", "FRASCO VIAL", "1 FCO", 580),
            ("2G", "FRASCO VIAL", "1 FCO", 950),
        ]),
        ("METOTREXATO IV", "METOTREXATO", [
            ("50MG/2ML", "FRASCO VIAL", "1 FCO", 85),
            ("500MG/20ML", "FRASCO VIAL", "1 FCO", 280),
            ("1G/40ML", "FRASCO VIAL", "1 FCO", 450),
            ("5G/200ML", "FRASCO VIAL", "1 FCO", 1800),
        ]),
        ("DACARBAZINA", "DACARBAZINA", [
            ("200MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 380),
        ]),
        ("BENDAMUSTINA", "BENDAMUSTINA", [
            ("25MG", "FRASCO VIAL LIOFILIZADO", "5 VIALES", 12000),
            ("100MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 8500),
        ]),
    ],

    # ---- TERAPIAS DIRIGIDAS ADICIONALES ----
    "TERAPIA DIRIGIDA": [
        ("SUTENT", "SUNITINIB", [
            ("12.5MG", "CAPSULAS", "CAJA 28 PIEZAS", 28000),
            ("25MG", "CAPSULAS", "CAJA 28 PIEZAS", 42000),
            ("50MG", "CAPSULAS", "CAJA 28 PIEZAS", 58000),
        ]),
        ("NEXAVAR", "SORAFENIB", [
            ("200MG", "TABLETAS", "CAJA 112 PIEZAS", 52000),
        ]),
        ("VOTRIENT", "PAZOPANIB", [
            ("200MG", "TABLETAS", "CAJA 30 PIEZAS", 18000),
            ("400MG", "TABLETAS", "CAJA 60 PIEZAS", 65000),
        ]),
        ("STIVARGA", "REGORAFENIB", [
            ("40MG", "TABLETAS", "CAJA 84 PIEZAS", 55000),
        ]),
        ("SPRYCEL", "DASATINIB", [
            ("50MG", "TABLETAS", "CAJA 60 PIEZAS", 48000),
            ("100MG", "TABLETAS", "CAJA 30 PIEZAS", 52000),
        ]),
        ("TASIGNA", "NILOTINIB", [
            ("150MG", "CAPSULAS", "CAJA 112 PIEZAS", 42000),
            ("200MG", "CAPSULAS", "CAJA 112 PIEZAS", 55000),
        ]),
        ("ALECENSA", "ALECTINIB", [
            ("150MG", "CAPSULAS", "CAJA 224 PIEZAS", 85000),
        ]),
        ("XALKORI", "CRIZOTINIB", [
            ("200MG", "CAPSULAS", "CAJA 60 PIEZAS", 72000),
            ("250MG", "CAPSULAS", "CAJA 60 PIEZAS", 85000),
        ]),
        ("LYNPARZA", "OLAPARIB", [
            ("100MG", "TABLETAS", "CAJA 56 PIEZAS", 42000),
            ("150MG", "TABLETAS", "CAJA 56 PIEZAS", 55000),
        ]),
        ("VERZENIO", "ABEMACICLIB", [
            ("50MG", "TABLETAS", "CAJA 56 PIEZAS", 35000),
            ("100MG", "TABLETAS", "CAJA 56 PIEZAS", 45000),
            ("150MG", "TABLETAS", "CAJA 56 PIEZAS", 55000),
            ("200MG", "TABLETAS", "CAJA 56 PIEZAS", 65000),
        ]),
        ("KISQALI", "RIBOCICLIB", [
            ("200MG", "TABLETAS", "CAJA 63 PIEZAS", 58000),
        ]),
        ("TUKYSA", "TUCATINIB", [
            ("50MG", "TABLETAS", "CAJA 84 PIEZAS", 75000),
            ("150MG", "TABLETAS", "CAJA 84 PIEZAS", 95000),
        ]),
        ("ENHERTU", "TRASTUZUMAB DERUXTECAN", [
            ("100MG", "FRASCO VIAL LIOFILIZADO", "1 FCO", 65000),
        ]),
        ("PERJETA", "PERTUZUMAB", [
            ("420MG/14ML", "FRASCO VIAL", "1 FCO", 38000),
        ]),
        ("VECTIBIX", "PANITUMUMAB", [
            ("100MG/5ML", "FRASCO VIAL", "1 FCO", 12000),
            ("400MG/20ML", "FRASCO VIAL", "1 FCO", 42000),
        ]),
        ("CYRAMZA", "RAMUCIRUMAB", [
            ("100MG/10ML", "FRASCO VIAL", "1 FCO", 18000),
            ("500MG/50ML", "FRASCO VIAL", "1 FCO", 75000),
        ]),
    ],

    # ---- INMUNOTERAPIAS ADICIONALES ----
    "INMUNOTERAPIA": [
        ("LIBTAYO", "CEMIPLIMAB", [
            ("350MG/7ML", "FRASCO VIAL", "1 FCO", 95000),
        ]),
        ("BAVENCIO", "AVELUMAB", [
            ("200MG/10ML", "FRASCO VIAL", "1 FCO", 65000),
        ]),
        ("JEMPERLI", "DOSTARLIMAB", [
            ("500MG/10ML", "FRASCO VIAL", "1 FCO", 120000),
        ]),
        ("CABOMETYX", "CABOZANTINIB", [
            ("20MG", "TABLETAS", "CAJA 30 PIEZAS", 42000),
            ("40MG", "TABLETAS", "CAJA 30 PIEZAS", 55000),
            ("60MG", "TABLETAS", "CAJA 30 PIEZAS", 68000),
        ]),
        ("LENVIMA", "LENVATINIB", [
            ("4MG", "CAPSULAS", "CAJA 30 PIEZAS", 28000),
            ("10MG", "CAPSULAS", "CAJA 30 PIEZAS", 52000),
        ]),
    ],

    # ---- ANTIBIOTICOS IV ADICIONALES ----
    "ANTIBIOTICOS IV": [
        ("COLISTIMETATO", "COLISTINA IV", [
            ("150MG", "FRASCO VIAL", "10 VIALES", 5800),
        ]),
        ("TIGECICLINA", "TIGECICLINA", [
            ("50MG", "FRASCO VIAL", "10 VIALES", 12000),
        ]),
        ("CEFTOLOZANO/TAZOBACTAM", "CEFTOLOZANO/TAZOBACTAM", [
            ("1G/0.5G", "FRASCO VIAL", "10 VIALES", 28000),
        ]),
        ("CEFTAZIDIMA/AVIBACTAM", "CEFTAZIDIMA/AVIBACTAM", [
            ("2G/0.5G", "FRASCO VIAL", "10 VIALES", 32000),
        ]),
        ("AZTREONAM", "AZTREONAM", [
            ("1G", "FRASCO VIAL", "10 VIALES", 3500),
            ("2G", "FRASCO VIAL", "10 VIALES", 6200),
        ]),
        ("CLINDAMICINA IV", "CLINDAMICINA", [
            ("600MG/4ML", "AMPOLLETA", "50 AMP", 1800),
            ("900MG/6ML", "AMPOLLETA", "50 AMP", 2500),
        ]),
        ("FLUCONAZOL IV", "FLUCONAZOL", [
            ("200MG/100ML", "BOLSA IV", "10 BOLSAS", 2200),
            ("400MG/200ML", "BOLSA IV", "10 BOLSAS", 3800),
        ]),
        ("MICAFUNGINA", "MICAFUNGINA", [
            ("50MG", "FRASCO VIAL", "1 FCO", 4500),
            ("100MG", "FRASCO VIAL", "1 FCO", 8200),
        ]),
        ("ANIDULAFUNGINA", "ANIDULAFUNGINA", [
            ("100MG", "FRASCO VIAL", "1 FCO", 9500),
        ]),
        ("ACICLOVIR IV", "ACICLOVIR", [
            ("250MG", "FRASCO VIAL", "5 VIALES", 850),
            ("500MG", "FRASCO VIAL", "5 VIALES", 1500),
        ]),
        ("GANCICLOVIR IV", "GANCICLOVIR", [
            ("500MG", "FRASCO VIAL", "1 FCO", 3200),
        ]),
    ],
}


def main():
    print("=" * 70)
    print("  AGREGAR MEDICAMENTOS HOSPITALARIOS V2")
    print("  (Solo productos que faltan en el catalogo)")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT MAX(id) FROM productos")
    next_id = (c.fetchone()[0] or 0) + 1

    total = 0
    resumen = {}

    for categoria, medicamentos in NUEVOS.items():
        count_cat = 0
        for comercial, principio, presentaciones in medicamentos:
            lab = random.choice(LABS)
            for concentracion, forma, piezas, precio_base in presentaciones:
                codigo = f"HOS{next_id:06d}"
                nombre = f"{comercial} ({principio}) {concentracion} {forma} {piezas} - {lab}"

                pv = round(precio_base * random.uniform(0.95, 1.05), 2)
                pc = round(pv * 0.6, 2)
                stock = random.randint(3, 80)
                lote = f"L{random.randint(20250101, 20261231)}"
                cad = (datetime.now() + timedelta(days=random.randint(90, 730))).strftime("%Y-%m-%d")

                p_sim = pv
                pm = {col: round(p_sim * random.uniform(lo, hi), 2)
                      for col, (lo, hi) in MARGENES.items()}

                c.execute("""INSERT INTO productos
                    (id, codigo, nombre, categoria, laboratorio, precio_costo, precio_venta,
                     aplica_iva, stock, lote, caducidad,
                     precio_similares, precio_fahorro, precio_guadalajara, precio_sanpablo,
                     precio_benavides, precio_walmart, precio_sams, precio_moderna)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (next_id, codigo, nombre, categoria, lab, pc, pv,
                     1, stock, lote, cad,
                     p_sim, pm["precio_fahorro"], pm["precio_guadalajara"],
                     pm["precio_sanpablo"], pm["precio_benavides"],
                     pm["precio_walmart"], pm["precio_sams"], pm["precio_moderna"]))

                next_id += 1
                count_cat += 1
                total += 1

        resumen[categoria] = count_cat
        print(f"  {categoria:<28} {count_cat:>4} productos")

    conn.commit()

    print(f"\n{'=' * 70}")
    print(f"  TOTAL NUEVOS: {total}")
    print(f"  TOTAL EN BD:  {next_id - 1}")
    print(f"{'=' * 70}")

    # Muestra
    for cat in NUEVOS.keys():
        print(f"\n  --- {cat} ---")
        c.execute("""SELECT nombre, precio_venta, precio_sams, precio_sanpablo
                     FROM productos WHERE categoria=?
                     ORDER BY id DESC LIMIT 3""", (cat,))
        for r in c.fetchall():
            print(f"    {r[0][:70]}")
            print(f"      PV: ${r[1]:>10,.2f} | Sams: ${r[2]:>10,.2f} | SanPablo: ${r[3]:>10,.2f}")

    # Resumen general por categoria
    print(f"\n{'=' * 70}")
    print(f"  {'CATEGORIA':<28} {'CANT':>5} {'PROMEDIO':>12} {'MIN':>12} {'MAX':>14}")
    print(f"  {'-'*73}")
    c.execute("""SELECT categoria, COUNT(*), ROUND(AVG(precio_venta),2),
                 ROUND(MIN(precio_venta),2), ROUND(MAX(precio_venta),2)
                 FROM productos GROUP BY categoria ORDER BY categoria""")
    for r in c.fetchall():
        print(f"  {r[0]:<28} {r[1]:>5} ${r[2]:>10,.2f} ${r[3]:>10,.2f} ${r[4]:>12,.2f}")

    conn.close()
    print(f"\n{'=' * 70}")
    print("  COMPLETADO")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
