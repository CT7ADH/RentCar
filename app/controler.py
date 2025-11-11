from app.models import Cliente, Veiculo, FormasPagamento, Reserva
from app import db
from datetime import date, timedelta
''' -------------------------------------------------------------------------------------------------- '''

class FormasPagamentoControler():
    def __init__(self):
        self.form_pagamento_model = FormasPagamento()


class ClienteControler():
    def __init__(self):
        self.cliente_model = Cliente()


class VeiculoControler():
    def __init__(self):
        self.veiculo_model = Veiculo()

    @classmethod
    def get_all_veiculos(cls):
        try:
            res = db.session.query(Veiculo).all()
        except Exception as e:
            res = []
            print(e)
        finally:
            db.session.close()
            return res

    def get_used_categorias(self):
        try:
            res = db.session.query.get(Veiculo.categoria)
        except Exception as e:
            res = []
            print(e)
        finally:
            db.session.close()
            return res

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




class ReservaControler():
    def __init__(self):
        self.reserva_model = Reserva()

