from flask import Flask, render_template, jsonify, send_file
import mysql.connector
import csv
import io
import os
from datetime import datetime

app = Flask(__name__)

def get_mysql_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
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

    cursor.execute("DELETE FROM lecturas")
    conn.close()

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'datos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
