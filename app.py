from flask import Flask, render_template, jsonify, request, session, flash, redirect, url_for
import sqlite3
import random
from database import autenticar_usuario, registrar_usuario, buscar_estado_ir, atualizar_estado_ir
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'sua_chave_secreta_segura'  # Necessário para usar sessões

def get_db_connection():
    conn = sqlite3.connect("ecologic.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    """Página inicial acessível para todos."""
    return render_template("index.html", user_logged_in='user_id' in session)

@app.route("/sobre")
def sobre():
    if 'user_id' not in session:
        flash("Você precisa estar logado para acessar esta página.", "error")
        return redirect(url_for("login"))
    return render_template("sobre.html")

@app.route("/sensores")
def sensores_page():
    if 'user_id' not in session:
        flash("Você precisa estar logado para acessar esta página.", "error")
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    sensores = conn.execute("SELECT * FROM sensores").fetchall()
    dispositivos_ir = conn.execute("SELECT * FROM dispositivos_ir").fetchall()
    conn.close()
    return render_template("sensores.html", sensores=sensores, dispositivos_ir=dispositivos_ir)

@app.route("/contato")
def contato():
    if 'user_id' not in session:
        flash("Você precisa estar logado para acessar esta página.", "error")
        return redirect(url_for("login"))
    return render_template("contato.html")

@app.route("/api/sensores")
def sensores_api():
    if 'user_id' not in session:
        return jsonify({"error": "Acesso negado"}), 403  # Proíbe acesso à API sem login

    dados = {
        "luminosidade": round(random.uniform(100, 1000), 2),
        "temperatura": round(random.uniform(18, 30), 2),
        "corrente": round(random.uniform(0, 5), 2),
    }
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sensores (luminosidade, temperatura, corrente) VALUES (?, ?, ?)",
                   (dados["luminosidade"], dados["temperatura"], dados["corrente"]))
    conn.commit()
    conn.close()

    return jsonify(dados)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        usuario = autenticar_usuario(email, password)
        if usuario:
            session['user_id'] = usuario[0]
            session['username'] = usuario[1]
            session['tipo'] = usuario[3]  # Salvar tipo de usuário na sessão

            flash('Login realizado com sucesso!', 'success')

            if session['tipo'] == 'admin':
                return redirect(url_for('admin_dashboard'))  # Redireciona admin para dashboard
            else:
                return redirect(url_for('profile'))  # Redireciona usuário comum para perfil
        else:
            flash('E-mail ou senha incorretos.', 'error')

    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('tipo') != 'admin':
        flash("Acesso negado. Área exclusiva para administradores.", "error")
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Buscar estatísticas
    total_usuarios = cursor.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    total_dispositivos = cursor.execute("SELECT COUNT(*) FROM dispositivos_ir").fetchone()[0]
    ultimos_sensores = cursor.execute("SELECT * FROM sensores ORDER BY id DESC LIMIT 5").fetchall()

    conn.close()

    return render_template('admin.html', 
                           username=session.get('username'),
                           total_usuarios=total_usuarios,
                           total_dispositivos=total_dispositivos,
                           ultimos_sensores=ultimos_sensores)



@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro acessível apenas para não logados."""
    if 'user_id' in session:
        return redirect(url_for('profile'))  # Usuário logado já é redirecionado

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        registrar_usuario(username, email, password)
        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))  

    return render_template('register.html')

@app.route('/profile')
def profile():
    """Perfil só pode ser acessado por usuários logados."""
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'error')
        return redirect(url_for('login'))
    return render_template('profile.html', username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()  
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('index'))

@app.route('/api/dispositivos_ir', methods=['GET'])
def obter_dispositivos_ir():
    if 'user_id' not in session:
        return jsonify({"error": "Acesso negado"}), 403  # Bloqueia API sem login
    dispositivos = buscar_estado_ir()
    return jsonify(dispositivos)

@app.route('/api/dispositivos_ir/atualizar', methods=['POST'])
def atualizar_dispositivo_ir():
    if 'user_id' not in session:
        return jsonify({"error": "Acesso negado"}), 403  

    data = request.json
    nome = data.get("nome")
    estado = data.get("estado")
    temperatura = data.get("temperatura")

    atualizar_estado_ir(nome, estado, temperatura)
    return jsonify({"message": "Estado atualizado com sucesso!"})
    
@app.route('/admin/usuarios')
def admin_usuarios():
    if 'user_id' not in session or session.get('tipo') != 'admin':
        flash("Acesso negado. Área exclusiva para administradores.", "error")
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    usuarios = cursor.execute("SELECT id, username, email, tipo FROM usuarios").fetchall()
    conn.close()

    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/usuario/deletar/<int:user_id>', methods=['POST'])
def deletar_usuario(user_id):
    if 'user_id' not in session or session.get('tipo') != 'admin':
        flash("Acesso negado.", "error")
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Impede que o admin se exclua
    if user_id == session['user_id']:
        flash("Você não pode excluir a si mesmo!", "error")
    else:
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
        conn.commit()
        flash("Usuário excluído com sucesso!", "success")
    
    conn.close()
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuario/promover/<int:user_id>', methods=['POST'])
def promover_usuario(user_id):
    if 'user_id' not in session or session.get('tipo') != 'admin':
        flash("Acesso negado.", "error")
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE usuarios SET tipo = 'admin' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    flash("Usuário promovido a administrador!", "success")
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuario/demover/<int:user_id>', methods=['POST'])
def demover_usuario(user_id):
    if 'user_id' not in session or session.get('tipo') != 'admin':
        flash("Acesso negado.", "error")
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Impede que o admin se remova como admin
    if user_id == session['user_id']:
        flash("Você não pode remover a si mesmo como administrador!", "error")
    else:
        cursor.execute("UPDATE usuarios SET tipo = 'usuario' WHERE id = ?", (user_id,))
        conn.commit()
        flash("Administrador rebaixado para usuário comum!", "success")
    
    conn.close()
    return redirect(url_for('admin_usuarios'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        flash('Você precisa estar logado para editar seu perfil.', 'error')
        return redirect(url_for('login'))

    username = request.form['username']
    email = request.form['email']
    password = request.form.get('password', None)
    avatar = request.files.get('avatar', None)

    conn = get_db_connection()
    cursor = conn.cursor()

    if password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("UPDATE usuarios SET username = ?, email = ?, password = ? WHERE id = ?", 
                       (username, email, hashed_password, session['user_id']))
    else:
        cursor.execute("UPDATE usuarios SET username = ?, email = ? WHERE id = ?", 
                       (username, email, session['user_id']))

    if avatar and avatar.filename != '':
        filename = secure_filename(avatar.filename)
        avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        avatar.save(avatar_path)
        avatar_url = f'/static/uploads/{filename}'
        session['avatar'] = avatar_url
        cursor.execute("UPDATE usuarios SET avatar = ? WHERE id = ?", (avatar_url, session['user_id']))

    conn.commit()
    conn.close()

    session['username'] = username
    session['email'] = email
    flash("Perfil atualizado com sucesso!", "success")
    return redirect(url_for('profile'))
    
if __name__ == "__main__":
    app.run(debug=True)
