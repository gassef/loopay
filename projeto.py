from flask import Flask, make_response
from markupsafe import escape
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://guilhermecunha:root@127.0.0.1/loopay_db'

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/sobre")
def sobre():
    return "<h1> Portal de vendas de artigos novos e usados</h1>"

@app.route("/cad/usuario")
def usuario():
    return render_template('usuario.html')

@app.route("/cad/caduser", methods=['post'])
def caduser():
    return request.form

@app.route("/cad/anuncio")
def anuncio():
    return render_template('anuncio.html')

@app.route("/cad/anuncio/cadanuncio", methods=['post'])
def cadanuncio():
    return request.form

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

