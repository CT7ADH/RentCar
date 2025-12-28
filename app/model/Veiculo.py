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
            # Colunas permitidas para busca (White List por segurança)
            colunas_validas = [
                "marca", "modelo", "categoria", "transmissao",
                "tipo_veiculo", "valor_diaria", "capacidade_pessoas"
            ]

            if arg_search in colunas_validas:
                # Obtém dinamicamente o atributo da classe Veiculo
                coluna = getattr(Veiculo, arg_search)

                res = db.session.query(coluna) \
                    .filter(Veiculo.ativo == True) \
                    .distinct() \
                    .order_by(coluna) \
                    .all()
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
'''
    def get_veiculos_avancado(self, **filtros):
        """
        Busca veículos com múltiplos filtros simultâneos e faixas de preço.
        Exemplo de uso: get_veiculos_avancado(marca="Toyota", preco_max=200, transmissao="Automático")
        """
        try:
            # Iniciamos com a query base
            query = db.session.query(Veiculo).filter(Veiculo.ativo == True)

            # 1. Filtros de Igualdade (Exatos)
            campos_exatos = ['marca', 'modelo', 'categoria', 'transmissao', 'tipo_veiculo', 'capacidade_pessoas']
            for campo in campos_exatos:
                valor = filtros.get(campo)
                if valor:
                    # Usa getattr para pegar a coluna dinamicamente
                    query = query.filter(getattr(Veiculo, campo) == valor)

            # 2. Filtro de Faixa de Preço (Mínimo e Máximo)
            preco_min = filtros.get('preco_min')
            preco_max = filtros.get('preco_max')

            if preco_min is not None:
                query = query.filter(Veiculo.valor_diaria >= float(preco_min))

            if preco_max is not None:
                query = query.filter(Veiculo.valor_diaria <= float(preco_max))

            # 3. Ordenação (Opcional: vindo nos filtros ou padrão)
            ordenar_por = filtros.get('ordem', 'valor_diaria')  # Padrão por preço
            if hasattr(Veiculo, ordenar_por):
                query = query.order_by(getattr(Veiculo, ordenar_por))

            return query.all()

        except Exception as e:
            print(f"Erro na filtragem avançada: {e}")
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

'''
'''
    def is_disponivel(self, data_inicio=None, data_fim=None):
        """Verifica se o veículo está disponível"""
        if not self.ativo:
            return False

        # Verifica se a inspeção está em dia (não pode ser superior a 1 ano)
        data_limite_inspecao = self.data_ultima_inspecao + timedelta(days=365)
        if date.today() > data_limite_inspecao:
            return False

        # Verifica se não passou da data da próxima revisão
        if date.today() > self.data_proxima_revisao:
            return False

        # Se data_inicio e data_fim foram fornecidas, verifica conflitos de reserva
        if data_inicio and data_fim:
            reservas_conflitantes = Reserva.query.filter(
                Reserva.veiculo_id == self.id,
                Reserva.status.in_(['confirmada', 'ativa']),
                db.or_(
                    db.and_(Reserva.data_inicio <= data_inicio, Reserva.data_fim > data_inicio),
                    db.and_(Reserva.data_inicio < data_fim, Reserva.data_fim >= data_fim),
                    db.and_(Reserva.data_inicio >= data_inicio, Reserva.data_fim <= data_fim)
                )
            ).first()

            if reservas_conflitantes:
                return False

        return True

'''




