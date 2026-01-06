# -*- coding: utf-8 -*-
# 1. Importações
from app.model.Reserva import Reserva
from app.model.Veiculo import Veiculo
from app import db
from datetime import datetime, date
from sqlalchemy import and_, or_

class ReservaControler():
    """Controller para gerir as reservas"""

    def __init__(self):
        self.reserva_model = Reserva()

    # ==================== MÉTODOS DE INSTÂNCIA ====================

    def verificar_disponibilidade(self, veiculo_id, data_inicio, data_fim, reserva_id_excluir=None):
        """
        Verifica se o veículo está disponível no período solicitado.
        Args:
            veiculo_id (int): ID do veículo
            data_inicio (date): Data de início da reserva
            data_fim (date): Data de fim da reserva
            reserva_id_excluir (int, optional): ID de reserva a excluir da verificação (para edição)
        Returns:
            tuple: (disponivel: bool, mensagem: str)
        """
        try:
            # Buscar reservas que conflitam com o período solicitado
            query = db.session.query(Reserva).filter(
                Reserva.veiculo_id == veiculo_id,
                Reserva.status.in_(['confirmada', 'ativa']),
                or_(
                    # Nova reserva inicia durante uma reserva existente
                    and_(Reserva.data_inicio <= data_inicio, Reserva.data_fim >= data_inicio),
                    # Nova reserva termina durante uma reserva existente
                    and_(Reserva.data_inicio <= data_fim, Reserva.data_fim >= data_fim),
                    # Nova reserva engloba uma reserva existente
                    and_(Reserva.data_inicio >= data_inicio, Reserva.data_fim <= data_fim)
                )
            )

            # Se estiver editando uma reserva, excluir ela da verificação
            if reserva_id_excluir:
                query = query.filter(Reserva.id != reserva_id_excluir)

            reservas_conflitantes = query.all()

            if reservas_conflitantes:
                return False, 'Veículo já está reservado para este período!'

            return True, 'Veículo disponível!'

        except Exception as e:
            print(f"Erro ao verificar disponibilidade: {e}")
            return False, f'Erro ao verificar disponibilidade: {str(e)}'

    def calcular_valor_total(self, veiculo_id, data_inicio, data_fim):
        """
        Calcula o valor total da reserva baseado no valor da diária e número de dias.
        Args:
            veiculo_id (int): ID do veículo
            data_inicio (date): Data de início
            data_fim (date): Data de fim
        Returns:
            tuple: (valor_total: float, quantidade_dias: int, mensagem_erro: str)
        """
        try:
            # Buscar veículo
            veiculo = Veiculo.query.get(veiculo_id)
            if not veiculo:
                return 0, 0, 'Veículo não encontrado!'

            # Calcular quantidade de dias
            quantidade_dias = (data_fim - data_inicio).days

            if quantidade_dias <= 0:
                return 0, 0, 'Data de fim deve ser posterior à data de início!'

            # Calcular valor total
            valor_total = float(veiculo.valor_diaria) * quantidade_dias

            return valor_total, quantidade_dias, ''

        except Exception as e:
            print(f"Erro ao calcular valor total: {e}")
            return 0, 0, f'Erro ao calcular valor: {str(e)}'

    def criar_reserva(self, cliente_id, veiculo_id, forma_pagamento_id,data_inicio, data_fim):
        """
        Cria uma nova reserva.
        Args:
            cliente_id (int): ID do cliente
            veiculo_id (int): ID do veículo
            forma_pagamento_id (int): ID da forma de pagamento
            data_inicio (date): Data de início
            data_fim (date): Data de fim
        Returns:
            tuple: (sucesso: bool, mensagem: str, reserva_id: int|None)
        """
        try:
            # Validar datas
            if data_inicio < date.today():
                return False, 'Data de início não pode ser no passado!', None

            if data_fim <= data_inicio:
                return False, 'Data de fim deve ser posterior à data de início!', None

            # Verificar se veículo existe e está ativo
            veiculo = Veiculo.query.get(veiculo_id)
            if not veiculo:
                return False, 'Veículo não encontrado!', None

            if not veiculo.ativo:
                return False, 'Veículo indisponível para reserva!', None

            # Verificar disponibilidade
            disponivel, mensagem = self.verificar_disponibilidade(veiculo_id, data_inicio, data_fim)
            if not disponivel:
                return False, mensagem, None

            # Calcular valor total
            valor_total, quantidade_dias, erro = self.calcular_valor_total(veiculo_id, data_inicio, data_fim)
            if erro:
                return False, erro, None

            # Criar reserva
            nova_reserva = Reserva(
                cliente_id=cliente_id,
                veiculo_id=veiculo_id,
                forma_pagamento_id=forma_pagamento_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                valor_total=valor_total,
                status='confirmada'
            )

            db.session.add(nova_reserva)
            db.session.commit()

            return True, f'Reserva criada com sucesso! Total: €{valor_total:.2f} ({quantidade_dias} dias)', nova_reserva.id

        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar reserva: {e}")
            return False, f'Erro ao criar reserva: {str(e)}', None

    def get_reservas_cliente(self, cliente_id, status=None):
        """
        Retorna todas as reservas de um cliente.
        Args:
            cliente_id (int): ID do cliente
            status (str, optional): Filtrar por status específico
        Returns:
            list: Lista de dicionários com dados das reservas
        """
        try:
            query = db.session.query(Reserva).filter(Reserva.cliente_id == cliente_id)

            if status:
                query = query.filter(Reserva.status == status)

            reservas = query.order_by(Reserva.data_reserva.desc()).all()

            # Converter para dicionário com dados do veículo
            resultado = []
            for reserva in reservas:
                dados = {
                    'id': reserva.id,
                    'veiculo': {
                        'id': reserva.veiculo.id,
                        'marca': reserva.veiculo.marca,
                        'modelo': reserva.veiculo.modelo,
                        'imagem_url': reserva.veiculo.imagem_url,
                    },
                    'data_inicio': reserva.data_inicio.isoformat(),
                    'data_fim': reserva.data_fim.isoformat(),
                    'valor_total': float(reserva.valor_total),
                    'status': reserva.status,
                    'data_reserva': reserva.data_reserva.isoformat(),
                    'forma_pagamento': reserva.formas_pagamento.nome if reserva.formas_pagamento else 'N/A'
                }
                resultado.append(dados)

            return resultado

        except Exception as e:
            print(f"Erro ao buscar reservas do cliente: {e}")
            return []

    def get_by_id(self, reserva_id):
        """
        Busca reserva por ID.
        Args:
            reserva_id (int): ID da reserva
        Returns:
            Reserva: Objeto Reserva ou None
        """
        try:
            return Reserva.query.get(reserva_id)
        except Exception as e:
            print(f"Erro ao buscar reserva por ID: {e}")
            return None

    def editar_reserva(self, reserva_id, cliente_id, nova_data_inicio, nova_data_fim):
        """
        Edita as datas de uma reserva existente.
        Args:
            reserva_id (int): ID da reserva
            cliente_id (int): ID do cliente (para validação)
            nova_data_inicio (date): Nova data de início
            nova_data_fim (date): Nova data de fim
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            # Buscar reserva
            reserva = Reserva.query.get(reserva_id)
            if not reserva:
                return False, 'Reserva não encontrada!'

            # Verificar se a reserva pertence ao cliente
            if reserva.cliente_id != cliente_id:
                return False, 'Você não tem permissão para editar esta reserva!'

            # Verificar se a reserva pode ser editada
            if reserva.status not in ['confirmada', 'ativa']:
                return False, f'Reserva com status "{reserva.status}" não pode ser editada!'

            # Validar datas
            if nova_data_inicio < date.today():
                return False, 'Data de início não pode ser no passado!'

            if nova_data_fim <= nova_data_inicio:
                return False, 'Data de fim deve ser posterior à data de início!'

            # Verificar disponibilidade (excluindo a própria reserva)
            disponivel, mensagem = self.verificar_disponibilidade(
                reserva.veiculo_id,
                nova_data_inicio,
                nova_data_fim,
                reserva_id_excluir=reserva_id
            )
            if not disponivel:
                return False, mensagem

            # Recalcular valor total
            novo_valor, quantidade_dias, erro = self.calcular_valor_total(
                reserva.veiculo_id,
                nova_data_inicio,
                nova_data_fim
            )
            if erro:
                return False, erro

            # Atualizar reserva
            reserva.data_inicio = nova_data_inicio
            reserva.data_fim = nova_data_fim
            reserva.valor_total = novo_valor

            db.session.commit()

            return True, f'Reserva atualizada com sucesso! Novo valor: €{novo_valor:.2f} ({quantidade_dias} dias)'

        except Exception as e:
            db.session.rollback()
            print(f"Erro ao editar reserva: {e}")
            return False, f'Erro ao editar reserva: {str(e)}'

    def cancelar_reserva(self, reserva_id, cliente_id, motivo=''):
        """
        Cancela uma reserva.
        Args:
            reserva_id (int): ‘ID’ da reserva
            cliente_id (int): ‘ID’ do cliente (para validação)
            motivo (str, optional): Motivo do cancelamento
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            # Buscar reserva
            reserva = Reserva.query.get(reserva_id)
            if not reserva:
                return False, 'Reserva não encontrada!'

            # Verificar se a reserva pertence ao cliente
            if reserva.cliente_id != cliente_id:
                return False, 'Você não tem permissão para cancelar esta reserva!'

            # Verificar se a reserva pode ser cancelada
            if reserva.status == 'cancelada':
                return False, 'Esta reserva já foi cancelada!'

            if reserva.status == 'finalizada':
                return False, 'Reserva finalizada não pode ser cancelada!'

            # Cancelar reserva
            reserva.status = 'cancelada'
            reserva.data_cancelamento = datetime.utcnow()
            reserva.motivo_cancelamento = motivo if motivo else 'Cancelado pelo cliente'

            db.session.commit()

            return True, 'Reserva cancelada com sucesso!'

        except Exception as e:
            db.session.rollback()
            print(f"Erro ao cancelar reserva: {e}")
            return False, f'Erro ao cancelar reserva: {str(e)}'

    def get_estatisticas_cliente(self, cliente_id):
        """
        Retorna estatísticas de reservas do cliente.
        Args:
            cliente_id (int): ID do cliente
        Returns:
            dict: Estatísticas do cliente
        """
        try:
            reservas = Reserva.query.filter_by(cliente_id=cliente_id).all()

            total_reservas = len(reservas)
            total_gasto = sum(float(r.valor_total) for r in reservas if r.status != 'cancelada')
            reservas_ativas = len([r for r in reservas if r.status in ['confirmada', 'ativa']])
            reservas_canceladas = len([r for r in reservas if r.status == 'cancelada'])
            reservas_finalizadas = len([r for r in reservas if r.status == 'finalizada'])

            return {
                'total_reservas': total_reservas,
                'total_gasto': total_gasto,
                'reservas_ativas': reservas_ativas,
                'reservas_canceladas': reservas_canceladas,
                'reservas_finalizadas': reservas_finalizadas
            }

        except Exception as e:
            print(f"Erro ao calcular estatísticas: {e}")
            return {
                'total_reservas': 0,
                'total_gasto': 0,
                'reservas_ativas': 0,
                'reservas_canceladas': 0,
                'reservas_finalizadas': 0
            }