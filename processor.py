import os
import sqlite3
from datetime import datetime

DB_NAME = "database.db"

def procesar_padron():
    now = datetime.now()
    year = now.year
    month = now.month
    month_str = f"{month:02d}"
    archivo_nombre = f"ARDJU008{month_str}{year}.TXT"

    if not os.path.exists(archivo_nombre):
        print(f"❌ No se encontró {archivo_nombre}")
        return

    print(f"🔁 Procesando: {archivo_nombre}")

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

    registros_insertados = 0
    registros_descartados = 0
    month_name = now.strftime("%B")

    with open(archivo_nombre, 'r', encoding='latin-1', errors='ignore') as f:
        for row_num, linea in enumerate(f, 1):
            try:
                row = linea.strip().split(';')

                if len(row) < 12:
                    registros_descartados += 1
                    continue

                cuit_raw = row[3]
                cuit = cuit_raw.strip().replace('-', '').replace('.', '').replace(' ', '')

                if not cuit.isdigit() or len(cuit) != 11:
                    registros_descartados += 1
                    continue

                tipo_contrib = row[4].strip()
                marca_alicuota = row[5].strip()

                try:
                    alicuota_percepcion = float(row[7].replace(',', '.')) if row[7] else 0.0
                    alicuota_retencion = float(row[8].replace(',', '.')) if row[8] else 0.0
                except:
                    alicuota_percepcion = 0.0
                    alicuota_retencion = 0.0

                # Buscar razón social a partir del campo 12 en adelante
                razon_social = row[12].strip() if len(row) > 12 else row[-1].strip()

                if cuit == "30500017704":
                    print(f"\n🟢 Encontrado CUIT {cuit} en fila {row_num}")
                    print(f"➡️ Razon social: {razon_social}")
                    print(f"➡️ Percepción: {alicuota_percepcion}, Retención: {alicuota_retencion}")

                cursor.execute("""
                    INSERT OR REPLACE INTO padron
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cuit,
                    razon_social,
                    tipo_contrib,
                    marca_alicuota,
                    alicuota_percepcion,
                    alicuota_retencion,
                    month_name,
                    str(year)
                ))

                registros_insertados += 1

            except Exception as e:
                registros_descartados += 1
                print(f"💥 Error en fila {row_num}: {e}")
                continue

    conn.commit()
    conn.close()

    print(f"\n✅ Proceso finalizado.")
    print(f"✔️ Registros insertados: {registros_insertados}")
    print(f"⚠️ Registros descartados: {registros_descartados}")

if __name__ == '__main__':
    procesar_padron()
