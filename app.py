from flask import Flask, render_template, jsonify, send_file
import mysql.connector
import io
import csv
from datetime import datetime
import os

app = Flask(__name__)  # Define la app aquí

def get_mysql_connection():
    return mysql.connector.connect(
        host='base-condensador.cjagmwui8z8e.us-east-2.rds.amazonaws.com',
        user='msuchiha',
        password='90_Naruto_26',
        database='datos-sensores',
        autocommit=True
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/datos')
def obtener_datos():
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lecturas ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        data = {
            'timestamp': row[1].strftime('%Y-%m-%d %H:%M:%S'),
            'temp_max': row[2],
            'temp_dht': row[3],
            'humedad': row[4]
        }
    else:
        data = {}

    return jsonify(data)

@app.route('/descargar')
def descargar_csv():
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lecturas")
    rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Timestamp', 'Temp MAX', 'Temp DHT', 'Humedad'])
    writer.writerows(rows)

    output.seek(0)

    # Borra datos después de descargar
    cursor.execute("DELETE FROM lecturas")
    conn.close()

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'datos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Puerto dinámico de Render
    app.run(host='0.0.0.0', port=port)
