# -*- coding: utf-8 -*-
from odoo import models, fields, api

class RelationType(models.Model):
    _name = 'crumges.relation.type'
    _description = 'Tipo de Relación Dinámica'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre de la Relación", required=True, copy=False, readonly=True, default='Nuevo', tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    
    model_a_id = fields.Many2one('ir.model', string="Modelo A", required=True, ondelete='cascade')
    model_b_id = fields.Many2one('ir.model', string="Modelo B", required=True, ondelete='cascade', tracking=True)
    
    model_a_name = fields.Char(related='model_a_id.model', string="Nombre Técnico Modelo A")
    model_b_name = fields.Char(related='model_b_id.model', string="Nombre Técnico Modelo B")
    
    domain_a = fields.Char(string="Dominio/Filtro Modelo A", help="Dominio para filtrar los documentos origen")
    domain_b = fields.Char(string="Dominio/Filtro Modelo B", help="Dominio para filtrar los documentos destino")
    
    state_label_a = fields.Char(string="Sub-tipo / Estado Lado A", help="Nombre descriptivo del estado o filtro (ej. 'Cotizaciones')", tracking=True)
    state_label_b = fields.Char(string="Sub-tipo / Estado Lado B", help="Nombre descriptivo del estado o filtro (ej. 'Cotizaciones')", tracking=True)
    
    show_in_model_a = fields.Boolean(string="Mostrar en Modelo A", default=True, help="Si está activo, el Smart Button aparecerá en el Modelo A.")
    show_in_model_b = fields.Boolean(string="Mostrar en Modelo B", default=True, help="Si está activo, el Smart Button aparecerá en el Modelo B.")
    
    hide_if_zero_a = fields.Boolean(string="Ocultar si es cero (A)", help="Ocultar el botón en Modelo A si no hay registros en B")
    hide_if_zero_b = fields.Boolean(string="Ocultar si es cero (B)", help="Ocultar el botón en Modelo B si no hay registros en A")
    
    stat_type_a = fields.Selection([('count', 'Contar Registros'), ('sum', 'Sumar Campo')], string="Tipo de Estadística en A", default='count', required=True)
    stat_type_b = fields.Selection([('count', 'Contar Registros'), ('sum', 'Sumar Campo')], string="Tipo de Estadística en B", default='count', required=True)
    
    sum_field_a_id = fields.Many2one('ir.model.fields', string="Campo a Sumar (visto en A)", domain="[('model_id', '=', model_b_id), ('ttype', 'in', ['integer', 'float', 'monetary'])]")
    sum_field_b_id = fields.Many2one('ir.model.fields', string="Campo a Sumar (visto en B)", domain="[('model_id', '=', model_a_id), ('ttype', 'in', ['integer', 'float', 'monetary'])]")
    
    icon_a_to_b = fields.Char(string="Icono en Modelo A", default="fa-link", tracking=True)
    icon_b_to_a = fields.Char(string="Icono en Modelo B", default="fa-link", tracking=True)
    
    label_a_to_b = fields.Char(string="Etiqueta (Vista en Modelo A)", help="Texto del botón que verá el Modelo A para ir al Modelo B", tracking=True)
    label_b_to_a = fields.Char(string="Etiqueta (Vista en Modelo B)", help="Texto del botón que verá el Modelo B para ir al Modelo A", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('crumges.relation.type') or 'Nuevo'
        return super().create(vals_list)

    @api.onchange('model_a_id', 'state_label_a')
    def _onchange_model_a(self):
        if self.model_a_id:
            # El Modelo B verá una etiqueta que lo lleva a A, 
            # por lo que el nombre debería sugerir lo que hay en A.
            self.label_b_to_a = self.state_label_a or self.model_a_id.name

    @api.onchange('model_b_id', 'state_label_b')
    def _onchange_model_b(self):
        if self.model_b_id:
            self.label_a_to_b = self.state_label_b or self.model_b_id.name

    @api.depends('name', 'model_a_id', 'model_b_id')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.name} ({rec.model_a_id.name} <-> {rec.model_b_id.name})"
