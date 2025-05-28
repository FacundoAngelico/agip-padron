import csv
import sqlite3
import os

def process_csv():
    csv_file = None
    for file in os.listdir():
        if file.endswith('.csv'):
            csv_file = file
            break
    if not csv_file:
        print("No CSV file found.")
        return
    conn = sqlite3.connect('padron.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS padron')
    cursor.execute('''
        CREATE TABLE padron (
            cuit TEXT PRIMARY KEY,
            nombre TEXT,
            direccion TEXT
        )
    ''')
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # Skip header
        for row in reader:
            cuit = row[0]
            nombre = row[1]
            direccion = row[2]
            cursor.execute('INSERT INTO padron (cuit, nombre, direccion) VALUES (?, ?, ?)', (cuit, nombre, direccion))
    conn.commit()
    conn.close()
    os.remove(csv_file)

if __name__ == '__main__':
    process_csv()
