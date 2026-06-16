from odoo import models, fields, api, _
import re
from odoo.exceptions import ValidationError

class BankStatementTemplate(models.Model):
    _name = 'bank.statement.template'
    _description = 'Plantilla de Extracto por Banco'

    name = fields.Char(string='Nombre de Plantilla', required=True)
    bank_id = fields.Many2one('res.bank', string='Banco del Sistema', help='Vincula este formato a un banco del sistema para preselección automática')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    
    start_row = fields.Integer(string='Fila de Inicio', required=True, default=2, help='Fila donde comienzan los registros (ignora encabezados e títulos). La primera fila es la 1.')
    
    col_date = fields.Char(string='Columna Fecha', required=True, help='Ejemplo: A, B, C...')
    col_label = fields.Char(string='Columna Etiqueta (Concepto)', required=True, help='Ejemplo: B, o B,C para concatenar varias columnas separadas por comas')
    
    amount_type = fields.Selection([
        ('single', 'Una columna (Importe Positivo/Negativo)'),
        ('split', 'Dos columnas (Débito y Crédito separados)')
    ], string='Tipo de Importe', required=True, default='single')
    
    col_amount = fields.Char(string='Columna Importe', help='Requerido si "Una columna"')
    col_debit = fields.Char(string='Columna Débitos (Egresos)', help='Requerido si "Dos columnas"')
    col_credit = fields.Char(string='Columna Créditos (Ingresos)', help='Requerido si "Dos columnas"')
    
    col_balance = fields.Char(string='Columna Saldo', required=True, help='Obligatorio para identificar de forma única las transacciones y evitar duplicados. Ejemplo: F')
    
    @api.onchange('bank_id')
    def _onchange_bank_id(self):
        if self.bank_id:
            self.name = f"Plantilla - {self.bank_id.name}"

    @api.constrains('col_label')
    def _check_col_label_format(self):
        for rec in self:
            if rec.col_label:
                # Permite "A", "A,B", " A , B " etc.
                if not re.match(r'^[A-Za-z]+(\s*,\s*[A-Za-z]+)*$', rec.col_label.strip()):
                    raise ValidationError(_("El formato de la Columna Etiqueta es incorrecto.\nDebe ser una letra (ej. B) o varias letras separadas por comas para concatenar (ej. B,C,D)."))
    
    @api.model
    def col_to_index(self, col_letter):
        """Convierte letra de columna Excel (A, B, C, AA...) a índice 0-based"""
        if not col_letter:
            return None
        col_letter = str(col_letter).strip().upper()
        if not col_letter.isalpha():
            # Si el usuario ingresó un número, asumimos 1-based index y lo pasamos a 0-based
            try:
                idx = int(col_letter)
                return max(0, idx - 1)
            except ValueError:
                return None
                
        idx = 0
        for char in col_letter:
            idx = idx * 26 + (ord(char) - ord('A') + 1)
        return idx - 1
