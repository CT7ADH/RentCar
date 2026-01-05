# -*- coding: utf-8 -*-
from datetime import date, timedelta
from app.model.Veiculo import Veiculo
from app.model.Reserva import Reserva
from app import db

class VeiculoControler():
    def __init__(self):
        self.veiculo_model = Veiculo()

    def check_is_activo(self):
        ''' Verificar se os veículos têm as inspeções e revisões em dia'''
        try:
            result = self.veiculo_model.check_is_activo()
        except Exception as e:
            print(f"Erro ao buscar categorias: {e}")
            result = []
        finally:
            return result

    def get_all(self, limit):
        """Retorna todos os veículos como lista de dicionários"""
        try:
            veiculos = self.veiculo_model.get_all(limit=limit)
            # Usa list comprehension com o method to_dict()
            return [veiculo.to_dict() for veiculo in veiculos]

        except Exception as e:
            print(f"Erro ao obter veículos: {e}")
            return []

    def get_by_id(self, id):
        """Retorna um veículo específico como dicionário"""
        try:
            veiculo = self.veiculo_model.get_by_id(id)
            return veiculo.to_dict() if veiculo else {}

        except Exception as e:
            print(f"Erro ao obter veículo por ID: {e}")
            return {}

    def get_used_categorias(self):
        """Retorna categorias únicas de veículos ativos"""
        try:
            return self.veiculo_model.get_categorias_ativas()
        except Exception as e:
            print(f"Erro ao buscar categorias: {e}")
            return []

    def get_search_type(self, arg_search):
        """Busca tipos disponíveis para filtro"""
        try:
            return self.veiculo_model.get_search_type(arg_search)
        except Exception as e:
            print(f"Erro ao buscar tipos: {e}")
            return []

    def get_veiculos_filtrados(self, tipo_filtro, valor_filtro):
        """Retorna veículos filtrados por tipo e valor"""
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