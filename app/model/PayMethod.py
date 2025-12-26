# -*- coding: utf-8 -*-
from app import db


''' Classe FormasPagamento para inserir as forma de pagamento'''
class PayMethod(db.Model):        # MB, MBway, CCredito,
    __tablename__ = 'formas_pagamento'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    ativo = db.Column(db.Boolean, default=True)
    # Relacionamentos
    reservas = db.relationship('Reserva', backref='formas_pagamento', lazy='dynamic')

    def __repr__(self):
        return self.nome

    def to_dict(self):
        if self.ativo == True:
            return {
                "id": self.id,
                "name": self.nome
            }
