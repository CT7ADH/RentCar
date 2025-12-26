# -*- coding: utf-8 -*-
from app.model.PayMethod import PayMethod
from app import db


class PayMethodControler():
    def __init__(self):
        self.method_pay_model = PayMethod()

    @staticmethod
    def get_all_method_pay():
        try:
            methods = PayMethod.query.all()
            return [m.to_dict() for m in methods]
        except Exception as e:
            print(e)
            return []
        finally:
            db.session.close()

