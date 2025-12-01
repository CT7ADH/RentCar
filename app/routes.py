# -*- coding: utf-8 -*-
from app import app, db
from flask import render_template, url_for, request, redirect, flash, session
from datetime import datetime, date
from app.controller import PayMethodControler, ClienteControler, VeiculoControler, ReservaControler, AuthController
from flask_login import login_user, logout_user, login_required, current_user

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

        veiculos = VeiculoControler().get_veiculos(limit=6)
        categorias = VeiculoControler().get_used_categorias()
        return render_template("index.html", context=veiculos, categorias=categorias)


# ''' -------------------------------------------------------------------------------------------------- '''
# @app.route("/car_list", methods=["GET", "POST"])
# def car_list():
#     """ Listagem de veículos com filtros """
#     if request.method == 'POST':
#         search_type = request.form.get("ordenar")
#
#         # Se for "None" ou vazio, mostra todos
#         if search_type and search_type != "None":
#             search_result = VeiculoControler().get_search_type(arg_search=search_type)
#         else:
#             search_result = []
#
#         context = VeiculoControler().get_veiculos(limit=None)
#         return render_template("car_list.html", context=context, search_result=search_result, ordenar=search_type)
#     else:
#         # GET - mostra todos os veículos
#         context = VeiculoControler().get_veiculos(limit=None)
#         search_result = []  # Lista vazia para o select de pesquisa
#         return render_template("car_list.html", context=context, search_result=search_result)

@app.route("/get_filter_options", methods=["GET"])
def get_filter_options():
    """Retorna opções de filtro baseado no tipo selecionado"""
    tipo = request.args.get('tipo')

    if not tipo or tipo == 'None':
        return jsonify({'opcoes': []})

    try:
        opcoes = VeiculoControler().get_search_type(arg_search=tipo)
        return jsonify({'opcoes': opcoes})
    except Exception as e:
        print(f"Erro ao buscar opções: {e}")
        return jsonify({'opcoes': [], 'erro': str(e)})


@app.route("/car_list", methods=["GET", "POST"])
def car_list():
    """ Listagem de veículos com filtros """
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
            context = VeiculoControler().get_veiculos(limit=None)

        return render_template(
            "car_list.html",
            context=context,
            search_result=search_result,
            ordenar=search_type,
            filtro_selecionado=filtro_valor
        )
    else:
        # GET - mostra todos os veículos
        context = VeiculoControler().get_veiculos(limit=None)
        search_result = []
        return render_template(
            "car_list.html",
            context=context,
            search_result=search_result
        )
''' -------------------------------------------------------------------------------------------------- '''
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


''' -------------------------------------------------------------------------------------------------- '''
@app.route("/logout")
@login_required
def logout():
    """Rota de logout"""
    sucesso, mensagem = AuthController.fazer_logout()
    flash(mensagem, 'info')
    return redirect(url_for('login'))


''' -------------------------------------------------------------------------------------------------- '''
@app.route("/registration", methods=['GET', 'POST'])
def registration():
    """ Registro de novos clientes """
    # if current_user.is_authenticated:
    #     return redirect(url_for('registration'))

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



''' -------------------------------------------------------------------------------------------------- '''
@app.route("/reserva")
def reserva():

    return render_template("reserva.html", data={'status': 200, 'msg': None, 'type': None})



''' -------------------------------------------------------------------------------------------------- '''
@app.route("/contact")
def contact():
    """Página de contato"""
    return render_template("contact.html")



''' -------------------------------------------------------------------------------------------------- '''
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
