from flask import Flask, render_template, jsonify, request
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
def sensores_page():
    conn = get_db_connection()
    sensores = conn.execute("SELECT * FROM sensores").fetchall()
    dispositivos_ir = conn.execute("SELECT * FROM dispositivos_ir").fetchall()
    conn.close()
    return render_template("sensores.html", sensores=sensores, dispositivos_ir=dispositivos_ir)


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

@app.route('/api/dispositivos_ir', methods=['GET'])
def obter_dispositivos_ir():
    dispositivos = database.buscar_estado_ir()
    return jsonify(dispositivos)

@app.route('/api/dispositivos_ir/atualizar', methods=['POST'])
def atualizar_dispositivo_ir():
    data = request.json
    nome = data.get("nome")
    estado = data.get("estado")
    temperatura = data.get("temperatura")

    database.atualizar_estado_ir(nome, estado, temperatura)
    return jsonify({"message": "Estado atualizado com sucesso!"})

@app.route("/atualizar_estado", methods=["POST"])
def atualizar_estado():
    data = request.json
    dispositivo_id = data.get("id")
    novo_estado = data.get("estado")
    conn = get_db_connection()
    conn.execute("UPDATE dispositivos_ir SET estado = ? WHERE id = ?", (novo_estado, dispositivo_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "estado": novo_estado})

@app.route("/atualizar_temperatura", methods=["POST"])
def atualizar_temperatura():
    data = request.json
    dispositivo_id = data.get("id")
    nova_temp = data.get("temperatura")
    conn = get_db_connection()
    conn.execute("UPDATE dispositivos_ir SET temperatura = ? WHERE id = ?", (nova_temp, dispositivo_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "temperatura": nova_temp})

if __name__ == "__main__":
    app.run(debug=True)
