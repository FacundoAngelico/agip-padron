import csv
import os
import sqlite3
import sys
from datetime import datetime

DB_NAME = "database.db"

def procesar_padron():
    now = datetime.now()
    year = now.year
    month = now.month
    month_str = f"{month:02d}"
    archivo_nombre = f"ARDJU008{month_str}{year}.TXT"

    if not os.path.exists(archivo_nombre):
        print(f"Error: No se encontró {archivo_nombre}")
        return

    print(f"Procesando: {archivo_nombre}")
    csv.field_size_limit(10_000_000)

    # Eliminar la base si existe
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS padron")
    cursor.execute("""
        CREATE TABLE padron (
            cuit TEXT PRIMARY KEY,
            razon_social TEXT,
            tipo_contrib TEXT,
            marca_alicuota TEXT,
            alicuota_percepcion REAL,
            alicuota_retencion REAL,
            vigencia_mes TEXT,
            vigencia_anio TEXT
        )
    """)

    encodings = ['latin-1', 'utf-8', 'cp1252', 'iso-8859-1']
    encoding_exito = None

    for encoding in encodings:
        try:
            with open(archivo_nombre, 'r', encoding=encoding) as f:
                f.readline()
            encoding_exito = encoding
            break
        except:
            continue

    if not encoding_exito:
        print("No se pudo determinar la codificación del archivo")
        return

    print(f"Codificación detectada: {encoding_exito}")

    month_name = now.strftime("%B")
    registros_insertados = 0

    with open(archivo_nombre, 'r', encoding=encoding_exito) as f:
        reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)

        for row_num, row in enumerate(reader, 1):
            try:
                if len(row) < 12:
                    continue

                cuit = row[3].strip()
                razon_social = row[11].strip()
                tipo_contrib = row[4].strip()
                marca_alicuota = row[6].strip()

                if not cuit.isdigit() or len(cuit) != 11:
                    continue

                try:
                    alicuota_percepcion = float(row[7].replace(',', '.')) if row[7] else 0.0
                    alicuota_retencion = float(row[8].replace(',', '.')) if row[8] else 0.0
                except:
                    alicuota_percepcion = 0.0
                    alicuota_retencion = 0.0

                cursor.execute("""
                    INSERT OR REPLACE INTO padron
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (cuit, razon_social, tipo_contrib, marca_alicuota,
                      alicuota_percepcion, alicuota_retencion,
                      month_name, str(year)))

                registros_insertados += 1

            except Exception as e:
                print(f"Error en fila {row_num}: {str(e)}")
                continue

    conn.commit()
    conn.close()
    print(f"\nProceso completado. Registros insertados: {registros_insertados}")

if __name__ == '__main__':
    procesar_padron()
