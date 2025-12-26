# -*- coding: utf-8 -*-
from app.model.Reserva import Reserva
from app import db


class ReservaControler():
    def __init__(self):
        self.reserva_model = Reserva()
