# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
from lxml import etree
import json

class Base(models.AbstractModel):
    _inherit = 'base'
    
    dynamic_relation_data = fields.Text(compute='_compute_dynamic_relation_data', default="{}")

    def _compute_dynamic_relation_data(self):
        for rec in self:
            result = {}
            if not rec.id:
                rec.dynamic_relation_data = "{}"
                continue
                
            relations = self.env['crumges.relation.type'].sudo().search([
                '|', ('model_a_id.model', '=', self._name), ('model_b_id.model', '=', self._name)
            ])
            for rel in relations:
                is_model_a = (rel.model_a_id.model == self._name)
                # Check visibility
                if is_model_a and not rel.show_in_model_a:
                    continue
                if not is_model_a and not rel.show_in_model_b:
                    continue
                
                my_domain_str = rel.domain_a if is_model_a else rel.domain_b
                if my_domain_str and my_domain_str != '[]':
                    try:
                        my_domain = safe_eval(my_domain_str)
                        if not rec.filtered_domain(my_domain):
                            continue
                    except Exception:
                        continue
                
                # We need to query the target model for matching links
                links = self.env['crumges.relation.link'].sudo().search([
                    ('relation_type_id', '=', rel.id),
                    ('res_id_a' if is_model_a else 'res_id_b', '=', rec.id)
                ])
                target_ids = links.mapped('res_id_b' if is_model_a else 'res_id_a')
                if not target_ids:
                    result[str(rel.id)] = {'count': 0, 'value': 0}
                    continue
                
                target_model_name = rel.model_b_id.model if is_model_a else rel.model_a_id.model
                target_model = self.env[target_model_name].sudo().with_context(active_test=False)
                
                base_domain = [('id', 'in', target_ids)]
                target_domain_str = rel.domain_b if is_model_a else rel.domain_a
                if target_domain_str and target_domain_str != '[]':
                    try:
                        target_domain = safe_eval(target_domain_str)
                        from odoo.osv import expression
                        base_domain = expression.AND([base_domain, target_domain])
                    except Exception:
                        pass
                
                stat_type = rel.stat_type_a if is_model_a else rel.stat_type_b
                if stat_type == 'count':
                    count = target_model.search_count(base_domain)
                    result[str(rel.id)] = {'count': count, 'value': count}
                else:
                    sum_field = rel.sum_field_a_id if is_model_a else rel.sum_field_b_id
                    if sum_field:
                        # read_group to sum the field
                        groups = target_model.read_group(base_domain, [sum_field.name], [])
                        sum_val = groups[0].get(sum_field.name, 0.0) if groups else 0.0
                        
                        # Apply monetary formatting if applicable?
                        currency_id = False
                        if 'currency_id' in target_model._fields:
                            first_rec = target_model.search(base_domain, limit=1)
                            if first_rec:
                                currency_id = first_rec.currency_id
                        
                        if currency_id:
                            # simple format
                            display_val = f"{currency_id.symbol} {sum_val:,.2f}"
                        else:
                            display_val = f"{sum_val:,.2f}"
                            
                        result[str(rel.id)] = {'count': target_model.search_count(base_domain), 'value': sum_val, 'display_value': display_val}
                    else:
                        result[str(rel.id)] = {'count': 0, 'value': 0}
            
            rec.dynamic_relation_data = json.dumps(result)

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)
        
        if view_type == 'form':
            # Check if this model is part of any active relation
            relations = self.env['crumges.relation.type'].sudo().search([
                '|', ('model_a_id.model', '=', self._name), ('model_b_id.model', '=', self._name)
            ])
            if relations:
                # En Odoo 17+, arch ya es un objeto lxml.etree._Element
                button_box = arch.xpath("//div[@name='button_box']")
                if button_box:
                    for rel in relations:
                        is_model_a = (rel.model_a_id.model == self._name)
                        
                        # Check visibility
                        if is_model_a and not rel.show_in_model_a:
                            continue
                        if not is_model_a and not rel.show_in_model_b:
                            continue
                            
                        icon = rel.icon_a_to_b if is_model_a else rel.icon_b_to_a
                        if not icon:
                            icon = 'fa-link'
                        label = rel.label_a_to_b if is_model_a else rel.label_b_to_a
                        hide_if_zero = rel.hide_if_zero_a if is_model_a else rel.hide_if_zero_b
                        
                        button = etree.Element('button', {
                            'class': 'oe_stat_button',
                            'icon': icon,
                            'type': 'object',
                            'name': 'action_open_dynamic_relations',
                            'context': str({'default_relation_type_id': rel.id}),
                        })
                        
                        # Inject the generic JSON field with our custom widget
                        field_options = {
                            'key': str(rel.id),
                            'label': label,
                            'hide_if_zero': hide_if_zero,
                        }
                        field = etree.Element('field', {
                            'name': 'dynamic_relation_data',
                            'widget': 'json_statinfo',
                            'options': str(field_options)
                        })
                        
                        button.append(field)
                        button_box[0].append(button)
        return arch, view

    def action_open_dynamic_relations(self):
        self.ensure_one()
        rel_type_id = self.env.context.get('default_relation_type_id')
        if not rel_type_id:
            return
            
        rel_type = self.env['crumges.relation.type'].browse(rel_type_id)
        is_model_a = (rel_type.model_a_id.model == self._name)
        
        target_model_name = rel_type.model_b_id.model if is_model_a else rel_type.model_a_id.model
        
        # Find related IDs
        domain = [('type_id', '=', rel_type.id)]
        if is_model_a:
            domain += [('res_model_a', '=', self._name), ('res_id_a', '=', self.id)]
        else:
            domain += [('res_model_b', '=', self._name), ('res_id_b', '=', self.id)]
            
        links = self.env['crumges.relation.link'].search(domain)
        target_ids = links.mapped('res_id_b' if is_model_a else 'res_id_a')
        
        # Add target domain if configured
                        
        action = {
            'name': rel_type.label_a_to_b if is_model_a else rel_type.label_b_to_a,
            'type': 'ir.actions.act_window',
            'res_model': target_model_name,
            'view_mode': 'list,form',
            'domain': [('id', 'in', target_ids)],
            'context': {
                'default_relation_wizard_type_id': rel_type.id,
                'default_relation_wizard_source_model': self._name,
                'default_relation_wizard_source_id': self.id,
            }
        }
        
        target_domain_str = rel_type.domain_b if is_model_a else rel_type.domain_a
        if target_domain_str and target_domain_str != '[]':
            from odoo.tools.safe_eval import safe_eval
            try:
                target_domain = safe_eval(target_domain_str)
                # Combine domains using AND
                from odoo.osv import expression
                action['domain'] = expression.AND([action['domain'], target_domain])
            except Exception:
                pass
                
        return action
