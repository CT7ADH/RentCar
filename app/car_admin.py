# -*- coding: utf-8 -*-
"""
Módulo de Administração de Veículos
"""
from datetime import datetime
from werkzeug.utils import secure_filename
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
    from tests.migrate import Veiculo

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
    """Extrai os dados do formulário"""
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
    from tests.migrate import Veiculo

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
