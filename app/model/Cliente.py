# -*- coding: utf-8 -*-
from datetime import datetime
from app import db, bcrypt, login_manager
from flask_login import UserMixin

''' Função para recuperar o usuario para sessão desde Cliente'''
@login_manager.user_loader
def load_user(user_id):
    return Cliente.query.get(user_id)

''' Classe Cliente para registar os clientes'''
class Cliente(db.Model, UserMixin):
    __tablename__ = 'clientes'

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


    def set_password(self, password):
        """Define a Password do usuário (criptografada)"""
        self.pass_hash = bcrypt.generate_password_hash(password.encode('utf-8'))

    def check_password(self, password):
        """Verifica se a Password está correta"""
        return bcrypt.check_password_hash(self.pass_hash, password)

    def __repr__(self):
        return f'<Usuario {self.name}'
