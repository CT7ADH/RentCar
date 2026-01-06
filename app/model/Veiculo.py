# -*- coding: utf-8 -*-
# 1. Importações
from datetime import datetime, date, timedelta
from app import db

class Veiculo(db.Model):
    """Modelo para registar veículos e os seus dados"""

    __tablename__ = 'veiculos'

    # Campos do modelo
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

    def to_dict(self, campos=None):
        """
        Converte o objeto Veiculo para dicionário.
        Returns:
            dict: Dicionário com os dados do veículo
        """
        dados_completos = {
            'id': self.id,
            'marca': self.marca,
            'modelo': self.modelo,
            'categoria': self.categoria,
            'transmissao': self.transmissao,
            'tipo_veiculo': self.tipo_veiculo,
            'capacidade_pessoas': self.capacidade_pessoas,
            'valor_diaria': float(self.valor_diaria),  # Converte Decimal para float
            'imagem_url': self.imagem_url,
            'cor': self.cor,
            'ano': self.ano,
            'kilometragem': self.kilometragem,
            'ativo': self.ativo,
            'matricula': self.matricula,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

        # Se forem especificados campos específicos, retorna apenas esses
        if campos:
            return {campo: dados_completos[campo] for campo in campos if campo in dados_completos}

        return dados_completos

    def __repr__(self):
        return f'<Veiculo {self.marca} {self.modelo} - {self.matricula}>'

    # ==================== MÉTODOS DE INSTÂNCIA ====================

    def get_all(self, limit=None):
        """
        Retorna todos os veículos.
        Args:
            limit (int, optional): Número máximo de veículos
        Returns:
            list: Lista de objetos Veiculo
        """
        try:
            if limit:
                res = db.session.query(Veiculo).order_by(Veiculo.data_cadastro.desc()).limit(limit)
            else:
                res = db.session.query(Veiculo).order_by(Veiculo.data_cadastro.desc())
            return res.all()
        except Exception as e:
            print(f"Erro ao buscar todos os veículos: {e}")
            return []
        finally:
            db.session.close()

    def get_all_activo(self, limit=None):
        """
        Retorna todos os veículos com a revisão e inspeção em dias.
        Args:
            limit (int, optional): Número máximo de veículos
        Returns:
            list: Lista de objetos Veiculo
        """
        try:
            if limit:
                res = db.session.query(Veiculo).filter(Veiculo.ativo == True).order_by(Veiculo.data_cadastro.desc()).limit(limit)
            else:
                res = db.session.query(Veiculo).filter(Veiculo.ativo == True).order_by(Veiculo.data_cadastro.desc())
            return res.all()
        except Exception as e:
            print(f"Erro ao buscar todos os veículos ativos: {e}")
            return []
        finally:
            db.session.close()

    def get_by_id(self, veiculo_id):
        """
        Retorna o veículo com o ID especificado.
        Args:
            veiculo_id (int): ID do veículo
        Returns:
            Veiculo: Objeto Veiculo ou None
        """
        try:
            #res = db.session.query(Veiculo).filter(Veiculo.id==id).first()
            return db.session.query(Veiculo).get(veiculo_id)
        except Exception as e:
            print(f"Erro ao buscar veículo por ID {veiculo_id}: {e}")
            return None
        finally:
            db.session.close()

    def get_search_type(self, arg_search):
        """
        Lista valores únicos para um campo específico (para filtros dinâmicos).
        Args:
            arg_search (str): Nome do campo
        Returns:
            list: Lista de valores únicos
        """
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
            return [resultado[0] for resultado in res]
        except Exception as e:
            print(f"Erro na busca: {e}")
            return []
        finally:
            db.session.close()

    def get_veiculos_by_filter(self, tipo_filtro, valor_filtro):
        """
        Busca veículos filtrados dinamicamente.
        Args:
            tipo_filtro (str): Campo pelo qual filtrar
            valor_filtro: Valor do filtro
        Returns:
            list: Lista de objetos Veiculo
        """
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
                if tipo_filtro == "capacidade_pessoas":
                    valor_filtro = int(valor_filtro)

                # Aplica o filtro e a ordenação dinamicamente
                res = query.filter(coluna == valor_filtro).order_by(coluna)

            return res.all()
        except Exception as e:
            print(f"Erro ao filtrar veículos: {e}")
            return []
        finally:
            db.session.close()

    def get_categorias_ativas(self):
        """
        Retorna categorias únicas de veículos ativos.
        Returns:
            list: Lista de categorias
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

    def check_is_activo(self):
        """
        Verifica e desativa veículos com inspeções/revisões expiradas.
        Returns:
            tuple: (quantidade_desativados, mensagem)
        """
        try:
            hoje = date.today()
            data_limite_inspecao = hoje - timedelta(days=365)

            # Busca veículos com problemas
            veiculos_problematicos = db.session.query(Veiculo).filter(Veiculo.ativo == True,db.or_(
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