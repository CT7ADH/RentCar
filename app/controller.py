# -*- coding: utf-8 -*-
from datetime import date, timedelta
from app import db
from flask_login import login_user, logout_user

from app.models import Cliente, Veiculo, PayMethod, Reserva
''' -------------------------------------------------------------------------------------------------- '''

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


''' -------------------------------------------------------------------------------------------------- '''
class ClienteControler():
    def __init__(self):
        self.cliente_model = Cliente()

    def validate_email(self, email):
        if Cliente.query.filter(email=email.data).first():
            return


''' -------------------------------------------------------------------------------------------------- '''
class VeiculoControler():
    def __init__(self):
        self.veiculo_model = Veiculo()

    def get_veiculos(self, limit):
        result = []
        try:
            res = self.veiculo_model.get_all(limit=limit)

            for r in res:
                result.append({
                    'id': r.id,
                    'marca': r.marca,
                    'modelo': r.modelo,
                    'categoria': r.categoria,
                    'transmissao':r.transmissao,
                    'tipo_veiculo': r.tipo_veiculo,
                    'capacidade_pessoas': r.capacidade_pessoas,
                    'valor_diaria' : r.valor_diaria,
                    'imagem_url' : r.imagem_url,
                    'cor' : r.cor,
                    'ano' : r.ano,
                    'kilometragem': r.kilometragem,
                    'ativo' : r.ativo

                })

        except Exception as e:
            print(e)
            result = []
        finally:
            return result

    def get_used_categorias(self):
        """Retorna categorias únicas de veículos ativos"""
        try:
            result = Veiculo.get_categorias_ativas()
        except Exception as e:
            print(f"Erro ao buscar categorias: {e}")
            result = []
        finally:
            return result

    def is_disponivel(self, data_inicio=None, data_fim=None):
        """Verifica se o veículo está disponível"""
        if not self.ativo:
            return False

        # Verifica se a inspeção está em dia (não pode ser superior a 1 ano)
        data_limite_inspecao = self.data_ultima_inspecao + timedelta(days=365)
        if date.today() > data_limite_inspecao:
            return False

        # Verifica se não passou da data da próxima revisão
        if date.today() > self.data_proxima_revisao:
            return False

        # Se data_inicio e data_fim foram fornecidas, verifica conflitos de reserva
        if data_inicio and data_fim:
            reservas_conflitantes = Reserva.query.filter(
                Reserva.veiculo_id == self.id,
                Reserva.status.in_(['confirmada', 'ativa']),
                db.or_(
                    db.and_(Reserva.data_inicio <= data_inicio, Reserva.data_fim > data_inicio),
                    db.and_(Reserva.data_inicio < data_fim, Reserva.data_fim >= data_fim),
                    db.and_(Reserva.data_inicio >= data_inicio, Reserva.data_fim <= data_fim)
                )
            ).first()

            if reservas_conflitantes:
                return False

        return True


''' -------------------------------------------------------------------------------------------------- '''
class ReservaControler():
    def __init__(self):
        self.reserva_model = Reserva()


''' -------------------------------------------------------------------------------------------------- '''
class AuthController:

    @staticmethod
    def registrar_usuario(name, email, password, re_pass, phone, birth_date):
        """
        Registra um novo usuário no sistema
        Retorna: (sucesso: bool, mensagem: str)
        """
        # Verifica se usuário já existe
        if Cliente.query.filter_by(name=name).first():
            return False, 'Nome de usuário já existe!'

        if Cliente.query.filter_by(email=email).first():
            return False, 'Email já cadastrado!'

        # Validação básica
        if len(password) < 6:
            return False, 'A senha deve ter pelo menos 6 caracteres!'
        if password != re_pass:
            return False, 'Passwords não coincidem!'

        if not name or not email:
            return False, 'Todos os campos são obrigatórios!'

        # Cria novo usuário
        try:
            novo_usuario = Cliente(name=name, email=email, pass_hash=password, phone=phone, birth_date=birth_date)
            novo_usuario.set_password(password)

            db.session.add(novo_usuario)
            db.session.commit()

            return True, 'Registro realizado com sucesso!'
        except Exception as e:
            db.session.rollback()
            return False, f'Erro ao registrar usuário: {str(e)}'

    @staticmethod
    def autenticar_usuario(email, password):
        """
        Autentica um usuário
        Retorna: (sucesso: bool, mensagem: str, usuario: Usuario ou None)
        """
        if not email or not password:
            return False, 'Preencha todos os campos!', None

        usuario = Cliente.query.filter_by(email=email).first()

        if not usuario:
            return False, 'Usuário não encontrado!', None

        if not usuario.check_password(password):
            return False, 'Senha incorreta!', None

        # Faz login
        login_user(usuario)
        return True, 'Login realizado com sucesso!', usuario

    @staticmethod
    def fazer_logout():
        """Realiza o logout do usuário"""
        logout_user()
        return True, 'Logout realizado com sucesso!'