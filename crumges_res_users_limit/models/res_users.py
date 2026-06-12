from odoo import models, api, _
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        self.env.cr.execute("SELECT count(id) FROM res_users WHERE share=false AND active=true")
        count_before = self.env.cr.fetchone()[0]

        users = super(ResUsers, self).create(vals_list)
        
        self.env.cr.execute("SELECT count(id) FROM res_users WHERE share=false AND active=true")
        count_after = self.env.cr.fetchone()[0]

        if count_after > count_before:
            self.sudo()._check_internal_user_limit()
            
        return users

    def write(self, vals):
        # Contamos cuántos usuarios internos hay ANTES de la modificación
        self.env.cr.execute("SELECT count(id) FROM res_users WHERE share=false AND active=true")
        count_before = self.env.cr.fetchone()[0]

        res = super(ResUsers, self).write(vals)
        
        # Contamos cuántos hay DESPUÉS
        self.env.cr.execute("SELECT count(id) FROM res_users WHERE share=false AND active=true")
        count_after = self.env.cr.fetchone()[0]

        # Si la cantidad de usuarios internos aumentó, verificamos el límite
        if count_after > count_before:
            self.sudo()._check_internal_user_limit()
                
        return res

    @api.model
    def _check_internal_user_limit(self):

        license_record = self.env['res.users.license'].search([], limit=1)
        limit = license_record.max_licenses if license_record else 0
        
        if limit > 0:
            count = self.search_count([('share', '=', False), ('active', '=', True)])
            if count > limit:
                raise ValidationError(_(
                    "Se ha alcanzado el límite máximo de %(limit)s usuarios internos permitidos. "
                    "Por favor, elimine o archive usuarios existentes para poder crear o habilitar nuevos usuarios."
                ) % {'limit': limit})
