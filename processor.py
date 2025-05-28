import csv
import os
import sqlite3
import sys

DB_NAME = "database.db"
ARCHIVO_ESPERADO = "ARDJU008052025.TXT"

def procesar_padron():
    if not os.path.exists(ARCHIVO_ESPERADO):
        print(f"Error: No se encontró {ARCHIVO_ESPERADO}")
        return

    print(f"Procesando: {ARCHIVO_ESPERADO}")

    # Aumentar el límite de tamaño de campo
    csv.field_size_limit(10_000_000)

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
            alicuota_retencion REAL
        )
    """)

    # Primero intentamos determinar la codificación correcta
    encodings = ['latin-1', 'utf-8', 'cp1252', 'iso-8859-1']
    encoding_exito = None
    
    for encoding in encodings:
        try:
            with open(ARCHIVO_ESPERADO, 'r', encoding=encoding) as f:
                # Solo leer una línea para probar
                f.readline()
            encoding_exito = encoding
            break
        except:
            continue

    if not encoding_exito:
        print("No se pudo determinar la codificación del archivo")
        return

    print(f"Codificación detectada: {encoding_exito}")

    # Procesar el archivo con la codificación correcta
    registros_insertados = 0
    with open(ARCHIVO_ESPERADO, 'r', encoding=encoding_exito) as f:
        # Configurar reader CSV con parámetros más flexibles
        reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        
        for row_num, row in enumerate(reader, 1):
            try:
                if len(row) < 12:
                    print(f"Fila {row_num}: No tiene suficientes columnas")
                    continue

                cuit = row[3].strip() if len(row) > 3 else ''
                razon_social = row[11].strip() if len(row) > 11 else ''
                tipo_contrib = row[4].strip() if len(row) > 4 else ''
                marca_alicuota = row[5].strip() if len(row) > 5 else ''

                # Validar CUIT
                if not cuit.isdigit() or len(cuit) != 11:
                    print(f"Fila {row_num}: CUIT inválido - {cuit}")
                    continue

                # Procesar alícuotas
                try:
                    alicuota_percepcion = float(row[7].replace(',', '.')) if len(row) > 7 and row[7] else 0.0
                    alicuota_retencion = float(row[8].replace(',', '.')) if len(row) > 8 and row[8] else 0.0
                except ValueError:
                    alicuota_percepcion = 0.0
                    alicuota_retencion = 0.0

                # Insertar en la base de datos
                cursor.execute("""
                    INSERT OR REPLACE INTO padron
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (cuit, razon_social, tipo_contrib, marca_alicuota, 
                      alicuota_percepcion, alicuota_retencion))
                
                registros_insertados += 1

                # Mostrar progreso cada 1000 registros
                if registros_insertados % 1000 == 0:
                    print(f"Procesados {registros_insertados} registros...")

            except Exception as e:
                print(f"Error en fila {row_num}: {str(e)}")
                continue

    conn.commit()
    conn.close()
    
    print(f"\nProceso completado. Registros insertados: {registros_insertados}")

if __name__ == '__main__':
    procesar_padron()