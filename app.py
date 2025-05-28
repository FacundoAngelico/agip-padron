from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_cuit_data(cuit):
    conn = sqlite3.connect('padron.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM padron WHERE cuit = ?", (cuit,))
    result = cursor.fetchone()
    conn.close()
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        cuit = request.form['cuit']
        result = get_cuit_data(cuit)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)

