# -*- coding: utf-8 -*-
# 1. Importações
from datetime import datetime
from app import db

class Reserva(db.Model):
    """ Modelo para registar as Reservas"""

    __tablename__ = 'reservas'

    # Campos do modelo
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

    # ==================== MÉTODOS DE INSTÂNCIA ====================

    def to_dict(self, incluir_detalhes=False):
        """
        Converte o objeto Reserva para dicionário.
        Args:
            incluir_detalhes (bool): Se True, inclui detalhes de veículo e cliente
        Returns:
            dict: Dicionário com dados da reserva
        """
        dados = {
            'id': self.id,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'valor_total': float(self.valor_total),
            'status': self.status,
            'data_reserva': self.data_reserva.isoformat() if self.data_reserva else None,
        }

        if incluir_detalhes:
            dados.update({
                'veiculo': {
                    'id': self.veiculo.id,
                    'marca': self.veiculo.marca,
                    'modelo': self.veiculo.modelo,
                    'imagem_url': self.veiculo.imagem_url
                } if self.veiculo else None,
                'cliente': {
                    'id': self.cliente.id,
                    'name': self.cliente.name,
                    'email': self.cliente.email
                } if self.cliente else None,
                'forma_pagamento': self.formas_pagamento.nome if self.formas_pagamento else None,
                'data_cancelamento': self.data_cancelamento.isoformat() if self.data_cancelamento else None,
                'motivo_cancelamento': self.motivo_cancelamento
            })

        return dados

    def calcular_dias(self):
        """
        Calcula a quantidade de dias da reserva.
        Returns:
            int: Número de dias
        """
        if self.data_inicio and self.data_fim:
            return (self.data_fim - self.data_inicio).days
        return 0

    def pode_ser_editada(self):
        """
        Verifica se a reserva pode ser editada.
        Returns:
            bool: True se pode ser editada
        """
        return self.status in ['confirmada', 'ativa']

    def pode_ser_cancelada(self):
        """
        Verifica se a reserva pode ser cancelada.
        Returns:
            bool: True se pode ser cancelada
        """
        return self.status in ['confirmada', 'ativa']

    def esta_ativa(self):
        """
        Verifica se a reserva está em período ativo.
        Returns:
            bool: True se está no período da reserva
        """
        hoje = datetime.now().date()
        return self.data_inicio <= hoje <= self.data_fim and self.status == 'ativa'

    def dias_ate_inicio(self):
        """
        Calcula quantos dias faltam para o início da reserva.
        Returns:
            int: Número de dias (negativo se já passou)
        """
        hoje = datetime.now().date()
        if self.data_inicio:
            return (self.data_inicio - hoje).days
        return 0

    def __repr__(self):
        return f'<Reserva {self.id} - Cliente:{self.cliente_id} Veículo:{self.veiculo_id} Status:{self.status}>'

    # ==================== MÉTODOS DE CLASSE (CLASS METHODS) ====================

    @classmethod
    def get_reservas_ativas(cls):
        """
        Retorna todas as reservas ativas no sistema.
        Returns:
            list: Lista de objetos Reserva com status ativa
        """
        try:
            return cls.query.filter_by(status='ativa').all()
        except Exception as e:
            print(f"Erro ao buscar reservas ativas: {e}")
            return []

    @classmethod
    def get_reservas_periodo(cls, data_inicio, data_fim):
        """
        Retorna reservas que ocorrem em um período específico.
        Args:
            data_inicio (date): Data de início do período
            data_fim (date): Data de fim do período
        Returns:
            list: Lista de objetos Reserva
        """
        try:
            from sqlalchemy import and_, or_

            return cls.query.filter(
                or_(
                    and_(cls.data_inicio <= data_inicio, cls.data_fim >= data_inicio),
                    and_(cls.data_inicio <= data_fim, cls.data_fim >= data_fim),
                    and_(cls.data_inicio >= data_inicio, cls.data_fim <= data_fim)
                )
            ).all()
        except Exception as e:
            print(f"Erro ao buscar reservas por período: {e}")
            return []

    @classmethod
    def estatisticas_gerais(cls):
        """
        Retorna estatísticas gerais do sistema de reservas.
        Returns:
            dict: Dicionário com estatísticas
        """
        try:
            total_reservas = cls.query.count()
            confirmadas = cls.query.filter_by(status='confirmada').count()
            ativas = cls.query.filter_by(status='ativa').count()
            finalizadas = cls.query.filter_by(status='finalizada').count()
            canceladas = cls.query.filter_by(status='cancelada').count()

            # Calcular receita total (excluindo canceladas)
            reservas_pagas = cls.query.filter(cls.status != 'cancelada').all()
            receita_total = sum(float(r.valor_total) for r in reservas_pagas)

            return {
                'total_reservas': total_reservas,
                'confirmadas': confirmadas,
                'ativas': ativas,
                'finalizadas': finalizadas,
                'canceladas': canceladas,
                'receita_total': receita_total
            }
        except Exception as e:
            print(f"Erro ao calcular estatísticas: {e}")
            return {
                'total_reservas': 0,
                'confirmadas': 0,
                'ativas': 0,
                'finalizadas': 0,
                'canceladas': 0,
                'receita_total': 0
            }