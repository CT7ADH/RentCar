# -*- coding: utf-8 -*-
"""
Módulo de Administração de Veículos
"""
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import flash, redirect, url_for, render_template, request
import os


# ========================
# FUNÇÕES DE VALIDAÇÃO
# ========================

def validar_campos_obrigatorios(marca, modelo, matricula):
    """Verifica se os campos obrigatórios estão preenchidos"""
    if not marca or not modelo or not matricula:
        return False, 'Marca, Modelo e Matrícula são obrigatórios!'
    return True, ''


def validar_matricula_existe(matricula):
    """Verifica se a matrícula já existe no banco"""
    from models import Veiculo

    if Veiculo.query.filter_by(matricula=matricula.upper()).first():
        return False, 'Esta matrícula já está cadastrada!'
    return True, ''


def validar_datas(data_ultima, data_proxima):
    """Valida se a data da próxima revisão é posterior à última"""
    if data_proxima <= data_ultima:
        return False, 'Data da próxima revisão deve ser posterior à última!'
    return True, ''


def validar_ano(ano):
    """Valida se o ano está num intervalo razoável"""
    ano_atual = datetime.now().year
    if ano < 1990 or ano > ano_atual + 1:
        return False, f'Ano deve estar entre 1990 e {ano_atual + 1}!'
    return True, ''


# ========================
# FUNÇÕES DE UPLOAD
# ========================

def salvar_imagem(imagem, static_folder):
    """
    Salva a imagem no servidor

    Retorna: (sucesso, nome_arquivo, mensagem_erro)
    """
    if not imagem or not imagem.filename:
        return True, None, ''

    # Validar extensão
    extensoes_permitidas = {'png', 'jpg', 'jpeg', 'gif'}
    extensao = imagem.filename.rsplit('.', 1)[1].lower() if '.' in imagem.filename else ''

    if extensao not in extensoes_permitidas:
        return False, None, 'Formato de imagem não permitido! Use PNG, JPG ou GIF.'

    # Validar tamanho (5MB)
    imagem.seek(0, os.SEEK_END)
    tamanho = imagem.tell()
    imagem.seek(0)

    if tamanho > 5 * 1024 * 1024:  # 5MB
        return False, None, 'Imagem muito grande! Máximo 5MB.'

    try:
        # Gerar nome único
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(imagem.filename)
        filename = f"{timestamp}_{filename}"

        # Criar pasta se não existir
        pasta_destino = os.path.join(static_folder, 'images', 'cars')
        os.makedirs(pasta_destino, exist_ok=True)

        # Salvar arquivo
        caminho_completo = os.path.join(pasta_destino, filename)
        imagem.save(caminho_completo)

        return True, filename, ''

    except Exception as e:
        return False, None, f'Erro ao salvar imagem: {str(e)}'


# ========================
# FUNÇÕES DE PROCESSAMENTO
# ========================

def extrair_dados_formulario(form):
    """Extrai e normaliza os dados do formulário"""
    try:
        dados = {
            'marca': form["marca"].strip().upper(),
            'modelo': form["modelo"].strip().title(),
            'categoria': form["categoria"],
            'transmissao': form["transmissao"],
            'tipo_veiculo': form["tipo_veiculo"],
            'capacidade_pessoas': int(form["capacidade_pessoas"]),
            'valor_diaria': float(form["valor_diaria"]),
            'matricula': form["matricula"].strip().upper(),
            'cor': form["cor"].strip().capitalize(),
            'ano': int(form["ano"]),
            'kilometragem': int(form.get("kilometragem", 0) or 0),
            'data_ultima_revisao': datetime.strptime(form["data_ultima_revisao"], '%Y-%m-%d').date(),
            'data_proxima_revisao': datetime.strptime(form["data_proxima_revisao"], '%Y-%m-%d').date(),
            'data_ultima_inspecao': datetime.strptime(form["data_ultima_inspecao"], '%Y-%m-%d').date(),
        }
        return dados, None
    except (ValueError, KeyError) as e:
        return None, 'Erro nos dados fornecidos. Verifique os campos.'


def validar_todos_dados(dados):
    """Executa todas as validações nos dados"""
    # Validar campos obrigatórios
    valido, msg = validar_campos_obrigatorios(dados['marca'], dados['modelo'], dados['matricula'])
    if not valido:
        return False, msg

    # Validar matrícula única
    valido, msg = validar_matricula_existe(dados['matricula'])
    if not valido:
        return False, msg

    # Validar datas
    valido, msg = validar_datas(dados['data_ultima_revisao'], dados['data_proxima_revisao'])
    if not valido:
        return False, msg

    # Validar ano
    valido, msg = validar_ano(dados['ano'])
    if not valido:
        return False, msg

    return True, ''


def criar_veiculo_no_banco(dados, imagem_url, db):
    """Cria o veículo no banco de dados"""
    from models import Veiculo

    veiculo = Veiculo(
        marca=dados['marca'],
        modelo=dados['modelo'],
        categoria=dados['categoria'],
        transmissao=dados['transmissao'],
        tipo_veiculo=dados['tipo_veiculo'],
        capacidade_pessoas=dados['capacidade_pessoas'],
        valor_diaria=dados['valor_diaria'],
        imagem_url=imagem_url,
        matricula=dados['matricula'],
        cor=dados['cor'],
        ano=dados['ano'],
        kilometragem=dados['kilometragem'],
        data_ultima_revisao=dados['data_ultima_revisao'],
        data_proxima_revisao=dados['data_proxima_revisao'],
        data_ultima_inspecao=dados['data_ultima_inspecao'],
    )

    db.session.add(veiculo)
    db.session.commit()


# ========================
# ROUTE PRINCIPAL
# ========================

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Administração de veículos - Versão Simplificada"""

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


# ========================
# EXEMPLO DE USO EM OUTROS LUGARES
# ========================

# Se precisar adicionar veículo por código:
def exemplo_adicionar_veiculo_programaticamente():
    """Exemplo de como usar as funções diretamente"""
    dados = {
        'marca': 'TOYOTA',
        'modelo': 'Corolla',
        'categoria': 'Médio',
        'transmissao': 'Automatico',
        'tipo_veiculo': 'Carro',
        'capacidade_pessoas': 5,
        'valor_diaria': 45.00,
        'matricula': 'AB-12-CD',
        'cor': 'Preto',
        'ano': 2023,
        'kilometragem': 15000,
        'data_ultima_revisao': datetime(2024, 6, 1).date(),
        'data_proxima_revisao': datetime(2024, 12, 1).date(),
        'data_ultima_inspecao': datetime(2024, 5, 15).date(),
    }

    # Validar
    valido, msg = validar_todos_dados(dados)
    if valido:
        criar_veiculo_no_banco(dados, None, db)
        print("Veículo criado com sucesso!")
    else:
        print(f"Erro: {msg}")