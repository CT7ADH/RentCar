# -*- coding: utf-8 -*-
from app.model.PayMethod import PayMethod
from app import db


class PayMethodControler():
    """Controller para gerenciar métodos de pagamento"""

    def __init__(self):
        self.method_pay_model = PayMethod()

    # ==================== MÉTODOS DE CLASSE (CLASS METHODS) ====================

    def get_all_method_pay(self):
        """
        Retorna todos os métodos de pagamento ativos.
        Returns:
            list: Lista de dicionários com métodos de pagamento
        """
        try:
            methods = self.method_pay_model.query.filter_by(ativo=True).all()
            return [m.to_dict() for m in methods]
        except Exception as e:
            print(f"Erro ao buscar métodos de pagamento: {e}")
            return []

    def get_by_id(self, method_id):
        """
        Busca method de pagamento por ID.
        Args:
            method_id (int): ID do method
        Returns:
            PayMethod: Objeto PayMethod ou None
        """
        try:
            return self.method_pay_model.query.get(method_id)
        except Exception as e:
            print(f"Erro ao buscar método de pagamento por ID: {e}")
            return None