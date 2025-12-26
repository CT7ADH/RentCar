# -*- coding: utf-8 -*-
from app.model.Cliente import Cliente
from flask_login import login_user, logout_user
from app import db

class AuthController:

    @staticmethod
    def registrar_usuario(name, email, password, re_pass, phone, birth_date, city, postal_code, genero):
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
            novo_usuario = Cliente(name=name, email=email, phone=phone, birth_date=birth_date, city=city, postal_code=postal_code, genero=genero, pass_hash=password)
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