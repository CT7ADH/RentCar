# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
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

    ''' ## READ ## '''
    def get_all(self, limit):
        '''Devolde todos os Veiculos'''
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
        ''' Devolde o Veículo com ID? '''
        try:
            res = db.session.query(Veiculo).filter(Veiculo.id==id).first()
        except Exception as e:
            res = []
            print(f"Erro ao buscar veículo por ID: {e}")
        finally:
            db.session.close()
            return res

    def get_search_type(self, arg_search):
        ''' Lista as variáveis para o segundo filtro dinamicamente '''
        try:
            # Colunas permitidas para busca (White List por segurança)
            colunas_validas = [
                "marca", "modelo", "categoria", "transmissao",
                "tipo_veiculo", "valor_diaria", "capacidade_pessoas"
            ]

            if arg_search in colunas_validas:
                # Obtém dinamicamente o atributo da classe Veiculo
                coluna = getattr(Veiculo, arg_search)

                res = db.session.query(coluna).filter(Veiculo.ativo == True).distinct() \
                    .order_by(coluna).all()
            else:
                # Caso padrão: retorna todos os objetos Veiculo
                res = db.session.query(Veiculo).all()

        except Exception as e:
            res = []
            print(f"Erro na busca: {e}")
        finally:
            db.session.close()

            # Lógica de conversão simplificada
            if res and not isinstance(res[0], Veiculo):
                return [indice[0] for indice in res]
            return res


    def get_veiculos_by_filter(self, tipo_filtro, valor_filtro):
        """Busca veículos baseado no filtro selecionado de forma dinâmica"""
        try:
            # 1. Iniciamos a query base (sempre ativos)
            query = db.session.query(Veiculo).filter(Veiculo.ativo == True)

            # 2. Tratamento especial para 'valor_diaria' (que apenas ordena no seu original)
            if tipo_filtro == "valor_diaria":
                return query.order_by(Veiculo.valor_diaria <= valor_filtro)

            # 3. Filtros que mapeiam diretamente para colunas do modelo
            # Adicione aqui qualquer novo campo que siga a mesma lógica
            filtros_validos = [
                "marca", "modelo", "categoria", "transmissao",
                "tipo_veiculo", "capacidade_pessoas"
            ]

            if tipo_filtro in filtros_validos:
                # Pega o atributo da classe Veiculo dinamicamente
                coluna = getattr(Veiculo, tipo_filtro)

                # Conversão de tipo necessária para capacidade
                valor = int(valor_filtro) if tipo_filtro == "capacidade_pessoas" else valor_filtro

                # Aplica o filtro e a ordenação dinamicamente
                query = query.filter(coluna == valor).order_by(coluna)

            return query.all()

        except Exception as e:
            print(f"Erro ao filtrar veículos: {e}")
            return []
        finally:
            db.session.close()

    def get_categorias_ativas(self):
        """
        Retorna lista de categorias únicas de veículos ativos.
        """
        try:
            categorias = db.session.query(Veiculo.categoria).filter(Veiculo.ativo == True) \
                .distinct().order_by(Veiculo.categoria).all()
            # Converte lista de tuplas em lista simples
            return [cat[0] for cat in categorias]
        except Exception as e:
            print(f"Erro ao buscar categorias: {e}")
            return []
        finally:
            db.session.close()

    ''' ### UPDATE ### '''
    def check_is_activo(self):
        """
        Verifica se as inspeções e as revisões estão expiradas.
        """
        try:
            hoje = date.today()
            data_limite_inspecao = hoje - timedelta(days=365)

            # Busca veículos com problemas
            veiculos_problematicos = db.session.query(Veiculo).filter(
                Veiculo.ativo == True,
                db.or_(
                    Veiculo.data_ultima_inspecao < data_limite_inspecao,
                    Veiculo.data_proxima_revisao < hoje
                )
            ).all()

            quantidade = len(veiculos_problematicos)

            if quantidade > 0:
                for veiculo in veiculos_problematicos:
                    veiculo.ativo = False

                    # Identifica o motivo da desativação
                    motivo = []
                    if veiculo.data_ultima_inspecao < data_limite_inspecao:
                        motivo.append("inspeção expirada")
                    if veiculo.data_proxima_revisao < hoje:
                        motivo.append("revisão atrasada")

                    print(
                        f"Veículo {veiculo.marca} {veiculo.modelo} (ID: {veiculo.id}) desativado - {', '.join(motivo)}")

                db.session.commit()
                return quantidade, f"{quantidade} veículo(s) desativado(s) por manutenção pendente"

            return 0, "Todas as manutenções estão em dia"

        except Exception as e:
            db.session.rollback()
            print(f"Erro ao verificar manutenções: {e}")
            return 0, f"Erro: {str(e)}"
        finally:
            db.session.close()