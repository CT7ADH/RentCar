# -*- coding: utf-8 -*-
from app import app
from app.controller import PayMethodControler, ClienteControler, VeiculoControler, ReservaControler


with app.app_context():

    context = PayMethodControler.get_all_method_pay()
    #context = VeiculoControler.get_all_veiculos()
    print(context)