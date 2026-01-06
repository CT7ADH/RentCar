# -*- coding: utf-8 -*-
# 1. Importações
from app.model.Cliente import Cliente

class ClienteControler():
    """Controller para gerenciar operações de clientes"""

    def __init__(self):
        self.cliente_model = Cliente()

    # ==================== MÉTODOS DE CLASSE (CLASS METHODS) ====================

    def validate_email(self, email):
        """
        Valida se o email já existe no banco.
        Args:
            email (str): Email a verificar
        Returns:
            bool: True se email é válido (não existe), False caso contrário
        """
        return Cliente.query.filter_by(email=email).first() is None

    def get_by_id(self, cliente_id):
        """
        Busca cliente por ID.
        Args:
            cliente_id (int): ID do cliente
        Returns:
            Cliente: Objeto Cliente ou None
        """
        try:
            return Cliente.query.get(cliente_id)
        except Exception as e:
            print(f"Erro ao buscar cliente por ID: {e}")
            return None

    def get_by_email(self, email):
        """
        Busca cliente por email.
        Args:
            email (str): Email do cliente
        Returns:
            Cliente: Objeto Cliente ou None
        """
        try:
            return Cliente.query.filter_by(email=email).first()
        except Exception as e:
            print(f"Erro ao buscar cliente por email: {e}")
            return None
