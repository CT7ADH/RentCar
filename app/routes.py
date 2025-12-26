# -*- coding: utf-8 -*-
# 1. Importações do Flask e Python
from app import app, db
from flask import render_template, url_for, request, redirect, flash, session
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

    if current_user.is_authenticated:
        return redirect(url_for('root'))

    if request.method == 'POST':
        pass
    else:
        # Method para controle de datas para disponibilizar veiculo


        veiculos = VeiculoControler().get_all(limit=6)
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
            context = VeiculoControler().get_veiculos_filtrados(search_type, filtro_valor)
        else:
            # Se só selecionou o tipo mas não o valor, mostrar todos
            context = VeiculoControler().get_all(limit=None)

        return render_template(
            "car_list.html",
            context=context,
            search_result=search_result,
            ordenar=search_type,
            filtro_selecionado=filtro_valor
        )
    else:
        # GET - mostra todos os veículos
        context = VeiculoControler().get_all(limit=None)
        search_result = []
        return render_template("car_list.html", context=context, search_result=search_result
        )


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

    return render_template('login.html', context={})


''' ---------------------------------------- Rota de logout ---------------------------------------- '''
@app.route("/logout")
@login_required
def logout():

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


    return render_template("registration.html", dados={})

''' ---------------------------------------- ??¿¿ nova reserva ---------------------------------------- '''
@app.route("/reserva")
def reserva():

    return render_template("reserva.html")

''' ---------------------------------------- Cria nova reserva recebendo ID do veiculo ---------------------------------------- '''
@app.route("/reserva/<int:id>")
def cria_reserva(id):

    veiculo = VeiculoControler().get_by_id(id)

    context = {
        'car': veiculo,

    }
    return render_template("reserva.html", context=context)




''' ---------------------------------------- Rota de contacto ---------------------------------------- '''
@app.route("/contact")
def contact():
    """Página de contato"""
    return render_template("contact.html")



''' ---------------------------------------- Rota para administração de veiculos ---------------------------------------- '''
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