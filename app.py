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

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/sensores")
def sensores_page():  # ✅ Renomeado para evitar conflito
    return render_template("sensores.html")

@app.route("/contato")
def contato():
    return render_template("contato.html")

@app.route("/api/sensores")  # ✅ Mantém a rota para os dados
def sensores_api():
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
