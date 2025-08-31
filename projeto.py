from flask import Flask, make_response
from markupsafe import escape
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from flask import redirect
from werkzeug.utils import secure_filename
import os
from flask_login import (LoginManager, login_user, login_required, logout_user, current_user)
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://guilhermecunha:root@127.0.0.1/loopay_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração da pasta de upload
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://guilhermecunha:root@127.0.0.1/loopay_db'

db = SQLAlchemy(app)

app.secret_key = 'gabi130390'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(db.Model):
    id = db.Column('id_usuario', db.Integer, primary_key=True)
    nome = db.Column('nome_usuario', db.String(250))
    email = db.Column('email_usuario', db.String(100))
    contato = db.Column('tel_usuario', db.String(15))
    end = db.Column('end_usuario', db.String(400))
    senha = db.Column('senha_usuario', db.String(10))

    def __init__(self, nome, email, contato, end, senha):
        self.nome = nome
        self.email = email
        self.contato = contato
        self.end = end
        self.senha = senha

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)    

class Anuncio(db.Model):
    id = db.Column('id_anuncio', db.Integer, primary_key=True)
    produto = db.Column('produto', db.String(250))
    valor = db.Column('valor', db.Float)
    descricao = db.Column('descricao', db.String(500))
    imagem = db.Column('imagem', db.String(200))  

    def __init__(self, produto, valor, descricao, imagem):
        self.produto = produto
        self.valor = valor
        self.descricao = descricao
        self.imagem = imagem

@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('404.html')

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)

@app.route("/")
@login_required
def index():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        usuario = Usuario.query.filter_by(email=email, senha=senha).first()

        if usuario:
            login_user(usuario)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/sobre")
def sobre():
    return "<h1> Portal de vendas de artigos novos e usados</h1>"

@app.route("/cad/usuario")
@login_required
def usuario():
    return render_template('usuario.html', usuarios= Usuario.query.all(), titulo="Usuario")


# UPDATE 
@app.route("/cad/usuario/editar/<int:id>", methods=['GET', 'POST'])
def editar_usuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        usuario.contato = request.form['contato']
        usuario.end = request.form['end']
        usuario.senha = hashlib.sha512(request.form.get('senha').encode("utf-8")).hexdigest()
        db.session.commit()
        return redirect(url_for('usuario'))
    return render_template('editar_usuario.html', usuario=usuario)

# DELETE 
@app.route("/cad/usuario/excluir/<int:id>", methods=['POST'])
def excluir_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/cad/caduser", methods=['POST'])
def caduser():
    senha_hash = hashlib.sha512(request.form.get('senha').encode("utf-8")).hexdigest()
    try:
        usuario = Usuario(request.form.get('nome'), 
                        request.form.get('email'), 
                        request.form.get('contato'), 
                        request.form.get('end'), 
                        request.form.get('senha'))
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('usuario'))
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao cadastrar usuário: {str(e)}")
        return "Erro ao cadastrar usuário. Verifique os dados e tente novamente.", 500

@app.route("/cad/anuncio")
@login_required
def anuncio():
    anuncios = Anuncio.query.all()
    return render_template('anuncio.html', anuncios=anuncios)

# CREATE 
@app.route("/cad/anuncio/cadanuncio", methods=['POST'])
def cadanuncio():
    try:
        arquivo = request.files.get('imagem')
        nome_arquivo = None
        if arquivo and arquivo.filename != '':
            nome_arquivo = secure_filename(arquivo.filename)
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo))
        
        anuncio = Anuncio(
            request.form.get('produto'),
            float(request.form.get('valor') or 0),
            request.form.get('descricao'),
            nome_arquivo
        )
        db.session.add(anuncio)
        db.session.commit()
        return redirect(url_for('anuncio'))
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao cadastrar anúncio: {str(e)}")
        return "Erro ao cadastrar anúncio. Verifique os dados e tente novamente.", 500

# UPDATE 
@app.route("/cad/anuncio/editar/<int:id>", methods=['GET', 'POST'])
def editar_anuncio(id):
    anuncio = Anuncio.query.get_or_404(id)
    if request.method == 'POST':
        anuncio.produto = request.form['produto']
        anuncio.valor = float(request.form['valor'])
        anuncio.descricao = request.form['descricao']
        arquivo = request.files.get('imagem')
        if arquivo and arquivo.filename != '':
            nome_arquivo = secure_filename(arquivo.filename)
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo))
            anuncio.imagem = nome_arquivo
        db.session.commit()
        return redirect(url_for('anuncio'))
    return render_template('editar_anuncio.html', anuncio=anuncio)

# DELETE 
@app.route("/cad/anuncio/excluir/<int:id>", methods=['POST'])
def excluir_anuncio(id):
    anuncio = Anuncio.query.get_or_404(id)
    db.session.delete(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))

@app.route("/anuncio/perguntas")
def perguntas():
    return render_template('perguntas.html')

@app.route("/anuncio/compra")
def compra():
    print("Produto comprado.")
    return ""

@app.route("/anuncio/favoritos")
def favoritos():
    print("favorito inserido")
    return "<h3>Produto salvo nos favoritos.</h3>"

@app.route("/config/categoria")
def categoria():
    return render_template('categoria.html')

@app.route("/relatorio/vendas")
def relatorio_vendas():
    return render_template('relatorio_vendas.html')

@app.route("/relatorio/compras")
def relatorio_compras():
    return render_template('relatorio_compras.html')


def init_db():
    with app.app_context():
        try:
            db.create_all()
            print("Banco de dados criado com sucesso!")
        except Exception as e:
            print(f"Erro ao criar banco de dados: {str(e)}")
            raise

if __name__ == '__main__':
    init_db()
    app.run(debug=True)