from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _logger.info("🧪 Analizando creación de lead: %s", vals)

            # Saltar si ya está definido como lead
            if vals.get('type') == 'lead':
                continue

            force_lead = False

            # 🔎 Detectar por source_id
            source_id = vals.get('source_id')
            if source_id and isinstance(source_id, int):
                source = self.env['utm.source'].browse(source_id)
                if source.exists() and 'bot' in (source.name or '').lower():
                    force_lead = True
                    _logger.info("✅ Detectado origen bot por source: %s", source.name)

            # 🔎 Detectar por tag_ids (etiquetas con 'bot')
            tag_ids = vals.get('tag_ids', [])
            if isinstance(tag_ids, list):
                for command in tag_ids:
                    if isinstance(command, (list, tuple)) and len(command) > 1:
                        tag = self.env['crm.tag'].browse(command[1])
                        if tag.exists() and 'bot' in (tag.name or '').lower():
                            force_lead = True
                            _logger.info("✅ Detectado origen bot por etiqueta: %s", tag.name)
                            break

            # 🔎 Detectar por canal de chat (Livechat)
            if vals.get('channel_id'):
                force_lead = True
                _logger.info("✅ Canal de chat detectado (channel_id: %s), forzando tipo 'lead'", vals.get('channel_id'))

            # ✅ Forzar tipo 'lead'
            if force_lead:
                vals['type'] = 'lead'
                _logger.info("✅ Tipo forzado a 'lead'")

        return super().create(vals_list)
