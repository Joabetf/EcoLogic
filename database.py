import sqlite3
import bcrypt

def conectar():
    return sqlite3.connect("ecologic.db")

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabela de Sensores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            luminosidade REAL NOT NULL,
            temperatura REAL NOT NULL,
            corrente REAL NOT NULL
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
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            avatar TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('admin', 'usuario')) NOT NULL DEFAULT 'usuario'
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

def registrar_usuario(username, email, password, tipo="usuario"):
    conn = conectar()
    cursor = conn.cursor()
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        cursor.execute('''
            INSERT INTO usuarios (username, email, password, tipo)
            VALUES (?, ?, ?, ?)
        ''', (username, email, hashed_password, tipo))
        conn.commit()
        print("Usuário registrado com sucesso!")
    except sqlite3.IntegrityError:
        print("Erro: Usuário ou e-mail já existe.")
    finally:
        conn.close()


def autenticar_usuario(email, password):
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, password, tipo FROM usuarios WHERE email = ?', (email,))
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario and bcrypt.checkpw(password.encode('utf-8'), usuario[2]):
        return usuario  # Retorna (id, username, password, tipo)
    else:
        return None

        
if __name__ == "__main__":
    criar_banco()
    print("Banco de dados criado com sucesso!")

    # Teste de registro
    registrar_usuario("testuser", "test@example.com", "testpassword")
    print("Usuário de teste registrado com sucesso!")

    # Teste de autenticação
    usuario = autenticar_usuario("test@example.com", "testpassword")
    if usuario:
        print("Autenticação bem-sucedida! Usuário:", usuario)
    else:
        print("Autenticação falhou.")
