from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    name_type = fields.Selection([
        ('manual', 'Manual Name'),
        ('auto_composed', 'Auto-generated Name')
    ], default='manual', required=True, tracking=True)

    purpose_id = fields.Many2one('task.purpose', string='Purpose')
    additional_info = fields.Char(string='Additional Info', help='E.g. License Plate, Internal No., etc.')

    is_name_frozen = fields.Boolean(default=False)

    @api.onchange('name_type', 'purpose_id', 'additional_info')
    def _compute_auto_name_onchange(self):
        for task in self:
            if task.name_type == 'auto_composed':
                task.name = task._get_composed_name()

    def _get_composed_name(self):
        self.ensure_one()
        task_id = self.id or _('New')
        purpose = self.purpose_id.name or ''
        info = self.additional_info or ''
        # Logic: [ID] - Purpose - Info
        return f"[{task_id}] - {purpose} - {info}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
             if vals.get('name_type') == 'auto_composed' and not vals.get('name'):
                 # Provide dummy name to pass NOT NULL constraint
                 vals['name'] = _("[New] - %s - %s", vals.get('purpose_id', ''), vals.get('additional_info', ''))
                 
        tasks = super().create(vals_list)
        for task in tasks:
            if task.name_type == 'auto_composed':
                # Update name with real ID after create
                task.name = task._get_composed_name()
                task.is_name_frozen = True
        return tasks

    def write(self, vals):
        res = super().write(vals)
        for task in self:
            if task.name_type == 'auto_composed' and any(f in vals for f in ['purpose_id', 'additional_info', 'name_type']):
                 task.name = task._get_composed_name()
            
            # Update frozen state
            if 'name_type' in vals:
                task.is_name_frozen = (task.name_type == 'auto_composed')
        return res
