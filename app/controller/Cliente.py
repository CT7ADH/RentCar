# -*- coding: utf-8 -*-
from app.model.Cliente import Cliente
from app import db

class ClienteControler():
    def __init__(self):
        self.cliente_model = Cliente()

    def validate_email(self, email):
        if Cliente.query.filter(email=email.data).first():
            return
