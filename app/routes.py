# -*- coding: utf-8 -*-
from app import app, db
from flask import render_template, url_for, request, redirect, flash, session
from datetime import datetime, date
from app.models import Cliente, Veiculo, Reserva, PayMethod # Esta linha tem que ser apagada, quando se finalizar o controler
from app.controller import PayMethodControler, ClienteControler, VeiculoControler, ReservaControler, AuthController
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from sqlalchemy import or_, and_
from app.car_admin import extrair_dados_formulario, validar_todos_dados, salvar_imagem, criar_veiculo_no_banco

''' -------------------------------------------------------------------------------------------------- '''

@app.route("/")
@app.route("/index", methods=["GET", "POST"])
def root():
    """ Página Inicial """
    if current_user.is_authenticated:
        return redirect(url_for('root'))

    if request.method == 'POST':
        pass
    else:

        context = VeiculoControler().get_all_veiculos()
        return render_template("index.html", context=context)


@app.route("/car_list", methods=["GET", "POST"])
def car_list():
    """ Listagem de veículos com filtros """
    if request.method == 'POST':
        pass
    else:
        '''
        # Buscar todos os veículos ativos
        query = Veiculo.query.filter_by(ativo=True)

        # Aplicar filtros se existirem
        categoria = request.args.get('categoria')
        transmissao = request.args.get('transmissao')
        tipo_veiculo = request.args.get('tipo_veiculo')
        capacidade = request.args.get('capacidade')
        preco_min = request.args.get('preco_min')
        preco_max = request.args.get('preco_max')
        busca = request.args.get('busca')

        if categoria:
            query = query.filter_by(categoria=categoria)

        if transmissao:
            query = query.filter_by(transmissao=transmissao)

        if tipo_veiculo:
            query = query.filter_by(tipo_veiculo=tipo_veiculo)

        if capacidade:
            if capacidade == '1-4':
                query = query.filter(Veiculo.capacidade_pessoas.between(1, 4))
            elif capacidade == '5-6':
                query = query.filter(Veiculo.capacidade_pessoas.between(5, 6))
            elif capacidade == '7+':
                query = query.filter(Veiculo.capacidade_pessoas >= 7)

        if preco_min:
            query = query.filter(Veiculo.valor_diaria >= float(preco_min))

        if preco_max:
            query = query.filter(Veiculo.valor_diaria <= float(preco_max))

        if busca:
            query = query.filter(
                or_(
                    Veiculo.marca.ilike(f'%{busca}%'),
                    Veiculo.modelo.ilike(f'%{busca}%')
                )
            )
        '''
        # Filtrar apenas veículos disponíveis (inspeção e revisão em dia)

        context = VeiculoControler().get_all_veiculos()
        return render_template("car_list.html", context=context)


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Rota de login """
    if current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        sucesso, mensagem, usuario = AuthController.autenticar_usuario(email=email.lower(), password=password)

        if sucesso:
            flash(mensagem, 'success')
            return redirect(url_for('car_list'))
        else:
            flash(mensagem, 'danger')

    return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    """Rota de logout"""
    sucesso, mensagem = AuthController.fazer_logout()
    flash(mensagem, 'info')
    return redirect(url_for('login'))


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    """ Registro de novos clientes """
    if current_user.is_authenticated:
        return redirect(url_for('registration'))

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        birth_date = datetime.strptime(request.form["birth_date"], '%Y-%m-%d').date()
        password = request.form["password"]
        re_pass = request.form["re_pass"]

        # Criar novo Cliente
        sucesso, mensagem = AuthController.registrar_usuario(
            name=name.title(),
            email=email.lower(),
            password=password,
            re_pass=re_pass,
            phone=phone,
            birth_date=birth_date,
        )

        if sucesso:
            flash(mensagem, 'success')
            return redirect(url_for('login'))
        else:
            flash(mensagem, 'danger')
    return render_template("registration.html")


@app.route("/reserva")
def reserva():

    return render_template("reserva.html", data={'status': 200, 'msg': None, 'type': None})

# Talvez se tenha que apagar
@app.route("/reserva/<veiculo_id>", methods=["GET", "POST"])
def reserva_id(veiculo_id):
    """Criar nova reserva"""
    veiculo = Veiculo.query.get_or_404(veiculo_id)
    formas_pagamento = PayMethod.query.filter_by(ativo=True).all()
    hoje = date.today().strftime('%Y-%m-%d')
    
    if request.method == "POST":
        try:
            # Coletar dados do formulário
            data_inicio = datetime.strptime(request.form["data_inicio"], '%Y-%m-%d').date()
            data_fim = datetime.strptime(request.form["data_fim"], '%Y-%m-%d').date()
            forma_pagamento_id = request.form["forma_pagamento_id"]
            
            # Validações
            if data_inicio < date.today():
                flash('A data de início não pode ser no passado!', 'danger')
                return redirect(url_for('reserva', veiculo_id=veiculo_id))
            
            if data_fim <= data_inicio:
                flash('A data de fim deve ser posterior à data de início!', 'danger')
                return redirect(url_for('reserva', veiculo_id=veiculo_id))
            
            # Verificar disponibilidade do veículo
            if not veiculo.is_disponivel(data_inicio, data_fim):
                flash('Este veículo não está disponível para as datas selecionadas!', 'danger')
                return redirect(url_for('car_list'))
            
            # Calcular valor total
            dias = (data_fim - data_inicio).days
            valor_total = float(veiculo.valor_diaria) * dias
            
            # Criar reserva
            reserva = Reserva(
                cliente_id=session['user_id'],
                veiculo_id=veiculo_id,
                forma_pagamento_id=forma_pagamento_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                valor_total=valor_total,
                status='confirmada'
            )
            
            db.session.add(reserva)
            db.session.commit()
            
            flash(f'Reserva confirmada! Valor total: €{valor_total:.2f}', 'success')
            return redirect(url_for('minhas_reservas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar reserva: {str(e)}', 'danger')
    
    return render_template("reserva.html", veiculo=veiculo, formas_pagamento=formas_pagamento, today=hoje)

'''
@app.route("/minhas-reservas")
@login_required
def minhas_reservas():
    """Listar reservas do cliente logado"""
    reservas = Reserva.query.filter_by(cliente_id=session['user_id']).order_by(Reserva.data_reserva.desc()).all()
    return render_template("minhas_reservas.html", reservas=reservas)


@app.route("/editar-reserva/<int:reserva_id>", methods=["GET", "POST"])
@login_required
def editar_reserva(reserva_id):
    """Editar datas de uma reserva"""
    reserva = Reserva.query.get_or_404(reserva_id)
    
    # Verificar se a reserva pertence ao cliente logado
    if reserva.cliente_id != session['user_id']:
        flash('Você não tem permissão para editar esta reserva!', 'danger')
        return redirect(url_for('minhas_reservas'))
    
    # Não permitir edição de reservas canceladas ou finalizadas
    if reserva.status in ['cancelada', 'finalizada']:
        flash('Esta reserva não pode ser editada!', 'warning')
        return redirect(url_for('minhas_reservas'))
    
    if request.method == "POST":
        try:
            nova_data_inicio = datetime.strptime(request.form["data_inicio"], '%Y-%m-%d').date()
            nova_data_fim = datetime.strptime(request.form["data_fim"], '%Y-%m-%d').date()
            
            # Validações
            if nova_data_inicio < date.today():
                flash('A data de início não pode ser no passado!', 'danger')
                return redirect(url_for('editar_reserva', reserva_id=reserva_id))
            
            if nova_data_fim <= nova_data_inicio:
                flash('A data de fim deve ser posterior à data de início!', 'danger')
                return redirect(url_for('editar_reserva', reserva_id=reserva_id))
            
            # Verificar disponibilidade (excluindo a reserva atual)
            reservas_conflitantes = Reserva.query.filter(
                Reserva.veiculo_id == reserva.veiculo_id,
                Reserva.id != reserva_id,
                Reserva.status.in_(['confirmada', 'ativa']),
                or_(
                    and_(Reserva.data_inicio <= nova_data_inicio, Reserva.data_fim > nova_data_inicio),
                    and_(Reserva.data_inicio < nova_data_fim, Reserva.data_fim >= nova_data_fim),
                    and_(Reserva.data_inicio >= nova_data_inicio, Reserva.data_fim <= nova_data_fim)
                )
            ).first()
            
            if reservas_conflitantes:
                flash('O veículo não está disponível para as novas datas!', 'danger')
                return redirect(url_for('editar_reserva', reserva_id=reserva_id))
            
            # Atualizar reserva
            reserva.data_inicio = nova_data_inicio
            reserva.data_fim = nova_data_fim
            
            # Recalcular valor total
            dias = (nova_data_fim - nova_data_inicio).days
            reserva.valor_total = float(reserva.veiculo.valor_diaria) * dias
            
            db.session.commit()
            
            flash('Reserva atualizada com sucesso!', 'success')
            return redirect(url_for('minhas_reservas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao editar reserva: {str(e)}', 'danger')
    
    return render_template("editar_reserva.html", reserva=reserva)


@app.route("/cancelar-reserva/<int:reserva_id>", methods=["POST"])
@login_required
def cancelar_reserva(reserva_id):
    """Cancelar uma reserva"""
    reserva = Reserva.query.get_or_404(reserva_id)
    
    # Verificar se a reserva pertence ao cliente logado
    if reserva.cliente_id != session['user_id']:
        flash('Você não tem permissão para cancelar esta reserva!', 'danger')
        return redirect(url_for('minhas_reservas'))
    
    # Não permitir cancelamento de reservas já canceladas ou finalizadas
    if reserva.status in ['cancelada', 'finalizada']:
        flash('Esta reserva não pode ser cancelada!', 'warning')
        return redirect(url_for('minhas_reservas'))
    
    try:
        motivo = request.form.get('motivo', 'Cancelamento solicitado pelo cliente')
        
        reserva.status = 'cancelada'
        reserva.data_cancelamento = datetime.utcnow()
        reserva.motivo_cancelamento = motivo
        
        db.session.commit()
        
        flash('Reserva cancelada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cancelar reserva: {str(e)}', 'danger')
    
    return redirect(url_for('minhas_reservas'))
'''

@app.route("/contact")
def contact():
    """Página de contato"""
    return render_template("contact.html")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Administração de veículos"""

    if request.method == "POST":
        try:
            # 1. Extrair dados do formulário
            dados, erro = extrair_dados_formulario(request.form)
            if erro:
                flash(erro, 'danger')
                return redirect(url_for('admin'))

            # 2. Validar todos os dados
            valido, mensagem = validar_todos_dados(dados)
            if not valido:
                flash(mensagem, 'danger')
                return redirect(url_for('admin'))

            # 3. Processar imagem
            imagem = request.files.get('imagem')
            sucesso, filename, mensagem = salvar_imagem(imagem, app.static_folder)
            if not sucesso:
                flash(mensagem, 'danger')
                return redirect(url_for('admin'))

            # 4. Criar veículo no banco
            criar_veiculo_no_banco(dados, filename, db)

            # 5. Sucesso!
            flash('Veículo registrado com sucesso!', 'success')
            return redirect(url_for('admin'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar veículo: {str(e)}', 'danger')
            print(f"ERRO: {e}")
            return redirect(url_for('admin'))

    return render_template("admin.html")



# @app.route('/dashboard')
# @login_required
# def dashboard():
#     """Dashboard do usuário (rota protegida)"""
#     return render_template('dashboard.html', usuario=current_user)
