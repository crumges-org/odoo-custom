from odoo import models, fields, api

class ResUsersLicense(models.Model):
    _name = "res.users.license"
    _description = "Tablero de Gestión de Licencias"

    name = fields.Char(default="Tablero de Licencias", readonly=True)
    
    max_licenses = fields.Integer(
        string="Límite Máximo de Licencias",
        default=0,
        help="0 significa sin límite. Si defines un número, no se podrán crear más usuarios que superen esta cantidad."
    )

    active_internal_users = fields.Integer(
        string="Internos Activos", 
        compute="_compute_license_stats"
    )
    portal_users = fields.Integer(
        string="Usuarios de Portal", 
        compute="_compute_license_stats"
    )
    occupied_licenses = fields.Integer(
        string="Licencias Ocupadas", 
        compute="_compute_license_stats"
    )
    available_licenses = fields.Integer(
        string="Licencias Disponibles", 
        compute="_compute_license_stats"
    )

    is_user_limit_editor = fields.Boolean(
        compute="_compute_is_user_limit_editor"
    )

    def _compute_is_user_limit_editor(self):
        has_group = self.env.user.has_group('crumges_res_users_limit.group_edit_user_limit')
        for record in self:
            record.is_user_limit_editor = has_group

    @api.depends('max_licenses')
    def _compute_license_stats(self):
        internal_count = self.env['res.users'].search_count([
            ('share', '=', False),
            ('active', '=', True)
        ])
        portal_count = self.env['res.users'].search_count([
            ('share', '=', True),
            ('active', '=', True)
        ])
        
        for record in self:
            record.active_internal_users = internal_count
            record.portal_users = portal_count
            record.occupied_licenses = internal_count
            
            if record.max_licenses > 0:
                record.available_licenses = record.max_licenses - internal_count
            else:
                record.available_licenses = 0

    @api.model
    def get_dashboard_data(self):
        record = self.search([], limit=1)
        if not record:
            record = self.sudo().create({})
        is_super = self.env.is_superuser()
        return {
            'active_internal_users': record.active_internal_users,
            'portal_users': record.portal_users,
            'occupied_licenses': record.occupied_licenses,
            'available_licenses': record.available_licenses,
            'max_licenses': record.max_licenses,
            'is_user_limit_editor': is_super
        }

    @api.model
    def update_max_licenses(self, new_limit):
        from odoo.exceptions import AccessError
        if not self.env.is_superuser():
            raise AccessError("Solo el Modo Superusuario (OdooBot) puede editar el límite de licencias.")
            
        limit_val = int(new_limit)
        
        record = self.search([], limit=1)
        if not record:
            record = self.sudo().create({})
        record.sudo().write({'max_licenses': limit_val})
        return self.get_dashboard_data()
