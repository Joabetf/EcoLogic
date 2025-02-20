import sqlite3

conn = sqlite3.connect("ecologic.db")
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

conn.commit()
conn.close()
print("Banco de dados atualizado com sucesso!")
