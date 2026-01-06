# -*- coding: utf-8 -*-
"""
Módulo de Administração de Veículos
"""
# 1. Importações
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


def validar_matricula_existe(matricula, veiculo_id=None):
    """
    Verifica se a matrícula já existe no banco.
    Args:
        matricula (str): Matrícula a verificar
        veiculo_id (int, optional): ID do veículo a excluir da verificação (para edição)
    Returns:
        tuple: (valido: bool, mensagem: str)
    """
    from app.model.Veiculo import Veiculo

    query = Veiculo.query.filter_by(matricula=matricula.upper())

    # Se estiver editando, excluir o próprio veículo da verificação
    if veiculo_id:
        query = query.filter(Veiculo.id != veiculo_id)

    if query.first():
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
    Salva a imagem no servidor.
    Args:
        imagem: Arquivo de imagem do Flask
        static_folder: Pasta static da aplicação
    Returns:
        tuple: (sucesso: bool, nome_arquivo: str|None, mensagem_erro: str)
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
        # Gerar nome único com timestamp
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
    """
    Extrai e processa dados do formulário.
    Args:
        form: Objeto request.form do Flask
    Returns:
        tuple: (dados: dict|None, erro: str|None)
    """
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
        print(f"Erro ao extrair dados do formulário: {e}")
        return None, 'Erro nos dados fornecidos. Verifique os campos.'


def validar_todos_dados(dados, veiculo_id=None):
    """
    Executa todas as validações nos dados.
    Args:
        dados (dict): Dicionário com dados do veículo
        veiculo_id (int, optional): ID do veículo (para edição)
    Returns:
        tuple: (valido: bool, mensagem: str)
    """
    # Validar campos obrigatórios
    valido, msg = validar_campos_obrigatorios(dados['marca'], dados['modelo'], dados['matricula'])
    if not valido:
        return False, msg

    # Validar matrícula única
    valido, msg = validar_matricula_existe(dados['matricula'], veiculo_id)
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
    """
    Cria o veículo no banco de dados.
    Args:
        dados (dict): Dicionário com dados do veículo
        imagem_url (str|None): Nome do arquivo de imagem ou None
        db: Instância do SQLAlchemy
    Raises:
        Exception: Se houver erro ao salvar no banco
    """
    from app.model.Veiculo import Veiculo

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
# FUNÇÕES PARA GESTÃO DE VEÍCULOS INATIVOS
# ========================

def atualizar_veiculo_no_banco(veiculo_id, dados, imagem_url, db):
    """
    Atualiza um veículo existente no banco de dados.
    Args:
        veiculo_id (int): ID do veículo a atualizar
        dados (dict): Dicionário com dados do veículo
        imagem_url (str|None): Nome do arquivo de imagem ou None (mantém atual se None)
        db: Instância do SQLAlchemy
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    from app.model.Veiculo import Veiculo

    try:
        veiculo = Veiculo.query.get(veiculo_id)
        if not veiculo:
            return False, 'Veículo não encontrado!'

        # Atualizar campos
        veiculo.marca = dados['marca']
        veiculo.modelo = dados['modelo']
        veiculo.categoria = dados['categoria']
        veiculo.transmissao = dados['transmissao']
        veiculo.tipo_veiculo = dados['tipo_veiculo']
        veiculo.capacidade_pessoas = dados['capacidade_pessoas']
        veiculo.valor_diaria = dados['valor_diaria']
        veiculo.matricula = dados['matricula']
        veiculo.cor = dados['cor']
        veiculo.ano = dados['ano']
        veiculo.kilometragem = dados['kilometragem']
        veiculo.data_ultima_revisao = dados['data_ultima_revisao']
        veiculo.data_proxima_revisao = dados['data_proxima_revisao']
        veiculo.data_ultima_inspecao = dados['data_ultima_inspecao']

        # Atualizar imagem apenas se foi enviada uma nova
        if imagem_url:
            veiculo.imagem_url = imagem_url

        db.session.commit()
        return True, 'Veículo atualizado com sucesso!'

    except Exception as e:
        db.session.rollback()
        return False, f'Erro ao atualizar veículo: {str(e)}'


def reativar_veiculo(veiculo_id, db):
    """
    Reativa um veículo após atualização de manutenções.
    Args:
        veiculo_id (int): ID do veículo
        db: Instância do SQLAlchemy
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    from app.model.Veiculo import Veiculo
    from datetime import date, timedelta

    try:
        veiculo = Veiculo.query.get(veiculo_id)
        if not veiculo:
            return False, 'Veículo não encontrado!'

        hoje = date.today()
        data_limite_inspecao = hoje - timedelta(days=365)

        # Verificar se pode ser reativado
        if veiculo.data_ultima_inspecao < data_limite_inspecao:
            return False, 'Inspeção ainda está expirada! Atualize a data da última inspeção.'

        if veiculo.data_proxima_revisao < hoje:
            return False, 'Revisão ainda está atrasada! Atualize a data da próxima revisão.'

        # Reativar
        veiculo.ativo = True
        db.session.commit()

        return True, 'Veículo reativado com sucesso!'

    except Exception as e:
        db.session.rollback()
        return False, f'Erro ao reativar veículo: {str(e)}'