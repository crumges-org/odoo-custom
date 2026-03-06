import re
import io
import xlsxwriter
from odoo import api, fields, models, exceptions, _

class QueryManager(models.Model):
    _name = "query.manager"
    _description = "Gestor de Consultas PostgreSQL"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char(string='Nombre o Descripción', required=True, tracking=True)
    active = fields.Boolean(string="Activo", default=True)
    
    query_text = fields.Text(string='Consulta SQL', required=True, help="Escribe la consulta SQL que deseas ejecutar.")
    note = fields.Text(string="Notas", help="Información adicional sobre la consulta, advertencias, etc.")
    
    query_type = fields.Selection([
        ('consulta', 'Consulta (SELECT)'),
        ('creacion', 'Creación (INSERT)'),
        ('edicion', 'Edición (UPDATE)'),
        ('eliminacion', 'Eliminación (DELETE/DROP)')
    ], string='Tipo de Consulta', compute='_compute_query_type', store=True, readonly=True, tracking=True)
    
    rowcount = fields.Char(string='Filas Afectadas/Encontradas', readonly=True)
    html_result = fields.Html(string='Resultados (HTML)', readonly=True)

    def _default_is_query_admin(self):
        return self.env.user.has_group('crumges_query_odoo_manager.group_query_manager_admin')

    is_query_admin = fields.Boolean(compute='_compute_is_query_admin', default=_default_is_query_admin, string='Is Admin')

    @api.depends_context('uid')
    def _compute_is_query_admin(self):
        is_admin = self.env.user.has_group('crumges_query_odoo_manager.group_query_manager_admin')
        for record in self:
            record.is_query_admin = is_admin

    @api.depends('query_text')
    def _compute_query_type(self):
        for record in self:
            if not record.query_text:
                record.query_type = False
                continue
                
            text = record.query_text.strip().upper()
            if text.startswith('SELECT'):
                record.query_type = 'consulta'
            elif text.startswith('INSERT'):
                record.query_type = 'creacion'
            elif text.startswith('UPDATE'):
                record.query_type = 'edicion'
            elif text.startswith('DELETE') or text.startswith('DROP') or text.startswith('TRUNCATE'):
                record.query_type = 'eliminacion'
            else:
                record.query_type = 'consulta' # Default or unhandled complex queries, treated as select

    @api.model_create_multi
    def create(self, vals_list):
        return super(QueryManager, self).create(vals_list)

    def write(self, vals):
        return super(QueryManager, self).write(vals)

    def _get_result_from_query(self, query):
        self = self.sudo()
        headers = []
        datas = []

        if query:
            try:
                self.env.cr.execute(query)
            except Exception as e:
                raise exceptions.UserError(_("Error al ejecutar la consulta:\n%s") % str(e))

            # Solo intentamos hacer fetchall si es un SELECT (que retorna filas) o tiene un RETURNING
            try:
                if self.env.cr.description:
                    headers = [d[0] for d in self.env.cr.description]
                    datas = self.env.cr.fetchall()
            except Exception as e:
                pass # Puede ser un UPDATE/INSERT sin RETURNING que no tiene fetchall

        return headers, datas

    def execute(self):
        for record in self:
            # Control de seguridad: Si no es admin y la query no es 'consulta', no dejar pasar (doble validacion)
            if not self.env.user.has_group('crumges_query_odoo_manager.group_query_manager_admin'):
                if record.query_type != 'consulta':
                    raise exceptions.AccessError(_("No tienes permisos para ejecutar consultas que no sean de lectura (SELECT)."))

            vals = {
                "rowcount": False,
                "html_result": False
            }

            if record.query_text:
                record.sudo().message_post(
                    body=_("Consulta ejecutada."),
                    author_id=self.env.user.partner_id.id
                )

                # Ejecutar
                headers, datas = record._get_result_from_query(record.query_text)

                rowcount = record.env.cr.rowcount
                vals["rowcount"] = _("{0} fila(s) procesada(s)").format(rowcount)

                # Si hay resultados, armar HTML
                if headers and datas:
                    header_html = "<tr><th>#</th>"
                    header_html += "".join(["<th style='border: 1px solid black; padding: 5px; background-color: #f8f9fa;'>"+str(header)+"</th>" for header in headers])
                    header_html += "</tr>"

                    body_html = ""
                    i = 0
                    for data in datas:
                        i += 1
                        body_line = f"<tr style='background-color: {'#eef9fd' if i%2 == 0 else 'white'}'> <td style='border: 1px solid black; padding: 5px; font-weight: bold;'>{i}</td>"
                        for value in data:
                            display_value = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") if value is not None else ''
                            body_line += f"<td style='border: 1px solid #ced4da; padding: 5px;'>{display_value}</td>"
                        body_line += "</tr>"
                        body_html += body_line

                    vals["html_result"] = f"""
                    <table style="text-align: left; width: 100%; border-collapse: collapse; margin-top: 10px;">
                        <thead>
                            {header_html}
                        </thead>
                        <tbody>
                            {body_html}
                        </tbody>
                    </table>
                    """
                elif not datas and record.query_type == 'consulta':
                    vals["html_result"] = _("<p>La consulta no devolvió resultados.</p>")
                else:
                    vals["html_result"] = _("<p>Consulta %s ejecutada correctamente.</p>") % record.query_type

            # Como el usuario ejecutor podría no tener permisos de escritura sobre query.manager
            # usamos sudo() para escribir los resultados de su propia ejecución
            record.sudo().write(vals)


    def export_excel(self):
        self.ensure_one()
        # Verificar permisos básicos si hiciera falta
        if not self.env.user.has_group('crumges_query_odoo_manager.group_query_manager_admin') and self.query_type != 'consulta':
            raise exceptions.AccessError(_("No tienes permisos para exportar consultas que no sean de lectura (SELECT)."))
        
        self.sudo().message_post(
            body=_("Datos exportados a Excel."),
            author_id=self.env.user.partner_id.id
        )

        # En lugar de generar aquí y guardar adjunto, devolvemos accion al controlador HTTP
        return {
            'type': 'ir.actions.act_url',
            'url': f'/query_manager/export_excel/{self.id}',
            'target': 'self',
        }
