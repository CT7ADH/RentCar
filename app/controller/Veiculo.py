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
            print(result)
            return result

    def get_all(self, limit):
        result = []
        try:
            res = self.veiculo_model.get_all(limit=limit)

            for r in res:
                result.append({
                    'id': r.id,
                    'marca': r.marca,
                    'modelo': r.modelo,
                    'categoria': r.categoria,
                    'transmissao':r.transmissao,
                    'tipo_veiculo': r.tipo_veiculo,
                    'capacidade_pessoas': r.capacidade_pessoas,
                    'valor_diaria' : r.valor_diaria,
                    'imagem_url' : r.imagem_url,
                    'cor' : r.cor,
                    'ano' : r.ano,
                    'kilometragem': r.kilometragem,
                    'ativo' : r.ativo

                })

        except Exception as e:
            print(e)
            result = []
            return False, f'Erro ao obter Veiculos: {str(e)}'
        finally:
            return result

    def get_by_id(self, id):
        result = []
        try:
            res = self.veiculo_model.get_by_id(id)

            if res:
                result={
                    'id': res.id,
                    'marca': res.marca,
                    'modelo': res.modelo,
                    'categoria': res.categoria,
                    'transmissao':res.transmissao,
                    'tipo_veiculo': res.tipo_veiculo,
                    'capacidade_pessoas': res.capacidade_pessoas,
                    'valor_diaria' : res.valor_diaria,
                    'imagem_url' : res.imagem_url,
                    'cor' : res.cor,
                    'ano' : res.ano,
                    'kilometragem': res.kilometragem,
                    'ativo' : res.ativo

                }



        except Exception as e:
            print(e)
            result = []
            return False, f'Erro ao obter Veiculo por ID: {str(e)}'
        finally:
            return result

    def get_used_categorias(self):
        """Retorna categorias únicas de veículos ativos"""
        try:
            result = self.veiculo_model.get_categorias_ativas()
        except Exception as e:
            print(f"Erro ao buscar categorias: {e}")
            result = []
        finally:
            print(result)
            return result

    def get_search_type(self, arg_search):
        try:
            search_type = self.veiculo_model.get_search_type(arg_search)
        except Exception as e:
            print(f"Erro ao buscar categorias: {str(e)}")
            search_type = []
            return False, f'Erro ao buscar: {str(e)}'
        finally:
            return search_type

    def get_veiculos_filtrados(self, tipo_filtro, valor_filtro):
        """Retorna veículos filtrados por tipo e valor"""
        result = []
        try:
            veiculos = self.veiculo_model.get_veiculos_by_filter(tipo_filtro, valor_filtro)

            for v in veiculos:
                result.append({
                    'id': v.id,
                    'marca': v.marca,
                    'modelo': v.modelo,
                    'categoria': v.categoria,
                    'transmissao': v.transmissao,
                    'tipo_veiculo': v.tipo_veiculo,
                    'capacidade_pessoas': v.capacidade_pessoas,
                    'valor_diaria': v.valor_diaria,
                    'imagem_url': v.imagem_url,
                    'cor': v.cor,
                    'ano': v.ano,
                    'kilometragem': v.kilometragem,
                    'ativo': v.ativo
                })
        except Exception as e:
            print(f"Erro ao buscar veículos filtrados: {str(e)}")
            result = []
            return False, f'Erro ao filtrar veiculos: {str(e)}'
        finally:
            return result