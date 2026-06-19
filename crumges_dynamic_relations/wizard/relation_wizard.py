# -*- coding: utf-8 -*-
from odoo import models, fields, api

class RelationWizard(models.TransientModel):
    _name = 'crumges.relation.wizard'
    _description = 'Wizard para Vincular Documentos'

    type_id = fields.Many2one('crumges.relation.type', string="Tipo de Relación", required=True)
    
    source_model = fields.Char(string="Modelo Origen", required=True)
    source_id = fields.Integer(string="ID Origen", required=True)
    
    target_model = fields.Char(string="Modelo Destino", compute='_compute_target_model')
    
    # We use a generic many2one reference to select the target document
    target_ref = fields.Reference(selection='_selection_target_model', string="Documento a Vincular", required=True)

    @api.depends('type_id', 'source_model')
    def _compute_target_model(self):
        for rec in self:
            if rec.type_id and rec.source_model:
                is_model_a = (rec.type_id.model_a_id.model == rec.source_model)
                rec.target_model = rec.type_id.model_b_id.model if is_model_a else rec.type_id.model_a_id.model
            else:
                rec.target_model = False

    @api.model
    def _selection_target_model(self):
        # We return all models because the field needs a static selection or a method.
        # But we will restrict the UI widget if possible, or just return all models for the reference field.
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]

    def action_link(self):
        self.ensure_one()
        if not self.target_ref:
            return

        is_model_a = (self.type_id.model_a_id.model == self.source_model)
        
        res_model_a = self.source_model if is_model_a else self.target_ref._name
        res_id_a = self.source_id if is_model_a else self.target_ref.id
        
        res_model_b = self.target_ref._name if is_model_a else self.source_model
        res_id_b = self.target_ref.id if is_model_a else self.source_id

        # Check if already exists
        existing = self.env['crumges.relation.link'].search([
            ('type_id', '=', self.type_id.id),
            ('res_model_a', '=', res_model_a),
            ('res_id_a', '=', res_id_a),
            ('res_model_b', '=', res_model_b),
            ('res_id_b', '=', res_id_b),
        ])
        
        if not existing:
            self.env['crumges.relation.link'].create({
                'type_id': self.type_id.id,
                'res_model_a': res_model_a,
                'res_id_a': res_id_a,
                'res_model_b': res_model_b,
                'res_id_b': res_id_b,
            })
            
        return {'type': 'ir.actions.act_window_close'}
