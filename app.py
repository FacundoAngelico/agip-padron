from flask import Flask, request, render_template
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "database.db"

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        cuit = request.form.get("cuit")
        monto = request.form.get("monto")

        if cuit and monto:
            try:
                monto = float(monto)
            except ValueError:
                monto = 0.0

            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT razon_social, tipo_contrib, marca_alicuota, alicuota_percepcion, alicuota_retencion FROM padron WHERE cuit = ?", (cuit,))
                row = cursor.fetchone()

                if row:
                    razon_social, tipo_contrib, marca_alicuota, alic_perc, alic_ret = row
                    resultado = {
                        "razon_social": razon_social,
                        "tipo_contrib": tipo_contrib,
                        "marca_alicuota": marca_alicuota,
                        "alicuota_percepcion": alic_perc,
                        "alicuota_retencion": alic_ret,
                        "monto_percepcion": f"{monto * (alic_perc / 100):.2f}",
                        "monto_retencion": f"{monto * (alic_ret / 100):.2f}"
                    }
                else:
                    resultado = {}  # CUIT no encontrado

    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
