# -*- coding: utf-8 -*-
# 1. Importações
from datetime import datetime
from app import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    """Função para recuperar o usuario para sessão"""
    return Cliente.query.get(int(user_id))

class Cliente(db.Model, UserMixin):
    """Modelo para registar os clientes"""

    __tablename__ = 'clientes'

    # Campos do modelo
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

    def to_dict(self, incluir_sensiveis=False):
        """
        Converte o objeto Cliente para dicionário.
        Args:
            incluir_sensiveis (bool): Se True, inclui dados sensíveis
        Returns:
            dict: Dicionário com dados do cliente
        """
        dados = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'city': self.city,
            'genero': self.genero,
            'date_created': self.date_created.isoformat() if self.date_created else None,
        }

        # Dados sensíveis apenas se solicitado
        if incluir_sensiveis:
            dados.update({
                'birth_date': self.birth_date.isoformat() if self.birth_date else None,
                'postal_code': self.postal_code,
            })

        return dados

    def __repr__(self):
        return f'<Cliente {self.name} - {self.email}>'

    # ==================== MÉTODOS DE CLASSE (CLASS METHODS) ====================

    def set_password(self, password):
        """
        Define a password do usuário (criptografada).

        Args:
            password (str): Password em texto plano
        """
        self.pass_hash = bcrypt.generate_password_hash(password.encode('utf-8')).decode('utf-8')

    def check_password(self, password):
        """
        Verifica se a password está correta.
        Args:
            password (str): Password em texto plano
        Returns:
            bool: True se a password está correta
        """
        return bcrypt.check_password_hash(self.pass_hash, password)