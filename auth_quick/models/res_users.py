# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
import logging

from odoo import fields, models
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    auth_quick_token = fields.Char()

    def _check_credentials(self, credential, env):
        try:
            return super(ResUsers, self)._check_credentials(credential, env)
        except AccessDenied:
            password = credential.get('password') if isinstance(credential, dict) else credential
            res = self.sudo().search(
                [("id", "=", self.env.uid), ("auth_quick_token", "=", password)]
            )
            if not res:
                raise
            res.sudo().write({"auth_quick_token": False})
            return {'uid': self.env.uid, 'auth_method': 'auth_quick'}
