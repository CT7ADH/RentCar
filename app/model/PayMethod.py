# -*- coding: utf-8 -*-
# 1. Importações
from app import db

class PayMethod(db.Model): # MB, MBway, CCredito,
    """Modelo para registar as formas de pagamento"""

    __tablename__ = 'formas_pagamento'

    # Campos do modelo
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    ativo = db.Column(db.Boolean, default=True)
    # Relacionamentos
    reservas = db.relationship('Reserva', backref='formas_pagamento', lazy='dynamic')

    def to_dict(self):
        if self.ativo == True:
            return {
                "id": self.id,
                "name": self.nome
            }

    def __repr__(self):
        return self.nome