from datetime import datetime

from flask_migrate import check

from app import db

"""
uma vez comfiguradas todas as tabelas para criar a base de dados temos que rodar o comando "flask db init", 
só se roda este comando uma vez por projecto.
"""

class Clientes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    data_registo = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    #def __init__(self, nome, email, senha, data_registo):


class Veiculos(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.Enum('Pequeno', 'Médio', 'Grande', 'SUV', 'Luxo'), nullable=False)        # ('Pequeno', 'Médio', 'Grande', 'SUV', 'Luxo')
    transmissao = db.Column(db.Enum('Automático', 'Manual'), nullable=False)
    tipo_veiculo = db.Column(db.Enum('Carro', 'Motor'), nullable=False)
    capacidade = db.Column(db.Integer, nullable=False)
    valor_diaria = db.Column(db.Float, nullable=False)
    imagem_url = db.Column(db.String(100))
    data_ultima_revisao = db.Column(db.String(10))
    data_proxima_revisao = db.Column(db.String(10))
    data_ultima_inspecao =db.Column(db.String(10))
    disponivel = db.Column(db.Boolean, default=True)

class FormasPagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(100), nullable=False)

class Reservas(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veicuos.id'), nullable=False)
    data_inicio = db.Column(db.String(10), nullable=False)
    data_fim = db.Column(db.String(10), nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('formas_pagamento.id'), nullable=False)



