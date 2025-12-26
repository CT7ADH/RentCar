# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from flask_login import UserMixin
from app import db, bcrypt, login_manager
from flask_migrate import check

''' -------------------------------------------------------------------------------------------------- '''
"""
1.> Uma vez criadas todas as tabelas da base de dados temos que rodar o comando:
        flask db init
este comando só se roda uma vez para iniciar a cnfiguração do 'migrate'.

2.> Para fazer o migrate despois de qualquer alteração: 
        flask db migrate -m "[mensagem migrate]"
        
3.> Para salvar o commit no banco de Dados:
        flask db upgrade
        
----------------------------------------------------------------------------------------- """
''' Função para recuperar o usuario para sessão desde Cliente'''

''' Classe FormasPagamento para inserir as forma de pagamento'''
class PayMethod(db.Model):        # MB, MBway, CCredito,
    __tablename__ = 'formas_pagamento'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    ativo = db.Column(db.Boolean, default=True)
    # Relacionamentos
    reservas = db.relationship('Reserva', backref='formas_pagamento', lazy='dynamic')

    def __repr__(self):
        return self.nome

    def to_dict(self):
        if self.ativo == True:
            return {
                "id": self.id,
                "name": self.nome
            }




''' Classe Cliente para registar os clientes'''
class Cliente(db.Model, UserMixin):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    genero = db.Column(db.String(50), nullable=False)
    pass_hash = db.Column(db.String(128), nullable=False)

    # Relacionamentos
    reservas = db.relationship('Reserva', backref='cliente', lazy=True)


    def set_password(self, password):
        """Define a Password do usuário (criptografada)"""
        self.pass_hash = bcrypt.generate_password_hash(password.encode('utf-8'))

    def check_password(self, password):
        """Verifica se a Password está correta"""
        return bcrypt.check_password_hash(self.pass_hash, password)

    def __repr__(self):
        return f'<Usuario {self.name}'



''' Classe Veiculo para registar os Veiculos e seus dados'''
class Veiculo(db.Model):
    __tablename__ = 'veiculos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    categoria = db.Column(db.String(20), nullable=False)  # Pequeno, Médio, Grande, SUV, Luxo
    transmissao = db.Column(db.String(20), nullable=False)  # Automatico, Manual
    tipo_veiculo = db.Column(db.String(10), nullable=False)  # Carro, Moto
    capacidade_pessoas = db.Column(db.Integer, nullable=False)
    valor_diaria = db.Column(db.Numeric(10, 2), nullable=False)
    imagem_url = db.Column(db.String(255), nullable=True, default="default.jpg")
    matricula = db.Column(db.String(10), unique=True, nullable=False)
    cor = db.Column(db.String(30), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    kilometragem = db.Column(db.Integer, default=0)
    # Datas importantes para disponibilidade
    data_ultima_revisao = db.Column(db.Date, nullable=False)
    data_proxima_revisao = db.Column(db.Date, nullable=False)
    data_ultima_inspecao = db.Column(db.Date, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    # Relacionamentos
    reservas = db.relationship('Reserva', backref='veiculo', lazy=True)

    # # Crias o Dicionario com as categorias
    # def to_dict(self):
    #     if self.ativo == True:
    #         return {
    #             "id": self.id,
    #             "categoria": self.categoria
    #         }

    def get_all(self, limit):
        try:
            if limit is None:
                res = db.session.query(Veiculo).all()
            else:
                res = db.session.query(Veiculo).order_by(Veiculo.data_cadastro).limit(limit).all()
        except Exception as e:
            res = []
            print(e)
        finally:
            db.session.close()
            return res

    def get_by_id(self, id):
        try:
            res = db.session.query(Veiculo).filter(Veiculo.id==id).first()
        except Exception as e:
            res = []
            print(f"Erro ao buscar veículo por ID: {e}")
        finally:
            db.session.close()
            return res

    def get_search_type(self, arg_search):
        try:
            if arg_search is None or arg_search == "None":
                res = db.session.query(Veiculo).all()
            elif arg_search == "marca":
                res = db.session.query(Veiculo.marca).filter(Veiculo.ativo == True).distinct().order_by(Veiculo.marca).all()
            elif arg_search == "modelo":
                res = db.session.query(Veiculo.modelo).filter(Veiculo.ativo == True).distinct().order_by(Veiculo.modelo).all()
            elif arg_search == "categoria":
                res = db.session.query(Veiculo.categoria).filter(Veiculo.ativo == True).distinct().order_by(Veiculo.categoria).all()
            elif arg_search == "transmissao":
                res = db.session.query(Veiculo.transmissao).filter(Veiculo.ativo == True).distinct().order_by(Veiculo.transmissao).all()
            elif arg_search == "tipo_veiculo":
                res = db.session.query(Veiculo.tipo_veiculo).filter(Veiculo.ativo == True).distinct().order_by(Veiculo.tipo_veiculo).all()
            elif arg_search == "valor_diaria":
                res = db.session.query(Veiculo.valor_diaria).filter(Veiculo.ativo == True).distinct().order_by(Veiculo.valor_diaria).all()
                print(res)
            elif arg_search == "capacidade_pessoas":
                res = db.session.query(Veiculo.capacidade_pessoas).filter(Veiculo.ativo == True).distinct().order_by(Veiculo.capacidade_pessoas).all()
            else:
                res = db.session.query(Veiculo).all()

        except Exception as e:
            res = []
            print(f"Erro na busca: {e}")
        finally:
            db.session.close()
            # Converte lista de tuplas em lista simples
            return [indice[0] for indice in res] if res and not isinstance(res[0], Veiculo) else res

    def get_veiculos_by_filter(self, tipo_filtro, valor_filtro):
        """Busca veículos baseado no filtro selecionado"""
        try:
            if tipo_filtro == "marca":
                res = db.session.query(Veiculo).filter(Veiculo.marca == valor_filtro,Veiculo.ativo == True).order_by(Veiculo.marca).all()

            elif tipo_filtro == "modelo":
                res = db.session.query(Veiculo).filter(Veiculo.modelo == valor_filtro,Veiculo.ativo == True).order_by(Veiculo.modelo).all()

            elif tipo_filtro == "categoria":
                res = db.session.query(Veiculo).filter(Veiculo.categoria == valor_filtro,Veiculo.ativo == True).order_by(Veiculo.categoria).all()

            elif tipo_filtro == "transmissao":
                res = db.session.query(Veiculo).filter(Veiculo.transmissao == valor_filtro,Veiculo.ativo == True).order_by(Veiculo.transmissao).all()

            elif tipo_filtro == "tipo_veiculo":
                res = db.session.query(Veiculo).filter(Veiculo.tipo_veiculo == valor_filtro,Veiculo.ativo == True).order_by(Veiculo.tipo_veiculo).all()

            elif tipo_filtro == "capacidade_pessoas":
                res = db.session.query(Veiculo).filter(Veiculo.capacidade_pessoas == int(valor_filtro),Veiculo.ativo == True).order_by(Veiculo.capacidade_pessoas).all()

            elif tipo_filtro == "valor_diaria":
                # Para valor diária, ordenar por preço
                res = db.session.query(Veiculo).filter(Veiculo.ativo == True).order_by(Veiculo.valor_diaria).all()
            else:
                res = db.session.query(Veiculo).filter(Veiculo.ativo == True).all()

            return res

        except Exception as e:
            print(f"Erro ao filtrar veículos: {e}")
            return []
        finally:
            db.session.close()

    # Metodo: Buscar categorias únicas de veículos ativos
    @staticmethod
    def get_categorias_ativas():
        """Retorna lista de categorias únicas de veículos ativos"""
        try:
            categorias = db.session.query(Veiculo.categoria).filter(Veiculo.ativo == True).distinct().order_by(Veiculo.categoria).all()
            # Converte lista de tuplas em lista simples
            return [cat[0] for cat in categorias]
        except Exception as e:
            print(f"Erro ao buscar categorias: {e}")
            return []
        finally:
            db.session.close()




''' Classe Reserva para registar as Reservas'''
class Reserva(db.Model):
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
