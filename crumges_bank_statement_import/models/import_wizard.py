import base64
import io
import json
import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re
import csv

_logger = logging.getLogger(__name__)

try:
    import openpyxl
except ImportError:
    _logger.error("OpenPyXL no está instalado")


class BankStatementImportWizard(models.TransientModel):
    _name = 'bank.statement.import.wizard'
    _description = 'Asistente de Importación de Extracto Bancario'

    file_data = fields.Binary(string='Archivo Excel', required=True)
    filename = fields.Char(string='Nombre Archivo')
    
    date_start = fields.Date(string='Desde', readonly=True)
    date_end = fields.Date(string='Hasta', readonly=True)
    limit_to_today = fields.Boolean(string='Hoy', default=True)
    import_up_to_date = fields.Date(string='Importar hasta', default=fields.Date.context_today, required=True, help="Movimientos posteriores a esta fecha serán ignorados.")
    
    bank_id = fields.Many2one('res.bank', string='Banco')
    template_id = fields.Many2one('bank.statement.template', string='Plantilla del Banco', required=True)
    journal_id = fields.Many2one(
        'account.journal', 
        string='Diario Bancario', 
        required=True, 
        domain="[('type', '=', 'bank')]"
    )
    
    line_ids = fields.One2many('bank.statement.import.line', 'wizard_id', string='Líneas')

    state = fields.Selection([
        ('upload', 'Carga'),
        ('review', 'Revisión'),
        ('done', 'Hecho')
    ], default='upload', string='Estado')

    @api.onchange('bank_id')
    def _onchange_bank_id(self):
        if not self.bank_id:
            return
            
        # 1. Preseleccionar el Diario Bancario
        journal = self.env['account.journal'].search([
            ('type', '=', 'bank'),
            ('bank_account_id.bank_id', '=', self.bank_id.id),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if not journal:
            journal = self.env['account.journal'].search([
                ('type', '=', 'bank'),
                ('company_id', '=', self.env.company.id)
            ], limit=1)
            
        if journal:
            self.journal_id = journal
            
        # 2. Preseleccionar el Formato del Banco
        format_rec = self.env['bank.statement.template'].search([
            ('bank_id', '=', self.bank_id.id),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if format_rec:
            self.template_id = format_rec

    @api.onchange('limit_to_today')
    def _onchange_limit_to_today(self):
        if self.limit_to_today:
            self.import_up_to_date = fields.Date.context_today(self)
            self._onchange_import_up_to_date()

    @api.onchange('import_up_to_date')
    def _onchange_import_up_to_date(self):
        if not self.line_ids:
            return
            
        for line in self.line_ids:
            if self.import_up_to_date and line.date and line.date > self.import_up_to_date:
                line.status = 'error'
                line.error_message = f'Movimiento futuro ({line.date} > {self.import_up_to_date}).'
                line.to_import = False
            elif line.status == 'error' and line.error_message and 'Movimiento futuro' in line.error_message:
                line.status = 'ready'
                line.error_message = False
                line.to_import = True
                
        # Re-verificar existentes por si alguna línea restaurada ya existía
        self._check_existing_lines()

    # --- Dashboard Fields ---
    view_filter = fields.Selection([
        ('all', 'Todos'),
        ('ready', 'Listos'),
        ('error', 'Errores'),
        ('exists', 'Existentes')
    ], default='all', string="Filtro de Vista")

    info_all = fields.Char(compute='_compute_dashboard_data')
    info_ready = fields.Char(compute='_compute_dashboard_data')
    info_error = fields.Char(compute='_compute_dashboard_data')
    info_exists = fields.Char(compute='_compute_dashboard_data')

    count_all = fields.Integer(compute='_compute_dashboard_data')
    count_ready = fields.Integer(compute='_compute_dashboard_data')
    count_error = fields.Integer(compute='_compute_dashboard_data')
    count_exists = fields.Integer(compute='_compute_dashboard_data')

    visible_line_ids = fields.Many2many(
        'bank.statement.import.line', compute='_compute_visible_lines', inverse='_inverse_visible_line_ids', store=True)

    def _inverse_visible_line_ids(self):
        # Este método inverso permite que las ediciones hechas desde la UI en `visible_line_ids`
        # (como cambiar el switch to_import) se guarden correctamente en la base de datos antes
        # de ejecutar las acciones (action_import).
        pass

    total_lines = fields.Integer(compute='_compute_total_lines')
    can_import = fields.Boolean(compute='_compute_can_import')

    @api.depends('line_ids')
    def _compute_total_lines(self):
        for wizard in self:
            wizard.total_lines = len(wizard.line_ids)

    @api.depends('line_ids.status', 'line_ids.to_import')
    def _compute_can_import(self):
        for wizard in self:
            wizard.can_import = any(l.status == 'ready' and l.to_import for l in wizard.line_ids)

    @api.depends('line_ids', 'line_ids.status')
    def _compute_dashboard_data(self):
        for wizard in self:
            base_lines = wizard.line_ids
            c_all = len(base_lines)
            c_ready = len(base_lines.filtered(lambda l: l.status == 'ready'))
            c_error = len(base_lines.filtered(lambda l: l.status == 'error'))
            c_exists = len(base_lines.filtered(lambda l: l.status == 'exists'))

            wizard.info_all = f"TODOS: {c_all}"
            wizard.info_ready = f"LISTOS: {c_ready}"
            wizard.info_error = f"ERRORES: {c_error}"
            wizard.info_exists = f"EXISTENTES: {c_exists}"

            wizard.count_all = c_all
            wizard.count_ready = c_ready
            wizard.count_error = c_error
            wizard.count_exists = c_exists

    @api.depends('line_ids', 'view_filter')
    def _compute_visible_lines(self):
        for wizard in self:
            if wizard.view_filter == 'all':
                wizard.visible_line_ids = wizard.line_ids
            elif wizard.view_filter == 'ready':
                wizard.visible_line_ids = wizard.line_ids.filtered(lambda l: l.status == 'ready')
            elif wizard.view_filter == 'error':
                wizard.visible_line_ids = wizard.line_ids.filtered(lambda l: l.status == 'error')
            elif wizard.view_filter == 'exists':
                wizard.visible_line_ids = wizard.line_ids.filtered(lambda l: l.status == 'exists')
            else:
                wizard.visible_line_ids = wizard.line_ids

    def _get_action_reopen(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Importación de Extracto Bancario',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def action_set_filter_all(self):
        self.view_filter = 'all'
        return self._get_action_reopen()

    def action_set_filter_ready(self):
        self.view_filter = 'ready'
        return self._get_action_reopen()

    def action_set_filter_error(self):
        self.view_filter = 'error'
        return self._get_action_reopen()

    def action_set_filter_exists(self):
        self.view_filter = 'exists'
        return self._get_action_reopen()

    def action_select_all_visible_lines(self):
        for wizard in self:
            lines_to_update = wizard.visible_line_ids.filtered(lambda l: l.status == 'ready')
            lines_to_update.write({'to_import': True})
        return self._get_action_reopen()

    def action_deselect_all_visible_lines(self):
        for wizard in self:
            wizard.visible_line_ids.write({'to_import': False})
        return self._get_action_reopen()

    show_select_all_ready = fields.Boolean(compute='_compute_ready_line_selection')
    show_deselect_all_ready = fields.Boolean(compute='_compute_ready_line_selection')

    @api.depends('visible_line_ids', 'visible_line_ids.to_import', 'visible_line_ids.status')
    def _compute_ready_line_selection(self):
        for wizard in self:
            ready_lines = wizard.visible_line_ids.filtered(lambda l: l.status == 'ready')
            if not ready_lines:
                wizard.show_select_all_ready = False
                wizard.show_deselect_all_ready = False
                continue
            
            selected_count = len(ready_lines.filtered('to_import'))
            total_count = len(ready_lines)
            
            wizard.show_select_all_ready = selected_count < total_count
            wizard.show_deselect_all_ready = selected_count > 0

    def _parse_date(self, date_val):
        if not date_val:
            return False
        if isinstance(date_val, datetime):
            return date_val.date()
        if hasattr(date_val, 'date'):
            return date_val.date()
        if isinstance(date_val, str):
            # Try some common formats
            for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%y'):
                try:
                    return datetime.strptime(date_val.strip(), fmt).date()
                except ValueError:
                    pass
        return False
        
    def _parse_float(self, val):
        if val is None or str(val).strip() == '':
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        # Limpiar strings como "$ 1.000,50" o "1,000.50"
        val_str = str(val).replace('$', '').replace('€', '').strip()
        # Si tiene coma y punto, asumimos que el último es el decimal
        if ',' in val_str and '.' in val_str:
            if val_str.rfind(',') > val_str.rfind('.'):
                # Formato europeo: 1.000,50 -> 1000.50
                val_str = val_str.replace('.', '').replace(',', '.')
            else:
                # Formato americano: 1,000.50 -> 1000.50
                val_str = val_str.replace(',', '')
        elif ',' in val_str:
            # Solo coma: asumimos separador decimal europeo
            val_str = val_str.replace(',', '.')
        try:
            return float(val_str)
        except ValueError:
            return 0.0

    def action_analyze(self):
        self.ensure_one()
        if not self.file_data:
            raise UserError(_("Por favor suba un archivo Excel."))

        fmt = self.template_id
        
        idx_date = fmt.col_to_index(fmt.col_date)
        
        label_cols = [c.strip() for c in fmt.col_label.split(',')] if fmt.col_label else []
        idx_labels = [fmt.col_to_index(c) for c in label_cols]
        
        idx_amount = fmt.col_to_index(fmt.col_amount) if fmt.amount_type == 'single' else None
        idx_debit = fmt.col_to_index(fmt.col_debit) if fmt.amount_type == 'split' else None
        idx_credit = fmt.col_to_index(fmt.col_credit) if fmt.amount_type == 'split' else None
        
        idx_balance = fmt.col_to_index(fmt.col_balance) if fmt.col_balance else None

        try:
            file_content = base64.b64decode(self.file_data)
            rows = []
            
            if self.filename and self.filename.lower().endswith('.csv'):
                try:
                    text_content = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    text_content = file_content.decode('latin-1')
                
                try:
                    # Intentar detectar el delimitador (coma o punto y coma)
                    dialect = csv.Sniffer().sniff(text_content[:2048])
                except Exception:
                    dialect = csv.excel
                
                reader = csv.reader(io.StringIO(text_content), dialect=dialect)
                rows = list(reader)
            else:
                wb = openpyxl.load_workbook(io.BytesIO(file_content), data_only=True)
                ws = wb.active
                rows = list(ws.iter_rows(values_only=True))
        except Exception as e:
            raise UserError(_("No se pudo leer el archivo. Asegúrese de que sea un Excel (.xlsx) o CSV válido. Error: %s") % e)
        start_row_idx = max(0, fmt.start_row - 1)
        
        if start_row_idx >= len(rows):
            raise UserError(_("La fila de inicio configurada (%s) es mayor a la cantidad de filas del archivo.") % fmt.start_row)

        # Clear previous lines
        self.line_ids.unlink()

        lines_values = []
        for i in range(start_row_idx, len(rows)):
            row = rows[i]
            
            # Check if row is mostly empty (skip empty rows)
            if not any(row):
                continue
                
            # Safely get column values
            def get_col(idx):
                return row[idx] if idx is not None and idx < len(row) else None

            date_val = get_col(idx_date)
            parsed_date = self._parse_date(date_val)
            
            label_parts = []
            for idx in idx_labels:
                val = get_col(idx)
                if val is not None and str(val).strip():
                    label_parts.append(str(val).strip())
            label_str = ' - '.join(label_parts)
            
            # Amount Logic
            amount = 0.0
            if fmt.amount_type == 'single':
                amount = self._parse_float(get_col(idx_amount))
            else:
                debit = self._parse_float(get_col(idx_debit))
                credit = self._parse_float(get_col(idx_credit))
                # Credit is positive, Debit is negative (usually)
                if credit != 0:
                    amount = abs(credit)
                elif debit != 0:
                    amount = -abs(debit)
                    
            # Balance Logic
            balance_val = get_col(idx_balance)
            balance = self._parse_float(balance_val) if balance_val is not None else 0.0
            
            # Validation
            status = 'ready'
            error_msg = ''
            to_import = True
            
            if not parsed_date:
                status = 'error'
                error_msg = 'Fecha inválida o vacía.'
                to_import = False
            elif amount == 0.0:
                # Omitir transacciones en cero
                continue
                
            # Hash único
            if idx_balance is not None and balance_val is not None:
                # Usar Saldo como parte de la llave
                unique_hash = f"{parsed_date}_{amount:.2f}_{balance:.2f}"
            else:
                # Usar Etiqueta como fallback
                unique_hash = f"{parsed_date}_{amount:.2f}_{label_str}"
                
            lines_values.append((0, 0, {
                'date': parsed_date,
                'label': label_str,
                'amount': amount,
                'balance': balance,
                'status': status,
                'error_message': error_msg,
                'to_import': to_import,
                'unique_hash': unique_hash
            }))

        if not lines_values:
            raise UserError(_("No se encontraron registros válidos para procesar."))

        # Computar fechas de inicio y fin reales encontradas
        valid_dates = [l[2]['date'] for l in lines_values if l[2]['date']]
        if valid_dates:
            self.date_start = min(valid_dates)
            self.date_end = max(valid_dates)

        self.write({'line_ids': lines_values})
        self._check_existing_lines()
        
        # Aplicar el filtro de fecha inicial basado en import_up_to_date
        self._onchange_import_up_to_date()
        
        self.state = 'review'
        return self._get_action_reopen()

    def _check_existing_lines(self):
        """Revisa qué líneas ya existen en el sistema (en este mismo diario)"""
        if not self.line_ids:
            return
            
        StatementLine = self.env['account.bank.statement.line']
        
        # Buscar líneas existentes en el diario seleccionado
        # Extraemos fechas mínimas y máximas para acotar la búsqueda
        valid_dates = [l.date for l in self.line_ids if l.date]
        if not valid_dates:
            return
            
        min_date = min(valid_dates)
        max_date = max(valid_dates)
        
        existing_lines = StatementLine.search([
            ('journal_id', '=', self.journal_id.id),
            ('date', '>=', min_date),
            ('date', '<=', max_date),
        ])
        
        # Construir hashes para las líneas existentes
        # Nota: account.bank.statement.line no tiene campo `balance` nativo que podamos usar fácilmente
        # Odoo calcula el running_balance, pero depende del orden.
        # Por lo tanto, si nuestro formato depende del saldo, puede que en la primera importación funcione bien, 
        # pero para comparar existentes usaremos amount, date, label y payment_ref si existe.
        
        # Por seguridad, si el banco tiene Saldo, intentamos ver si guardamos ese saldo en alguna parte, 
        # pero como en Odoo 18 no está por defecto en el modelo de línea, nos limitaremos a Date, Amount.
        # Si Amount y Date coinciden, compararemos la Etiqueta (payment_ref).
        
        existing_hashes = set()
        for el in existing_lines:
            amount_str = f"{el.amount:.2f}"
            date_str = str(el.date)
            # Para mayor certeza, construiremos hashes flexibles: 
            # 1. Sólo Date + Amount
            # 2. Date + Amount + Label
            existing_hashes.add(f"{date_str}_{amount_str}")
            if el.payment_ref:
                existing_hashes.add(f"{date_str}_{amount_str}_{el.payment_ref}")

        # Check existing and mark in memory
        for line in self.line_ids.filtered(lambda l: l.status == 'ready'):
            # Construimos los equivalentes para la línea del wizard
            h1 = f"{line.date}_{line.amount:.2f}"
            h2 = f"{line.date}_{line.amount:.2f}_{line.label}"
            
            # Si coinciden en Date, Amount, y Label, es casi seguro un duplicado.
            if h2 in existing_hashes:
                line.status = 'exists'
                line.to_import = False
                line.error_message = 'Línea idéntica ya existe en Odoo.'
            # Si el banco tiene muchas transacciones el mismo día por el mismo monto pero distinta etiqueta,
            # h1 podría dar falsos positivos. Solo usaremos h2 (Etiqueta).
            # Idealmente, guardaremos el "hash" original en un campo custom de account.bank.statement.line 
            # si quisiéramos usar el saldo, pero esto requeriría heredar el modelo.
            # Como aproximación sin modificar account.bank.statement.line: usamos Date + Amount + Label

    def action_import(self):
        self.ensure_one()
        lines_to_import = self.line_ids.filtered(lambda l: l.status == 'ready' and l.to_import)
        
        if not lines_to_import:
            raise UserError(_("No hay líneas listas para importar."))
            
        Statement = self.env['account.bank.statement']
        StatementLine = self.env['account.bank.statement.line']
        
        statement_name = f"Extracto {self.bank_id.name or 'Manual'} - {fields.Date.context_today(self)}"
        new_statement = Statement.create({
            'name': statement_name,
            'journal_id': self.journal_id.id,
            'date': fields.Date.context_today(self),
        })

        create_vals = []
        for line in lines_to_import:
            create_vals.append({
                'date': line.date,
                'payment_ref': line.label or 'Extracto Importado',
                'amount': line.amount,
                'journal_id': self.journal_id.id,
                'statement_id': new_statement.id,
            })
            
        if create_vals:
            new_lines = StatementLine.create(create_vals)
            
            # Crear historial
            history = self.env['bank.statement.import.history'].create({
                'name': f"Importación {self.bank_id.name or 'Manual'} - {fields.Date.today()}",
                'filename': self.filename,
                'file_data': self.file_data,
                'bank_id': self.bank_id.id,
                'journal_id': self.journal_id.id,
                'statement_id': new_statement.id,
                'statement_line_ids': [(6, 0, new_lines.ids)],
            })
            
            self.state = 'done'
            return {
                'name': 'Historial de Importación',
                'type': 'ir.actions.act_window',
                'res_model': 'bank.statement.import.history',
                'view_mode': 'form',
                'res_id': history.id,
            }
            
        self.state = 'done'
        return self._get_action_reopen()

    def action_reset(self):
        self.line_ids.unlink()
        self.state = 'upload'
        return self._get_action_reopen()
