import sqlite3

def conectar():
    return sqlite3.connect("ecologic.db")

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabela de Sensores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            localizacao TEXT NOT NULL
        )
    ''')

    # Tabela de Leituras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id INTEGER,
            valor REAL NOT NULL,
            unidade TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sensor_id) REFERENCES sensores(id)
        )
    ''')

    # Tabela de Dispositivos IR
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dispositivos_ir (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('projetor', 'ar_condicionado')) NOT NULL,
            estado TEXT CHECK(estado IN ('ligado', 'desligado')) NOT NULL,
            temperatura INTEGER DEFAULT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Banco de dados atualizado com sucesso!")

def inserir_dispositivo_ir(nome, tipo, estado, temperatura=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO dispositivos_ir (nome, tipo, estado, temperatura)
        VALUES (?, ?, ?, ?)
    ''', (nome, tipo, estado, temperatura))
    conn.commit()
    conn.close()

def atualizar_estado_ir(nome, estado, temperatura=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE dispositivos_ir 
        SET estado = ?, temperatura = ? 
        WHERE nome = ?
    ''', (estado, temperatura, nome))
    conn.commit()
    conn.close()

def buscar_estado_ir():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, tipo, estado, temperatura FROM dispositivos_ir")
    dispositivos = cursor.fetchall()
    conn.close()
    return dispositivos

if __name__ == "__main__":
    criar_banco()
