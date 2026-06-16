from odoo import models, fields

class BankStatementImportLine(models.TransientModel):
    _name = 'bank.statement.import.line'
    _description = 'Línea Transitoria de Importación de Extracto'

    wizard_id = fields.Many2one('bank.statement.import.wizard', string='Wizard', ondelete='cascade')
    
    date = fields.Date(string='Fecha')
    label = fields.Char(string='Etiqueta')
    amount = fields.Float(string='Importe')
    balance = fields.Float(string='Saldo')
    
    status = fields.Selection([
        ('ready', 'Listo para importar'),
        ('exists', 'Ya existe'),
        ('error', 'Error')
    ], string='Estado', default='ready')
    
    error_message = fields.Char(string='Mensaje de Error')
    to_import = fields.Boolean(string='Importar', default=True)
    
    # Campo para almacenar la representación interna única generada durante el preanálisis
    unique_hash = fields.Char(string='Hash Único')
