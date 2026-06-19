# -*- coding: utf-8 -*-
from odoo import models, fields, api

class RelationLink(models.Model):
    _name = 'crumges.relation.link'
    _description = 'Vínculo entre Documentos'

    type_id = fields.Many2one('crumges.relation.type', string="Tipo de Relación", required=True, ondelete='cascade')
    
    res_model_a = fields.Char(string="Modelo Origen", required=True)
    res_id_a = fields.Integer(string="ID Origen", required=True)
    
    res_model_b = fields.Char(string="Modelo Destino", required=True)
    res_id_b = fields.Integer(string="ID Destino", required=True)

    _sql_constraints = [
        ('unique_link', 'unique(type_id, res_model_a, res_id_a, res_model_b, res_id_b)', 'El vínculo ya existe.')
    ]
