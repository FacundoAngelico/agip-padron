import requests
import os
import rarfile
from datetime import datetime

def download_and_extract():
    month_names = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    now = datetime.now()
    year = now.year
    month = now.month
    month_name = month_names[month]
    month_str = f"{month:02d}"
    filename = f"ARDJU008{month_str}{year}.rar"
    url = f"https://imagenes.agip.gob.ar/filemanager/source/Agentes/De%20Recaudacion/{year}/{month_name}/{filename}"
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    with rarfile.RarFile(filename) as rf:
        rf.extractall()
    os.remove(filename)

if __name__ == '__main__':
    download_and_extract()
