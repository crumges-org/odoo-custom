from odoo import models, fields, api

class BankStatementImportHistory(models.Model):
    _name = 'bank.statement.import.history'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Historial de Importación de Extractos'
    _order = 'create_date desc'

    name = fields.Char(string='Descripción', required=True)
    filename = fields.Char(string='Nombre Archivo')
    file_data = fields.Binary(string='Archivo Excel')
    user_id = fields.Many2one('res.users', string='Usuario', default=lambda self: self.env.user, readonly=True)
    
    bank_id = fields.Many2one('res.bank', string='Banco', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Diario', readonly=True)
    
    statement_line_ids = fields.Many2many('account.bank.statement.line', string='Líneas Creadas', readonly=True)
    line_count = fields.Integer(string='Cant. Líneas', compute='_compute_line_count', store=True)
    reconciled_count = fields.Integer(string='Conciliadas', compute='_compute_reconciled_count')
    can_delete = fields.Boolean(compute='_compute_can_delete')
    
    @api.depends('statement_line_ids')
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.statement_line_ids)

    def _compute_reconciled_count(self):
        for rec in self:
            rec.reconciled_count = len(rec.statement_line_ids.filtered(lambda l: l.is_reconciled))

    def _compute_can_delete(self):
        for rec in self:
            rec.can_delete = any(not l.is_reconciled for l in rec.statement_line_ids) or not rec.statement_line_ids

    def action_delete_import(self):
        self.ensure_one()
        lines_to_delete = self.statement_line_ids.filtered(lambda l: not l.is_reconciled)
        if lines_to_delete:
            lines_to_delete.unlink()
        
        self.unlink()
        
        return {
            'name': 'Historial de Importaciones',
            'type': 'ir.actions.act_window',
            'res_model': 'bank.statement.import.history',
            'view_mode': 'list,form',
        }

    def action_view_lines(self):
        self.ensure_one()
        return {
            'name': 'Líneas Importadas',
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement.line',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.statement_line_ids.ids)],
            'context': {'create': False}
        }

    def action_view_reconciled_lines(self):
        self.ensure_one()
        reconciled_ids = self.statement_line_ids.filtered(lambda l: l.is_reconciled).ids
        return {
            'name': 'Líneas Conciliadas',
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement.line',
            'view_mode': 'list,form',
            'domain': [('id', 'in', reconciled_ids)],
            'context': {'create': False}
        }
