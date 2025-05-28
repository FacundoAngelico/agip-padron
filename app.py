from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "database.db"

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        cuit = request.form.get("cuit")
        if cuit:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM padron WHERE cuit = ?", (cuit,))
                resultado = cursor.fetchone()
                columnas = [desc[0] for desc in cursor.description]
                if resultado:
                    resultado = dict(zip(columnas, resultado))
    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
