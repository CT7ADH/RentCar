# -*- coding: utf-8 -*-
# 1. Importações do Flask e Python
from app import app, db
from flask import render_template, url_for, request, redirect, flash, session, jsonify
from datetime import datetime, date
from flask_login import login_required, current_user

# 2. Importação do Admin
from app.car_admin import extrair_dados_formulario, validar_todos_dados, salvar_imagem, criar_veiculo_no_banco

# 3. Importações dos Controllers
from app.controller import ClienteControler, VeiculoControler, ReservaControler, AuthController, PayMethodControler

''' ---------------------------------------- Página Inicial ---------------------------------------- '''
@app.route("/")
@app.route("/index", methods=["GET", "POST"])
def root():
    '''
    VERIFICAÇÃO AUTOMÁTICA DE INSPEÇÕES EXPIRADAS
    Se a data da última inspeção for superior a 1 ano da data atual,
    o veículo passa a indisponível. Em Produção alterar esta função para rodar uma "task scheduler"
    '''
    try:
        quantidade, mensagem = VeiculoControler().check_is_activo()

        # Opcional: registrar em log ou mostrar flash message apenas se houver desativações
        if quantidade > 0:
            print(f"ATENÇÃO: {mensagem}")
            #flash(mensagem, 'warning')  # avisa o usuário
    except Exception as e:
        print(f"Erro na verificação automática: {e}")
    '''
    Função para quando há user logado
    '''
    if current_user.is_authenticated:
        return redirect(url_for('car_list'))

    if request.method == 'POST':
        pass
    else:   # Method GET:> mostra todos os veículos

        veiculos = VeiculoControler().get_all_activo(limit=10)
        categories = VeiculoControler().get_used_categorias()
        context = {
            'veiculos': veiculos,
            'categories': categories,
        }
        return render_template("index.html", context=context)

''' ---------------------------------------- Listagem de veículos com filtros ---------------------------------------- '''
@app.route("/car_list", methods=["GET", "POST"])
def car_list():

    if request.method == 'POST':
        search_type = request.form.get("ordenar")
        filtro_valor = request.form.get("filtro_valor")

        # Buscar as opções para o select de filtro baseado no tipo
        if search_type and search_type != "None":
            search_result = VeiculoControler().get_search_type(arg_search=search_type)
        else:
            search_result = []

        # Se houver um valor de filtro específico, filtrar os veículos
        if filtro_valor and filtro_valor != "":
            veiculos_filtrados = VeiculoControler().get_veiculos_filtrados(search_type, filtro_valor)
        else:
            # Se só selecionou o tipo, mas não o valor, mostrar todos
            veiculos_filtrados = VeiculoControler().get_all(limit=None)

        context = {
            'veiculos' : veiculos_filtrados,
            'search_result' : search_result,
            'ordenar' : search_type,
            'filtro_selecionado' : filtro_valor
        }

        return render_template(
            "car_list.html", context=context)
    else:   # Method GET:>
        # GET - mostra todos os veículos
        veiculos = VeiculoControler().get_all_activo(limit=None)
        search_result = []
        categories = VeiculoControler().get_used_categorias()
        context = {
            'veiculos' : veiculos,
            'search_result' : search_result,
            'categories': categories,
        }
        return render_template("car_list.html", context=context)

''' ---------------------------------------- Rota de login ---------------------------------------- '''
@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('car_list'))

    if request.method == 'POST':

        login_data = {
            "email": request.form["email"].lower(),
            "password": request.form["password"]
        }
        # use o desempacotamento de dicionário (**)
        sucesso, mensagem, usuario = AuthController.autenticar_usuario(**login_data)

        if sucesso:
            flash(mensagem, 'success')
            return redirect(url_for('car_list'))
        else:
            flash(mensagem, 'danger')
            return render_template('login.html', context=login_data)

    else:   # Method GET:>
        return render_template('login.html', context={})

''' ---------------------------------------- Logout da sessão de usuário ---------------------------------------- '''
@app.route("/logout")
@login_required
def logout():
    # logout do usuario
    sucesso, mensagem = AuthController.fazer_logout()
    flash(mensagem, 'info')
    return redirect(url_for('login'))

''' ---------------------------------------- Registro de novos clientes ---------------------------------------- '''
@app.route("/registration", methods=['GET', 'POST'])
def registration():
    # if current_user.is_authenticated:
    #     return redirect(url_for('registration'))

    if request.method == "POST":

        # 1. Extrair e processar os dados do formulário em um Dicionário
        dados_usuario = {
            "name": request.form["name"].title(),  # Aplica title() logo na extração
            "email": request.form["email"].lower(),  # Aplica lower() logo na extração
            "phone": request.form["phone"],
            # Converte a string de data para objeto date()
            "birth_date": datetime.strptime(request.form["birth_date"], '%Y-%m-%d').date(),
            "city": request.form["cidade"].title(),
            "postal_code": request.form["codigo_postal"],
            "genero": request.form["genero"],
            "password": request.form["password"],
            "re_pass": request.form["re_pass"],
        }

        # 2. Chamar o méthod de registro passando o dicionário (melhor prática, se o AuthController aceitar kwargs)
        # ATENÇÃO: Se o AuthController só aceitar argumentos nomeados (como no seu código original),
        # use o desempacotamento de dicionário (**)

        sucesso, mensagem = AuthController.registrar_usuario(**dados_usuario)

        if sucesso:
            flash(mensagem, 'success')
            return redirect(url_for('login'))
        else:
            flash(mensagem, 'danger')
            return render_template("registration.html", dados=dados_usuario)
    else:   # Method GET:>
        return render_template("registration.html", dados={})

''' ---------------------------------------- Minhas Reservas - Lista ---------------------------------------- '''
@app.route("/minhas-reservas")
@login_required
def minhas_reservas():
    '''
    Página para visualizar todas as reservas do cliente logado
    '''
    try:
        # Buscar reservas do cliente
        reservas = ReservaControler().get_reservas_cliente(current_user.id)

        # Buscar estatísticas
        estatisticas = ReservaControler().get_estatisticas_cliente(current_user.id)

        context = {
            'reservas': reservas,
            'estatisticas': estatisticas
        }

        return render_template("minhas_reservas.html", context=context)

    except Exception as e:
        print(f"Erro ao carregar reservas: {e}")
        flash('Erro ao carregar suas reservas. Tente novamente.', 'danger')
        return redirect(url_for('car_list'))

''' ---------------------------------------- Criar nova reserva - Form ---------------------------------------- '''
@app.route("/reserva/<int:id>", methods=["GET", "POST"])
@login_required
def cria_reserva(id):
    '''
    Página para criar uma nova reserva
    '''
    if request.method == "POST":
        try:
            # Extrair dados do formulário
            data_inicio_str = request.form.get("data_inicio")
            data_fim_str = request.form.get("data_fim")
            forma_pagamento_id = request.form.get("forma_pagamento")

            # Validação básica
            if not data_inicio_str or not data_fim_str or not forma_pagamento_id:
                flash('Preencha todos os campos obrigatórios!', 'danger')
                return redirect(url_for('cria_reserva', id=id))

            # Converter datas
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()

            # Criar reserva
            sucesso, mensagem, reserva_id = ReservaControler().criar_reserva(
                cliente_id=current_user.id,
                veiculo_id=id,
                forma_pagamento_id=int(forma_pagamento_id),
                data_inicio=data_inicio,
                data_fim=data_fim
            )

            if sucesso:
                flash(mensagem, 'success')
                return redirect(url_for('minhas_reservas'))
            else:
                flash(mensagem, 'danger')
                return redirect(url_for('cria_reserva', id=id))

        except ValueError as e:
            flash('Formato de data inválido!', 'danger')
            return redirect(url_for('cria_reserva', id=id))
        except Exception as e:
            print(f"Erro ao criar reserva: {e}")
            flash('Erro ao criar reserva. Tente novamente.', 'danger')
            return redirect(url_for('cria_reserva', id=id))

    # GET - Mostrar formulário
    veiculo = VeiculoControler().get_by_id(id)

    if not veiculo:
        flash('Veículo não encontrado!', 'danger')
        return redirect(url_for('car_list'))

    # Buscar formas de pagamento
    formas_pagamento = PayMethodControler().get_all_method_pay()

    context = {
        'car': veiculo,
        'formas_pagamento': formas_pagamento,
        'data_hoje': date.today().isoformat()
    }

    return render_template("reserva1.html", context=context)

''' ---------------------------------------- Editar Reserva ---------------------------------------- '''
@app.route("/editar-reserva/<int:id>", methods=["GET", "POST"])
@login_required
def editar_reserva(id):
    '''
    Página para editar uma reserva existente
    '''
    if request.method == "POST":
        try:
            # Extrair novas datas
            nova_data_inicio_str = request.form.get("data_inicio")
            nova_data_fim_str = request.form.get("data_fim")

            if not nova_data_inicio_str or not nova_data_fim_str:
                flash('Preencha todos os campos!', 'danger')
                return redirect(url_for('editar_reserva', id=id))

            # Converter datas
            nova_data_inicio = datetime.strptime(nova_data_inicio_str, '%Y-%m-%d').date()
            nova_data_fim = datetime.strptime(nova_data_fim_str, '%Y-%m-%d').date()

            # Editar reserva
            sucesso, mensagem = ReservaControler().editar_reserva(
                reserva_id=id,
                cliente_id=current_user.id,
                nova_data_inicio=nova_data_inicio,
                nova_data_fim=nova_data_fim
            )

            if sucesso:
                flash(mensagem, 'success')
                return redirect(url_for('minhas_reservas'))
            else:
                flash(mensagem, 'danger')
                return redirect(url_for('editar_reserva', id=id))

        except Exception as e:
            print(f"Erro ao editar reserva: {e}")
            flash('Erro ao editar reserva. Tente novamente.', 'danger')
            return redirect(url_for('editar_reserva', id=id))

    # GET - Mostrar formulário de edição
    reserva = ReservaControler().get_by_id(id)

    if not reserva:
        flash('Reserva não encontrada!', 'danger')
        return redirect(url_for('minhas_reservas'))

    # Verificar se a reserva pertence ao usuário
    if reserva.cliente_id != current_user.id:
        flash('Você não tem permissão para editar esta reserva!', 'danger')
        return redirect(url_for('minhas_reservas'))

    context = {
        'reserva': reserva,
        'data_hoje': date.today().isoformat()
    }

    return render_template("editar_reserva.html", context=context)

''' ---------------------------------------- Cancelar Reserva ---------------------------------------- '''
@app.route("/cancelar-reserva/<int:id>", methods=["POST"])
@login_required
def cancelar_reserva(id):
    '''
    Rota para cancelar uma reserva
    '''
    try:
        motivo = request.form.get("motivo", "")

        sucesso, mensagem = ReservaControler().cancelar_reserva(
            reserva_id=id,
            cliente_id=current_user.id,
            motivo=motivo
        )

        if sucesso:
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'danger')

    except Exception as e:
        print(f"Erro ao cancelar reserva: {e}")
        flash('Erro ao cancelar reserva. Tente novamente.', 'danger')

    return redirect(url_for('minhas_reservas'))

''' ---------------------------------------- API - Verificar Disponibilidade ---------------------------------------- '''
@app.route("/api/verificar-disponibilidade", methods=["POST"])
@login_required
def api_verificar_disponibilidade():
    '''
    API para verificar disponibilidade de veículo em tempo real (AJAX)
    '''
    try:
        data = request.get_json()

        veiculo_id = data.get('veiculo_id')
        data_inicio_str = data.get('data_inicio')
        data_fim_str = data.get('data_fim')

        if not veiculo_id or not data_inicio_str or not data_fim_str:
            return jsonify({'sucesso': False, 'mensagem': 'Dados incompletos'}), 400

        # Converter datas
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()

        # Verificar disponibilidade
        disponivel, mensagem = ReservaControler().verificar_disponibilidade(
            veiculo_id, data_inicio, data_fim
        )

        # Calcular valor se disponível
        valor_total = 0
        quantidade_dias = 0
        if disponivel:
            valor_total, quantidade_dias, _ = ReservaControler().calcular_valor_total(
                veiculo_id, data_inicio, data_fim
            )

        return jsonify({
            'sucesso': True,
            'disponivel': disponivel,
            'mensagem': mensagem,
            'valor_total': valor_total,
            'quantidade_dias': quantidade_dias
        })

    except Exception as e:
        print(f"Erro na API de disponibilidade: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao verificar disponibilidade'}), 500

''' ---------------------------------------- Reserva sem login ---------------------------------------- '''
@app.route("/reserva")
def reserva():
    '''
    Esta rota aparace quando não há usuario registado
    '''
    if current_user.is_authenticated:
        return redirect(url_for('minhas_reservas'))
     
    mensagem = "Sem Login efectuado"
    flash(mensagem, 'danger')
    return render_template("reserva.html")

''' ---------------------------------------- Página de contato ---------------------------------------- '''
@app.route("/contact")
def contact():

    return render_template("contact.html")

''' ---------------------------------------- Administração de veículos ---------------------------------------- '''
@app.route("/admin", methods=["GET", "POST"])
def admin():

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

@app.route("/admin/verificar-inspecoes")
def verificar_inspecoes_manual():
    """Rota para testar a verificação manualmente"""
    quantidade, mensagem = VeiculoControler().check_is_activo()
    flash(mensagem, 'info')
    return redirect(url_for('admin'))

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     """Dashboard do usuário (rota protegida)"""
#     return render_template('dashboard.html', usuario=current_user)