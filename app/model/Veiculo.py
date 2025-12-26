# -*- coding: utf-8 -*-
from datetime import datetime
from app import db

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



