# -*- coding: utf-8 -*-
"""
Extensión del modelo project.task para modificar la visibilidad
predeterminada de las subtareas en Odoo 18
"""

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    """
    Hereda y extiende el modelo project.task para modificar
    el comportamiento predeterminado de la visibilidad de subtareas
    """
    _inherit = 'project.task'
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        Override del método create para asegurar que las subtareas
        se creen con visibilidad activada por defecto
        """
        for vals in vals_list:
            # Si es una subtarea (tiene parent_id)
            if vals.get('parent_id'):
                # Intentar establecer todos los posibles campos de visibilidad a True
                # Odoo 18 puede usar diferentes nombres de campo según la configuración
                
                # Campo principal de visibilidad en Odoo 18
                if 'display_in_project' not in vals:
                    vals['display_in_project'] = True
                
                # Otros posibles nombres de campo (por compatibilidad)
                visibility_fields = [
                    'is_visible',
                    'show_in_kanban',
                    'show_in_list', 
                    'subtask_visible',
                    'child_visible'
                ]
                
                for field in visibility_fields:
                    # Solo establecer si el campo existe en el modelo
                    if field in self._fields and field not in vals:
                        vals[field] = True
                
                # Si hay un campo inverso (ocultar), establecerlo a False
                hide_fields = [
                    'is_hidden',
                    'hide_from_view',
                    'hide_subtask'
                ]
                
                for field in hide_fields:
                    if field in self._fields and field not in vals:
                        vals[field] = False
                
                _logger.info(f"Creando subtarea con visibilidad activada por defecto")
        
        # Llamar al método padre para crear las tareas
        return super(ProjectTask, self).create(vals_list)
    
    @api.model
    def default_get(self, fields_list):
        """
        Override para establecer valores por defecto cuando se crea
        una nueva subtarea desde la interfaz
        """
        defaults = super(ProjectTask, self).default_get(fields_list)
        
        # Si estamos creando una subtarea (verificar contexto)
        if self._context.get('default_parent_id'):
            # Establecer visibilidad por defecto para todos los campos posibles
            visibility_fields = {
                'display_in_project': True,
                'is_visible': True,
                'show_in_kanban': True,
                'show_in_list': True,
                'subtask_visible': True,
                'child_visible': True,
                'is_hidden': False,
                'hide_from_view': False,
                'hide_subtask': False,
            }
            
            for field, value in visibility_fields.items():
                if field in fields_list and field in self._fields:
                    defaults[field] = value
            
            _logger.info("Valores por defecto de visibilidad establecidos para nueva subtarea")
        
        return defaults
    
    def write(self, vals):
        """
        Override opcional del método write para logging
        """
        # Si se está modificando la visibilidad de subtareas
        if self.filtered(lambda t: t.parent_id) and any(
            field in vals for field in ['display_in_project', 'is_visible', 'hide_subtask']
        ):
            _logger.debug(f"Modificando visibilidad de subtarea(s): {self.mapped('name')}")
        
        return super(ProjectTask, self).write(vals)


# Intentar parchear el campo display_in_project si existe
def _patch_display_field():
    """
    Función para parchear el campo display_in_project si existe
    Se ejecuta al cargar el módulo
    """
    try:
        # Intentar obtener el modelo
        Task = models.Model._get('project.task')
        if Task and hasattr(Task, '_fields'):
            # Buscar el campo display_in_project
            if 'display_in_project' in Task._fields:
                field = Task._fields['display_in_project']
                # Si es un campo Boolean, cambiar su default
                if isinstance(field, fields.Boolean):
                    original_default = field.default
                    field.default = True
                    _logger.info(f"Campo display_in_project parcheado: default cambió de {original_default} a True")
    except Exception as e:
        _logger.debug(f"No se pudo parchear el campo display_in_project: {e}")


# Ejecutar el parche al cargar el módulo
_patch_display_field()