from datetime import datetime, date, timedelta

from flask_migrate import check

from app import db, bcrypt

"""
uma vez comfiguradas todas as tabelas para criar a base de dados temos que rodar o comando "flask db init", 
só se roda este comando uma vez por projecto.
- fazer o migrate despois de qualquer alteração: 'flask db migrate -m "[mensagem migrate]"
- salvar o commit no banco de Dados: flask db upgrade
"""
''' Classe Cliente para registo dos clientes'''
class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pass_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    registration_data = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    reservas = db.relationship('Reserva', backref='cliente', lazy='dynamic')

    def set_password(self, password):
        self.pass_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.pass_hash, password)

''' Classe Veiculo para registo dos Veiculos da empresa'''
class Veiculo(db.Model):
    __tablename__ = 'veiculos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    categoria = db.Column(db.String(20), nullable=False)  # Pequeno, Médio, Grande, SUV, Luxo
    transmissao = db.Column(db.String(20), nullable=False)  # Automatico, Manual
    tipo_veiculo = db.Column(db.String(10), nullable=False)  # Carro, Moto
    capacidade_pessoas = db.Column(db.Integer, nullable=False)
    valor_diaria = db.Column(db.Numeric(10, 2), nullable=False)
    imagem_url = db.Column(db.String(255), nullable=True)
    matricula = db.Column(db.String(10), unique=True, nullable=False)
    cor = db.Column(db.String(30), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    kilometragem = db.Column(db.Integer, default=0)

    # Datas importantes para disponibilidade
    data_ultima_revisao = db.Column(db.Date, nullable=False)
    data_proxima_revisao = db.Column(db.Date, nullable=False)
    data_ultima_inspecao = db.Column(db.Date, nullable=False)

    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    reservas = db.relationship('Reserva', backref='veiculo', lazy=True)

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


''' Classe FormasPagamento onde se regista as forma de pagamento'''
class FormasPagamento(db.Model):        # MB, MBway, CCredito,
    __tablename__ = 'formas_pagamento'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamentos
    reservas = db.relationship('Reserva', backref='formas_pagamento', lazy='dynamic')

''' Classe Reserva para registo dos Veiculos da empresa'''
class Reserva(db.Model):
    __tablename__ = 'reservas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('formas_pagamento.id'), nullable=False)

    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='confirmada')  # confirmada, ativa, finalizada, cancelada

    data_reserva = db.Column(db.DateTime, default=datetime.utcnow)
    data_cancelamento = db.Column(db.DateTime, nullable=True)
    motivo_cancelamento = db.Column(db.Text, nullable=True)

    def calcular_valor_total(self):
        """Calcula o valor total baseado no número de dias"""
        if self.data_inicio and self.data_fim and self.veiculo:
            dias = (self.data_fim - self.data_inicio).days
            if dias <= 0:
                dias = 1
            return float(self.veiculo.valor_diaria) * dias
        return 0.0

    def get_numero_dias(self):
        """Retorna o número de dias da reserva"""
        if self.data_inicio and self.data_fim:
            dias = (self.data_fim - self.data_inicio).days
            return dias if dias > 0 else 1
        return 0


