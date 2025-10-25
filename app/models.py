from datetime import datetime

from flask_migrate import check

from app import db

"""
uma vez comfiguradas todas as tabelas para criar a base de dados temos que rodar o comando "flask db init", 
só se roda este comando uma vez por projecto.
- fazer o migrate despois de qualquer alteração: 'flask db migrate -m "[mensagem migrate]"
- salvar o commit no banco de Dados: flask db upgrade
"""

class Clientes(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    nic = db.Column(db.String(14), unique=True, nullable=False) #numero identificação civil
    data_nascimento = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.Text, nullable=False)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    #def __init__(self, nome, email, senha, data_registo):


class Veiculos(db.Model):
    __tablename__ = 'veiculos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    categoria = db.Column(db.String(20), nullable=False)  # Pequeno, Médio, Grande, SUV, Luxo
    transmissao = db.Column(db.String(20), nullable=False)  # Automatico, Manual
    tipo_veiculo = db.Column(db.String(10), nullable=False)  # Carro, Moto
    capacidade_pessoas = db.Column(db.Integer, nullable=False)
    valor_diaria = db.Column(db.Numeric(10, 2), nullable=False)
    imagem_url = db.Column(db.String(255), nullable=True)
    matricula = db.Column(db.String(10), unique=True, nullable=False)
    cor = db.Column(db.String(30), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    kilometragem = db.Column(db.Integer, default=0)

class FormasPagamento(db.Model):        # MB, MBway, CCredito,
    __tablename__ = 'formas_pagamento'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    ativo = db.Column(db.Boolean, default=True)

class Reservas(db.Model):
    __tablename__ = 'reservas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('formas_pagamento.id'), nullable=False)

    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='confirmada')  # confirmada, ativa, finalizada, cancelada

    data_reserva = db.Column(db.DateTime, default=datetime.utcnow)
    data_cancelamento = db.Column(db.DateTime, nullable=True)
    motivo_cancelamento = db.Column(db.Text, nullable=True)


