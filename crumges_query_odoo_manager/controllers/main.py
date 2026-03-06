from odoo import http, fields, _
from odoo.http import request
import io
import xlsxwriter

class QueryManagerController(http.Controller):

    @http.route('/query_manager/export_excel/<int:query_id>', type='http', auth='user')
    def export_excel(self, query_id, **kw):
        query_record = request.env['query.manager'].browse(query_id)
        
        if not query_record.exists():
            return request.not_found()

        # Seguridad extra en controlador
        if not request.env.user.has_group('crumges_query_odoo_manager.group_query_manager_admin') and query_record.query_type != 'consulta':
            return request.make_response("No tienes permisos para exportar esta consulta", headers=[('Content-Type', 'text/plain')])

        # Extraer data (sudo porque el user comun quiza no puede guardar la ejecucion)
        headers, datas = query_record.sudo()._get_result_from_query(query_record.query_text)

        # Crear archivo excel en memoria
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Resultados')

        # Estilos
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'valign': 'vcenter'
        })
        
        meta_format = workbook.add_format({
            'italic': True,
            'font_color': '#555555',
            'valign': 'vcenter'
        })

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#f8f9fa',
            'border': 1,
            'valign': 'vcenter'
        })
        
        index_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'valign': 'vcenter'
        })
        
        cell_format_odd = workbook.add_format({'border': 1, 'bg_color': '#ffffff', 'valign': 'vcenter'})
        cell_format_even = workbook.add_format({'border': 1, 'bg_color': '#eef9fd', 'valign': 'vcenter'})

        # Escribir Metadatos (Título, fecha, usuario)
        worksheet.merge_range('A1:J1', f"Consulta: {query_record.name}", title_format)
        
        tz = request.env.user.tz or 'UTC'
        now = fields.Datetime.context_timestamp(request.env.user, fields.Datetime.now())
        fecha_str = now.strftime('%d/%m/%Y %H:%M:%S')
        
        worksheet.merge_range('A2:J2', f"Exportado el: {fecha_str} | Por: {request.env.user.name}", meta_format)

        # Escribir cabeceras (ahora empiezan en la fila 3)
        row_offset = 3
        worksheet.write(row_offset, 0, '#', header_format)
        for col_num, header in enumerate(headers):
            worksheet.write(row_offset, col_num + 1, str(header), header_format)

        # Escribir datos
        if datas:
            for row_num, row_data in enumerate(datas):
                actual_row = row_offset + row_num + 1
                cell_format = cell_format_even if actual_row % 2 == 0 else cell_format_odd
                
                # Escribir índice
                worksheet.write(actual_row, 0, row_num + 1, index_format)
                
                # Escribir datos
                for col_num, cell_data in enumerate(row_data):
                    val = str(cell_data) if cell_data is not None else ''
                    worksheet.write(actual_row, col_num + 1, val, cell_format)

        # Ajuste de anchura de columnas empírico pero útil
        worksheet.set_column(0, 0, 5) # Col #
        if headers:
            worksheet.set_column(1, len(headers), 20)

        workbook.close()
        output.seek(0)
        
        # Nombre archivo
        filename = f"Consulta_{query_record.id}_{query_record.query_type}.xlsx"

        response = request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )
        return response
