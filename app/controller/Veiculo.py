# -*- coding: utf-8 -*-
# 1. Importações do Flask e Python
from app.model.Veiculo import Veiculo

class VeiculoControler():
    def __init__(self):
        self.veiculo_model = Veiculo()

    # ==================== MÉTODOS DE CLASSE (CLASS METHODS) ====================

    def check_is_activo(self):
        ''' Verificar se os veículos têm as inspeções e revisões em dia'''
        try:
            return self.veiculo_model.check_is_activo()
        except Exception as e:
            print(f"Erro ao verificar status: {e}")
            return 0, f"Erro ao verificar status: {str(e)}"

    def get_all(self, limit=None):
        """
        Retorna todos os veículos como lista de dicionários.
        Args:
            limit (int, optional): Número máximo de veículos a retornar
        Returns:
            list: Lista de dicionários com dados dos veículos
        """
        try:
            veiculos = self.veiculo_model.get_all(limit=limit)
            return [veiculo.to_dict() for veiculo in veiculos]
        except Exception as e:
            print(f"Erro ao obter veículos: {e}")
            return []

    def get_all_activo(self, limit=None):
        """
        Retorna todos os veículos com a revisão e inspeção em dia como lista de dicionários.
        Args:
            limit (int, optional): Número máximo de veículos a retornar
        Returns:
            list: Lista de dicionários com dados dos veículos
        """
        try:
            veiculos = self.veiculo_model.get_all_activo(limit=limit)
            return [veiculo.to_dict() for veiculo in veiculos]
        except Exception as e:
            print(f"Erro ao obter veículos: {e}")
            return []

    def get_by_id(self, veiculo_id):
        """
        Retorna um veículo específico como dicionário.
        Args:
            veiculo_id (int): ID do veículo
        Returns:
            dict: Dicionário com dados do veículo ou dict vazio
        """
        try:
            veiculo = self.veiculo_model.get_by_id(veiculo_id)
            return veiculo.to_dict() if veiculo else {}
        except Exception as e:
            print(f"Erro ao obter veículo por ID {veiculo_id}: {e}")
            return {}

    def get_used_categorias(self):
        """
        Retorna categorias únicas de veículos ativos.
        Returns:
            list: Lista de categorias disponíveis
        """
        try:
            return self.veiculo_model.get_categorias_ativas()
        except Exception as e:
            print(f"Erro ao buscar categorias: {e}")
            return []

    def get_search_type(self, arg_search):
        """
        Busca tipos disponíveis para filtro dinâmico.
        Args:
            arg_search (str): Tipo de campo para buscar (marca, modelo, etc.)
        Returns:
            list: Lista de valores únicos para o campo especificado
        """
        try:
            return self.veiculo_model.get_search_type(arg_search)
        except Exception as e:
            print(f"Erro ao buscar tipos de filtro: {e}")
            return []

    def get_veiculos_filtrados(self, tipo_filtro, valor_filtro):
        """
        Retorna veículos filtrados por tipo e valor.
        Args:
            tipo_filtro (str): Campo pelo qual filtrar
            valor_filtro (str): Valor do filtro
        Returns:
            list: Lista de dicionários com veículos filtrados
        """
        try:
            veiculos = self.veiculo_model.get_veiculos_by_filter(tipo_filtro, valor_filtro)
            return [veiculo.to_dict() for veiculo in veiculos]
        except Exception as e:
            print(f"Erro ao filtrar veículos: {e}")
            return []

    def get_veiculos_resumo(self):
        """Retorna apenas campos essenciais dos veículos"""
        try:
            veiculos = self.veiculo_model.get_all(limit=None)
            campos_resumo = ['id', 'marca', 'modelo', 'valor_diaria', 'imagem_url']
            return [v.to_dict(campos=campos_resumo) for v in veiculos]
        except Exception as e:
            print(f"Erro: {e}")
            return []