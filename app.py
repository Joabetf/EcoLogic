from flask import Flask, render_template, jsonify
import sqlite3
import random

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("ecologic.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/sensores")
def sensores():
    # Simulação de sensores
    dados = {
        "luminosidade": round(random.uniform(100, 1000), 2),
        "temperatura": round(random.uniform(18, 30), 2),
        "corrente": round(random.uniform(0, 5), 2),
    }
    
    # Salva no banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sensores (luminosidade, temperatura, corrente) VALUES (?, ?, ?)",
                   (dados["luminosidade"], dados["temperatura"], dados["corrente"]))
    conn.commit()
    conn.close()

    return jsonify(dados)

if __name__ == "__main__":
    app.run(debug=True)
