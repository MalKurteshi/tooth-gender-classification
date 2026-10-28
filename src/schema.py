"""Versioned input contract matching the Per_ANN_v1 workbook."""

APP_VERSION = "2.2.0"
SCHEMA_VERSION = "v1"
SEED_FILENAME = "Per_ANN_v1.xlsx"

FEATURES = [
    "UM2 MD (mm)",
    "UM1 MD (mm)",
    "UP2 MD (mm)",
    "UP1 MD (mm)",
    "13 BO (mm)",
    "13 MD (mm)",
    "12MD (mm)",
    "11 MD (mm)",
    "21 MD (mm)",
    "22 MD (mm)",
    "23 MD (mm)",
    "23 BO (mm)",
    "LM2 MD (mm)",
    "LM1 MD (mm)",
    "LP2 MD (mm)",
    "LP1 MD (mm)",
    "43 BO (mm)",
    "43 MD (mm)",
    "42MD (mm)",
    "41 MD (mm)",
    "31 MD (mm)",
    "32 MD (mm)",
    "33 MD (mm)",
    "33 BO (mm)",
    "Harku interkanin mandibullar",
    "Indeksi i kaninëve",
    "Indeksi i incizivëve Maksillar",
    "Gjatesia e ramusit",
    "Gonion:Gnathion",
    "Gjeresia minimale e ramusit",
    "Gjeresia bigoniale",
]

MIN_MEASUREMENTS = (len(FEATURES) + 1) // 2
